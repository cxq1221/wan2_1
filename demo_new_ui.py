#!/usr/bin/env python3
"""
演示脚本：展示新的文生视频UI界面
"""

import gradio as gr

def create_demo_interface():
    """创建演示界面"""
    
    # 自定义CSS样式
    custom_css = """
    <style>
    /* Gradio样式修复 - 解决 .gap.svelte-vt1mxs 等内部样式问题 */
    .gap.svelte-vt1mxs,
    .gap.svelte-*,
    .gap {
        gap: 0 !important;
    }
    
    .gr-form,
    .gr-form > * {
        gap: 0 !important;
    }
    
    .gr-form-row,
    .gr-form-column,
    .gr-form-group {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .gr-box,
    .gr-block,
    .gr-block-label {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .accordion {
        gap: 0 !important;
    }
    
    .accordion > * {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    *[class*="gap"] {
        gap: 0 !important;
    }
    
    [class*="svelte-"] {
        gap: 0 !important;
    }

    .content-wrapper {
        background: white;
        border-radius: 20px;
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    .header-section {
        border-bottom: 2px solid #e1e8ff;
        padding: 40px 30px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .header-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(74, 144, 226, 0.05) 0%, rgba(53, 122, 189, 0.03) 100%);
        pointer-events: none;
    }
    .header-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 12px;
        color: #2c3e50;
        position: relative;
        z-index: 1;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .header-subtitle {
        font-size: 18px;
        color: #5a6b7c;
        font-weight: 400;
        position: relative;
        z-index: 1;
        letter-spacing: 0.2px;
        opacity: 0.85;
    }
    .main-content {
        display: flex;
        min-height: 600px;
    }
    .left-panel {
        width: 450px;
        background: linear-gradient(180deg, #f8f9ff 0%, #e8f2ff 100%);
        padding: 30px;
        border-right: 2px solid #e1e8ff;
        overflow-y: auto;
    }
    .right-panel {
        flex: 1;
        background: white;
        padding: 30px;
        display: flex;
        flex-direction: column;
    }
    .section-title {
        color: #4a90e2;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* 覆盖Gradio内部的gap样式 */
    .gap.svelte-vt1mxs,
    .gap {
        gap: 0 !important;
    }
    
    /* 覆盖Gradio的Row和Column间距 */
    .gr-form > .gr-form-row,
    .gr-form > .gr-form-column,
    .gr-form > .gr-form-group {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 覆盖Gradio的默认间距 */
    .gr-form {
        gap: 0 !important;
    }
    
    /* 确保我们的自定义间距生效 */
    .examples-grid {
        gap: 12px !important;
    }
    
    .setting-row {
        gap: 0 !important;
    }
    .examples-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 25px;
    }
    .example-item {
        background: white;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        border: 2px solid #e1e8ff;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .example-item:hover {
        border-color: #4a90e2;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(74, 144, 226, 0.2);
    }
    .create-btn {
        background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
        color: white;
        border: none;
        padding: 18px 40px;
        border-radius: 25px;
        font-size: 18px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(74, 144, 226, 0.3);
        width: 100%;
        margin-top: 20px;
    }
    .create-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(74, 144, 226, 0.4);
    }
    .video-section {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
        border-radius: 20px;
        padding: 40px;
        border: 2px dashed #e1e8ff;
        min-height: 400px;
    }
    .video-placeholder {
        text-align: center;
        color: #7a9bb8;
    }
    .video-placeholder i {
        font-size: 80px;
        color: #b8c5d6;
        margin-bottom: 20px;
        display: block;
    }
    .video-placeholder h3 {
        color: #4a90e2;
        font-size: 24px;
        margin-bottom: 15px;
        font-weight: 600;
    }
    .video-placeholder p {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    </style>
    """
    
    def simulate_generation(prompt, progress=gr.Progress()):
        """模拟视频生成过程"""
        if not prompt.strip():
            return "请先输入提示词！", "无任务"
        
        # 模拟进度更新
        progress(0.1, desc="初始化模型...")
        progress(0.3, desc="分析提示词...")
        progress(0.5, desc="生成视频帧...")
        progress(0.7, desc="优化视频质量...")
        progress(0.9, desc="保存视频文件...")
        progress(1.0, desc="生成完成！")
        
        return f"基于提示词 '{prompt}' 的视频生成完成！", "生成完成"
    
    with gr.Blocks(css=custom_css, title="文生视频 - 演示界面") as demo:
        with gr.Column(elem_classes="main-container"):
            with gr.Column(elem_classes="content-wrapper"):
                # 头部区域
                with gr.Column(elem_classes="header-section"):
                    gr.Markdown("""
                    <div class="header-title">🎬 文生视频</div>
                    <div class="header-subtitle">AI智能视频生成平台</div>
                    """)
                
                # 主要内容区域
                with gr.Row(elem_classes="main-content"):
                    # 左侧面板
                    with gr.Column(elem_classes="left-panel"):
                        # 提示词输入
                        with gr.Column():
                            gr.Markdown('<div class="section-title">📝 输入提示词</div>')
                            prompt_input = gr.Textbox(
                                label="",
                                placeholder="请描述您想要生成的视频内容，例如：一只可爱的小猫在花园里玩耍，阳光明媚，画面温馨...",
                                lines=4,
                                container=False
                            )
                        
                        # 参考样例
                        with gr.Column():
                            gr.Markdown('<div class="section-title">💡 参考样例</div>')
                            with gr.Row(elem_classes="examples-grid"):
                                with gr.Column(elem_classes="example-item"):
                                    gr.Markdown('<div style="background: linear-gradient(45deg, #e1e8ff, #f0f5ff); height: 60px; border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">🌿</div>')
                                    gr.Markdown('<h4 style="color: #4a90e2; font-size: 13px; font-weight: 600; margin-bottom: 4px;">自然风景</h4>')
                                    gr.Markdown('<p style="color: #7a9bb8; font-size: 11px; line-height: 1.3;">美丽的大自然</p>')
                                
                                with gr.Column(elem_classes="example-item"):
                                    gr.Markdown('<div style="background: linear-gradient(45deg, #e1e8ff, #f0f5ff); height: 60px; border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">🌃</div>')
                                    gr.Markdown('<h4 style="color: #4a90e2; font-size: 13px; font-weight: 600; margin-bottom: 4px;">城市夜景</h4>')
                                    gr.Markdown('<p style="color: #7a9bb8; font-size: 11px; line-height: 1.3;">繁华都市夜色</p>')
                                
                                with gr.Column(elem_classes="example-item"):
                                    gr.Markdown('<div style="background: linear-gradient(45deg, #e1e8ff, #f0f5ff); height: 60px; border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">🐰</div>')
                                    gr.Markdown('<h4 style="color: #4a90e2; font-size: 13px; font-weight: 600; margin-bottom: 4px;">动物世界</h4>')
                                    gr.Markdown('<p style="color: #7a9bb8; font-size: 11px; line-height: 1.3;">可爱的小动物</p>')
                        
                        # 生成设置
                        with gr.Column():
                            gr.Markdown('<div class="section-title">⚙️ 生成设置</div>')
                            
                            with gr.Accordion("基础参数", open=True):
                                resolution = gr.Dropdown(
                                    label='视频分辨率',
                                    choices=['480*832', '832*480', '624*624', '704*544', '544*704'],
                                    value='480*832'
                                )
                                
                                with gr.Row():
                                    steps = gr.Slider(label="扩散步数", minimum=1, maximum=100, value=50, step=1)
                                    guide_scale = gr.Slider(label="引导比例", minimum=4.0, maximum=10.0, value=6.0, step=0.5)
                        
                        # 创作按钮
                        with gr.Column():
                            generate_btn = gr.Button("🎬 开始创作", elem_classes="create-btn")
                    
                    # 右侧面板
                    with gr.Column(elem_classes="right-panel"):
                        gr.Markdown('<div style="text-align: center; margin-bottom: 30px;"><h2 style="color: #4a90e2; font-size: 28px; font-weight: 600; margin-bottom: 10px;">🎥 视频生成</h2><p style="color: #7a9bb8; font-size: 16px;">输入提示词，AI将为您生成独特的视频内容</p></div>')
                        
                        # 视频生成区域
                        with gr.Column(elem_classes="video-section"):
                            with gr.Column(elem_classes="video-placeholder"):
                                gr.Markdown('<div style="font-size: 80px; color: #b8c5d6; margin-bottom: 20px;">🎬</div>')
                                gr.Markdown('<h3 style="color: #4a90e2; font-size: 24px; margin-bottom: 15px; font-weight: 600;">准备生成视频</h3>')
                                gr.Markdown('<p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px;">请在左侧输入提示词，然后点击"开始创作"按钮</p>')
                        
                        # 结果显示
                        result_text = gr.Textbox(label="生成结果", interactive=False)
                        status_text = gr.Textbox(label="状态", value="无任务", interactive=False)
                
                # 事件绑定
                generate_btn.click(
                    fn=simulate_generation,
                    inputs=[prompt_input],
                    outputs=[result_text, status_text]
                )
                
                # 添加JavaScript功能
                gr.HTML("""
                <script>
                // 样例点击功能
                document.addEventListener('DOMContentLoaded', function() {
                    const examples = [
                        "一只可爱的小猫在花园里玩耍，阳光明媚，画面温馨，背景是美丽的花朵和绿树",
                        "繁华的城市夜景，霓虹灯闪烁，车流如织，高楼大厦灯火通明，天空中有星星点缀",
                        "一只小兔子在森林里跳跃，周围是高大的树木和绿色的草地，阳光透过树叶洒下斑驳的光影"
                    ];
                    
                    const promptInput = document.querySelector('textarea[placeholder*="请描述您想要生成的视频内容"]');
                    if (promptInput) {
                        const exampleItems = document.querySelectorAll('.example-item');
                        exampleItems.forEach((item, index) => {
                            item.addEventListener('click', function() {
                                if (examples[index]) {
                                    promptInput.value = examples[index];
                                    promptInput.dispatchEvent(new Event('input', { bubbles: true }));
                                }
                            });
                        });
                    }
                });
                </script>
                """)
    
    return demo

if __name__ == "__main__":
    demo = create_demo_interface()
    demo.launch(server_name="0.0.0.0", share=False, server_port=7860)
