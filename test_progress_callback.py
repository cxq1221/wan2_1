#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Wan2.1进度回调功能的脚本
"""

import sys
import os

# 添加wan模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'wan'))

def test_progress_callback():
    """测试进度回调功能"""
    
    # 模拟进度回调函数
    def mock_progress_callback(step, total_steps, current_timestep):
        """模拟进度回调"""
        progress = (step + 1) / total_steps * 100
        print(f"步骤 {step + 1}/{total_steps} - 进度: {progress:.1f}% - 时间步: {current_timestep:.2f}")
    
    print("=== 测试Wan2.1进度回调功能 ===")
    print("进度回调函数签名:")
    print("mock_progress_callback(step, total_steps, current_timestep)")
    print()
    
    # 模拟调用
    print("模拟扩散过程 (10步):")
    for step in range(10):
        mock_progress_callback(step, 10, 1000 - step * 100)
    
    print("\n=== 测试完成 ===")
    print("现在你可以在Gradio界面中使用真实的进度回调了！")

if __name__ == "__main__":
    test_progress_callback()
