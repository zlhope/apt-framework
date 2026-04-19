# -*- coding: utf-8 -*-
"""
京东应用启动完成时间测试
测量从点击到应用UI第一帧渲染完成的完整耗时
"""

import pytest
import allure
import time
import os
import sys
import json

# 添加项目根目录到Python路径
current_file = os.path.abspath(__file__)
testcases_dir = os.path.dirname(current_file)
project_root = os.path.dirname(testcases_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils import DeviceUtils, ConfigUtils, LoggerUtils
from aw.performance import TraceCollector, StartupCompleteTimeAnalyzer, BaselineManager

# 加载配置文件
config_path = os.path.join(project_root, "config", "user_config.xml")
user_config = ConfigUtils.load_xml_config(config_path)
case_config_path = os.path.join(project_root, "testcases", "test_jingdong_startup_complete.json")
case_config = ConfigUtils.load_json_config(case_config_path)


@allure.feature("京东应用性能测试")
@allure.story("启动完成时间")
class TestJingdongStartupComplete:
    """京东APP启动完成时间测试"""
    
    @allure.step("初始化测试环境")
    def setup_method(self, method):
        """测试方法前执行"""
        # 连接设备
        self.device_id = user_config['configuration']['device']['id']
        self.device = DeviceUtils.connect_device(self.device_id)
        
        # 初始化性能工具
        self.perfetto_utils = TraceCollector(device_id=self.device_id)
        self.analyzer = StartupCompleteTimeAnalyzer(self.perfetto_utils)
        self.baseline_manager = BaselineManager()
        
    @allure.step("清理测试环境")
    def teardown_method(self, method):
        """测试方法后执行 - 只返回桌面，不停止应用"""
        from aw import AppVerifier
        AppVerifier.return_to_home(self.device, sleep_time=1)
    
    @allure.title("冷启动完成时间测试")
    @allure.description("测试京东APP冷启动的完整时间（从点击到UI第一帧）")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cold_startup_complete(self):
        """测试冷启动完成时间"""
        
        with allure.step("步骤1: 准备冷启动环境"):
            package = "com.jingdong.app.mall"
            activity = ".main.MainActivity"
            
            # 强制停止应用（不清除数据）
            self.device.app_stop(package)
            time.sleep(1)
            LoggerUtils.log_info("应用已停止，准备冷启动")
        
        with allure.step("步骤2: 执行冷启动并采集数据"):
            test_name = "test_cold_startup_complete"
            
            # 测量冷启动时间
            result = self.analyzer.measure_cold_start(
                package_name=package,
                activity=activity,
                test_name=test_name
            )
            
            if 'error' in result:
                LoggerUtils.log_warning(f"冷启动测试失败: {result.get('error')}")
                pytest.fail(f"冷启动测试失败: {result.get('error')}")
            
            LoggerUtils.log_info(f"冷启动结果: {result}")
            print(f"[OK] 冷启动完成时间: {result.get('start_complete_time', 0):.2f}ms")
            print(f"[OK] 启动类型: {result.get('startup_type', 'unknown')}")
        
        with allure.step("步骤3: 验证启动类型和性能指标"):
            startup_type = result.get('startup_type', 'unknown')
            complete_time = result.get('start_complete_time', 0)
            key_functions = result.get('key_functions', {})
            
            # 记录详细数据
            allure.attach(
                json.dumps(result, indent=2, ensure_ascii=False),
                name="冷启动完成时间详情",
                attachment_type=allure.attachment_type.JSON
            )
            
            # 验证启动类型应为 cold
            assert startup_type == "cold", f"期望冷启动，实际为: {startup_type}"
            
            # 验证关键函数
            has_bind = key_functions.get('bindApplication', False)
            assert has_bind, "冷启动应包含 bindApplication 事件"
            
            # 基线检查
            baseline_check = result.get('baseline_check', {})
            allure.attach(
                json.dumps(baseline_check, indent=2, ensure_ascii=False),
                name="基线检查结果",
                attachment_type=allure.attachment_type.JSON
            )
            
            # 断言：冷启动时间应小于3000ms
            assert complete_time < 3000, f"冷启动时间过长: {complete_time:.2f}ms"
            assert complete_time > 0, "启动完成时间为0，测试异常"
            
            print(f"[OK] 冷启动测试通过，完成时间: {complete_time:.2f}ms")
    
    @allure.title("热启动完成时间测试")
    @allure.description("测试京东APP热启动的完整时间（应用已在后台）")
    @allure.severity(allure.severity_level.NORMAL)
    def test_warm_startup_complete(self):
        """测试热启动完成时间"""
        
        with allure.step("步骤1: 准备热启动环境"):
            package = "com.jingdong.app.mall"
            activity = ".main.MainActivity"
            
            # 先启动应用
            self.device.app_start(package, activity=activity, wait=True)
            time.sleep(3)
            
            # 按Home键将应用置于后台
            self.device.press("home")
            time.sleep(2)
            LoggerUtils.log_info("应用已置于后台，准备热启动")
        
        with allure.step("步骤2: 执行热启动并采集数据"):
            test_name = "test_warm_startup_complete"
            
            # 测量热启动时间
            result = self.analyzer.measure_warm_start(
                package_name=package,
                activity=activity,
                test_name=test_name
            )
            
            if 'error' in result:
                LoggerUtils.log_warning(f"热启动测试失败: {result.get('error')}")
                pytest.fail(f"热启动测试失败: {result.get('error')}")
            
            LoggerUtils.log_info(f"热启动结果: {result}")
            print(f"[OK] 热启动完成时间: {result.get('start_complete_time', 0):.2f}ms")
            print(f"[OK] 启动类型: {result.get('startup_type', 'unknown')}")
        
        with allure.step("步骤3: 验证启动类型和性能指标"):
            startup_type = result.get('startup_type', 'unknown')
            complete_time = result.get('start_complete_time', 0)
            
            # 记录详细数据
            allure.attach(
                json.dumps(result, indent=2, ensure_ascii=False),
                name="热启动完成时间详情",
                attachment_type=allure.attachment_type.JSON
            )
            
            # 验证启动类型应为 warm 或 hot
            assert startup_type in ["warm", "hot"], f"期望温/热启动，实际为: {startup_type}"
            
            # 基线检查
            baseline_check = result.get('baseline_check', {})
            allure.attach(
                json.dumps(baseline_check, indent=2, ensure_ascii=False),
                name="基线检查结果",
                attachment_type=allure.attachment_type.JSON
            )
            
            # 断言：热启动时间应小于1500ms
            assert complete_time < 1500, f"热启动时间过长: {complete_time:.2f}ms"
            assert complete_time > 0, "启动完成时间为0，测试异常"
            
            print(f"[OK] 热启动测试通过，完成时间: {complete_time:.2f}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--alluredir=./allure-results"])
