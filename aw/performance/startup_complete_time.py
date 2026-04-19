"""
应用启动性能分析引擎
基于 Perfetto Trace 实现冷/温启动全链路耗时测量
"""

import time
import subprocess
from typing import Dict, Optional
from .trace_collector import TraceCollector, PerfettoProcessor
from .baseline_manager import BaselineManager


class StartupCompleteTimeAnalyzer:
    """
    启动耗时分析器
    提供冷启动、温启动的端到端性能评估能力
    """
    
    # 启动模式枚举
    COLD_START = "cold"
    WARM_START = "warm"
    HOT_START = "hot"
    
    def __init__(self, trace_collector: TraceCollector):
        """
        构建分析器实例
        
        Parameters:
            trace_collector: Trace 采集控制器
        """
        self.utils = trace_collector
        self.baseline_manager = BaselineManager()
        
    def measure_cold_start(self, package_name: str, activity: str = ".MainActivity",
                          test_name: str = None) -> Dict:
        """
        执行冷启动性能测试
        
        Parameters:
            package_name: 目标应用包名
            activity: 主 Activity 路径
            test_name: 测试场景标识
            
        Returns:
            包含启动耗时、关键时间节点、CPU 负载及基线评估结果的字典
        """
        # 1. 强制停止应用（不清除数据）
        subprocess.run(f"adb -s {self.utils.device_id} shell am force-stop {package_name}", 
                      shell=True, capture_output=True)
        time.sleep(1)
        
        # 2. 开始录制
        self.utils.start_recording(duration=20, config_type="standard")
        time.sleep(0.5)
        
        # 3. 使用 monkey 启动应用
        cmd_monkey = f"adb -s {self.utils.device_id} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
        subprocess.run(cmd_monkey, shell=True, capture_output=True, text=True)
        
        # 4. 等待启动完成
        time.sleep(15)
        
        # 5. 停止录制并解析
        trace_path = self.utils.stop_recording(test_name=test_name)
        processor = self.utils.parse_trace(trace_path)
        
        # 6. 获取时间范围
        start_ts, end_ts = processor.get_trace_bounds()
        
        # 7. 检查关键函数
        key_functions = self._check_key_functions(processor, package_name, start_ts, end_ts)
        
        # 8. 判断启动类型
        startup_type = self._determine_startup_type(key_functions)
        
        # 9. 分析启动数据
        result = self._analyze_startup_completion(processor, package_name, start_ts, end_ts)
        result["startup_type"] = startup_type
        result["key_functions"] = key_functions
        
        # 10. 获取 CPU 使用情况
        result["cpu_usage"] = self._get_cpu_usage(processor, package_name, start_ts, end_ts)
        
        return result
    
    def measure_warm_start(self, package_name: str, activity: str = ".MainActivity",
                          test_name: str = None) -> Dict:
        """
        执行温启动性能测试（应用驻留后台场景）
        
        Parameters:
            package_name: 目标应用包名
            activity: Activity 路径
            test_name: 测试场景标识
            
        Returns:
            启动性能指标字典
        """
        # 1. 确保应用在后台运行
        subprocess.run(f"adb -s {self.utils.device_id} shell am start -n {package_name}/{activity}", 
                      shell=True, capture_output=True)
        time.sleep(3)
        subprocess.run(f"adb -s {self.utils.device_id} shell input keyevent KEYCODE_HOME", 
                      shell=True, capture_output=True)
        time.sleep(2)
        
        # 2. 开始录制
        self.utils.start_recording(duration=15, config_type="standard")
        
        # 3. 从后台恢复应用
        cmd_start = f"adb -s {self.utils.device_id} shell am start -n {package_name}/{activity}"
        subprocess.run(cmd_start, shell=True, capture_output=True)
        
        # 4. 等待恢复完成
        time.sleep(10)
        
        # 5. 停止录制并解析
        trace_path = self.utils.stop_recording(test_name=test_name)
        processor = self.utils.parse_trace(trace_path)
        
        # 6. 获取时间范围
        start_ts, end_ts = processor.get_trace_bounds()
        
        # 7. 检查关键函数
        key_functions = self._check_key_functions(processor, package_name, start_ts, end_ts)
        
        # 8. 判断启动类型（应该为 warm 或 hot）
        startup_type = self._determine_startup_type(key_functions)
        
        # 9. 分析启动数据
        result = self._analyze_startup_completion(processor, package_name, start_ts, end_ts)
        result["startup_type"] = startup_type
        result["key_functions"] = key_functions
        
        # 10. 获取 CPU 使用情况
        result["cpu_usage"] = self._get_cpu_usage(processor, package_name, start_ts, end_ts)
        
        return result
    
    def analyze_with_processor(self, processor: PerfettoProcessor, package_name: str,
                              startup_type: str = COLD_START,
                              start_ts: int = None, end_ts: int = None) -> Dict:
        """
        基于已有 Trace 解析器执行分析
        
        Parameters:
            processor: Trace 数据解析引擎
            package_name: 应用包名
            startup_type: 启动模式
            start_ts: 分析起始时间
            end_ts: 分析结束时间
            
        Returns:
            启动性能评估结果
        """
        if start_ts is None or end_ts is None:
            start_ts, end_ts = processor.get_trace_bounds()
        
        result = self._analyze_startup_completion(processor, package_name, start_ts, end_ts)
        result["startup_type"] = startup_type
        result["has_bind_application"] = self._check_bind_application(processor, package_name)
        result["cpu_usage"] = self._get_cpu_usage(processor, package_name, start_ts, end_ts)
        
        return result
    
    def _analyze_startup_completion(self, processor: PerfettoProcessor, package_name: str,
                                   start_ts: int, end_ts: int) -> Dict:
        """
        核心分析逻辑：提取启动全链路时间节点
        
        Parameters:
            processor: Trace 解析器
            package_name: 应用包名
            start_ts: 搜索起始点
            end_ts: 搜索终止点
            
        Returns:
            包含 IQ、Buffer、Composite 等关键时间戳的指标集
        """
        # === 1. 提取 IQ 事件标记（起点）===
        iq_first_ts = TraceCollector.extract_input_queue_timestamp(
            processor, start_ts=start_ts, end_ts=end_ts, location=0
        )
        if iq_first_ts is None:
            return {
                "error": "未找到 IQ 事件",
                "start_complete_time": 0
            }
        click_ts = iq_first_ts  # 兼容旧字段名
        
        # === 2. 定位 UI 线程首帧渲染 ===
        first_frame = self._find_app_ui_first_frame(processor, package_name, click_ts, end_ts)
        if not first_frame:
            return {
                "error": "未找到应用 UI 第一帧",
                "click_ts": click_ts,
                "start_complete_time": 0
            }
        first_frame_ts = first_frame['ts']
        
        # === 3. 匹配 Buffer 传输下降沿 ===
        draw_layer = f"{package_name}/{package_name}"
        first_buffer_ts = TraceCollector.locate_buffer_falling_edge(
            processor, process_name=draw_layer,
            start_ts=first_frame_ts, end_ts=end_ts
        )
        
        if first_buffer_ts is None:
            return {
                "error": "未找到 Buffer 下降沿",
                "click_ts": click_ts,
                "first_frame_ts": first_frame_ts,
                "start_complete_time": 0
            }
        
        # === 4. 捕获 Composite 合成完成时刻（终点）===
        composite_name, composite_end_ts = TraceCollector.capture_composite_completion(
            processor, start_ts=first_buffer_ts, end_ts=end_ts
        )
        
        if composite_end_ts is None:
            return {
                "error": "未找到 Composite 事件",
                "click_ts": click_ts,
                "first_frame_ts": first_frame_ts,
                "buffer_ts": first_buffer_ts,
                "start_complete_time": 0
            }
        
        # === 5. 计算端到端启动耗时 ===
        complete_time_ns = composite_end_ts - click_ts
        complete_time_ms = complete_time_ns / 1_000_000  # ns -> ms
        
        # === 6. 执行基线合规性检查 ===
        baseline_check = self.baseline_manager.check_startup_time(
            complete_time_ms, self.COLD_START
        )
        
        return {
            "click_ts": click_ts,
            "first_frame_ts": first_frame_ts,
            "buffer_ts": first_buffer_ts,
            "composite_end_ts": composite_end_ts,
            "composite_name": composite_name,
            "start_complete_time": round(complete_time_ms, 2),
            "baseline_check": baseline_check
        }

    
    def _find_app_ui_first_frame(self, processor: PerfettoProcessor, package_name: str,
                                start_ts: int, end_ts: int) -> Optional[Dict]:
        """
        检索应用 UI 线程的首次帧渲染事件
        
        Parameters:
            processor: Trace 解析器
            package_name: 应用标识
            start_ts: 搜索起点
            end_ts: 搜索终点
            
        Returns:
            首帧事件信息，未找到返回 None
        """
        sql = f"""
        SELECT p.name AS process_name, p.pid AS pid, S.name AS name, S.ts AS ts, S.dur AS dur
        FROM slice AS S
        LEFT JOIN thread_track AS tt ON tt.id = S.track_id
        LEFT JOIN thread AS t ON t.utid = tt.utid
        LEFT JOIN process AS p ON p.upid = t.upid
        WHERE S.name LIKE '%Choreographer#doFrame%'
        AND instr('{package_name}', p.name) > 0
        AND S.ts >= {start_ts} AND S.ts <= {end_ts}
        ORDER BY S.ts ASC
        LIMIT 1
        """
        result = processor.execute_sql(sql)
        if not result.empty:
            return result.iloc[0].to_dict()
        return None
    
    def _check_bind_application(self, processor: PerfettoProcessor, package_name: str) -> bool:
        """
        检测 bindApplication 生命周期事件（冷启动标志）
        
        Parameters:
            processor: Trace 解析器
            package_name: 应用包名
            
        Returns:
            是否存在 bindApplication 事件
        """
        sql = f"""
        SELECT COUNT(*) as cnt
        FROM slice AS S
        LEFT JOIN thread_track AS tt ON tt.id = S.track_id
        LEFT JOIN thread AS t ON t.utid = tt.utid
        LEFT JOIN process AS p ON p.upid = t.upid
        WHERE S.name LIKE '%bindApplication%'
        AND instr('{package_name}', p.name) > 0
        """
        result = processor.execute_sql(sql)
        if not result.empty and result.iloc[0]['cnt'] > 0:
            return True
        return False
    
    def _get_cpu_usage(self, processor: PerfettoProcessor, package_name: str,
                      start_ts: int, end_ts: int) -> Dict:
        """
        统计应用 CPU 资源消耗
        
        Parameters:
            processor: Trace 解析器
            package_name: 应用包名
            start_ts: 统计起始时间
            end_ts: 统计终止时间
            
        Returns:
            CPU 周期数、线程数及 Top3 线程详情
        """
        try:
            # 获取线程 CPU 周期数据
            cpu_data = TraceCollector.analyze_thread_cpu_consumption(processor, start_ts, end_ts, package_name)
            
            if cpu_data.empty:
                return {"total_cpu_cycles": 0}
            
            total_cycles = cpu_data['total_dur'].sum()
            return {
                "total_cpu_cycles": int(total_cycles),
                "thread_count": len(cpu_data),
                "top_threads": cpu_data.head(3).to_dict('records')
            }
        except Exception as e:
            return {"error": str(e), "total_cpu_cycles": 0}
    
    def _check_key_functions(self, processor: PerfettoProcessor, package_name: str,
                            start_ts: int, end_ts: int) -> Dict:
        """
        扫描关键生命周期函数执行情况
        
        Parameters:
            processor: Trace 解析器
            package_name: 应用包名
            start_ts: 扫描起始时间
            end_ts: 扫描终止时间
            
        Returns:
            各关键函数的存在状态字典
        """
        key_functions = {
            'bindApplication': False,
            'activityStart': False,
            'activityResume': False,
            'performResume': False,
            'performStart': False
        }
        
        try:
            # 查询关键函数
            sql = f"""
            SELECT p.name AS process_name, S.name AS name
            FROM slice AS S
            LEFT JOIN thread_track AS tt ON tt.id = S.track_id
            LEFT JOIN thread AS t ON t.utid = tt.utid
            LEFT JOIN process AS p ON p.upid = t.upid
            WHERE instr('{package_name}', p.name) > 0
            AND S.ts >= {start_ts} AND S.ts <= {end_ts}
            AND (
                S.name LIKE '%bindApplication%' OR
                S.name LIKE '%activityStart%' OR
                S.name LIKE '%activityResume%' OR
                S.name LIKE '%performResume%' OR
                S.name LIKE '%performStart%'
            )
            """
            result = processor.execute_sql(sql)
            
            if not result.empty:
                for _, row in result.iterrows():
                    func_name = str(row['name'])
                    if 'bindApplication' in func_name:
                        key_functions['bindApplication'] = True
                    elif 'activityStart' in func_name:
                        key_functions['activityStart'] = True
                    elif 'activityResume' in func_name:
                        key_functions['activityResume'] = True
                    elif 'performResume' in func_name:
                        key_functions['performResume'] = True
                    elif 'performStart' in func_name:
                        key_functions['performStart'] = True
        except Exception as e:
            print(f"检查关键函数失败: {e}")
        
        return key_functions
    
    def _determine_startup_type(self, key_functions: Dict) -> str:
        """
        基于生命周期事件推断启动模式
        
        Parameters:
            key_functions: 关键函数执行状态
            
        Returns:
            启动类型标识：cold/warm/hot/unknown
        """
        has_bind = key_functions.get('bindApplication', False)
        has_activity_start = key_functions.get('activityStart', False)
        has_resume = (key_functions.get('activityResume', False) or 
                     key_functions.get('performResume', False))
        has_perform_start = key_functions.get('performStart', False)
        
        if has_bind:
            return self.COLD_START
        elif has_activity_start:
            if has_resume:
                return self.WARM_START
            else:
                return self.HOT_START
        elif has_resume or has_perform_start:
            return self.HOT_START
        else:
            return "unknown"
