# Copyright 2024-2025 The Alibaba Wan Team Authors. All rights reserved.
import argparse
import os
import os.path as osp
import sys
import warnings

import gradio as gr

warnings.filterwarnings('ignore')

# Model
sys.path.insert(
    0, os.path.sep.join(osp.realpath(__file__).split(os.path.sep)[:-2]))
import wan
from wan.configs import WAN_CONFIGS
# from wan.utils.prompt_extend import DashScopePromptExpander, QwenPromptExpander
from wan.utils.utils import cache_video

# Global Var
# prompt_expander = None
wan_t2v = None
args = None  # 全局变量，用于存储命令行参数


# Button Func
def prompt_enc(prompt, tar_lang):
    # 关闭prompt_extend功能，直接返回原prompt
    return prompt


def t2v_generation(txt2vid_prompt, resolution, sd_steps, guide_scale,
                   shift_scale, seed, n_prompt, offload_model_ui, progress=gr.Progress()):
    global wan_t2v, args  # 添加args全局变量访问
    # print(f"{txt2vid_prompt},{resolution},{sd_steps},{guide_scale},{shift_scale},{seed},{n_prompt}")

    try:
        W = int(resolution.split("*")[0])
        H = int(resolution.split("*")[1])
        
        # 优先级：命令行参数 > 界面基础参数
        actual_shift = float(args.sample_shift) if hasattr(args, 'sample_shift') else float(shift_scale)
        actual_guide_scale = float(args.sample_guide_scale) if hasattr(args, 'sample_guide_scale') else float(guide_scale)
        actual_offload = bool(args.offload_model) if hasattr(args, 'offload_model') else bool(offload_model_ui)
        
        # T5 CPU设置：使用命令行参数，默认为True（开启）
        actual_t5_cpu = args.t5_cpu
        
        print(f"生成参数: 分辨率={W}x{H}, 偏移={actual_shift}, 引导比例={actual_guide_scale}, 卸载={actual_offload}, T5_CPU={actual_t5_cpu}")
        print(f"命令行参数: sample_shift={getattr(args, 'sample_shift', 'N/A')}, sample_guide_scale={getattr(args, 'sample_guide_scale', 'N/A')}, offload_model={getattr(args, 'offload_model', 'N/A')}, t5_cpu={getattr(args, 't5_cpu', 'N/A')}")
        print(f"界面基础参数: guide_scale={guide_scale}, shift_scale={shift_scale}")
        print(f"界面高级参数: offload_model={offload_model_ui}")
        
        # 更新进度和状态
        progress(0.01, desc="初始化模型...")
        
        # 简化的进度回调函数
        def progress_callback(step, total_steps_count, current_timestep):
            """扩散步骤进度回调函数"""
            # 计算真实进度：1%初始化 + 89%扩散 + 10%保存
            progress_value = 0.01 + 0.89 * (step / total_steps_count)
            desc = f"扩散步骤 {step + 1}/{total_steps_count} (时间步: {current_timestep:.2f})"
            
            print(f"后台线程 - 进度: {progress_value:.2f} - {desc}")
            
            # 直接更新Gradio进度条
            try:
                progress(progress_value, desc)
            except Exception as e:
                print(f"进度更新错误: {e}")
        
        # 直接调用模型生成，不使用多线程
        print(f"开始生成视频...")
        video = wan_t2v.generate(
            txt2vid_prompt,
            size=(W, H),
            shift=actual_shift,
            sampling_steps=sd_steps,
            guide_scale=actual_guide_scale,
            n_prompt=n_prompt,
            seed=seed,
            offload_model=actual_offload,
            progress_callback=progress_callback)  # 使用简化的进度回调
        
        if video is None:
            raise Exception("视频生成失败")
        
        # 更新进度
        progress(0.9, desc="生成视频完成，正在保存...")
        
        # 保存视频
        cache_video(
            tensor=video[None],
            save_file="example.mp4",
            fps=16,
            nrow=1,
            normalize=True,
            value_range=(-1, 1))
        
        progress(1.0, desc="视频生成完成！")
        
        return "example.mp4"
        
    except Exception as e:
        print(f"生成视频时发生错误: {e}")
        raise gr.Error(f"视频生成失败: {str(e)}")


# Interface
def gradio_interface():
    # 自定义CSS样式
    custom_css = """
    <style>
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 20px;
    }
    .content-wrapper {
        background: white;
        border-radius: 20px;
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    .header-section {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
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
    .example-item img {
        width: 100%;
        height: 60px;
        object-fit: cover;
        border-radius: 6px;
        margin-bottom: 8px;
        background: linear-gradient(45deg, #e1e8ff, #f0f5ff);
    }
    .example-item h4 {
        color: #4a90e2;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .example-item p {
        color: #7a9bb8;
        font-size: 11px;
        line-height: 1.3;
    }
    .setting-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .setting-label {
        color: #5a6b7c;
        font-size: 14px;
        font-weight: 500;
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
    .progress-container {
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
    }
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e1e8ff;
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 15px;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4a90e2, #357abd);
        border-radius: 4px;
        transition: width 0.3s ease;
        width: 0%;
    }
    .progress-text {
        text-align: center;
        color: #4a90e2;
        font-size: 14px;
        font-weight: 500;
    }
    .accordion-custom {
        border: 2px solid #e1e8ff;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .accordion-custom .accordion-header {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
        border-radius: 12px 12px 0 0;
        padding: 15px 20px;
        font-weight: 600;
        color: #4a90e2;
    }
    </style>
    """
    
    with gr.Blocks(css=custom_css) as demo:
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
                            txt2vid_prompt = gr.Textbox(
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
                            
                            # 基础参数
                            with gr.Accordion("基础参数", open=True, elem_classes="accordion-custom"):
                                resolution = gr.Dropdown(
                                    label='视频分辨率',
                                    choices=[
                                        '480*832',
                                        '832*480',
                                        '624*624',
                                        '704*544',
                                        '544*704',
                                    ],
                                    value='480*832',
                                    container=True
                                )
                                
                                with gr.Row():
                                    sd_steps = gr.Slider(
                                        label="扩散步数",
                                        minimum=1,
                                        maximum=1000,
                                        value=50,
                                        step=1,
                                        container=True
                                    )
                                    guide_scale = gr.Slider(
                                        label="引导比例",
                                        minimum=4.0,
                                        maximum=10.0,
                                        value=6.0,
                                        step=0.5,
                                        container=True
                                    )
                                
                                with gr.Row():
                                    shift_scale = gr.Slider(
                                        label="偏移比例",
                                        minimum=4.0,
                                        maximum=12.0,
                                        value=8.0,
                                        step=0.5,
                                        container=True
                                    )
                                    seed = gr.Slider(
                                        label="随机种子",
                                        minimum=-1,
                                        maximum=2147483647,
                                        step=1,
                                        value=-1,
                                        container=True
                                    )
                                
                                n_prompt = gr.Textbox(
                                    label="负面提示词",
                                    placeholder="描述你不希望在视频中看到的内容",
                                    lines=2,
                                    container=True
                                )
                            
                            # 高级参数
                            with gr.Accordion("高级参数", open=False, elem_classes="accordion-custom"):
                                offload_model_ui = gr.Checkbox(
                                    label="模型卸载",
                                    value=True,
                                    container=True
                                )
                                
                                gr.Markdown("""
                                **说明**: 时间偏移和引导比例参数使用上方基础参数区域的设置。
                                如需覆盖，请使用命令行参数 `--sample_shift` 和 `--sample_guide_scale`。
                                """)
                        
                        # 创作按钮
                        with gr.Column():
                            run_t2v_button = gr.Button("🎬 开始创作", elem_classes="create-btn")
                            cancel_button = gr.Button("取消", visible=False, variant="stop")
                    
                    # 右侧面板
                    with gr.Column(elem_classes="right-panel"):
                        gr.Markdown('<div style="text-align: center; margin-bottom: 30px;"><h2 style="color: #4a90e2; font-size: 28px; font-weight: 600; margin-bottom: 10px;">🎥 视频生成</h2><p style="color: #7a9bb8; font-size: 16px;">输入提示词，AI将为您生成独特的视频内容</p></div>')
                        
                        # 视频生成区域
                        with gr.Column(elem_classes="video-section"):
                            # 默认状态
                            with gr.Column(elem_classes="video-placeholder", visible=True) as default_state:
                                gr.Markdown('<div style="font-size: 80px; color: #b8c5d6; margin-bottom: 20px;">🎬</div>')
                                gr.Markdown('<h3 style="color: #4a90e2; font-size: 24px; margin-bottom: 15px; font-weight: 600;">准备生成视频</h3>')
                                gr.Markdown('<p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px;">请在左侧输入提示词，选择模型和风格，然后点击"开始创作"按钮</p>')
                            
                            # 生成中状态
                            with gr.Column(elem_classes="video-placeholder", visible=False) as generating_state:
                                gr.Markdown('<div style="font-size: 80px; color: #4a90e2; margin-bottom: 20px;">⚡</div>')
                                gr.Markdown('<h3 style="color: #4a90e2; font-size: 24px; margin-bottom: 15px; font-weight: 600;">正在生成视频...</h3>')
                                gr.Markdown('<p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px;">AI正在根据您的提示词创作视频，请稍候</p>')
                                
                                # 进度条
                                with gr.Column(elem_classes="progress-container"):
                                    progress_bar = gr.Progress()
                        
                        # 结果视频（隐藏，用于存储结果）
                        result_gallery = gr.Video(visible=False)
                
                # 添加JavaScript功能
                gr.HTML("""
                <script>
                // 样例点击功能
                document.addEventListener('DOMContentLoaded', function() {
                    // 为样例添加点击事件
                    const examples = [
                        "一只可爱的小猫在花园里玩耍，阳光明媚，画面温馨，背景是美丽的花朵和绿树",
                        "繁华的城市夜景，霓虹灯闪烁，车流如织，高楼大厦灯火通明，天空中有星星点缀",
                        "一只小兔子在森林里跳跃，周围是高大的树木和绿色的草地，阳光透过树叶洒下斑驳的光影"
                    ];
                    
                    // 查找提示词输入框
                    const promptInput = document.querySelector('textarea[placeholder*="请描述您想要生成的视频内容"]');
                    if (promptInput) {
                        // 为每个样例添加点击事件
                        const exampleItems = document.querySelectorAll('.example-item');
                        exampleItems.forEach((item, index) => {
                            item.addEventListener('click', function() {
                                if (examples[index]) {
                                    promptInput.value = examples[index];
                                    // 触发输入事件
                                    promptInput.dispatchEvent(new Event('input', { bubbles: true }));
                                }
                            });
                        });
                    }
                });
                
                // 状态管理
                function updateUIState(state) {
                    const defaultState = document.querySelector('.video-placeholder:first-child');
                    const generatingState = document.querySelector('.video-placeholder:nth-child(2)');
                    
                    if (state === 'generating') {
                        if (defaultState) defaultState.style.display = 'none';
                        if (generatingState) generatingState.style.display = 'block';
                    } else {
                        if (defaultState) defaultState.style.display = 'block';
                        if (generatingState) generatingState.style.display = 'none';
                    }
                }
                </script>
                """)

        # 按钮状态控制函数
        def on_generate_start():
            return (
                gr.Button(interactive=False, elem_classes="create-btn"),  # 生成按钮不可点击
                gr.Button(visible=True),       # 取消按钮可见
                gr.Column(visible=False),     # 隐藏默认状态
                gr.Column(visible=True)       # 显示生成中状态
            )
        
        def on_generate_complete():
            return (
                gr.Button(interactive=True, elem_classes="create-btn"),   # 生成按钮可点击
                gr.Button(visible=False),      # 取消按钮隐藏
                gr.Column(visible=True),      # 显示默认状态
                gr.Column(visible=False)      # 隐藏生成中状态
            )
        
        def on_cancel():
            return (
                gr.Button(interactive=True, elem_classes="create-btn"),   # 生成按钮可点击
                gr.Button(visible=False),      # 取消按钮隐藏
                gr.Column(visible=True),      # 显示默认状态
                gr.Column(visible=False)      # 隐藏生成中状态
            )
        
        # 视频生成按钮
        run_t2v_button.click(
            fn=on_generate_start,
            outputs=[run_t2v_button, cancel_button, default_state, generating_state]
        ).then(
            fn=t2v_generation,
            inputs=[
                txt2vid_prompt, resolution, sd_steps, guide_scale, shift_scale,
                seed, n_prompt, offload_model_ui
            ],
            outputs=[result_gallery],
            show_progress=True  # 启用进度条显示
        ).then(
            fn=on_generate_complete,
            outputs=[run_t2v_button, cancel_button, default_state, generating_state]
        )
        
        # 取消按钮
        cancel_button.click(
            fn=on_cancel,
            outputs=[run_t2v_button, cancel_button, default_state, generating_state]
        )

    return demo


# Main
def _parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a video from a text prompt or image using Gradio")
    parser.add_argument(
        "--ckpt_dir",
        type=str,
        default="../Wan2.1-T2V-1.3B",
        help="The path to the checkpoint directory.")
    parser.add_argument(
        "--prompt_extend_method",
        type=str,
        default="none",
        choices=["none"],
        help="The prompt extend method to use.")
    parser.add_argument(
        "--prompt_extend_model",
        type=str,
        default=None,
        help="The prompt extend model to use.")
    
    # 模型卸载参数：将模型权重从GPU内存卸载到CPU内存，减少GPU显存占用
    # 适用于显存不足的情况，但会降低推理速度
    parser.add_argument(
        "--offload_model",
        action="store_true",
        default=True,
        help="Whether to offload model weights to CPU memory to save GPU VRAM (default: True)")
    
    # T5模型CPU运行参数：将T5文本编码器放在CPU上运行
    # 可以节省大量GPU显存，适合显存受限的环境
    # 默认开启T5 CPU运行以节省显存
    parser.add_argument(
        "--t5_cpu",
        type=lambda x: x.lower() == 'true',
        default=True,
        help="Place T5 text encoder on CPU to save GPU VRAM (default: True, use --t5_cpu false to disable)")
    
    # 采样偏移参数：控制视频生成过程中的时间偏移强度
    # 值越大，相邻帧之间的变化越剧烈，视频动态效果越明显
    parser.add_argument(
        "--sample_shift",
        type=float,
        default=8.0,
        help="Sampling shift scale for temporal consistency control (default: 8.0)")
    
    # 采样引导比例参数：控制生成视频对文本提示词的遵循程度
    # 值越大，生成内容越严格遵循提示词，但可能降低视频质量
    parser.add_argument(
        "--sample_guide_scale",
        type=float,
        default=6.0,
        help="Classifier-free guidance scale for text adherence (default: 6.0)")

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = _parse_args()
    globals()['args'] = args  # 将args设为全局变量，供其他函数使用

    print("Step1: Prompt extend disabled...", end='', flush=True)
    # 关闭prompt_extend功能
    print("done", flush=True)

    print("Step2: Init 1.3B t2v model...", end='', flush=True)
    cfg = WAN_CONFIGS['t2v-1.3B']

    
    # 调试：显示所有参数
    print("\n=== 调试信息 ===")
    print(f"args.offload_model: {args.offload_model} (类型: {type(args.offload_model)})")
    print(f"args.t5_cpu: {args.t5_cpu} (类型: {type(args.t5_cpu)})")
    print(f"args.sample_shift: {args.sample_shift} (类型: {type(args.sample_shift)})")
    print(f"args.sample_guide_scale: {args.sample_guide_scale} (类型: {type(args.sample_guide_scale)})")
    print("================\n")
    
    # T5 CPU设置：使用命令行参数，默认为True（开启）
    t5_cpu_setting = args.t5_cpu
    
    # wan_t2v = wan.WanT2V(
    #     config=cfg,
    #     checkpoint_dir=args.ckpt_dir,
    #     device_id=0,
    #     rank=0,
    #     t5_fsdp=False,
    #     dit_fsdp=False,
    #     use_usp=False,
    #     t5_cpu=t5_cpu_setting,  # 默认开启T5 CPU运行以节省显存
    # )
    print("done", flush=True)

    demo = gradio_interface()
    demo.launch(server_name="0.0.0.0", share=False, server_port=7860)
