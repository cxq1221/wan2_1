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
    with gr.Blocks() as demo:
        gr.Markdown("""
                    <div style="text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 20px;">
                        Wan2.1 (T2V-1.3B)
                    </div>
                    <div style="text-align: center; font-size: 16px; font-weight: normal; margin-bottom: 20px;">
                        Wan: Open and Advanced Large-Scale Video Generative Models.
                    </div>
                    """)

        with gr.Row():
            with gr.Column():
                txt2vid_prompt = gr.Textbox(
                    label="Prompt",
                    placeholder="Describe the video you want to generate",
                )
                tar_lang = gr.Radio(
                    choices=["ZH", "EN"],
                    label="Target language of prompt enhance",
                    value="ZH")
                run_p_button = gr.Button(value="Prompt Enhance")

                with gr.Accordion("生成参数设置", open=True):
                    # 基础参数
                    gr.Markdown("### 基础参数")
                    resolution = gr.Dropdown(
                        label='视频分辨率 (Width*Height)',
                        choices=[
                            '480*832',
                            '832*480',
                            '624*624',
                            '704*544',
                            '544*704',
                        ],
                        value='480*832',
                        info="选择生成视频的分辨率")

                    with gr.Row():
                        sd_steps = gr.Slider(
                            label="扩散步数 (Diffusion steps)",
                            minimum=1,
                            maximum=1000,
                            value=50,
                            step=1,
                            info="扩散采样步数，步数越多质量越高但速度越慢")
                        guide_scale = gr.Slider(
                            label="引导比例 (Guide scale)",
                            minimum=4.0,
                            maximum=10.0,
                            value=6.0,
                            step=0.5,
                            info="分类器自由引导比例，控制文本遵循程度，值越大越严格遵循提示词")
                    
                    with gr.Row():
                        shift_scale = gr.Slider(
                            label="偏移比例 (Shift scale)",
                            minimum=4.0,
                            maximum=12.0,
                            value=8.0,
                            step=0.5,
                            info="时间偏移强度，控制视频动态效果，值越大变化越剧烈")
                        seed = gr.Slider(
                            label="随机种子 (Seed)",
                            minimum=-1,
                            maximum=2147483647,
                            step=1,
                            value=-1,
                            info="随机种子，-1表示随机生成")
                    
                    n_prompt = gr.Textbox(
                        label="负面提示词 (Negative Prompt)",
                        placeholder="描述你不希望在视频中看到的内容",
                        info="用于排除不希望出现的内容")
                    
                    # 高级优化参数
                    gr.Markdown("### 高级优化参数")
                    gr.Markdown("""
                    **注意**: 这些参数会覆盖上方的设置，优先级更高
                    """)
                    
                    with gr.Row():
                        offload_model_ui = gr.Checkbox(
                            label="模型卸载 (--offload_model)",
                            value=True,
                            info="将模型权重从GPU卸载到CPU，节省显存但降低速度")
                    
                    gr.Markdown("""
                    **说明**: 时间偏移和引导比例参数使用上方基础参数区域的设置。
                    如需覆盖，请使用命令行参数 `--sample_shift` 和 `--sample_guide_scale`。
                    """)

                # 生成按钮和进度显示
                with gr.Row():
                    run_t2v_button = gr.Button("Generate Video", variant="primary", size="lg")
                    cancel_button = gr.Button("Cancel", variant="stop", size="lg", visible=False)
                
                # 进度条和状态显示
                progress_bar = gr.Progress()
                status_text = gr.Textbox(
                    label="生成状态",
                    value="准备就绪",
                    interactive=False,
                    lines=2
                )

            with gr.Column():
                result_gallery = gr.Video(
                    label='Generated Video', interactive=False, height=600)

        # 按钮状态控制函数
        def on_generate_start():
            return (
                gr.Button(interactive=False),  # 生成按钮不可点击
                gr.Button(visible=True),       # 取消按钮可见
                gr.Textbox(value="正在生成视频...", interactive=False)
            )
        
        def on_generate_complete():
            return (
                gr.Button(interactive=True),   # 生成按钮可点击
                gr.Button(visible=False),      # 取消按钮隐藏
                gr.Textbox(value="准备就绪", interactive=False)
            )
        
        def on_cancel():
            return (
                gr.Button(interactive=True),   # 生成按钮可点击
                gr.Button(visible=False),      # 取消按钮隐藏
                gr.Textbox(value="已取消", interactive=False)
            )
        
        # 提示词增强按钮
        run_p_button.click(
            fn=prompt_enc,
            inputs=[txt2vid_prompt, tar_lang],
            outputs=[txt2vid_prompt])

        # 视频生成按钮
        run_t2v_button.click(
            fn=on_generate_start,
            outputs=[run_t2v_button, cancel_button, status_text]
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
            outputs=[run_t2v_button, cancel_button, status_text]
        )
        
        # 取消按钮
        cancel_button.click(
            fn=on_cancel,
            outputs=[run_t2v_button, cancel_button, status_text]
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
    
    wan_t2v = wan.WanT2V(
        config=cfg,
        checkpoint_dir=args.ckpt_dir,
        device_id=0,
        rank=0,
        t5_fsdp=False,
        dit_fsdp=False,
        use_usp=False,
        t5_cpu=t5_cpu_setting,  # 默认开启T5 CPU运行以节省显存
    )
    print("done", flush=True)

    demo = gradio_interface()
    demo.launch(server_name="0.0.0.0", share=False, server_port=7860)
