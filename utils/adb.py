# -*- coding: utf-8 -*-
"""
ADB 命令完整封装模块
提供所有常用 ADB 命令的 Python 接口
"""
import subprocess
import os
from typing import List, Dict, Optional, Any
from enum import Enum


class KeyCodes(Enum):
    """Android 按键代码枚举"""
    HOME = 3
    BACK = 4
    MENU = 82
    ENTER = 66
    VOLUME_UP = 24
    VOLUME_DOWN = 25
    POWER = 26
    CALL = 5
    ENDCALL = 6
    CAMERA = 27
    BRIGHTNESS_DOWN = 224
    BRIGHTNESS_UP = 225
    VOLUME_MUTE = 164
    MEDIA_PLAY = 126
    MEDIA_PAUSE = 127
    MEDIA_STOP = 128
    MEDIA_NEXT = 87
    MEDIA_PREVIOUS = 88
    RECENT_APPS = 187
    NOTIFICATION = 209
    QUICK_SETTINGS = 210
    ESCAPE = 111
    TAB = 61
    SPACE = 62
    COMMA = 55
    PERIOD = 56
    LEFT_BRACKET = 71
    RIGHT_BRACKET = 72
    BACKSLASH = 73
    SEMICOLON = 74
    APOSTROPHE = 75
    SLASH = 76
    AT = 77
    EQUALS = 70
    PLUS = 81
    MINUS = 69
    STAR = 17
    POUND = 18
    FOCUS = 80
    ZOOM_IN = 168
    ZOOM_OUT = 169


class AdbUtils:
    """ADB 工具类 - 完整封装所有 ADB 功能"""
    
    _adb_path: str = "adb"
    
    # ========== 设备管理 ==========
    @staticmethod
    def get_adb_path() -> str:
        """获取 ADB 可执行文件路径"""
        return AdbUtils._adb_path
    
    @staticmethod
    def set_adb_path(path: str):
        """设置 ADB 可执行文件路径
        
        Args:
            path: ADB 可执行文件的完整路径
        """
        if os.path.exists(path):
            AdbUtils._adb_path = path
        else:
            raise FileNotFoundError(f"ADB 文件不存在：{path}")
    
    @staticmethod
    def run_command(command: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """执行 ADB 命令
        
        Args:
            command: ADB 命令列表，如 ['adb', 'devices']
            timeout: 超时时间（秒）
            
        Returns:
            命令执行结果对象
            
        Raises:
            subprocess.TimeoutExpired: 命令执行超时
            Exception: 其他执行异常
        """
        try:
            result = subprocess.run(
                [AdbUtils._adb_path] + command,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            return result
        except subprocess.TimeoutExpired:
            raise subprocess.TimeoutExpired(cmd=command, timeout=timeout)
        except Exception as e:
            raise Exception(f"执行 ADB 命令失败：{str(e)}")
    
    @staticmethod
    def list_devices() -> List[Dict[str, str]]:
        """列出所有连接的设备
        
        Returns:
            设备信息列表，每个设备包含 serial 和 status
        """
        result = AdbUtils.run_command(['devices', '-l'])
        devices = []
        
        lines = result.stdout.strip().split('\n')
        for line in lines[1:]:  # 跳过第一行标题
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    device_info = {
                        'serial': parts[0],
                        'status': parts[1]
                    }
                    # 解析额外信息
                    for part in parts[2:]:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            device_info[key] = value
                    devices.append(device_info)
        
        return devices
    
    @staticmethod
    def get_device_state(device_id: str = None) -> str:
        """获取设备状态
        
        Args:
            device_id: 设备 ID
            
        Returns:
            设备状态：device, offline, unauthorized, missing
        """
        cmd = ['devices']
        if device_id:
            cmd = ['-s', device_id, 'devices']
        
        result = AdbUtils.run_command(cmd)
        lines = result.stdout.strip().split('\n')
        
        for line in lines[1:]:
            if line.strip():
                parts = line.split()
                if parts[0] == device_id or not device_id:
                    return parts[1] if len(parts) > 1 else 'missing'
        
        return 'missing'
    
    @staticmethod
    def wait_for_device(timeout: int = 30, device_id: str = None):
        """等待设备连接
        
        Args:
            timeout: 超时时间（秒）
            device_id: 设备 ID
            
        Raises:
            TimeoutError: 等待超时
        """
        cmd = ['wait-for-device']
        if device_id:
            cmd = ['-s', device_id, 'wait-for-device']
        
        try:
            AdbUtils.run_command(cmd, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"等待设备连接超时：{timeout}秒")
    
    @staticmethod
    def kill_server():
        """关闭 ADB 服务"""
        AdbUtils.run_command(['kill-server'])
    
    @staticmethod
    def start_server():
        """启动 ADB 服务"""
        AdbUtils.run_command(['start-server'])
    
    @staticmethod
    def get_version() -> str:
        """获取 ADB 版本
        
        Returns:
            ADB 版本号
        """
        result = AdbUtils.run_command(['version'])
        lines = result.stdout.strip().split('\n')
        if lines:
            return lines[0]
        return "unknown"
    
    # ========== 应用管理 ==========
    @staticmethod
    def install_apk(apk_path: str, device_id: str = None, 
                    replace: bool = True, allow_test: bool = False):
        """安装 APK
        
        Args:
            apk_path: APK 文件路径
            device_id: 设备 ID
            replace: 是否替换已存在的应用
            allow_test: 是否允许测试应用
            
        Raises:
            FileNotFoundError: APK 文件不存在
            RuntimeError: 安装失败
        """
        if not os.path.exists(apk_path):
            raise FileNotFoundError(f"APK 文件不存在：{apk_path}")
        
        cmd = ['install']
        if replace:
            cmd.append('-r')
        if allow_test:
            cmd.append('-t')
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        cmd.append(apk_path)
        result = AdbUtils.run_command(cmd)
        
        if 'Failure' in result.stderr or 'Failure' in result.stdout:
            raise RuntimeError(f"安装失败：{result.stderr or result.stdout}")
    
    @staticmethod
    def uninstall_app(package_name: str, device_id: str = None, 
                     keep_data: bool = False):
        """卸载应用
        
        Args:
            package_name: 应用包名
            device_id: 设备 ID
            keep_data: 是否保留数据
            
        Raises:
            RuntimeError: 卸载失败
        """
        cmd = ['uninstall']
        if keep_data:
            cmd.append('-k')
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        cmd.append(package_name)
        result = AdbUtils.run_command(cmd)
        
        if 'Failure' in result.stderr or 'Failure' in result.stdout:
            raise RuntimeError(f"卸载失败：{result.stderr or result.stdout}")
    
    @staticmethod
    def start_activity(activity: str, package_name: str = None, 
                      device_id: str = None, action: str = None,
                      category: str = None, data_uri: str = None,
                      mime_type: str = None, extras: Dict = None):
        """启动 Activity
        
        Args:
            activity: Activity 名称
            package_name: 包名
            device_id: 设备 ID
            action: Intent Action
            category: Intent Category
            data_uri: Data URI
            mime_type: MIME 类型
            extras: 额外参数
        """
        cmd = ['shell', 'am', 'start']
        
        if package_name and activity:
            cmd.extend(['-n', f"{package_name}/{activity}"])
        
        if action:
            cmd.extend(['-a', action])
        
        if category:
            cmd.extend(['-c', category])
        
        if data_uri:
            cmd.extend(['-d', data_uri])
        
        if mime_type:
            cmd.extend(['-t', mime_type])
        
        if extras:
            for key, value in extras.items():
                if isinstance(value, str):
                    cmd.extend(['--es', key, value])
                elif isinstance(value, int):
                    cmd.extend(['--ei', key, str(value)])
                elif isinstance(value, bool):
                    cmd.extend(['--ez', key, str(value).lower()])
        
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def force_stop(package_name: str, device_id: str = None):
        """强制停止应用
        
        Args:
            package_name: 应用包名
            device_id: 设备 ID
        """
        cmd = ['shell', 'am', 'force-stop', package_name]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def clear_data(package_name: str, device_id: str = None):
        """清除应用数据
        
        Args:
            package_name: 应用包名
            device_id: 设备 ID
        """
        cmd = ['shell', 'pm', 'clear', package_name]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def grant_permission(package_name: str, permission: str, 
                        device_id: str = None):
        """授予权限
        
        Args:
            package_name: 应用包名
            permission: 权限名称
            device_id: 设备 ID
        """
        cmd = ['shell', 'pm', 'grant', package_name, permission]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def revoke_permission(package_name: str, permission: str, 
                         device_id: str = None):
        """撤销权限
        
        Args:
            package_name: 应用包名
            permission: 权限名称
            device_id: 设备 ID
        """
        cmd = ['shell', 'pm', 'revoke', package_name, permission]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def check_permission(package_name: str, permission: str, 
                        device_id: str = None) -> bool:
        """检查权限
        
        Args:
            package_name: 应用包名
            permission: 权限名称
            device_id: 设备 ID
            
        Returns:
            是否已授予权限
        """
        cmd = ['shell', 'dumpsys', 'package', package_name]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        return f"{permission}: granted=true" in result.stdout or \
               f"{permission}=granted" in result.stdout
    
    @staticmethod
    def list_packages(device_id: str = None, 
                     system_only: bool = False,
                     third_party_only: bool = False) -> List[str]:
        """列出已安装的应用包名
        
        Args:
            device_id: 设备 ID
            system_only: 仅系统应用
            third_party_only: 仅第三方应用
            
        Returns:
            包名列表
        """
        cmd = ['shell', 'pm', 'list', 'packages']
        
        if system_only:
            cmd.append('-s')
        elif third_party_only:
            cmd.append('-3')
        
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        packages = []
        
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                packages.append(line.replace('package:', '').strip())
        
        return packages
    
    @staticmethod
    def get_package_info(package_name: str, device_id: str = None) -> Dict:
        """获取应用信息
        
        Args:
            package_name: 应用包名
            device_id: 设备 ID
            
        Returns:
            应用信息字典
        """
        cmd = ['shell', 'dumpsys', 'package', package_name]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        
        # 解析基本信息
        info = {
            'package_name': package_name,
            'raw_output': result.stdout
        }
        
        # 提取版本号
        for line in result.stdout.split('\n'):
            if 'versionName=' in line:
                info['version_name'] = line.split('=')[1].strip()
            elif 'versionCode=' in line:
                info['version_code'] = line.split('=')[1].strip()
        
        return info
    
    @staticmethod
    def dump_package(package_name: str, device_id: str = None) -> str:
        """导出 APK 文件路径
        
        Args:
            package_name: 应用包名
            device_id: 设备 ID
            
        Returns:
            APK 文件在设备上的路径
        """
        cmd = ['shell', 'pm', 'path', package_name]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                return line.replace('package:', '').strip()
        
        return ""
    
    # ========== 文件操作 ==========
    @staticmethod
    def push(local_path: str, device_path: str, 
             device_id: str = None, mode: int = 0o644):
        """推送文件到设备
        
        Args:
            local_path: 本地文件路径
            device_path: 设备文件路径
            device_id: 设备 ID
            mode: 文件权限模式
        """
        cmd = ['push', local_path, device_path]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
        
        # 设置文件权限
        if mode:
            AdbUtils.shell(f'chmod {oct(mode)} {device_path}', device_id)
    
    @staticmethod
    def pull(device_path: str, local_path: str, 
             device_id: str = None):
        """从设备拉取文件
        
        Args:
            device_path: 设备文件路径
            local_path: 本地文件路径
            device_id: 设备 ID
        """
        cmd = ['pull', device_path, local_path]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def delete_file(device_path: str, device_id: str = None):
        """删除设备文件
        
        Args:
            device_path: 设备文件路径
            device_id: 设备 ID
        """
        cmd = ['shell', 'rm', device_path]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def list_files(device_path: str, device_id: str = None, 
                  recursive: bool = False) -> List[str]:
        """列出目录文件
        
        Args:
            device_path: 设备目录路径
            device_id: 设备 ID
            recursive: 是否递归列出
            
        Returns:
            文件路径列表
        """
        cmd = ['shell', 'ls']
        if recursive:
            cmd.append('-R')
        cmd.append(device_path)
        
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    
    @staticmethod
    def file_exists(device_path: str, device_id: str = None) -> bool:
        """检查文件是否存在
        
        Args:
            device_path: 设备文件路径
            device_id: 设备 ID
            
        Returns:
            文件是否存在
        """
        cmd = ['shell', 'test', '-e', device_path, '&&', 'echo', 'exists']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        return 'exists' in result.stdout
    
    # ========== 屏幕控制 ==========
    @staticmethod
    def screenshot(filename: str = None, device_id: str = None) -> Any:
        """截图
        
        Args:
            filename: 保存文件名，如果为 None 则返回 PIL Image 对象
            device_id: 设备 ID
            
        Returns:
            PIL Image 对象或 None
        """
        import tempfile
        
        # 在设备上截图
        temp_file = '/sdcard/screenshot.png'
        cmd = ['shell', 'screencap', '-p', temp_file]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
        
        # 拉取到本地
        if filename:
            AdbUtils.pull(temp_file, filename, device_id)
        else:
            # 返回 PIL Image
            try:
                from PIL import Image
                import io
                
                # 临时文件
                local_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                local_temp.close()
                
                AdbUtils.pull(temp_file, local_temp.name, device_id)
                
                with open(local_temp.name, 'rb') as f:
                    img = Image.open(io.BytesIO(f.read()))
                
                # 清理临时文件
                os.unlink(local_temp.name)
                
                # 清理设备上的截图
                AdbUtils.delete_file(temp_file, device_id)
                
                return img
            except ImportError:
                print("需要安装 Pillow: pip install Pillow")
                return None
        
        # 清理设备上的截图
        AdbUtils.delete_file(temp_file, device_id)
    
    @staticmethod
    def screenrecord(output_file: str, duration: int = 180, 
                    size: str = "1920x1080", bitrate: str = "4M",
                    device_id: str = None):
        """录制屏幕
        
        Args:
            output_file: 输出文件路径
            duration: 录制时长（秒），最大 180 秒
            size: 视频尺寸
            bitrate: 比特率
            device_id: 设备 ID
        """
        duration = min(duration, 180)  # 限制最大 180 秒
        
        cmd = ['shell', 'screenrecord', '--time-limit', str(duration),
               '--size', size, '--bit-rate', bitrate, output_file]
        
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd, timeout=duration + 10)
        
        # 拉取视频文件
        if output_file.startswith('/sdcard/'):
            local_file = os.path.basename(output_file)
            AdbUtils.pull(output_file, local_file, device_id)
    
    @staticmethod
    def get_resolution(device_id: str = None) -> Dict[str, int]:
        """获取屏幕分辨率
        
        Args:
            device_id: 设备 ID
            
        Returns:
            包含 width 和 height 的字典
        """
        cmd = ['shell', 'wm', 'size']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        
        # 解析输出：Physical size: 1080x1920
        for line in result.stdout.strip().split('\n'):
            if 'size:' in line:
                size_str = line.split(':')[-1].strip()
                if 'x' in size_str:
                    width, height = map(int, size_str.split('x'))
                    return {'width': width, 'height': height}
        
        return {'width': 0, 'height': 0}
    
    @staticmethod
    def set_resolution(width: int, height: int, 
                      device_id: str = None, density: int = None):
        """设置屏幕分辨率
        
        Args:
            width: 宽度
            height: 高度
            device_id: 设备 ID
            density: 屏幕密度（可选）
        """
        cmd = ['shell', 'wm', 'size', f'{width}x{height}']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
        
        if density:
            AdbUtils.set_density(density, device_id)
    
    @staticmethod
    def get_density(device_id: str = None) -> int:
        """获取屏幕密度
        
        Args:
            device_id: 设备 ID
            
        Returns:
            屏幕密度值
        """
        cmd = ['shell', 'wm', 'density']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        
        for line in result.stdout.strip().split('\n'):
            if 'density:' in line:
                return int(line.split(':')[-1].strip())
        
        return 0
    
    @staticmethod
    def set_density(density: int, device_id: str = None):
        """设置屏幕密度
        
        Args:
            density: 密度值
            device_id: 设备 ID
        """
        cmd = ['shell', 'wm', 'density', str(density)]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def get_brightness(device_id: str = None) -> int:
        """获取屏幕亮度
        
        Args:
            device_id: 设备 ID
            
        Returns:
            亮度值（0-255）
        """
        cmd = ['shell', 'settings', 'get', 'system', 'screen_brightness']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        try:
            return int(result.stdout.strip())
        except ValueError:
            return 0
    
    @staticmethod
    def set_brightness(brightness: int, device_id: str = None):
        """设置屏幕亮度
        
        Args:
            brightness: 亮度值（0-255）
            device_id: 设备 ID
        """
        brightness = max(0, min(255, brightness))
        cmd = ['shell', 'settings', 'put', 'system', 'screen_brightness', str(brightness)]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def set_timeout(timeout_ms: int, device_id: str = None):
        """设置屏幕超时时间
        
        Args:
            timeout_ms: 超时时间（毫秒）
            device_id: 设备 ID
        """
        cmd = ['shell', 'settings', 'put', 'system', 'screen_off_timeout', str(timeout_ms)]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    # ========== 输入事件 ==========
    @staticmethod
    def tap(x: int, y: int, device_id: str = None):
        """点击坐标
        
        Args:
            x: X 坐标
            y: Y 坐标
            device_id: 设备 ID
        """
        cmd = ['shell', 'input', 'tap', str(x), str(y)]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def double_tap(x: int, y: int, device_id: str = None):
        """双击坐标
        
        Args:
            x: X 坐标
            y: Y 坐标
            device_id: 设备 ID
        """
        AdbUtils.tap(x, y, device_id)
        time.sleep(0.1)
        AdbUtils.tap(x, y, device_id)
    
    @staticmethod
    def long_press(x: int, y: int, duration: int = 1000, 
                   device_id: str = None):
        """长按坐标
        
        Args:
            x: X 坐标
            y: Y 坐标
            duration: 按压时长（毫秒）
            device_id: 设备 ID
        """
        cmd = ['shell', 'input', 'swipe', str(x), str(y), 
               str(x), str(y), str(duration)]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def swipe(start_x: int, start_y: int, end_x: int, end_y: int, 
              duration: int = 300, device_id: str = None):
        """滑动
        
        Args:
            start_x: 起始 X 坐标
            start_y: 起始 Y 坐标
            end_x: 结束 X 坐标
            end_y: 结束 Y 坐标
            duration: 滑动时长（毫秒）
            device_id: 设备 ID
        """
        cmd = ['shell', 'input', 'swipe', str(start_x), str(start_y),
               str(end_x), str(end_y), str(duration)]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def drag(start_x: int, start_y: int, end_x: int, end_y: int, 
             duration: int = 300, device_id: str = None):
        """拖动
        
        Args:
            start_x: 起始 X 坐标
            start_y: 起始 Y 坐标
            end_x: 结束 X 坐标
            end_y: 结束 Y 坐标
            duration: 拖动时长（毫秒）
            device_id: 设备 ID
        """
        cmd = ['shell', 'input', 'drag', str(start_x), str(start_y),
               str(end_x), str(end_y), str(duration)]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def press_key(keycode: int, device_id: str = None):
        """按下按键（使用键码）
        
        Args:
            keycode: 键码值
            device_id: 设备 ID
        """
        cmd = ['shell', 'input', 'keyevent', str(keycode)]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def press_home(device_id: str = None):
        """按 Home 键"""
        AdbUtils.press_key(KeyCodes.HOME.value, device_id)
    
    @staticmethod
    def press_back(device_id: str = None):
        """按返回键"""
        AdbUtils.press_key(KeyCodes.BACK.value, device_id)
    
    @staticmethod
    def press_menu(device_id: str = None):
        """按菜单键"""
        AdbUtils.press_key(KeyCodes.MENU.value, device_id)
    
    @staticmethod
    def press_enter(device_id: str = None):
        """按回车键"""
        AdbUtils.press_key(KeyCodes.ENTER.value, device_id)
    
    @staticmethod
    def press_recent(device_id: str = None):
        """按最近任务键"""
        AdbUtils.press_key(KeyCodes.RECENT_APPS.value, device_id)
    
    @staticmethod
    def press_volume_up(device_id: str = None):
        """按音量加键"""
        AdbUtils.press_key(KeyCodes.VOLUME_UP.value, device_id)
    
    @staticmethod
    def press_volume_down(device_id: str = None):
        """按音量减键"""
        AdbUtils.press_key(KeyCodes.VOLUME_DOWN.value, device_id)
    
    @staticmethod
    def press_mute(device_id: str = None):
        """按静音键"""
        AdbUtils.press_key(KeyCodes.VOLUME_MUTE.value, device_id)
    
    @staticmethod
    def press_power(device_id: str = None):
        """按电源键"""
        AdbUtils.press_key(KeyCodes.POWER.value, device_id)
    
    @staticmethod
    def input_text(text: str, device_id: str = None):
        """输入文本
        
        Args:
            text: 要输入的文本
            device_id: 设备 ID
        """
        # 转义特殊字符
        escaped_text = text.replace(' ', '%s').replace('&', '\\&')
        cmd = ['shell', 'input', 'text', escaped_text]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def input_keyevent(keycode: int, device_id: str = None):
        """输入键事件
        
        Args:
            keycode: 键码值
            device_id: 设备 ID
        """
        AdbUtils.press_key(keycode, device_id)
    
    # ========== 系统信息 ==========
    @staticmethod
    def get_device_info(device_id: str = None) -> Dict[str, Any]:
        """获取设备详细信息
        
        Args:
            device_id: 设备 ID
            
        Returns:
            设备信息字典
        """
        props = {
            'brand': 'ro.product.brand',
            'model': 'ro.product.model',
            'manufacturer': 'ro.product.manufacturer',
            'device': 'ro.product.device',
            'android_version': 'ro.build.version.release',
            'sdk_version': 'ro.build.version.sdk',
            'security_patch': 'ro.build.version.security_patch',
            'fingerprint': 'ro.build.fingerprint',
        }
        
        info = {}
        for key, prop in props.items():
            cmd = ['shell', 'getprop', prop]
            if device_id:
                cmd.insert(0, device_id)
                cmd.insert(0, '-s')
            
            result = AdbUtils.run_command(cmd)
            info[key] = result.stdout.strip()
        
        # 获取序列号
        info['serial'] = AdbUtils.get_serial_number(device_id)
        
        return info
    
    @staticmethod
    def get_android_version(device_id: str = None) -> str:
        """获取 Android 版本"""
        cmd = ['shell', 'getprop', 'ro.build.version.release']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        return result.stdout.strip()
    
    @staticmethod
    def get_sdk_version(device_id: str = None) -> int:
        """获取 SDK 版本"""
        cmd = ['shell', 'getprop', 'ro.build.version.sdk']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        try:
            return int(result.stdout.strip())
        except ValueError:
            return 0
    
    @staticmethod
    def get_manufacturer(device_id: str = None) -> str:
        """获取设备制造商"""
        cmd = ['shell', 'getprop', 'ro.product.manufacturer']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        return result.stdout.strip()
    
    @staticmethod
    def get_model(device_id: str = None) -> str:
        """获取设备型号"""
        cmd = ['shell', 'getprop', 'ro.product.model']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        return result.stdout.strip()
    
    @staticmethod
    def get_serial_number(device_id: str = None) -> str:
        """获取序列号"""
        cmd = ['get-serialno']
        if device_id:
            cmd = ['-s', device_id, 'get-serialno']
        
        result = AdbUtils.run_command(cmd)
        return result.stdout.strip()
    
    @staticmethod
    def get_network_type(device_id: str = None) -> str:
        """获取网络类型"""
        cmd = ['shell', 'dumpsys', 'telephony.registry']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        
        if 'mDataNetworkType=' in result.stdout:
            for line in result.stdout.split('\n'):
                if 'mDataNetworkType=' in line:
                    return line.split('=')[1].strip()
        
        return "unknown"
    
    @staticmethod
    def get_ip_address(device_id: str = None) -> str:
        """获取 IP 地址"""
        cmd = ['shell', 'ip', 'addr', 'show', 'wlan0']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        
        for line in result.stdout.split('\n'):
            if 'inet ' in line and 'brd' in line:
                ip = line.split()[1].split('/')[0]
                return ip
        
        return ""
    
    @staticmethod
    def get_battery_info(device_id: str = None) -> Dict:
        """获取电池信息"""
        cmd = ['shell', 'dumpsys', 'battery']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        info = {}
        
        for line in result.stdout.split('\n'):
            if 'level:' in line:
                info['level'] = int(line.split(':')[1].strip())
            elif 'status:' in line:
                info['status'] = int(line.split(':')[1].strip())
            elif 'plugged:' in line:
                info['plugged'] = int(line.split(':')[1].strip())
            elif 'temperature:' in line:
                info['temperature'] = float(line.split(':')[1].strip()) / 10
            elif 'voltage:' in line:
                info['voltage'] = int(line.split(':')[1].strip())
        
        return info
    
    @staticmethod
    def get_memory_info(device_id: str = None) -> Dict:
        """获取内存信息"""
        cmd = ['shell', 'cat', '/proc/meminfo']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        info = {}
        
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':')
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                info[key] = value
        
        return info
    
    @staticmethod
    def get_cpu_info(device_id: str = None) -> Dict:
        """获取 CPU 信息"""
        cmd = ['shell', 'cat', '/proc/cpuinfo']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        info = {}
        
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':')
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                info[key] = value
        
        return info
    
    @staticmethod
    def get_storage_info(device_id: str = None) -> Dict:
        """获取存储信息"""
        cmd = ['shell', 'df', '-h']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        info = {}
        
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            headers = lines[0].split()
            values = lines[1].split()
            
            for i, header in enumerate(headers):
                if i < len(values):
                    info[header.lower()] = values[i]
        
        return info
    
    # ========== 日志抓取 ==========
    @staticmethod
    def get_logcat(output_file: str = None, lines: int = 1000, 
                   filter_spec: str = None, device_id: str = None) -> str:
        """抓取 logcat 日志
        
        Args:
            output_file: 输出文件路径（可选）
            lines: 获取行数
            filter_spec: 过滤规则，如 "ActivityManager:I"
            device_id: 设备 ID
            
        Returns:
            日志内容
        """
        cmd = ['logcat', '-d', '-t', str(lines)]
        
        if filter_spec:
            cmd.append(filter_spec)
        
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
        
        return result.stdout
    
    @staticmethod
    def clear_logcat(device_id: str = None):
        """清空 logcat 日志"""
        cmd = ['logcat', '-c']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def get_crash_logs(device_id: str = None) -> Dict:
        """获取崩溃日志
        
        Args:
            device_id: 设备 ID
            
        Returns:
            崩溃日志字典
        """
        crashes = {}
        
        # 获取 ANR 日志
        anr_cmd = ['shell', 'cat', '/data/anr/traces.txt']
        if device_id:
            anr_cmd.insert(0, device_id)
            anr_cmd.insert(0, '-s')
        
        try:
            result = AdbUtils.run_command(anr_cmd)
            crashes['anr'] = result.stdout[:10000]  # 限制大小
        except:
            crashes['anr'] = ""
        
        # 获取 tombstone 日志
        tomb_cmd = ['shell', 'ls', '/data/tombstones/']
        if device_id:
            tomb_cmd.insert(0, device_id)
            tomb_cmd.insert(0, '-s')
        
        try:
            result = AdbUtils.run_command(tomb_cmd)
            crashes['tombstones'] = result.stdout.strip().split('\n')
        except:
            crashes['tombstones'] = []
        
        return crashes
    
    @staticmethod
    def dumpsys(service_name: str = None, device_id: str = None) -> str:
        """获取 dumpsys 信息
        
        Args:
            service_name: 服务名称，如 "battery", "meminfo"
            device_id: 设备 ID
            
        Returns:
            dumpsys 输出内容
        """
        if service_name:
            cmd = ['shell', 'dumpsys', service_name]
        else:
            cmd = ['shell', 'dumpsys']
        
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd, timeout=60)
        return result.stdout
    
    @staticmethod
    def dumpsys_battery(device_id: str = None) -> Dict:
        """获取电池 dumpsys 信息"""
        output = AdbUtils.dumpsys('battery', device_id)
        return AdbUtils.parse_dumpsys_output(output)
    
    @staticmethod
    def dumpsys_memory(device_id: str = None) -> Dict:
        """获取内存 dumpsys 信息"""
        output = AdbUtils.dumpsys('meminfo', device_id)
        return AdbUtils.parse_dumpsys_output(output)
    
    @staticmethod
    def dumpsys_cpu(device_id: str = None) -> Dict:
        """获取 CPU dumpsys 信息"""
        output = AdbUtils.dumpsys('cpuinfo', device_id)
        return AdbUtils.parse_dumpsys_output(output)
    
    @staticmethod
    def parse_dumpsys_output(output: str) -> Dict:
        """解析 dumpsys 输出
        
        Args:
            output: dumpsys 输出内容
            
        Returns:
            解析后的字典
        """
        # 简单解析，实际可以更复杂
        return {'raw': output}
    
    # ========== 网络管理 ==========
    @staticmethod
    def enable_wifi(device_id: str = None):
        """启用 WiFi"""
        AdbUtils.shell('svc wifi enable', device_id)
    
    @staticmethod
    def disable_wifi(device_id: str = None):
        """禁用 WiFi"""
        AdbUtils.shell('svc wifi disable', device_id)
    
    @staticmethod
    def connect_wifi(ip: str, port: int = 5555, device_id: str = None):
        """WiFi 连接设备
        
        Args:
            ip: 设备 IP 地址
            port: 端口号，默认 5555
            device_id: 设备 ID
        """
        # 先切换到 TCP 模式
        if device_id:
            AdbUtils.tcpip(port, device_id)
        
        # 连接到 WiFi
        cmd = ['connect', f'{ip}:{port}']
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def disconnect_wifi(device_id: str = None):
        """断开 WiFi 连接"""
        cmd = ['disconnect']
        if device_id:
            cmd.append(device_id)
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def list_wifi_connections(device_id: str = None) -> List[Dict]:
        """列出 WiFi 连接"""
        cmd = ['devices', '-l']
        result = AdbUtils.run_command(cmd)
        
        connections = []
        for line in result.stdout.strip().split('\n')[1:]:
            if line.strip() and '.' in line:  # IP 地址包含点
                parts = line.split()
                if len(parts) >= 2:
                    connections.append({
                        'address': parts[0],
                        'status': parts[1]
                    })
        
        return connections
    
    @staticmethod
    def tcpip(port: int = 5555, device_id: str = None):
        """切换到 TCP/IP 模式
        
        Args:
            port: 端口号
            device_id: 设备 ID
        """
        cmd = ['tcpip', str(port)]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def enable_bluetooth(device_id: str = None):
        """启用蓝牙"""
        AdbUtils.shell('svc bluetooth enable', device_id)
    
    @staticmethod
    def disable_bluetooth(device_id: str = None):
        """禁用蓝牙"""
        AdbUtils.shell('svc bluetooth disable', device_id)
    
    @staticmethod
    def toggle_airplane_mode(enable: bool, device_id: str = None):
        """切换飞行模式
        
        Args:
            enable: True 开启，False 关闭
            device_id: 设备 ID
        """
        state = 'enable' if enable else 'disable'
        AdbUtils.shell(f'svc airplane {state}', device_id)
    
    @staticmethod
    def toggle_mobile_data(enable: bool, device_id: str = None):
        """切换移动数据
        
        Args:
            enable: True 开启，False 关闭
            device_id: 设备 ID
        """
        state = 'enable' if enable else 'disable'
        AdbUtils.shell(f'svc data {state}', device_id)
    
    # ========== 剪贴板 ==========
    @staticmethod
    def set_clipboard(text: str, device_id: str = None):
        """设置剪贴板
        
        Args:
            text: 文本内容
            device_id: 设备 ID
        """
        # 需要使用 input method 或者通过 am broadcast
        cmd = ['shell', 'am', 'broadcast', '-a', 'CLIPBOARD_SET', 
               '--es', 'text', text]
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def get_clipboard(device_id: str = None) -> str:
        """获取剪贴板
        
        Args:
            device_id: 设备 ID
            
        Returns:
            剪贴板内容
        """
        # 这个需要通过 accessibility 或者 root 权限获取
        # 这里提供一个简化的实现
        return ""
    
    # ========== 通知栏 ==========
    @staticmethod
    def open_notification(device_id: str = None):
        """打开通知栏"""
        cmd = ['shell', 'cmd', 'statusbar', 'expand-notifications']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def close_notification(device_id: str = None):
        """关闭通知栏"""
        cmd = ['shell', 'cmd', 'statusbar', 'collapse']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)
    
    @staticmethod
    def expand_notification(device_id: str = None):
        """展开通知栏"""
        AdbUtils.open_notification(device_id)
    
    @staticmethod
    def collapse_notification(device_id: str = None):
        """收起通知栏"""
        AdbUtils.close_notification(device_id)
    
    # ========== Shell 命令 ==========
    @staticmethod
    def shell(command: str, device_id: str = None, 
             timeout: int = 30) -> str:
        """执行 Shell 命令
        
        Args:
            command: Shell 命令
            device_id: 设备 ID
            timeout: 超时时间（秒）
            
        Returns:
            命令输出
        """
        cmd = ['shell'] + command.split()
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        result = AdbUtils.run_command(cmd, timeout=timeout)
        return result.stdout
    
    @staticmethod
    def shell_background(command: str, device_id: str = None):
        """后台执行 Shell 命令
        
        Args:
            command: Shell 命令
            device_id: 设备 ID
        """
        cmd = ['shell', command, '&']
        if device_id:
            cmd.insert(0, device_id)
            cmd.insert(0, '-s')
        
        AdbUtils.run_command(cmd)


# 导入 time 模块用于延时
import time
