# Android Performance Toolkit (APT)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Perfetto](https://img.shields.io/badge/Perfetto-integrated-green.svg)](https://perfetto.dev/)

## 简介

基于 Perfetto 的 Android 性能测试框架，提供系统级性能数据采集与分析能力。本框架采用分层架构设计，支持启动完成时间、滑动流畅度、动画性能等多维度性能指标测量。

## 核心特性

- ✅ **分层架构设计**：utils → aw → testcases 三层解耦，职责清晰
- ✅ **Perfetto 深度集成**：支持 IQ → Buffer → Composite 全链路分析
- ✅ **基线管理机制**：自动化性能阈值评估与质量门禁
- ✅ **可扩展设计**：模块化分析器，易于添加新的性能指标
- ✅ **配置外置化**：XML + JSON 双配置体系，灵活可维护

## 技术栈

- **Python**: 3.8+
- **Android 自动化**: uiautomator2
- **性能分析**: Perfetto (trace_processor)
- **测试框架**: pytest + allure-pytest
- **数据处理**: pandas

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Perfetto Trace Processor

从 [Perfetto 官网](https://perfetto.dev/docs/analysis/trace-processor) 下载对应平台的二进制文件：

**Windows:**
```powershell
# 创建目录
New-Item -Path "tools\perfetto" -ItemType Directory -Force

# 下载 trace_processor (Windows amd64)
Invoke-WebRequest -Uri "https://get.perfetto.dev/trace_processor_shell-windows-amd64" -OutFile "tools\perfetto\trace_processor.exe"
```

**Linux:**
```bash
mkdir -p tools/perfetto
wget https://get.perfetto.dev/trace_processor_shell-linux-amd64 -O tools/perfetto/trace_processor
chmod +x tools/perfetto/trace_processor
```

**Mac (Intel):**
```bash
mkdir -p tools/perfetto
wget https://get.perfetto.dev/trace_processor_shell-darwin-amd64 -O tools/perfetto/trace_processor
chmod +x tools/perfetto/trace_processor
```

**Mac (Apple Silicon):**
```bash
mkdir -p tools/perfetto
wget https://get.perfetto.dev/trace_processor_shell-darwin-arm64 -O tools/perfetto/trace_processor
chmod +x tools/perfetto/trace_processor
```

或将其放置到系统 PATH 中。

### 3. 配置设备

编辑 `config/user_config.xml`，设置您的设备信息：

```xml
<configuration>
    <device>
        <id>emulator-5554</id>
        <type>usb</type>
    </device>
</configuration>
```

### 4. 运行测试

```bash
# 运行启动完成时间测试
pytest testcases/test_startup_complete.py -v --alluredir=./allure-results

# 查看报告
allure serve ./allure-results
```

## 架构设计

### 分层架构

```
testcases/          # 测试用例层：业务场景编排
    └─ 调用 aw 层的分析器
    
aw/                 # 原子工作流层：可复用的性能分析模块
    ├─ app_ops.py   # 应用操作原子方法
    ├─ test_helper.py  # 测试辅助工具
    └─ performance/ # 性能分析器
        ├─ trace_collector.py      # Trace 采集引擎
        ├─ startup_complete_time.py # 启动完成时间分析
        └─ baseline_manager.py     # 基线管理
        
utils/              # 工具类层：基础能力封装
    ├─ device_utils.py    # 设备管理
    ├─ config_utils.py    # 配置加载
    └─ logger_utils.py    # 日志工具
```

### 核心流程

```
1. 测试用例发起性能测试请求
         ↓
2. TraceCollector 启动 Perfetto 录制
         ↓
3. 执行被测操作（如应用启动）
         ↓
4. 停止录制并获取 trace 文件
         ↓
5. StartupCompleteTimeAnalyzer 分析 trace
         ↓
6. BaselineManager 评估结果是否达标
         ↓
7. 生成 Allure 报告
```

## 示例：启动完成时间测试

### 测试原理

启动完成时间测量从用户点击图标到应用完全就绪的总耗时，包含：

1. **IQ (Input Queue)**: 输入事件入队时间
2. **Buffer**: SurfaceFlinger 接收第一帧缓冲
3. **Composite**: 屏幕合成完成

通过 Perfetto 的 process_counter_track 和 slice 表，精确捕获各阶段时间戳。

### 关键代码

```python
from aw.performance import TraceCollector, StartupCompleteTimeAnalyzer, BaselineManager

# 初始化
utils = TraceCollector(device_id="emulator-5554")
analyzer = StartupCompleteTimeAnalyzer(utils)
baseline_mgr = BaselineManager()

# 执行测试
result = analyzer.measure_cold_start(
    package_name="com.example.app",
    activity=".MainActivity"
)

# 基线评估
is_pass = baseline_mgr.check_startup_time(
    objective_ms=result["startup_time_ms"],
    serious_ms=2000
)
```

### SQL 查询示例

```sql
-- 获取 IQ 时间戳
SELECT c.ts FROM process_counter_track AS T
LEFT JOIN counter AS c ON c.track_id = T.id
WHERE T.name = 'iq'
ORDER BY c.ts LIMIT 1

-- 获取 Buffer 下降沿
SELECT c.ts FROM process_counter_track AS T
LEFT JOIN counter AS c ON c.track_id = T.id
WHERE T.name LIKE 'BufferTX - com.example.app%'
ORDER BY c.ts

-- 获取 Composite 结束时间
SELECT S.ts + S.dur AS end_ts FROM slice AS S
LEFT JOIN thread AS t ON t.utid = S.track_id
WHERE t.name LIKE '%surfaceflinger%'
AND S.name LIKE 'composite%'
ORDER BY S.ts LIMIT 1
```

## 配置说明

### 测试用例配置 (JSON)

```json
{
  "config": {
    "package": "com.example.app",
    "timeout": 30,
    "retry_count": 3,
    "activity": ".MainActivity"
  }
}
```

### Perfetto 配置

框架提供两种 Perfetto 采集配置：

- `android.txt`: 标准配置，适用于大多数性能测试场景
- 自定义配置：可根据需求调整数据源和采样频率

## 扩展开发

### 添加新的性能分析器

1. 在 `aw/performance/` 创建新的分析器类
2. 实现 `measure_xxx()` 方法
3. 使用 `TraceCollector.execute_sql()` 执行 Perfetto 查询
4. 返回标准化的指标字典

### 示例

```python
class MyCustomAnalyzer:
    def __init__(self, trace_collector: TraceCollector):
        self.utils = trace_collector
    
    def measure_custom_metric(self, package_name: str) -> Dict:
        # 执行 Perfetto 查询
        sql = "SELECT ..."
        result = self.utils.execute_sql(sql)
        
        # 计算指标
        metric_value = self._calculate(result)
        
        return {
            "metric_name": metric_value,
            "unit": "ms"
        }
```

## 最佳实践

1. **保持登录状态**：性能测试不清除应用数据，模拟真实用户场景
2. **多次测量取平均值**：减少偶然误差，提高结果可靠性
3. **建立基线**：设定合理的性能阈值，自动化质量门禁
4. **趋势分析**：定期运行测试，监控性能退化

## License

MIT License

## Author

Performance Testing Team
