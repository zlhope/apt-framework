# -*- coding: utf-8 -*-
"""
通用工具类模块
提供时间、文件、数据、日志等通用工具方法
"""
import xml.etree.ElementTree as ET
import json
import time
import os
import logging
import random
import string
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
# 延迟导入 uiautomator2（避免 Python 3.14 兼容性问题）

class TimeUtils:
    """时间工具类"""
    
    @staticmethod
    def get_timestamp() -> int:
        """获取当前时间戳（毫秒）
        
        Returns:
            当前时间戳（毫秒）
        """
        return int(time.time() * 1000)
    
    @staticmethod
    def get_timestamp_seconds() -> int:
        """获取当前时间戳（秒）
        
        Returns:
            当前时间戳（秒）
        """
        return int(time.time())
    
    @staticmethod
    def sleep(seconds: float):
        """智能休眠
        
        Args:
            seconds: 休眠秒数
        """
        time.sleep(seconds)
    
    @staticmethod
    def get_formatted_time(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取格式化时间
        
        Args:
            format_str: 时间格式字符串
            
        Returns:
            格式化后的时间字符串
        """
        return datetime.now().strftime(format_str)
    
    @staticmethod
    def get_date() -> str:
        """获取当前日期
        
        Returns:
            日期字符串，格式：YYYY-MM-DD
        """
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def get_time() -> str:
        """获取当前时间
        
        Returns:
            时间字符串，格式：HH:MM:SS
        """
        return datetime.now().strftime("%H:%M:%S")
    
    @staticmethod
    def get_datetime() -> str:
        """获取当前日期时间
        
        Returns:
            日期时间字符串，格式：YYYY-MM-DD HH:MM:SS
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def parse_time(time_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """解析时间字符串
        
        Args:
            time_str: 时间字符串
            format_str: 时间格式
            
        Returns:
            datetime 对象
        """
        return datetime.strptime(time_str, format_str)
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """格式化 datetime 对象
        
        Args:
            dt: datetime 对象
            format_str: 时间格式
            
        Returns:
            格式化后的时间字符串
        """
        return dt.strftime(format_str)
    
    @staticmethod
    def get_time_diff(start_time: str, end_time: str, 
                     format_str: str = "%Y-%m-%d %H:%M:%S") -> float:
        """计算时间差（秒）
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            format_str: 时间格式
            
        Returns:
            时间差（秒）
        """
        start = datetime.strptime(start_time, format_str)
        end = datetime.strptime(end_time, format_str)
        diff = (end - start).total_seconds()
        return diff


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def create_directory(dir_path: str, exist_ok: bool = True):
        """创建目录
        
        Args:
            dir_path: 目录路径
            exist_ok: 如果目录已存在是否不报错
        """
        os.makedirs(dir_path, exist_ok=exist_ok)
    
    @staticmethod
    def delete_directory(dir_path: str, ignore_errors: bool = True):
        """删除目录
        
        Args:
            dir_path: 目录路径
            ignore_errors: 是否忽略错误
        """
        shutil.rmtree(dir_path, ignore_errors=ignore_errors)
    
    @staticmethod
    def copy_file(src: str, dst: str):
        """复制文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
        """
        shutil.copy2(src, dst)
    
    @staticmethod
    def move_file(src: str, dst: str):
        """移动文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
        """
        shutil.move(src, dst)
    
    @staticmethod
    def delete_file(file_path: str):
        """删除文件
        
        Args:
            file_path: 文件路径
        """
        if os.path.exists(file_path):
            os.remove(file_path)
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            True 如果文件存在
        """
        return os.path.exists(file_path)
    
    @staticmethod
    def dir_exists(dir_path: str) -> bool:
        """检查目录是否存在
        
        Args:
            dir_path: 目录路径
            
        Returns:
            True 如果目录存在
        """
        return os.path.isdir(dir_path)
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件大小（字节）
        """
        return os.path.getsize(file_path)
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """获取文件扩展名
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件扩展名（包含点）
        """
        return os.path.splitext(file_path)[1]
    
    @staticmethod
    def get_file_name(file_path: str, with_extension: bool = False) -> str:
        """获取文件名
        
        Args:
            file_path: 文件路径
            with_extension: 是否包含扩展名
            
        Returns:
            文件名
        """
        basename = os.path.basename(file_path)
        if with_extension:
            return basename
        else:
            return os.path.splitext(basename)[0]
    
    @staticmethod
    def get_parent_directory(file_path: str) -> str:
        """获取父目录
        
        Args:
            file_path: 文件路径
            
        Returns:
            父目录路径
        """
        return os.path.dirname(os.path.abspath(file_path))
    
    @staticmethod
    def list_files(directory: str, pattern: str = "*") -> List[str]:
        """列出目录下的文件
        
        Args:
            directory: 目录路径
            pattern: 匹配模式
            
        Returns:
            文件路径列表
        """
        import glob
        return glob.glob(os.path.join(directory, pattern))
    
    @staticmethod
    def list_directories(directory: str) -> List[str]:
        """列出目录下的子目录
        
        Args:
            directory: 目录路径
            
        Returns:
            子目录列表
        """
        return [d for d in os.listdir(directory) 
                if os.path.isdir(os.path.join(directory, d))]
    
    @staticmethod
    def read_file(file_path: str, encoding: str = "utf-8") -> str:
        """读取文件内容
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            
        Returns:
            文件内容
        """
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def read_lines(file_path: str, encoding: str = "utf-8") -> List[str]:
        """按行读取文件
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            
        Returns:
            文本行列表
        """
        with open(file_path, 'r', encoding=encoding) as f:
            return f.readlines()
    
    @staticmethod
    def write_file(file_path: str, content: str, 
                  encoding: str = "utf-8", append: bool = False):
        """写入文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 文件编码
            append: 是否追加模式
        """
        mode = 'a' if append else 'w'
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
    
    @staticmethod
    def write_lines(file_path: str, lines: List[str], 
                   encoding: str = "utf-8", append: bool = False):
        """按行写入文件
        
        Args:
            file_path: 文件路径
            lines: 文本行列表
            encoding: 文件编码
            append: 是否追加模式
        """
        mode = 'a' if append else 'w'
        with open(file_path, mode, encoding=encoding) as f:
            f.writelines(lines)
    
    @staticmethod
    def get_absolute_path(file_path: str) -> str:
        """获取绝对路径
        
        Args:
            file_path: 文件路径
            
        Returns:
            绝对路径
        """
        return os.path.abspath(file_path)
    
    @staticmethod
    def join_path(*paths) -> str:
        """拼接路径
        
        Args:
            *paths: 路径段
            
        Returns:
            拼接后的路径
        """
        return os.path.join(*paths)
    
    @staticmethod
    def normalize_path(file_path: str) -> str:
        """规范化路径
        
        Args:
            file_path: 文件路径
            
        Returns:
            规范化后的路径
        """
        return os.path.normpath(file_path)
    
    @staticmethod
    def make_temp_file(prefix: str = "tmp", suffix: str = "", 
                      directory: str = None) -> str:
        """创建临时文件
        
        Args:
            prefix: 文件名前缀
            suffix: 文件扩展名
            directory: 临时目录
            
        Returns:
            临时文件路径
        """
        import tempfile
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=directory)
        os.close(fd)
        return path


class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def parse_json(json_str: str) -> Dict:
        """解析 JSON 字符串
        
        Args:
            json_str: JSON 字符串
            
        Returns:
            解析后的字典
        """
        return json.loads(json_str)
    
    @staticmethod
    def to_json(data: Any, indent: int = 4, 
               ensure_ascii: bool = False) -> str:
        """转换为 JSON 字符串
        
        Args:
            data: 数据对象
            indent: 缩进空格数
            ensure_ascii: 是否转义非 ASCII 字符
            
        Returns:
            JSON 字符串
        """
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
    
    @staticmethod
    def load_json_file(file_path: str, encoding: str = "utf-8") -> Dict:
        """加载 JSON 文件
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            
        Returns:
            JSON 字典
        """
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    
    @staticmethod
    def save_json_file(file_path: str, data: Any, 
                      encoding: str = "utf-8", indent: int = 4):
        """保存 JSON 文件
        
        Args:
            file_path: 文件路径
            data: 数据对象
            encoding: 文件编码
            indent: 缩进空格数
        """
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def random_string(length: int = 8, 
                     characters: str = None) -> str:
        """生成随机字符串
        
        Args:
            length: 字符串长度
            characters: 字符集，默认字母和数字
            
        Returns:
            随机字符串
        """
        if characters is None:
            characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def random_number(min_val: int = 0, max_val: int = 100) -> int:
        """生成随机整数
        
        Args:
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            随机整数
        """
        return random.randint(min_val, max_val)
    
    @staticmethod
    def random_float(min_val: float = 0.0, 
                    max_val: float = 1.0) -> float:
        """生成随机浮点数
        
        Args:
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            随机浮点数
        """
        return random.uniform(min_val, max_val)
    
    @staticmethod
    def random_email(length: int = 8) -> str:
        """生成随机邮箱
        
        Args:
            length: 用户名长度
            
        Returns:
            随机邮箱地址
        """
        username = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        return f"{username}@{random.choice(domains)}"
    
    @staticmethod
    def random_phone() -> str:
        """生成随机手机号
        
        Returns:
            随机手机号码
        """
        prefixes = ['138', '139', '150', '151', '158', '159', '188', '187']
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choice(string.digits) for _ in range(8))
        return f"{prefix}{suffix}"
    
    @staticmethod
    def random_chinese(length: int = 1) -> str:
        """生成随机中文
        
        Args:
            length: 中文字符个数
            
        Returns:
            随机中文字符串
        """
        # 常用汉字 Unicode 范围：\u4e00-\u9fa5
        return ''.join(chr(random.randint(0x4e00, 0x9fa5)) for _ in range(length))
    
    @staticmethod
    def uuid() -> str:
        """生成 UUID
        
        Returns:
            UUID 字符串
        """
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def md5(text: str) -> str:
        """计算 MD5
        
        Args:
            text: 输入文本
            
        Returns:
            MD5 哈希值（32 位小写）
        """
        import hashlib
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def base64_encode(text: str) -> str:
        """Base64 编码
        
        Args:
            text: 原始文本
            
        Returns:
            Base64 编码后的字符串
        """
        import base64
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def base64_decode(encoded_str: str) -> str:
        """Base64 解码
        
        Args:
            encoded_str: Base64 编码的字符串
            
        Returns:
            解码后的原始文本
        """
        import base64
        return base64.b64decode(encoded_str.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def url_encode(text: str) -> str:
        """URL 编码
        
        Args:
            text: 原始文本
            
        Returns:
            URL 编码后的字符串
        """
        from urllib.parse import quote
        return quote(text)
    
    @staticmethod
    def url_decode(encoded_str: str) -> str:
        """URL 解码
        
        Args:
            encoded_str: URL 编码的字符串
            
        Returns:
            解码后的原始文本
        """
        from urllib.parse import unquote
        return unquote(encoded_str)
    
    @staticmethod
    def is_empty(value: Any) -> bool:
        """判断是否为空
        
        Args:
            value: 要判断的值
            
        Returns:
            True 如果为空
        """
        if value is None:
            return True
        if isinstance(value, (str, list, dict, tuple, set)):
            return len(value) == 0
        return False
    
    @staticmethod
    def is_not_empty(value: Any) -> bool:
        """判断是否不为空
        
        Args:
            value: 要判断的值
            
        Returns:
            True 如果不为空
        """
        return not DataUtils.is_empty(value)
    
    @staticmethod
    def trim(text: str) -> str:
        """去除首尾空格
        
        Args:
            text: 文本字符串
            
        Returns:
            处理后的文本
        """
        return text.strip()
    
    @staticmethod
    def camel_to_snake(camel_case: str) -> str:
        """驼峰转下划线
        
        Args:
            camel_case: 驼峰命名
            
        Returns:
            下划线命名
        """
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def snake_to_camel(snake_case: str) -> str:
        """下划线转驼峰
        
        Args:
            snake_case: 下划线命名
            
        Returns:
            驼峰命名
        """
        parts = snake_case.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])


class LoggerUtils:
    """日志工具类"""
    
    _loggers: Dict[str, logging.Logger] = {}
    
    @classmethod
    def setup_logger(cls, name: str = "default", 
                    level: int = logging.INFO,
                    log_file: str = None,
                    format_str: str = None,
                    console_output: bool = True) -> logging.Logger:
        """配置日志
        
        Args:
            name: 日志名称
            level: 日志级别
            log_file: 日志文件路径
            format_str: 日志格式
            console_output: 是否输出到控制台
            
        Returns:
            Logger 对象
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 设置日志格式
        if format_str is None:
            format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(format_str)
        
        # 添加控制台处理器
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def get_logger(cls, name: str = "default") -> logging.Logger:
        """获取日志记录器
        
        Args:
            name: 日志名称
            
        Returns:
            Logger 对象
        """
        if name not in cls._loggers:
            cls.setup_logger(name)
        return cls._loggers[name]
    
    @staticmethod
    def log_info(message: str, logger_name: str = "default"):
        """记录 INFO 日志
        
        Args:
            message: 日志消息
            logger_name: 日志名称
        """
        logger = LoggerUtils.get_logger(logger_name)
        logger.info(message)
    
    @staticmethod
    def log_error(message: str, logger_name: str = "default", 
                 exc_info: bool = True):
        """记录 ERROR 日志
        
        Args:
            message: 日志消息
            logger_name: 日志名称
            exc_info: 是否记录异常信息
        """
        logger = LoggerUtils.get_logger(logger_name)
        logger.error(message, exc_info=exc_info)
    
    @staticmethod
    def log_debug(message: str, logger_name: str = "default"):
        """记录 DEBUG 日志
        
        Args:
            message: 日志消息
            logger_name: 日志名称
        """
        logger = LoggerUtils.get_logger(logger_name)
        logger.debug(message)
    
    @staticmethod
    def log_warning(message: str, logger_name: str = "default"):
        """记录 WARNING 日志
        
        Args:
            message: 日志消息
            logger_name: 日志名称
        """
        logger = LoggerUtils.get_logger(logger_name)
        logger.warning(message)
    
    @staticmethod
    def log_critical(message: str, logger_name: str = "default"):
        """记录 CRITICAL 日志
        
        Args:
            message: 日志消息
            logger_name: 日志名称
        """
        logger = LoggerUtils.get_logger(logger_name)
        logger.critical(message)


class AssertUtils:
    """断言工具类（保留原有功能）"""
    
    @staticmethod
    def assert_equal(actual: Any, expected: Any, message: str = ""):
        """断言相等
        
        Args:
            actual: 实际值
            expected: 期望值
            message: 自定义错误消息
        """
        if actual != expected:
            raise AssertionError(message or f"期望值：{expected}, 实际值：{actual}")
    
    @staticmethod
    def assert_not_equal(actual: Any, expected: Any, message: str = ""):
        """断言不相等
        
        Args:
            actual: 实际值
            expected: 期望值
            message: 自定义错误消息
        """
        if actual == expected:
            raise AssertionError(message or f"期望值不等于：{expected}, 但实际值为：{actual}")
    
    @staticmethod
    def assert_true(condition: bool, message: str = ""):
        """断言为真
        
        Args:
            condition: 条件
            message: 自定义错误消息
        """
        if not condition:
            raise AssertionError(message or "断言条件为假")
    
    @staticmethod
    def assert_false(condition: bool, message: str = ""):
        """断言为假
        
        Args:
            condition: 条件
            message: 自定义错误消息
        """
        if condition:
            raise AssertionError(message or "断言条件为真")
    
    @staticmethod
    def assert_in(member: Any, container: Any, message: str = ""):
        """断言包含
        
        Args:
            member: 成员
            container: 容器
            message: 自定义错误消息
        """
        if member not in container:
            raise AssertionError(message or f"{member} 不在 {container} 中")
    
    @staticmethod
    def assert_not_in(member: Any, container: Any, message: str = ""):
        """断言不包含
        
        Args:
            member: 成员
            container: 容器
            message: 自定义错误消息
        """
        if member in container:
            raise AssertionError(message or f"{member} 在 {container} 中")
    
    @staticmethod
    def assert_is_none(value: Any, message: str = ""):
        """断言为 None
        
        Args:
            value: 要判断的值
            message: 自定义错误消息
        """
        if value is not None:
            raise AssertionError(message or f"{value} 不是 None")
    
    @staticmethod
    def assert_is_not_none(value: Any, message: str = ""):
        """断言不为 None
        
        Args:
            value: 要判断的值
            message: 自定义错误消息
        """
        if value is None:
            raise AssertionError(message or f"{value} 是 None")
    
    @staticmethod
    def assert_greater(a: Any, b: Any, message: str = ""):
        """断言大于
        
        Args:
            a: 值 a
            b: 值 b
            message: 自定义错误消息
        """
        if not (a > b):
            raise AssertionError(message or f"{a} 不大于 {b}")
    
    @staticmethod
    def assert_greater_or_equal(a: Any, b: Any, message: str = ""):
        """断言大于等于
        
        Args:
            a: 值 a
            b: 值 b
            message: 自定义错误消息
        """
        if not (a >= b):
            raise AssertionError(message or f"{a} 不大于等于 {b}")
    
    @staticmethod
    def assert_less(a: Any, b: Any, message: str = ""):
        """断言小于
        
        Args:
            a: 值 a
            b: 值 b
            message: 自定义错误消息
        """
        if not (a < b):
            raise AssertionError(message or f"{a} 不小于 {b}")
    
    @staticmethod
    def assert_less_or_equal(a: Any, b: Any, message: str = ""):
        """断言小于等于
        
        Args:
            a: 值 a
            b: 值 b
            message: 自定义错误消息
        """
        if not (a <= b):
            raise AssertionError(message or f"{a} 不小于等于 {b}")
    
    @staticmethod
    def assert_instance_of(obj: Any, cls: type, message: str = ""):
        """断言类型
        
        Args:
            obj: 对象
            cls: 类型
            message: 自定义错误消息
        """
        if not isinstance(obj, cls):
            raise AssertionError(message or f"{obj} 不是 {cls} 的实例")
    
    @staticmethod
    def assert_almost_equal(first: float, second: float, 
                           places: int = 7, message: str = ""):
        """断言近似相等
        
        Args:
            first: 第一个浮点数
            second: 第二个浮点数
            places: 小数位数
            message: 自定义错误消息
        """
        if round(abs(first - second), places) != 0:
            raise AssertionError(message or f"{first} 和 {second} 在小数点后{places}位不相等")


class DeviceUtils:
    """
    设备操作工具类（保留向后兼容）
    """
    
    @staticmethod
    def connect_device(device_id: str = None):
        """
        连接设备
        
        Args:
            device_id: 设备 ID
            
        Returns:
            uiautomator2 设备实例
        """
        # 延迟导入避免 Python 3.14 兼容性问题
        import uiautomator2 as u2
        try:
            if device_id:
                return u2.connect(device_id)
            else:
                return u2.connect()
        except Exception as e:
            raise ConnectionError(f"无法连接到设备 {device_id}: {str(e)}")
    
    @staticmethod
    def get_device_info(device):  # 参数类型改为普通对象
        """获取设备信息"""
        info = device.info
        return {
            "deviceName": info.get("deviceName", ""),
            "brand": info.get("brand", ""),
            "model": info.get("model", ""),
            "sdkVersion": info.get("sdkVersion", ""),
            "platformVersion": info.get("platformVersion", "")
        }
    
    @staticmethod
    def screenshot(device, filename: str = None):  # 参数类型改为普通对象
        """截图"""
        return device.screenshot(filename)
    
    @staticmethod
    def press_key(device, key: str):  # 参数类型改为普通对象
        """按下按键"""
        device.press(key)
    
    @staticmethod
    def wait_for_element(device, locator: Dict[str, Any], timeout: int = 10) -> bool:  # 参数类型改为普通对象
        """等待元素出现"""
        try:
            element = device(**locator)
            return element.wait(timeout=timeout)
        except Exception:
            return False

class ConfigUtils:
    """
    配置文件处理工具类（保留向后兼容）
    """
    
    @staticmethod
    def load_xml_config(config_path: str) -> Dict[str, Any]:
        """加载多层嵌套XML配置文件"""
        try:
            tree = ET.parse(config_path)
            root = tree.getroot()
            
            def parse_element(element):
                """递归解析XML元素"""
                result = {}
                
                # 处理元素属性
                if element.attrib:
                    result['@attributes'] = element.attrib
                
                # 处理子元素
                children = list(element)
                if children:
                    child_dict = {}
                    for child in children:
                        child_data = parse_element(child)
                        if child.tag in child_dict:
                            # 如果标签已存在，转换为列表
                            if not isinstance(child_dict[child.tag], list):
                                child_dict[child.tag] = [child_dict[child.tag]]
                            child_dict[child.tag].append(child_data)
                        else:
                            child_dict[child.tag] = child_data
                    result.update(child_dict)
                
                # 处理文本内容
                if element.text and element.text.strip():
                    if result:
                        result['#text'] = element.text.strip()
                    else:
                        return element.text.strip()
                
                return result
            
            return {root.tag: parse_element(root)}
            
        except Exception as e:
            raise ValueError(f"无法解析配置文件 {config_path}: {str(e)}")
    

    @staticmethod
    def load_json_config(config_path: str) -> Dict[str, Any]:
        """加载JSON配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"无法解析配置文件 {config_path}: {str(e)}")
        
    @staticmethod
    def get_test_suite_from_config(config_dict) -> List[str]:
        """
        从字典格式的配置中获取测试套件列表
        """
        if config_dict is not None:
            # 获取根标签名
            root_tag = list(config_dict.keys())[0] if config_dict.keys() else None
            
            if root_tag and root_tag in config_dict:
                # 检查 testsuite 是否存在
                if 'testsuite' in config_dict[root_tag]:
                    test_suite_data = config_dict[root_tag]['testsuite']
                    
                    # 如果是字符串，直接处理
                    if isinstance(test_suite_data, str):
                        return [case.strip() for case in test_suite_data.split(',') if case.strip()]
                    # 如果是字典且包含#text键
                    elif isinstance(test_suite_data, dict) and '#text' in test_suite_data:
                        return [case.strip() for case in test_suite_data['#text'].split(',') if case.strip()]
                    # 如果是字典但不包含#text键，检查是否有文本内容
                    elif isinstance(test_suite_data, dict):
                        # 尝试获取文本内容的不同方式
                        text_content = test_suite_data.get('#text', '')
                        
                        if not text_content and len(test_suite_data) == 1:
                            # 如果字典只有一个键值对，且值是字符串，可能是文本内容
                            for key, value in test_suite_data.items():
                                if isinstance(value, str) and key != '@attributes':
                                    text_content = value
                                    break
                        
                        if text_content:
                            return [case.strip() for case in text_content.split(',') if case.strip()]
        return []

class TestUtils:
    """
    测试工具类（保留向后兼容，使用 AssertUtils）
    """
    
    @staticmethod
    def assert_equal(actual: Any, expected: Any, message: str = ""):
        """断言相等（已迁移到 AssertUtils）"""
        AssertUtils.assert_equal(actual, expected, message)
    
    @staticmethod
    def assert_not_equal(actual: Any, expected: Any, message: str = ""):
        """断言不相等（已迁移到 AssertUtils）"""
        AssertUtils.assert_not_equal(actual, expected, message)
    
    @staticmethod
    def assert_true(condition: bool, message: str = ""):
        """断言为真（已迁移到 AssertUtils）"""
        AssertUtils.assert_true(condition, message)
    
    @staticmethod
    def assert_false(condition: bool, message: str = ""):
        """断言为假（已迁移到 AssertUtils）"""
        AssertUtils.assert_false(condition, message)
