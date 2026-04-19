# conftest.py
import pytest
import os
import sys
import xml.etree.ElementTree as ET

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.Utils import ConfigUtils

def pytest_collection_modifyitems(config, items):
    """
    修改测试项收集过程，如果没有指定测试用例，则从配置文件加载
    """
    # 检查是否通过命令行指定了测试用例
    file_or_dir = config.getoption("file_or_dir", [])
    
    # 如果没有指定测试用例，且没有通过标记(-m)选择，则从配置文件加载
    markexpr = config.getoption("-m", None)
    
    if not file_or_dir and not markexpr:
        # 尝试从配置文件加载测试套件
        config_path = "config/user_config.xml"
        if os.path.exists(config_path):
            try:
                config_root = ConfigUtils.load_xml_config(config_path)
                test_suite = ConfigUtils.get_test_suite_from_config(config_root)
                
                if test_suite:
                    print(f"从配置文件加载了 {len(test_suite)} 个测试用例:")
                    for i, case in enumerate(test_suite, 1):
                        print(f"  {i}. {case}")
                    
                    # 根据test_suite过滤测试项
                    selected_items = []
                    for item in items:
                        for test_case in test_suite:
                            # 精确匹配或前缀匹配
                            if item.nodeid == test_case or item.nodeid.startswith(test_case + "::"):
                                selected_items.append(item)
                                break
                    
                    # 更新items列表
                    items[:] = selected_items
                    print(f"最终选择 {len(items)} 个测试项执行")
                    
            except Exception as e:
                print(f"从配置文件读取测试套件时出错: {e}")

def pytest_configure(config):
    """pytest配置时添加allure报告目录"""
    # 添加allure结果目录选项
    if not config.getoption("--alluredir", None):
        config.option.allure_report_dir = "./allure-results"

def pytest_unconfigure(config):
    """pytest结束时的清理工作"""
    # Allure会自动处理报告生成，这里可以添加其他清理工作
    print("\n测试执行完成，Allure报告已生成到 ./allure-results/ 目录")
    print("使用以下命令查看报告:")
    print("  allure serve ./allure-results")
    print("或生成静态报告:")
    print("  allure generate ./allure-results -o ./allure-report --clean")