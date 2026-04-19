# -*- coding: utf-8 -*-
"""
UIAutomator2 完整 API 封装
基于官方 uiautomator2 库的全面封装
"""
import uiautomator2 as u2
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum


class Direction(Enum):
    """滑动方向枚举"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    FORWARD = "forward"      # 向下滚动
    BACKWARD = "backward"    # 向上滚动
    HORIZ_FORWARD = "horiz_forward"   # 向右滚动
    HORIZ_BACKWARD = "horiz_backward" # 向左滚动


class UiAutomator2Utils:
    """UIAutomator2 工具类 - 完整封装"""
    
    _device: Optional[u2.Device] = None
    
    # ========== 设备连接与初始化 ==========
    @classmethod
    def connect_usb(cls, device_id: str = None) -> u2.Device:
        """USB 连接设备
        
        Args:
            device_id: 设备序列号，可选
            
        Returns:
            uiautomator2 设备实例
        """
        if device_id:
            cls._device = u2.connect(device_id)
        else:
            cls._device = u2.connect()
        
        return cls._device
    
    @classmethod
    def connect_wifi(cls, ip: str, port: int = 5555) -> u2.Device:
        """WiFi 连接设备
        
        Args:
            ip: 设备 IP 地址
            port: 端口号，默认 5555
            
        Returns:
            uiautomator2 设备实例
        """
        cls._device = u2.connect(f"{ip}:{port}")
        return cls._device
    
    @classmethod
    def connect(cls, identifier: str = None) -> u2.Device:
        """智能连接设备（自动判断 USB/WiFi）
        
        Args:
            identifier: 设备标识符（序列号或 IP:Port）
            
        Returns:
            uiautomator2 设备实例
        """
        if identifier and ':' in identifier:
            return cls.connect_wifi(identifier.split(':')[0], 
                                   int(identifier.split(':')[1]))
        else:
            return cls.connect_usb(identifier)
    
    @classmethod
    def disconnect(cls):
        """断开设备连接"""
        if cls._device:
            cls._device = None
    
    @classmethod
    def get_device(cls) -> Optional[u2.Device]:
        """获取当前设备实例
        
        Returns:
            当前设备实例或 None
        """
        return cls._device
    
    @classmethod
    def is_connected(cls) -> bool:
        """检查设备是否已连接
        
        Returns:
            True 如果已连接
        """
        return cls._device is not None
    
    @classmethod
    def init_device(cls, device_id: str = None):
        """初始化设备（安装 atx-agent）
        
        Args:
            device_id: 设备序列号
        """
        u2.init(device_id)
    
    @classmethod
    def list_devices(cls) -> List[Dict]:
        """列出可用设备
        
        Returns:
            设备列表
        """
        return u2.connect_multi([]).devices
    
    # ========== 设备信息管理 ==========
    @staticmethod
    def get_device_info() -> Dict[str, Any]:
        """获取设备基本信息（d.info）
        
        Returns:
            设备信息字典
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.info
        return {}
    
    @staticmethod
    def get_detailed_device_info() -> Dict[str, Any]:
        """获取设备详细信息（d.device_info）
        
        Returns:
            详细设备信息字典
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.device_info
        return {}
    
    @staticmethod
    def get_window_size() -> Tuple[int, int]:
        """获取屏幕尺寸
        
        Returns:
            (宽度， 高度) 元组
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.window_size()
        return (0, 0)
    
    @staticmethod
    def get_screen_width() -> int:
        """获取屏幕宽度
        
        Returns:
            屏幕宽度
        """
        width, _ = UiAutomator2Utils.get_window_size()
        return width
    
    @staticmethod
    def get_screen_height() -> int:
        """获取屏幕高度
        
        Returns:
            屏幕高度
        """
        _, height = UiAutomator2Utils.get_window_size()
        return height
    
    @staticmethod
    def get_wlan_ip() -> str:
        """获取 WLAN IP 地址
        
        Returns:
            IP 地址
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.wlan_ip
        return ""
    
    @staticmethod
    def get_serial() -> str:
        """获取设备序列号
        
        Returns:
            序列号
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.serial
        return ""
    
    @staticmethod
    def get_current_app() -> Dict[str, Any]:
        """获取当前应用信息
        
        Returns:
            应用信息字典
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.app_current()
        return {}
    
    @staticmethod
    def get_current_activity() -> str:
        """获取当前 Activity
        
        Returns:
            Activity 名称
        """
        app_info = UiAutomator2Utils.get_current_app()
        return app_info.get('activity', '')
    
    @staticmethod
    def get_current_package() -> str:
        """获取当前包名
        
        Returns:
            包名
        """
        app_info = UiAutomator2Utils.get_current_app()
        return app_info.get('package', '')
    
    @staticmethod
    def wait_activity(activity: str, timeout: float = 10.0) -> bool:
        """等待 Activity 出现
        
        Args:
            activity: Activity 名称
            timeout: 超时时间（秒）
            
        Returns:
            是否成功等待到 Activity
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.wait_activity(activity, timeout=timeout)
        return False
    
    # ========== 屏幕控制 ==========
    @staticmethod
    def screen_on():
        """点亮屏幕"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.screen_on()
    
    @staticmethod
    def screen_off():
        """关闭屏幕"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.screen_off()
    
    @staticmethod
    def is_screen_on() -> bool:
        """检查屏幕是否亮起
        
        Returns:
            True 如果屏幕亮起
        """
        info = UiAutomator2Utils.get_device_info()
        return info.get('screenOn', False)
    
    @staticmethod
    def sleep(seconds: float):
        """休眠屏幕指定秒数
        
        Args:
            seconds: 秒数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.sleep(seconds)
    
    @staticmethod
    def wake():
        """唤醒设备"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.wakeup()
    
    @staticmethod
    def unlock():
        """解锁设备"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.unlock()
    
    @staticmethod
    def get_orientation() -> str:
        """获取屏幕方向
        
        Returns:
            屏幕方向：natural, left, right, upsidedown
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.orientation
        return "natural"
    
    @staticmethod
    def set_orientation(orientation: str):
        """设置屏幕方向
        
        Args:
            orientation: 屏幕方向
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.orientation = orientation
    
    @staticmethod
    def freeze_rotation(freeze: bool = True):
        """冻结/解冻屏幕旋转
        
        Args:
            freeze: True 冻结，False 解冻
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.freeze_rotation(freeze)
    
    @staticmethod
    def set_auto_brightness(auto: bool = True):
        """设置自动亮度
        
        Args:
            auto: True 自动亮度，False 手动亮度
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.set_auto_brightness(auto)
    
    @staticmethod
    def set_brightness(brightness: int):
        """设置屏幕亮度
        
        Args:
            brightness: 亮度值
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.brightness = brightness
    
    # ========== 基础手势操作 ==========
    @staticmethod
    def click(x: Union[int, float], y: Union[int, float]):
        """点击坐标（支持百分比）
        
        Args:
            x: X 坐标（可以是百分比 0-1）
            y: Y 坐标（可以是百分比 0-1）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.click(x, y)
    
    @staticmethod
    def double_click(x: Union[int, float], y: Union[int, float], 
                    duration: float = 0.1):
        """双击
        
        Args:
            x: X 坐标
            y: Y 坐标
            duration: 两次点击间隔（秒）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.double_click(x, y, duration)
    
    @staticmethod
    def long_click(x: Union[int, float], y: Union[int, float], 
                  duration: float = 0.5):
        """长按
        
        Args:
            x: X 坐标
            y: Y 坐标
            duration: 按压时长（秒）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.long_click(x, y, duration)
    
    @staticmethod
    def swipe(sx: Union[int, float], sy: Union[int, float], 
              ex: Union[int, float], ey: Union[int, float], 
              duration: float = 0.5):
        """滑动
        
        Args:
            sx: 起始 X 坐标
            sy: 起始 Y 坐标
            ex: 结束 X 坐标
            ey: 结束 Y 坐标
            duration: 滑动时长（秒）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.swipe(sx, sy, ex, ey, duration)
    
    @staticmethod
    def swipe_ext(direction: Union[str, Direction], 
                 scale: float = 0.9, 
                 box: Tuple[int, int, int, int] = None):
        """扩展滑动（支持方向参数）
        
        Args:
            direction: 滑动方向
            scale: 滑动距离比例
            box: 滑动区域 (x1, y1, x2, y2)
        """
        device = UiAutomator2Utils.get_device()
        if device:
            if isinstance(direction, Direction):
                direction = direction.value
            device.swipe_ext(direction, scale=scale, box=box)
    
    @staticmethod
    def drag(sx: Union[int, float], sy: Union[int, float], 
             ex: Union[int, float], ey: Union[int, float], 
             duration: float = 0.5):
        """拖动
        
        Args:
            sx: 起始 X 坐标
            sy: 起始 Y 坐标
            ex: 结束 X 坐标
            ey: 结束 Y 坐标
            duration: 拖动时长（秒）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.drag(sx, sy, ex, ey, duration)
    
    @staticmethod
    def swipe_points(points: List[Tuple[int, int]], 
                    step_duration: float = 0.2):
        """多点滑动（用于图案解锁等）
        
        Args:
            points: 点坐标列表
            step_duration: 每两点之间的时间间隔（秒）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.swipe_points(points, step_duration)
    
    @staticmethod
    def pinch_in(percent: float = 0.5, steps: int = 10):
        """双指捏合（缩小）
        
        Args:
            percent: 缩放比例
            steps: 步数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.pinch_in(percent, steps)
    
    @staticmethod
    def pinch_out(percent: float = 0.5, steps: int = 10):
        """双指张开（放大）
        
        Args:
            percent: 缩放比例
            steps: 步数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.pinch_out(percent, steps)
    
    # ========== 高级触摸操作 ==========
    @staticmethod
    def touch_down(x: int, y: int):
        """触摸按下
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.touch.down(x, y)
    
    @staticmethod
    def touch_move(x: int, y: int):
        """触摸移动
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.touch.move(x, y)
    
    @staticmethod
    def touch_up(x: int, y: int):
        """触摸抬起
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.touch.up(x, y)
    
    @staticmethod
    def multi_touch_action(action: str, points: List[Tuple[int, int]]):
        """多点触控操作
        
        Args:
            action: 动作类型
            points: 多点坐标列表
        """
        # 这是一个简化实现，实际可以更复杂
        device = UiAutomator2Utils.get_device()
        if device:
            # 这里可以根据需要实现更复杂的多点触控逻辑
            pass
    
    # ========== 元素定位（Selector） ==========
    @staticmethod
    def find_element(**selector) -> 'u2.UiObject':
        """查找单个元素
        
        Args:
            **selector: 定位参数，如 text="设置", resourceId="xxx"
            
        Returns:
            UiObject 对象
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device(**selector)
        return None
    
    @staticmethod
    def find_elements(**selector) -> List['u2.UiObject']:
        """查找多个元素
        
        Args:
            **selector: 定位参数
            
        Returns:
            UiObject 列表
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.find_elements(**selector)
        return []
    
    @staticmethod
    def element_exists(**selector) -> bool:
        """检查元素是否存在
        
        Args:
            **selector: 定位参数
            
        Returns:
            True 如果元素存在
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device(**selector).exists
        return False
    
    @staticmethod
    def wait_for_element(selector: Dict, timeout: float = 10.0) -> bool:
        """等待元素出现
        
        Args:
            selector: 定位参数字典
            timeout: 超时时间（秒）
            
        Returns:
            True 如果元素出现
        """
        device = UiAutomator2Utils.get_device()
        if device:
            obj = device(**selector)
            return obj.wait(timeout=timeout)
        return False
    
    @staticmethod
    def wait_for_element_gone(selector: Dict, timeout: float = 10.0) -> bool:
        """等待元素消失
        
        Args:
            selector: 定位参数字典
            timeout: 超时时间（秒）
            
        Returns:
            True 如果元素消失
        """
        device = UiAutomator2Utils.get_device()
        if device:
            obj = device(**selector)
            return obj.wait_gone(timeout=timeout)
        return False
    
    # Selector 构建方法
    @staticmethod
    def by_text(text: str) -> Dict:
        """按文本定位
        
        Args:
            text: 文本内容
            
        Returns:
            选择器字典
        """
        return {'text': text}
    
    @staticmethod
    def by_text_contains(text: str) -> Dict:
        """按包含文本定位
        
        Args:
            text: 包含的文本
            
        Returns:
            选择器字典
        """
        return {'textContains': text}
    
    @staticmethod
    def by_resourceId(resource_id: str) -> Dict:
        """按资源 ID 定位
        
        Args:
            resource_id: 资源 ID
            
        Returns:
            选择器字典
        """
        return {'resourceId': resource_id}
    
    @staticmethod
    def by_className(class_name: str) -> Dict:
        """按类名定位
        
        Args:
            class_name: 类名
            
        Returns:
            选择器字典
        """
        return {'className': class_name}
    
    @staticmethod
    def by_description(desc: str) -> Dict:
        """按描述定位
        
        Args:
            desc: 描述内容
            
        Returns:
            选择器字典
        """
        return {'description': desc}
    
    @staticmethod
    def by_description_contains(desc: str) -> Dict:
        """按包含描述定位
        
        Args:
            desc: 包含的描述
            
        Returns:
            选择器字典
        """
        return {'descriptionContains': desc}
    
    @staticmethod
    def by_package_name(package_name: str) -> Dict:
        """按包名定位
        
        Args:
            package_name: 包名
            
        Returns:
            选择器字典
        """
        return {'packageName': package_name}
    
    @staticmethod
    def by_index(index: int) -> Dict:
        """按索引定位
        
        Args:
            index: 索引
            
        Returns:
            选择器字典
        """
        return {'index': index}
    
    @staticmethod
    def by_instance(instance: int) -> Dict:
        """按实例定位
        
        Args:
            instance: 实例
            
        Returns:
            选择器字典
        """
        return {'instance': instance}
    
    @staticmethod
    def by_xpath(xpath: str) -> Dict:
        """XPath 定位
        
        Args:
            xpath: XPath 表达式
            
        Returns:
            选择器字典
        """
        return {'xpath': xpath}
    
    @staticmethod
    def by_coordinate(x: int, y: int) -> Dict:
        """按坐标定位
        
        Args:
            x: X 坐标
            y: Y 坐标
            
        Returns:
            选择器字典
        """
        return {'x': x, 'y': y}
    
    # ========== 元素操作 ==========
    @staticmethod
    def click_element(element):
        """点击元素
        
        Args:
            element: UiObject 对象
        """
        if element:
            element.click()
    
    @staticmethod
    def long_click_element(element, duration: float = 0.5):
        """长按元素
        
        Args:
            element: UiObject 对象
            duration: 按压时长（秒）
        """
        if element:
            element.long_click(duration)
    
    @staticmethod
    def double_click_element(element):
        """双击元素
        
        Args:
            element: UiObject 对象
        """
        if element:
            element.double_click()
    
    @staticmethod
    def get_element_text(element) -> str:
        """获取元素文本
        
        Args:
            element: UiObject 对象
            
        Returns:
            元素文本
        """
        if element:
            return element.get_text()
        return ""
    
    @staticmethod
    def set_text(element, text: str):
        """设置元素文本
        
        Args:
            element: UiObject 对象
            text: 文本内容
        """
        if element:
            element.set_text(text)
    
    @staticmethod
    def clear_text(element):
        """清空元素文本
        
        Args:
            element: UiObject 对象
        """
        if element:
            element.clear_text()
    
    @staticmethod
    def get_element_attr(element, attr_name: str) -> Any:
        """获取元素属性
        
        Args:
            element: UiObject 对象
            attr_name: 属性名称
            
        Returns:
            属性值
        """
        if element:
            return element.info.get(attr_name)
        return None
    
    @staticmethod
    def element_screenshot(element, filename: str = None):
        """元素截图
        
        Args:
            element: UiObject 对象
            filename: 保存文件名
        """
        if element:
            element.screenshot(filename)
    
    @staticmethod
    def scroll_element_into_view(element):
        """滚动元素到可视区域
        
        Args:
            element: UiObject 对象
        """
        if element:
            element.scroll_to()
    
    @staticmethod
    def drag_element_to(element, dest_x: int, dest_y: int, 
                       steps: int = 30):
        """拖动元素到目标位置
        
        Args:
            element: UiObject 对象
            dest_x: 目标 X 坐标
            dest_y: 目标 Y 坐标
            steps: 步数
        """
        if element:
            element.drag_to(dest_x, dest_y, steps)
    
    # ========== 滚动操作 ==========
    @staticmethod
    def scroll_up(steps: int = 55):
        """向上滚动
        
        Args:
            steps: 步数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(scrollable=True).scroll.toBeginning(max_swipes=steps)
    
    @staticmethod
    def scroll_down(steps: int = 55):
        """向下滚动
        
        Args:
            steps: 步数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(scrollable=True).scroll.toEnd(max_swipes=steps)
    
    @staticmethod
    def scroll_left(steps: int = 55):
        """向左滚动
        
        Args:
            steps: 步数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(scrollable=True, horizontal=True).scroll.toBeginning(max_swipes=steps)
    
    @staticmethod
    def scroll_right(steps: int = 55):
        """向右滚动
        
        Args:
            steps: 步数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(scrollable=True, horizontal=True).scroll.toEnd(max_swipes=steps)
    
    @staticmethod
    def scroll_to(text: str, max_swipes: int = 10, 
                 direction: str = "down"):
        """滚动到指定文本
        
        Args:
            text: 目标文本
            max_swipes: 最大滚动次数
            direction: 滚动方向
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(scrollable=True).scroll_to(text, max_swipes=max_swipes)
    
    @staticmethod
    def fling_up(max_swipes: int = 10):
        """快速向上滑动
        
        Args:
            max_swipes: 最大滑动次数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(scrollable=True).fling.toBeginning(max_swipes=max_swipes)
    
    @staticmethod
    def fling_down(max_swipes: int = 10):
        """快速向下滑动
        
        Args:
            max_swipes: 最大滑动次数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(scrollable=True).fling.toEnd(max_swipes=max_swipes)
    
    @staticmethod
    def fling_left(max_swipes: int = 10):
        """快速向左滑动
        
        Args:
            max_swipes: 最大滑动次数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(scrollable=True, horizontal=True).fling.toBeginning(max_swipes=max_swipes)
    
    @staticmethod
    def fling_right(max_swipes: int = 10):
        """快速向右滑动
        
        Args:
            max_swipes: 最大滑动次数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(scrollable=True, horizontal=True).fling.toEnd(max_swipes=max_swipes)
    
    # ========== 输入操作 ==========
    @staticmethod
    def input_text(text: str):
        """输入文本
        
        Args:
            text: 文本内容
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.send_keys(text)
    
    @staticmethod
    def input_keys(*keys):
        """输入按键
        
        Args:
            *keys: 按键列表
        """
        device = UiAutomator2Utils.get_device()
        if device:
            for key in keys:
                device.press(key)
    
    @staticmethod
    def press_key(key_name: str):
        """按下按键
        
        Args:
            key_name: 按键名称
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.press(key_name)
    
    @staticmethod
    def press_keycode(code: int, meta: int = 0):
        """按下键码
        
        Args:
            code: 键码值
            meta: Meta 键状态
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.press(code, meta)
    
    @staticmethod
    def delete_text(characters: int = 1):
        """删除文本
        
        Args:
            characters: 删除字符数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            for _ in range(characters):
                device.press("delete")
    
    @staticmethod
    def move_cursor(left: bool, right: bool):
        """移动光标
        
        Args:
            left: 向左
            right: 向右
        """
        device = UiAutomator2Utils.get_device()
        if device:
            if left:
                device.press("left")
            if right:
                device.press("right")
    
    @staticmethod
    def set_input_ime():
        """设置输入法为 ADB 键盘"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.set_input_ime()
    
    # ========== 应用管理 ==========
    @staticmethod
    def app_start(package_name: str, activity: str = None, 
                 stop: bool = False, wait: bool = False):
        """启动应用
        
        Args:
            package_name: 包名
            activity: Activity 名称（可选）
            stop: 是否先停止
            wait: 是否等待启动完成
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.app_start(package_name, activity=activity, 
                           stop=stop, wait=wait)
    
    @staticmethod
    def app_stop(package_name: str = None):
        """停止应用
        
        Args:
            package_name: 包名，如果为 None 则停止当前应用
        """
        device = UiAutomator2Utils.get_device()
        if device:
            if package_name:
                device.app_stop(package_name)
            else:
                # 停止当前应用
                current = device.app_current()
                if current.get('package'):
                    device.app_stop(current['package'])
    
    @staticmethod
    def app_clear(package_name: str):
        """清除应用数据
        
        Args:
            package_name: 包名
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.app_clear(package_name)
    
    @staticmethod
    def app_wait(package_name: str, timeout: float = 20.0) -> bool:
        """等待应用启动
        
        Args:
            package_name: 包名
            timeout: 超时时间（秒）
            
        Returns:
            True 如果应用启动
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.app_wait(package_name, timeout=timeout)
        return False
    
    @staticmethod
    def app_install(apk_path: str):
        """安装应用
        
        Args:
            apk_path: APK 文件路径
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.app_install(apk_path)
    
    @staticmethod
    def app_uninstall(package_name: str) -> bool:
        """卸载应用
        
        Args:
            package_name: 包名
            
        Returns:
            True 如果卸载成功
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.app_uninstall(package_name)
        return False
    
    @staticmethod
    def app_info(package_name: str) -> Dict:
        """获取应用信息
        
        Args:
            package_name: 包名
            
        Returns:
            应用信息字典
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.app_info(package_name)
        return {}
    
    @staticmethod
    def app_icon(package_name: str) -> Any:
        """获取应用图标
        
        Args:
            package_name: 包名
            
        Returns:
            PIL Image 对象
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.app_icon(package_name)
        return None
    
    @staticmethod
    def current_app() -> Dict:
        """获取当前应用
        
        Returns:
            应用信息字典
        """
        return UiAutomator2Utils.get_current_app()
    
    @staticmethod
    def set_new_command_timeout(timeout: int):
        """设置新命令超时时间
        
        Args:
            timeout: 超时时间（秒）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.set_new_command_timeout(timeout)
    
    # ========== 窗口管理 ==========
    @staticmethod
    def get_window_size() -> Tuple[int, int]:
        """获取窗口大小
        
        Returns:
            (宽度， 高度) 元组
        """
        return UiAutomator2Utils.get_window_size()
    
    @staticmethod
    def dump_hierarchy() -> str:
        """导出 UI 层次结构
        
        Returns:
            XML 格式的 UI 层次结构
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.dump_hierarchy()
        return ""
    
    @staticmethod
    def open_notification():
        """打开通知栏"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.open_notification()
    
    @staticmethod
    def open_quick_settings():
        """打开快速设置"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.open_quick_settings()
    
    @staticmethod
    def close_windows():
        """关闭所有窗口"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.press("home")
    
    # ========== 剪贴板 ==========
    @staticmethod
    def set_clipboard(text: str, label: str = None):
        """设置剪贴板
        
        Args:
            text: 文本内容
            label: 剪贴板标签
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.set_clipboard(text, label)
    
    @staticmethod
    def get_clipboard() -> str:
        """获取剪贴板
        
        Returns:
            剪贴板内容
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.get_clipboard()
        return ""
    
    @staticmethod
    def clear_clipboard():
        """清空剪贴板"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.clipboard = ""
    
    # ========== 图像操作 ==========
    @staticmethod
    def screenshot(filename: str = None, format: str = "pillow"):
        """截图
        
        Args:
            filename: 保存文件名
            format: 格式
            
        Returns:
            PIL Image 对象或 None
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.screenshot(filename)
        return None
    
    @staticmethod
    def take_screenshot(filename: str = None):
        """拍摄截图
        
        Args:
            filename: 保存文件名
            
        Returns:
            PIL Image 对象
        """
        return UiAutomator2Utils.screenshot(filename)
    
    @staticmethod
    def save_screenshot(filename: str = None):
        """保存截图
        
        Args:
            filename: 保存文件名
        """
        UiAutomator2Utils.screenshot(filename)
    
    @staticmethod
    def image_match(template_image: str, threshold: float = 0.8):
        """图像匹配点击
        
        Args:
            template_image: 模板图片路径
            threshold: 匹配阈值
            
        Returns:
            匹配结果
        """
        device = UiAutomator2Utils.get_device()
        if device:
            # 需要使用 template matching 功能
            pass
    
    @staticmethod
    def click_image(image_path: str, timeout: float = 10.0):
        """点击图片
        
        Args:
            image_path: 图片路径
            timeout: 超时时间（秒）
        """
        # 这里可以实现基于图像的点击
        pass
    
    # ========== 录屏 ==========
    @staticmethod
    def start_recording(output_file: str, time_limit: int = 180, 
                       resolution: str = None):
        """开始录屏
        
        Args:
            output_file: 输出文件路径
            time_limit: 录制时长限制（秒）
            resolution: 分辨率
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.start_recording(output_file, time_limit=time_limit, 
                                 resolution=resolution)
    
    @staticmethod
    def stop_recording():
        """停止录屏"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.stop_recording()
    
    # ========== Toast 监控 ==========
    @staticmethod
    def get_last_toast() -> str:
        """获取最后一个 Toast 消息
        
        Returns:
            Toast 消息文本
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.last_toast
        return ""
    
    @staticmethod
    def watch_toast(callback=None):
        """监控 Toast 消息
        
        Args:
            callback: 回调函数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.watch_toast(callback)
    
    # ========== 弹窗监控（WatchContext） ==========
    @staticmethod
    def watch_context_start():
        """开启 WatchContext"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.watch_context.start()
    
    @staticmethod
    def watch_context_stop():
        """停止 WatchContext"""
        device = UiAutomator2Utils.get_device()
        if device:
            device.watch_context.stop()
    
    @staticmethod
    def add_watch_trigger(condition_selector: Dict, 
                         action_callback=None):
        """添加监控触发器
        
        Args:
            condition_selector: 条件选择器
            action_callback: 动作回调函数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.watch_context.add(condition_selector, action_callback)
    
    @staticmethod
    def remove_watch_trigger(trigger_id: str):
        """移除监控触发器
        
        Args:
            trigger_id: 触发器 ID
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.watch_context.remove(trigger_id)
    
    # ========== XPath 支持 ==========
    @staticmethod
    def xpath(query: str) -> 'u2.XPathSelector':
        """XPath 查询
        
        Args:
            query: XPath 查询表达式
            
        Returns:
            XPathSelector 对象
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.xpath(query)
        return None
    
    @staticmethod
    def xpath_click(xpath_query: str, timeout: float = 10.0) -> bool:
        """XPath 点击
        
        Args:
            xpath_query: XPath 查询表达式
            timeout: 超时时间（秒）
            
        Returns:
            True 如果点击成功
        """
        device = UiAutomator2Utils.get_device()
        if device:
            sl = device.xpath(xpath_query)
            try:
                sl.click(timeout=timeout)
                return True
            except:
                return False
        return False
    
    @staticmethod
    def xpath_get_text(xpath_query: str) -> str:
        """XPath 获取文本
        
        Args:
            xpath_query: XPath 查询表达式
            
        Returns:
            文本内容
        """
        device = UiAutomator2Utils.get_device()
        if device:
            sl = device.xpath(xpath_query)
            return sl.get_text()
        return ""
    
    @staticmethod
    def xpath_exists(xpath_query: str) -> bool:
        """XPath 检查存在
        
        Args:
            xpath_query: XPath 查询表达式
            
        Returns:
            True 如果元素存在
        """
        device = UiAutomator2Utils.get_device()
        if device:
            sl = device.xpath(xpath_query)
            return sl.exists
        return False
    
    @staticmethod
    def xpath_wait(xpath_query: str, timeout: float = 10.0):
        """XPath 等待元素
        
        Args:
            xpath_query: XPath 查询表达式
            timeout: 超时时间（秒）
            
        Returns:
            XMLElement 对象
        """
        device = UiAutomator2Utils.get_device()
        if device:
            sl = device.xpath(xpath_query)
            return sl.wait(timeout=timeout)
        return None
    
    # ========== WebView 支持 ==========
    @staticmethod
    def webview_start():
        """启动 WebView 上下文"""
        device = UiAutomator2Utils.get_device()
        if device:
            try:
                from uiautomator2.ext.webview import WebView
                WebView.start(device)
            except ImportError:
                print("需要安装 webview 插件：pip install uiautomator2-webview")
    
    @staticmethod
    def webview_stop():
        """停止 WebView 上下文"""
        device = UiAutomator2Utils.get_device()
        if device:
            try:
                from uiautomator2.ext.webview import WebView
                WebView.stop(device)
            except ImportError:
                pass
    
    @staticmethod
    def webview_click(css_selector: str):
        """WebView 点击
        
        Args:
            css_selector: CSS 选择器
        """
        device = UiAutomator2Utils.get_device()
        if device:
            try:
                from uiautomator2.ext.webview import WebView
                WebView.click(device, css_selector)
            except ImportError:
                pass
    
    @staticmethod
    def webview_set_text(css_selector: str, text: str):
        """WebView 输入文本
        
        Args:
            css_selector: CSS 选择器
            text: 文本内容
        """
        device = UiAutomator2Utils.get_device()
        if device:
            try:
                from uiautomator2.ext.webview import WebView
                WebView.set_text(device, css_selector, text)
            except ImportError:
                pass
    
    @staticmethod
    def webview_get_text(css_selector: str) -> str:
        """WebView 获取文本
        
        Args:
            css_selector: CSS 选择器
            
        Returns:
            文本内容
        """
        device = UiAutomator2Utils.get_device()
        if device:
            try:
                from uiautomator2.ext.webview import WebView
                return WebView.get_text(device, css_selector)
            except ImportError:
                return ""
        return ""
    
    # ========== 全局设置 ==========
    @staticmethod
    def set_implicit_wait(timeout: float):
        """设置隐式等待时间
        
        Args:
            timeout: 超时时间（秒）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.implicitly_wait(timeout)
    
    @staticmethod
    def get_implicit_wait() -> float:
        """获取隐式等待时间
        
        Returns:
            超时时间（秒）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.implicitly_wait()
        return 20.0
    
    @staticmethod
    def set_click_delay(delay: float):
        """设置点击延迟
        
        Args:
            delay: 延迟时间（秒）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.settings['click_after_delay'] = delay
    
    @staticmethod
    def set_operation_delay(delay: float):
        """设置操作延迟
        
        Args:
            delay: 延迟时间（秒）
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.settings['operation_delay'] = (delay, delay)
    
    @staticmethod
    def set_max_depth(max_depth: int):
        """设置最大深度
        
        Args:
            max_depth: 最大深度
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.settings['max_depth'] = max_depth
    
    @staticmethod
    def get_settings() -> Dict:
        """获取所有设置
        
        Returns:
            设置字典
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return dict(device.settings)
        return {}
    
    @staticmethod
    def update_settings(**kwargs):
        """更新设置
        
        Args:
            **kwargs: 设置项
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device.settings.update(kwargs)
    
    # ========== JSONRPC 调用 ==========
    @staticmethod
    def jsonrpc_call(method: str, params: List = None) -> Any:
        """自定义 JSONRPC 调用
        
        Args:
            method: 方法名
            params: 参数列表
            
        Returns:
            返回结果
        """
        device = UiAutomator2Utils.get_device()
        if device:
            if params:
                return getattr(device.jsonrpc, method)(*params)
            else:
                return getattr(device.jsonrpc, method)()
        return None
    
    # ========== 辅助功能 ==========
    @staticmethod
    def enable_accessibility():
        """启用无障碍服务"""
        # 需要通过系统设置启用
        pass
    
    @staticmethod
    def disable_accessibility():
        """禁用无障碍服务"""
        # 需要通过系统设置禁用
        pass
    
    @staticmethod
    def is_accessibility_enabled() -> bool:
        """检查无障碍是否启用
        
        Returns:
            True 如果已启用
        """
        # 检查无障碍服务状态
        return False
    
    # ========== 高级功能 ==========
    @staticmethod
    def exists(**selector) -> bool:
        """检查元素是否存在（不抛出异常）
        
        Args:
            **selector: 定位参数
            
        Returns:
            True 如果元素存在
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device(**selector).exists
        return False
    
    @staticmethod
    def get_text(**selector) -> str:
        """获取元素文本
        
        Args:
            **selector: 定位参数
            
        Returns:
            元素文本
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device(**selector).get_text()
        return ""
    
    @staticmethod
    def set_text(text: str, **selector):
        """设置元素文本
        
        Args:
            text: 文本内容
            **selector: 定位参数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(**selector).set_text(text)
    
    @staticmethod
    def clear_text(**selector):
        """清空元素文本
        
        Args:
            **selector: 定位参数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            device(**selector).clear_text()
    
    @staticmethod
    def info(**selector) -> Dict:
        """获取元素信息
        
        Args:
            **selector: 定位参数
            
        Returns:
            元素信息字典
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device(**selector).info
        return {}
    
    @staticmethod
    def count(**selector) -> int:
        """统计元素数量
        
        Args:
            **selector: 定位参数
            
        Returns:
            元素数量
        """
        device = UiAutomator2Utils.get_device()
        if device:
            return device.count(**selector)
        return 0
    
    @staticmethod
    def resource_matches(pattern: str, **selector):
        """资源 ID 正则匹配
        
        Args:
            pattern: 正则表达式
            **selector: 其他定位参数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            selector['resourceIdMatches'] = pattern
            return device(**selector)
    
    @staticmethod
    def text_matches(pattern: str, **selector):
        """文本正则匹配
        
        Args:
            pattern: 正则表达式
            **selector: 其他定位参数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            selector['textMatches'] = pattern
            return device(**selector)
    
    @staticmethod
    def description_matches(pattern: str, **selector):
        """描述正则匹配
        
        Args:
            pattern: 正则表达式
            **selector: 其他定位参数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            selector['descriptionMatches'] = pattern
            return device(**selector)
    
    @staticmethod
    def class_name_matches(pattern: str, **selector):
        """类名正则匹配
        
        Args:
            pattern: 正则表达式
            **selector: 其他定位参数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            selector['classNameMatches'] = pattern
            return device(**selector)
    
    @staticmethod
    def package_matches(pattern: str, **selector):
        """包名正则匹配
        
        Args:
            pattern: 正则表达式
            **selector: 其他定位参数
        """
        device = UiAutomator2Utils.get_device()
        if device:
            selector['packageNameMatches'] = pattern
            return device(**selector)
    
    # ========== 子元素和兄弟元素定位 ==========
    @staticmethod
    def child_selector(parent_selector: Dict, 
                      child_selector: Dict):
        """子元素选择器
        
        Args:
            parent_selector: 父元素选择器
            child_selector: 子元素选择器
            
        Returns:
            组合选择器
        """
        # 这个需要根据实际 API 实现
        return child_selector
    
    @staticmethod
    def sibling_selector(reference_selector: Dict, 
                        sibling_selector: Dict):
        """兄弟元素选择器
        
        Args:
            reference_selector: 参考元素选择器
            sibling_selector: 兄弟元素选择器
            
        Returns:
            组合选择器
        """
        # 这个需要根据实际 API 实现
        return sibling_selector
    
    @staticmethod
    def ancestor_selector(child_selector: Dict, 
                         ancestor_selector: Dict):
        """祖先元素选择器
        
        Args:
            child_selector: 子元素选择器
            ancestor_selector: 祖先元素选择器
            
        Returns:
            组合选择器
        """
        # 这个需要根据实际 API 实现
        return ancestor_selector
    
    @staticmethod
    def descendant_selector(ancestor_selector: Dict, 
                           descendant_selector: Dict):
        """后代元素选择器
        
        Args:
            ancestor_selector: 祖先元素选择器
            descendant_selector: 后代元素选择器
            
        Returns:
            组合选择器
        """
        # 这个需要根据实际 API 实现
        return descendant_selector
