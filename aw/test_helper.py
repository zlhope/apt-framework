# -*- coding: utf-8 -*-
"""
测试辅助工具类（aw层）
提供应用启动验证、截图等通用测试辅助功能
遵循分层原则：调用 utils 层的底层工具
"""
import os
import sys
import time
from typing import Optional
from datetime import datetime

# 添加项目根目录到Python路径
current_file = os.path.abspath(__file__)
aw_dir = os.path.dirname(current_file)
project_root = os.path.dirname(aw_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils import LoggerUtils


class AppVerifier:
    """应用验证工具类"""
    
    @staticmethod
    def verify_app_started(device, package_name: str, timeout: int = 10) -> bool:
        """
        验证应用是否启动成功
        
        Args:
            device: DeviceUtils 设备对象
            package_name: 应用包名
            timeout: 超时时间（秒）
            
        Returns:
            bool: 应用是否启动成功
        """
        LoggerUtils.log_info(f"验证应用启动状态: {package_name}")
        
        # 方式1: 检查进程是否存在
        try:
            result = device.shell(f"pidof {package_name}")
            
            # 正确处理 ShellResponse 对象
            if hasattr(result, 'output'):
                # ShellResponse 对象
                pid_output = result.output.strip() if result.output else ""
                exit_code = result.exit_code if hasattr(result, 'exit_code') else -1
            else:
                # 普通字符串
                pid_output = str(result).strip() if result else ""
                exit_code = 0 if pid_output else 1
            
            if pid_output and exit_code == 0:
                LoggerUtils.log_info(f"✓ 进程存在: {pid_output}")
                
                # 方式2: 检查是否有窗口
                windows = device.shell("dumpsys window windows")
                if hasattr(windows, 'output'):
                    windows_str = str(windows.output) if windows.output else ""
                else:
                    windows_str = str(windows) if windows else ""
                    
                if package_name in windows_str:
                    LoggerUtils.log_info("✓ 应用窗口已显示")
                    return True
                else:
                    LoggerUtils.log_warning("⚠ 进程存在但窗口未显示")
                    return False
            else:
                LoggerUtils.log_error(f"✗ 应用进程不存在 (exit_code={exit_code})")
                return False
        except Exception as e:
            LoggerUtils.log_error(f"验证应用启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def safe_start_app(device, package: str, activity: str = None, 
                      wait: bool = True, sleep_time: float = 10,
                      use_monkey: bool = False) -> bool:
        """
        安全启动应用（带验证）
        
        Args:
            device: DeviceUtils 设备对象
            package: 应用包名
            activity: Activity 名称
            wait: 是否等待启动完成
            sleep_time: 启动后等待时间（秒），默认10秒
            use_monkey: 是否使用 monkey 命令启动（解决 exported=false 问题）
            
        Returns:
            bool: 应用是否启动成功
            
        Raises:
            Exception: 应用启动失败时抛出异常
        """
        import subprocess
        
        # 强制停止应用
        LoggerUtils.log_info(f"强制停止应用: {package}")
        device.app_stop(package)
        time.sleep(1)
        
        # 启动应用
        LoggerUtils.log_info(f"启动应用: {package}")
        if use_monkey:
            # 使用 monkey 命令启动（更可靠）
            device_id = getattr(device, 'serial', None)
            if device_id:
                cmd = f"adb -s {device_id} shell monkey -p {package} -c android.intent.category.LAUNCHER 1"
            else:
                cmd = f"adb shell monkey -p {package} -c android.intent.category.LAUNCHER 1"
            subprocess.run(cmd, shell=True, capture_output=True)
            LoggerUtils.log_info("✓ 启动命令已发送（monkey）")
        else:
            if activity:
                device.app_start(package, activity=activity, wait=wait)
            else:
                device.app_start(package, wait=wait)
        
        # 等待应用启动
        LoggerUtils.log_info(f"等待应用启动 ({sleep_time}秒)...")
        time.sleep(sleep_time)
        
        # 验证启动是否成功
        if not AppVerifier.verify_app_started(device, package):
            error_msg = f"应用 {package} 启动失败"
            LoggerUtils.log_error(error_msg)
            raise Exception(error_msg)
        
        LoggerUtils.log_info(f"✓ 应用 {package} 启动成功")
        return True
    
    @staticmethod
    def start_app_by_icon(device, app_name: str, sleep_time: float = 5) -> bool:
        """
        通过点击桌面图标启动应用
            
        Args:
            device: DeviceUtils 设备对象
            app_name: 应用名称（用于查找桌面图标）
            sleep_time: 启动后等待时间（秒），默认5秒
            
        Returns:
            bool: 应用是否启动成功
            
        Raises:
            Exception: 未找到应用图标时抛出异常
        """
        # 返回桌面
        LoggerUtils.log_info("返回桌面...")
        device.press("home")
        time.sleep(2)
        
        # 查找应用图标
        LoggerUtils.log_info(f"查找应用图标: {app_name}")
        app_icon = device(text=app_name)
        if not app_icon.exists(timeout=5):
            # 尝试模糊匹配
            app_icon = device(textContains=app_name)
        
        if app_icon.exists:
            LoggerUtils.log_info(f"找到{app_name}图标，点击启动...")
            app_icon.click()
            time.sleep(sleep_time)
            LoggerUtils.log_info(f"✓ {app_name} 已启动")
            return True
        else:
            error_msg = f"未找到应用图标: {app_name}"
            LoggerUtils.log_error(error_msg)
            raise Exception(error_msg)
    
    @staticmethod
    def return_to_home(device, sleep_time: float = 1):
        """
        返回桌面（不停止应用，保留数据）
        
        Args:
            device: DeviceUtils 设备对象
            sleep_time: 等待时间（秒），默认1秒
        """
        try:
            LoggerUtils.log_info("返回桌面...")
            device.press("home")
            time.sleep(sleep_time)
            LoggerUtils.log_info("✓ 已返回桌面（保留应用数据）")
        except Exception as e:
            LoggerUtils.log_warning(f"返回桌面失败: {e}")


class ScreenshotHelper:
    """截图辅助工具类"""
    
    @staticmethod
    def take_screenshot(device, name: str = "screenshot", 
                       save_dir: str = None) -> str:
        """
        截图并保存到指定目录
        
        Args:
            device: DeviceUtils 设备对象
            name: 截图文件名（不含扩展名）
            save_dir: 保存目录，默认为 allure-results
            
        Returns:
            str: 截图文件路径，失败返回空字符串
        """
        if save_dir is None:
            save_dir = os.path.join(project_root, "allure-results")
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        os.makedirs(save_dir, exist_ok=True)
        screenshot_path = os.path.join(save_dir, filename)
        
        try:
            # 截图
            device.screenshot(screenshot_path)
            LoggerUtils.log_info(f"截图已保存: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            LoggerUtils.log_error(f"截图失败: {e}")
            return ""
    
    @staticmethod
    def attach_to_allure(screenshot_path: str, name: str = "错误截图"):
        """
        将截图附加到 Allure 报告
        
        Args:
            screenshot_path: 截图文件路径
            name: Allure 报告中显示的名称
        """
        try:
            import allure
            
            if os.path.exists(screenshot_path):
                allure.attach.file(
                    screenshot_path,
                    name=name,
                    attachment_type=allure.attachment_type.PNG
                )
                LoggerUtils.log_info(f"截图已附加到 Allure 报告: {name}")
        except ImportError:
            LoggerUtils.log_warning("Allure 未安装，跳过附件添加")
        except Exception as e:
            LoggerUtils.log_error(f"附加截图到 Allure 失败: {e}")


class TestErrorHandler:
    """测试错误处理工具类"""
    
    @staticmethod
    def handle_test_failure(device, error_msg: str, screenshot_name: str = "error",
                           save_dir: str = None) -> str:
        """
        处理测试失败（截图 + 记录日志）
        
        Args:
            device: DeviceUtils 设备对象
            error_msg: 错误信息
            screenshot_name: 截图文件名
            save_dir: 截图保存目录
            
        Returns:
            str: 截图文件路径
        """
        LoggerUtils.log_error(error_msg)
        
        # 截图
        screenshot_path = ScreenshotHelper.take_screenshot(
            device, screenshot_name, save_dir
        )
        
        # 附加到 Allure
        if screenshot_path:
            ScreenshotHelper.attach_to_allure(
                screenshot_path, 
                f"错误截图 - {screenshot_name}"
            )
        
        return screenshot_path
