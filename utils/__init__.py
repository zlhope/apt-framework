# -*- coding: utf-8 -*-
"""
utils 包
通用工具函数库
"""

# ADB 工具 - 不依赖 uiautomator2，可以独立使用
from .adb import AdbUtils, KeyCodes

# 通用工具 - 向后兼容（注意：文件名是 Utils.py 不是 utils.py）
from .Utils import (
    TimeUtils,
    FileUtils,
    DataUtils,
    LoggerUtils,
    AssertUtils,
    # 向后兼容的类
    DeviceUtils,
    ConfigUtils,
    TestUtils
)

# UIAutomator2 工具（延迟导入，避免 pkg_resources 问题）
try:
    from aw.uiautomator2_api import UiAutomator2Utils, Direction
    __uiautomator2_available__ = True
except (AttributeError, ImportError):
    # Python 3.14+ 兼容性问题
    __uiautomator2_available__ = False
    print("警告：UiAutomator2Utils 暂时不可用（Python 版本兼容性问题）")

__version__ = "1.0.0"
__author__ = "Your Team"
__all__ = [
    # ADB
    "AdbUtils",
    "KeyCodes",
    
    # UIAutomator2 (如果可用)
    "UiAutomator2Utils" if __uiautomator2_available__ else None,
    "Direction" if __uiautomator2_available__ else None,
    
    # Utils
    "TimeUtils",
    "FileUtils",
    "DataUtils",
    "LoggerUtils",
    "AssertUtils",
    
    # 向后兼容
    "DeviceUtils",
    "ConfigUtils",
    "TestUtils",
]
