"""
高性能性能测试与分析工具集
提供全链路 Perfetto 数据采集、解析与指标计算能力
"""

from .trace_collector import TraceCollector, PerfettoProcessor
from .startup_complete_time import StartupCompleteTimeAnalyzer
from .baseline_manager import BaselineManager

__all__ = [
    "TraceCollector",
    "PerfettoProcessor",
    "StartupCompleteTimeAnalyzer",
    "BaselineManager",
]
