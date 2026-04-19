# -*- coding: utf-8 -*-
"""
AppOperations - 应用级原子操作
"""

from utils import LoggerUtils, TimeUtils
from utils.Utils import DeviceUtils


class AppOperations:
    """应用级原子操作"""
    
    @staticmethod
    def launch_app(package_name: str):
        """启动应用"""
        LoggerUtils.log_info(f"启动应用：{package_name}")
        device = DeviceUtils.connect_device()
        device.app_start(package_name)
        TimeUtils.sleep(3)
        LoggerUtils.log_info(f"✅ {package_name} 已启动")
    
    @staticmethod
    def close_app(package_name: str):
        """关闭应用"""
        LoggerUtils.log_info(f"关闭应用：{package_name}")
        device = DeviceUtils.connect_device()
        device.app_stop(package_name)
        LoggerUtils.log_info(f"✅ {package_name} 已关闭")
    
    @staticmethod
    def clear_app_data(package_name: str):
        """清除应用数据"""
        LoggerUtils.log_info(f"清除应用数据：{package_name}")
        device = DeviceUtils.connect_device()
        device.app_clear(package_name)
        LoggerUtils.log_info(f"✅ {package_name} 数据已清除")


__all__ = ['AppOperations']
