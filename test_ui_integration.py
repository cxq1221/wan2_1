#!/usr/bin/env python3
"""
测试脚本：验证t2v_1.3B_singleGPU.py的UI集成
"""

import sys
import os

# 添加gradio目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gradio'))

def test_import():
    """测试模块导入"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("t2v_module", "gradio/t2v_1.3B_singleGPU.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ 模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
        return False

def test_interface_creation():
    """测试界面创建"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("t2v_module", "gradio/t2v_1.3B_singleGPU.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        demo = module.gradio_interface()
        print("✅ 界面创建成功")
        return True
    except Exception as e:
        print(f"❌ 界面创建失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试UI集成...")
    print("=" * 50)
    
    # 测试1：模块导入
    if not test_import():
        return False
    
    # 测试2：界面创建
    if not test_interface_creation():
        return False
    
    print("=" * 50)
    print("🎉 所有测试通过！UI集成成功")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
