"""
性能基线评估引擎
提供阈值加载、合规性检查及质量门禁功能
"""

import json
import os
from typing import Dict, List, Optional


class BaselineManager:
    """
    基线合规性管理器
    """
    
    def __init__(self, baseline_file: str = None):
        """
        构建基线管理器
        
        Parameters:
            baseline_file: 基线配置文件路径（可选）
        """
        if baseline_file is None:
            # 默认使用 config/performance_baseline.json
            # aw/performance/baseline_manager.py -> aw/performance -> aw -> project_root
            current_file = os.path.abspath(__file__)
            performance_dir = os.path.dirname(current_file)
            aw_dir = os.path.dirname(performance_dir)
            project_root = os.path.dirname(aw_dir)
            baseline_file = os.path.join(project_root, "config", "performance_baseline.json")
        
        self.baseline = self._load_baseline(baseline_file)
    
    def _load_baseline(self, file_path: str) -> Dict:
        """加载基线阈值配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载基线配置失败: {e}")
            return {}
    
    def check_startup_time(self, value: float, startup_type: str = "cold") -> Dict:
        """
        评估启动耗时是否满足质量标准
        
        Parameters:
            value: 实测启动时间（毫秒）
            startup_type: 启动类别（cold/hot）
            
        Returns:
            包含实测值、告警状态及阈值列表的评估报告
        """
        key_map = {
            "cold": "cold_start_complete_thresholds",
            "hot": "hot_start_complete_thresholds"
        }
        
        key = key_map.get(startup_type)
        if not key or key not in self.baseline.get("startup_time", {}):
            return {"value": value, "is_warning": False, "thresholds": []}
        
        thresholds = self.baseline["startup_time"][key]
        is_warning = any(value > threshold for threshold in thresholds)
        
        return {
            "value": value,
            "is_warning": is_warning,
            "thresholds": thresholds,
            "unit": "ms"
        }
