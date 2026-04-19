"""
Perfetto 性能数据采集与分析引擎
提供系统级 Trace 录制、解析及多维度指标提取能力
"""

import os
import subprocess
import time
from typing import Tuple, List, Dict, Optional
import pandas as pd


class PerfettoProcessor:
    """
    Trace 数据解析引擎
    封装 Perfetto trace_processor，提供统一的 SQL 查询接口
    """
    
    def __init__(self, trace_path: str):
        """
        构建解析器实例
        
        Parameters:
            trace_path: Trace 文件绝对路径
        """
        self.trace_path = trace_path
        self._trace_processor_path = self._find_trace_processor()
        self._tp = None  # TraceProcessor 实例
        self._initialize_trace_processor()
    
    def _initialize_trace_processor(self):
        """建立 TraceProcessor 连接"""
        try:
            from perfetto.trace_processor import TraceProcessor, TraceProcessorConfig
            
            config = TraceProcessorConfig(
                bin_path=self._trace_processor_path,
                verbose=False
            )
            self._tp = TraceProcessor(trace=self.trace_path, config=config)
        except Exception as e:
            print(f"TraceProcessor 初始化失败: {e}")
            self._tp = None
        
    def _find_trace_processor(self) -> str:
        """定位 trace_processor 可执行文件"""
        # 优先使用项目内的工具
        # __file__ 是当前文件的路径: aw/performance/perfetto_utils.py
        current_file = os.path.abspath(__file__)
        performance_dir = os.path.dirname(current_file)  # aw/performance
        aw_dir = os.path.dirname(performance_dir)         # aw
        project_root = os.path.dirname(aw_dir)            # 项目根目录
        
        possible_paths = [
            os.path.join(project_root, "tools", "perfetto", "trace_processor.exe"),
            os.path.join(project_root, "tools", "perfetto", "trace_processor"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 如果找不到，尝试系统 PATH 中的命令
        return "trace_processor"
    
    def execute_sql(self, sql: str) -> pd.DataFrame:
        """
        执行 Perfetto SQL 查询
        
        Parameters:
            sql: 标准 SQL 查询语句
            
        Returns:
            pandas DataFrame 格式的查询结果集
        """
        if not self._tp:
            print("TraceProcessor 未初始化")
            return pd.DataFrame()
        
        try:
            # 使用 Perfetto Python API 执行查询
            query_result = self._tp.query(sql)
            
            # 将查询结果转换为 DataFrame
            rows = []
            columns = None
            
            for row in query_result:
                # Row 对象通过属性访问，dir() 返回列名
                if columns is None:
                    columns = [x for x in dir(row) if not x.startswith('_')]
                
                row_values = [getattr(row, col) for col in columns]
                rows.append(row_values)
            
            if columns and rows:
                df = pd.DataFrame(rows, columns=columns)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"SQL 执行失败: {e}")
            return pd.DataFrame()
    
    def get_trace_bounds(self) -> Tuple[int, int]:
        """
        提取 Trace 时间边界
        
        Returns:
            (起始时间戳, 结束时间戳)，单位：纳秒
        """
        sql = "SELECT start_ts, end_ts FROM trace_bounds"
        result = self.execute_sql(sql)
        if not result.empty:
            return int(result.iloc[0]['start_ts']), int(result.iloc[0]['end_ts'])
        return 0, 0


class TraceCollector:
    """
    Perfetto 数据采集控制器
    负责 Trace 录制启动、停止及文件管理
    """
    
    # === 性能数据采集类别 ===
    PERFETTO_CATEGORIES = [
        "input",           # 输入事件捕获
        "view",            # UI 视图渲染
        "wm",              # 窗口管理器
        "am",              # Activity 生命周期
        "SurfaceFlinger",  # 显示合成服务
        "RenderEngine",    # GPU 渲染管线
        "gfx",             # 图形子系统
        "app",             # 应用层事件
        "sched",           # CPU 调度信息
        "cpu*",            # CPU 频率与负载
    ]
    
    def __init__(self, device_id: str = None):
        """
        构建采集器实例
        
        Parameters:
            device_id: Android 设备标识符
        """
        self.device_id = device_id
        # 使用系统允许的 Trace 输出路径
        self.trace_path = "/data/misc/perfetto-traces/trace.perfetto-trace"
        # 使用 Android 系统允许的配置路径
        self.config_path = "/data/misc/perfetto-configs/perfetto_config.txt"
        
    def _push_config_via_base64(self, local_config_path: str, device_config_path: str) -> bool:
        """
        通过 base64 编码安全地推送配置文件到设备，避免编码问题
        Args:
            local_config_path: 本地配置文件路径
            device_config_path: 设备上的目标路径
        Returns:
            bool: 推送是否成功
        """
        import base64
        
        try:
            # 读取文件为二进制
            with open(local_config_path, 'rb') as f:
                file_data = f.read()
            
            # Base64 编码
            encoded = base64.b64encode(file_data).decode('ascii')
            
            # 在设备上创建临时文件
            temp_b64 = "/tmp/perfetto_config_b64.txt"
            
            # 分块写入 base64 数据（避免命令行过长）
            chunk_size = 500
            chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]
            
            # 清空临时文件
            subprocess.run(f'adb -s {self.device_id} shell "echo -n > {temp_b64}"', 
                          shell=True, capture_output=True)
            
            # 逐块追加
            for chunk in chunks:
                cmd = f'adb -s {self.device_id} shell "echo -n \'{chunk}\' >> {temp_b64}"'
                subprocess.run(cmd, shell=True, capture_output=True)
            
            # 解码 base64 到目标文件
            result = subprocess.run(
                f'adb -s {self.device_id} shell "base64 -d {temp_b64} > {device_config_path} && rm -f {temp_b64}"',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"[OK] 配置文件已通过 base64 安全推送到: {device_config_path}")
                return True
            else:
                print(f"[ERROR] base64 推送失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] base64 推送异常: {e}")
            return False
    
    def start_recording(self, duration: int = 30, buffer_size: int = 32768, config_type: str = "standard"):
        """
        开始录制 Perfetto 日志
        Args:
            duration: 录制时长（秒）
            buffer_size: 缓冲区大小（KB）
            config_type: 配置类型 ("standard"=标准配置, "cpu_load"=CPU负载分析)
        """
        # 1. 选择配置文件
        # __file__ = aw/performance/perfetto_utils.py
        current_file = os.path.abspath(__file__)
        performance_dir = os.path.dirname(current_file)  # aw/performance
        aw_dir = os.path.dirname(performance_dir)         # aw
        project_root = os.path.dirname(aw_dir)            # 项目根目录
        
        config_dir = os.path.join(project_root, "config", "perfetto_configs")
        
        config_files = {
            "standard": os.path.join(config_dir, "android.txt"),  # 使用标准配置
            "cpu_load": os.path.join(config_dir, "android_cpu_load.txt"),
        }
        
        config_file = config_files.get(config_type)
        
        if config_file and os.path.exists(config_file):
            # 使用预定义的配置文件
            with open(config_file, 'r', encoding='utf-8') as f:
                config_content = f.read()
            print(f"[OK] 使用预定义配置: {config_type} ({os.path.basename(config_file)})")
        else:
            #  fallback 到动态生成配置
            print(f"[WARN] 配置文件不存在，使用默认配置")
            config_content = self._generate_default_config(buffer_size)
        
        # 2. 推送配置文件到设备（使用系统允许的路径）
        temp_config = "temp_perfetto_config.txt"
        with open(temp_config, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # 先创建目录（如果不存在）
        cmd_mkdir_config = f"adb -s {self.device_id} shell mkdir -p /data/misc/perfetto-configs"
        cmd_mkdir_trace = f"adb -s {self.device_id} shell mkdir -p /data/misc/perfetto-traces"
        subprocess.run(cmd_mkdir_config, shell=True, check=False)
        subprocess.run(cmd_mkdir_trace, shell=True, check=False)
        
        # 使用 base64 安全推送配置文件，避免编码问题
        device_config_target = "/data/misc/perfetto-configs/perfetto_config.txt"
        push_success = self._push_config_via_base64(temp_config, device_config_target)
        
        # 清理临时文件
        if os.path.exists(temp_config):
            os.remove(temp_config)
        
        if push_success:
            self.config_path = device_config_target
        else:
            print("[WARN] base64 推送失败，尝试备用方案...")
            # 备用方案：直接通过 adb push
            cmd_push = f"adb -s {self.device_id} push {temp_config} {device_config_target}"
            result = subprocess.run(cmd_push, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"[ERROR] 配置文件推送失败: {result.stderr}")
                print("尝试使用备用路径...")
                # 最后的备用方案：直接通过 shell 写入
                escaped_config = config_content.replace('"', '\\"').replace('\n', '\\n')
                cmd_write = f'adb -s {self.device_id} shell "echo \"{escaped_config}\" > /data/local/tmp/perfetto_config.txt"'
                subprocess.run(cmd_write, shell=True, check=False)
                self.config_path = "/data/local/tmp/perfetto_config.txt"
            else:
                self.config_path = device_config_target
        
        # 3. 开始录制（使用正确的配置路径和 --txt 参数）
        # 先停止任何正在运行的 perfetto 进程
        subprocess.run(f'adb -s {self.device_id} shell "killall -2 perfetto 2>/dev/null || true"', shell=True, capture_output=True)
        time.sleep(1)
        
        # 删除旧的 trace 文件
        subprocess.run(f'adb -s {self.device_id} shell "rm -f {self.trace_path}"', shell=True, capture_output=True)
        
        # 启动录制（使用 nohup 确保后台运行）
        cmd_record = f'adb -s {self.device_id} shell "nohup perfetto --txt -c {self.config_path} -o {self.trace_path} > /dev/null 2>&1 &"'
        subprocess.Popen(cmd_record, shell=True)
        
        # 等待录制真正开始
        print(f"[WAIT] 等待 Perfetto 录制启动...")
        time.sleep(3)
        
        # 验证录制是否成功启动
        result = subprocess.run(f'adb -s {self.device_id} shell "ps | grep perfetto"', shell=True, capture_output=True, text=True)
        if 'perfetto' in result.stdout:
            print(f"[OK] Perfetto 录制已启动，时长：{duration}秒")
            print(f"   配置文件: {self.config_path}")
            print(f"   Trace 文件: {self.trace_path}")
        else:
            print(f"[WARN] 警告：Perfetto 进程未检测到，可能启动失败")
            print(f"   尝试检查设备日志...")
    
    def _generate_default_config(self, buffer_size: int) -> str:
        """生成默认配置（fallback）"""
        return f"""
buffers {{
    size_kb: {buffer_size}
}}
write_into_file: true
flush_period_ms: 1000
data_sources: {{
    config {{
        name: "android.input"
        target_buffer: 0
    }}
}}
data_sources: {{
    config {{
        name: "android.view"
        target_buffer: 0
    }}
}}
data_sources: {{
    config {{
        name: "android.app.wm"
        target_buffer: 0
    }}
}}
""".strip()
        
    def stop_recording(self, output_dir: str = "./allure-results", test_name: str = None) -> str:
        """
        停止录制并下载日志
        Args:
            output_dir: 输出目录
            test_name: 测试用例名称（可选），用于生成文件名
        Returns:
            本地 trace 文件路径
        """
        # 1. 停止录制
        print("[WAIT] 停止 Perfetto 录制...")
        subprocess.run(f"adb -s {self.device_id} shell killall -2 perfetto", shell=True, capture_output=True)
        time.sleep(3)  # 等待写入完成
        
        # 验证 trace 文件是否存在且有内容
        result = subprocess.run(f'adb -s {self.device_id} shell "ls -l {self.trace_path}"', shell=True, capture_output=True, text=True)
        if self.trace_path in result.stdout:
            # 提取文件大小
            import re
            match = re.search(r'(\d+)\s+', result.stdout)
            if match:
                file_size = int(match.group(1))
                print(f"[OK] Trace 文件大小: {file_size / 1024:.2f} KB")
                if file_size < 1000:  # 小于 1KB 认为有问题
                    print(f"[WARN] 警告：Trace 文件过小，可能录制失败")
        else:
            print(f"[WARN] 警告：Trace 文件不存在")
        
        # 2. 生成带时间戳和用例名的文件名
        os.makedirs(output_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if test_name:
            # 清理用例名中的非法字符
            safe_test_name = "".join(c for c in test_name if c.isalnum() or c in ('_', '-', '.'))
            filename = f"trace_{safe_test_name}_{timestamp}.perfetto-trace"
        else:
            filename = f"trace_{timestamp}.perfetto-trace"
        
        local_path = os.path.join(output_dir, filename)
        cmd_pull = f"adb -s {self.device_id} pull {self.trace_path} {local_path}"
        subprocess.run(cmd_pull, shell=True, check=True)
        
        print(f"[OK] Perfetto 日志已保存到：{local_path}")
        return local_path
    
    def parse_trace(self, trace_path: str) -> PerfettoProcessor:
        """
        解析 Perfetto 日志
        Args:
            trace_path: trace 文件路径
        Returns:
            PerfettoProcessor 实例
        """
        return PerfettoProcessor(trace_path)
    
    # === CPU 相关方法 ⭐
    @staticmethod
    def query_cpu_frequency_metrics(processor: PerfettoProcessor, start_ns: int, end_ns: int) -> pd.DataFrame:
        """
        查询 CPU 频率性能指标
        
        Parameters:
            processor: Trace 解析器
            start_ns: 查询起始时间
            end_ns: 查询终止时间
            
        Returns:
            CPU 频率数据 DataFrame（包含 ts, dur, freq_khz, cpu）
        """
        sql = f"""
        SELECT ts, dur, freq_khz, cpu
        FROM cpu_freq
        WHERE ts >= {start_ns} AND ts < {end_ns}
        ORDER BY ts
        """
        return processor.execute_sql(sql)
    
    @staticmethod
    def analyze_thread_cpu_consumption(processor: PerfettoProcessor, start_ns: int, end_ns: int, 
                                      package_name: Optional[str] = None) -> pd.DataFrame:
        """
        分析线程级 CPU 资源消耗
        
        Parameters:
            processor: Trace 解析器
            start_ns: 分析起始时间（纳秒）
            end_ns: 分析终止时间（纳秒）
            package_name: 应用包名过滤器（可选）
            
        Returns:
            DataFrame 包含进程名、线程名、总耗时及调度次数
        """
        filter_clause = ""
        if package_name:
            filter_clause = f"WHERE process.name = '{package_name}'"
            
        sql = f"""
        WITH timestamp AS (SELECT {start_ns} AS start_time, {end_ns} AS end_time)
        SELECT 
            process.name AS process_name,
            thread.name AS thread_name,
            SUM(dur) AS total_dur,
            COUNT(*) AS sched_count
        FROM sched
        JOIN thread ON sched.utid = thread.id
        JOIN process ON thread.upid = process.id
        {filter_clause}
        GROUP BY process.name, thread.name
        ORDER BY total_dur DESC
        """
        return processor.execute_sql(sql)
    
    @staticmethod
    def retrieve_trace_boundaries(processor: PerfettoProcessor) -> Tuple[int, int]:
        """
        检索 Trace 时间边界
        
        Parameters:
            processor: Trace 解析器
            
        Returns:
            (起始时间戳, 结束时间戳)，单位：纳秒
        """
        return processor.get_trace_bounds()
    
    @staticmethod
    def extract_input_queue_timestamp(processor: PerfettoProcessor, action_ts: int = None,
                                     start_ts: int = None, end_ts: int = None,
                                     location: int = 0) -> Optional[int]:
        """
        提取输入事件队列（IQ）时间标记
        
        Parameters:
            processor: Trace 解析器实例
            action_ts: 目标动作时间戳（用于过滤）
            start_ts: 查询起始边界
            end_ts: 查询结束边界
            location: 索引位置（0=首个，-1=末尾）
            
        Returns:
            IQ 事件时间戳（纳秒），未找到返回 None
        """
        try:
            time_str = ""
            if start_ts is not None and end_ts is not None:
                time_str = f"AND c.ts >= {start_ts} AND c.ts <= {end_ts}"
            
            sql = f"""
            SELECT p.name AS process_name, p.pid AS pid, T.name AS name, 
                   c.ts AS ts, c.value AS value 
            FROM process_counter_track AS T
            LEFT JOIN process AS p ON p.upid = T.upid
            LEFT JOIN counter AS c ON c.track_id = T.id
            WHERE T.name = 'iq' {time_str}
            ORDER BY c.ts
            """
            result = processor.execute_sql(sql)
            
            if result.empty:
                return None
            
            # 筛选 value=1 的 IQ 事件（上升沿）
            iq_list = []
            for _, row in result.iterrows():
                if row['value'] == 1:
                    if action_ts is None or row['ts'] <= action_ts:
                        iq_list.append(int(row['ts']))
            
            if not iq_list:
                return None
            
            # 返回指定位置的 IQ
            if location >= 0:
                idx = min(location, len(iq_list) - 1)
            else:
                idx = max(0, len(iq_list) + location)
            
            return iq_list[idx]
        except Exception as e:
            print(f"获取 IQ 失败: {e}")
            return None
    
    @staticmethod
    def locate_buffer_falling_edge(processor: PerfettoProcessor, process_name: str,
                                  start_ts: int = None, end_ts: int = None) -> Optional[int]:
        """
        定位 Buffer 传输信号的下降沿时刻
        
        Parameters:
            processor: Trace 解析器实例
            process_name: 目标渲染进程标识
            start_ts: 搜索起始时间
            end_ts: 搜索结束时间
            
        Returns:
            首个下降沿时间戳（纳秒），未找到返回 None
        """
        try:
            time_str = ""
            if start_ts is not None and end_ts is not None:
                time_str = f"AND c.ts >= {start_ts} AND c.ts <= {end_ts}"
            
            # 根据是否指定进程名构建不同的 SQL
            if process_name:
                # 指定了进程名，只查找该进程的 Buffer
                sql = f"""
                SELECT p.name AS process_name, p.pid AS pid, T.name AS name,
                       c.ts AS ts, c.value AS value 
                FROM process_counter_track AS T
                LEFT JOIN process AS p ON p.upid = T.upid
                LEFT JOIN counter AS c ON c.track_id = T.id
                WHERE p.name = '/system/bin/surfaceflinger'
                AND T.name LIKE 'BufferTX - {process_name}%'
                {time_str}
                ORDER BY c.ts
                """
            else:
                # 未指定进程名，查找所有进程的 Buffer
                sql = f"""
                SELECT p.name AS process_name, p.pid AS pid, T.name AS name,
                       c.ts AS ts, c.value AS value 
                FROM process_counter_track AS T
                LEFT JOIN process AS p ON p.upid = T.upid
                LEFT JOIN counter AS c ON c.track_id = T.id
                WHERE p.name = '/system/bin/surfaceflinger'
                AND T.name LIKE 'BufferTX - %'
                {time_str}
                ORDER BY c.ts
                """
            result = processor.execute_sql(sql)
            
            if result.empty:
                return None
            
            # 查找下降沿（当前值 < 前一个值）
            prev_value = None
            for _, row in result.iterrows():
                current_value = row['value']
                if prev_value is not None and current_value < prev_value:
                    return int(row['ts'])
                prev_value = current_value
            
            return None
        except Exception as e:
            print(f"获取 Buffer 下降沿失败: {e}")
            return None
    
    @staticmethod
    def capture_composite_completion(processor: PerfettoProcessor, start_ts: int,
                                    end_ts: int = None) -> Tuple[Optional[str], Optional[int]]:
        """
        捕获 SurfaceFlinger 合成完成事件
        
        Parameters:
            processor: Trace 解析器实例
            start_ts: 搜索起点
            end_ts: 搜索终点（可选）
            
        Returns:
            (composite事件名称, 完成时间戳)，未找到返回 (None, None)
        """
        try:
            end_condition = ""
            if end_ts is not None:
                end_condition = f"AND S.ts <= {end_ts}"
            
            # 方法1: 从 slice 表查询 SurfaceFlinger 的 composite 事件
            sql = f"""
            SELECT p.name AS process_name, S.name AS name, 
                   S.ts AS ts, S.dur AS dur
            FROM slice AS S
            LEFT JOIN thread_track AS tt ON tt.id = S.track_id
            LEFT JOIN thread AS t ON t.utid = tt.utid
            LEFT JOIN process AS p ON p.upid = t.upid
            WHERE LOWER(t.name) LIKE '%surfaceflinger%'
            AND (LOWER(S.name) LIKE 'composite%' OR LOWER(S.name) LIKE 'postcomposition%')
            AND S.ts >= {start_ts}
            {end_condition}
            ORDER BY S.ts ASC
            LIMIT 1
            """
            result = processor.execute_sql(sql)
            
            if not result.empty:
                row = result.iloc[0]
                composite_name = str(row['name'])
                composite_end_ts = int(row['ts']) + int(row['dur'])
                return composite_name, composite_end_ts
            
            # 方法2: 如果方法1失败，尝试查询所有进程的 composite 事件
            LoggerUtils.log_warning("方法1未找到 Composite 事件，尝试方法2...")
            sql_fallback = f"""
            SELECT p.name AS process_name, S.name AS name, 
                   S.ts AS ts, S.dur AS dur
            FROM slice AS S
            LEFT JOIN thread_track AS tt ON tt.id = S.track_id
            LEFT JOIN thread AS t ON t.utid = tt.utid
            LEFT JOIN process AS p ON p.upid = t.upid
            WHERE LOWER(S.name) LIKE '%composite%'
            AND S.ts >= {start_ts}
            {end_condition}
            ORDER BY S.ts ASC
            LIMIT 1
            """
            result = processor.execute_sql(sql_fallback)
            
            if not result.empty:
                row = result.iloc[0]
                composite_name = str(row['name'])
                composite_end_ts = int(row['ts']) + int(row['dur'])
                LoggerUtils.log_info(f"方法2找到 Composite: {composite_name} (进程: {row['process_name']})")
                return composite_name, composite_end_ts
            
            # 方法3: 尝试从 android.surfaceflinger.frametimeline 表查询
            LoggerUtils.log_warning("方法2也未找到，尝试方法3 (frametimeline)...")
            sql_frametimeline = f"""
            SELECT name, ts, dur
            FROM surface_slices
            WHERE ts >= {start_ts}
            {end_condition}
            AND (LOWER(name) LIKE '%composite%' OR LOWER(name) LIKE '%present%')
            ORDER BY ts ASC
            LIMIT 1
            """
            try:
                result = processor.execute_sql(sql_frametimeline)
                if not result.empty:
                    row = result.iloc[0]
                    composite_name = str(row['name'])
                    composite_end_ts = int(row['ts']) + int(row['dur'])
                    LoggerUtils.log_info(f"方法3找到 Composite: {composite_name}")
                    return composite_name, composite_end_ts
            except Exception as e:
                LoggerUtils.log_warning(f"方法3查询失败: {e}")
            
            # 所有方法都失败
            LoggerUtils.log_error("所有方法都未找到 Composite 事件")
            return None, None
            
        except Exception as e:
            print(f"获取 Composite 结束时间失败: {e}")
            import traceback
            traceback.print_exc()
            return None, None
