#!/bin/bash

# 检查CUDA是否可用
if ! command -v nvidia-smi &> /dev/null; then
    echo "错误: 未检测到NVIDIA GPU或CUDA环境"
    exit 1
fi

echo "检测到CUDA环境，开始启动Wan2.1 T2V-1.3B..."

# 检查模型目录是否存在
if [ ! -d "../Wan2.1-T2V-1.3B" ]; then
    echo "错误: 模型目录 ../Wan2.1-T2V-1.3B 不存在"
    exit 1
fi

echo "模型目录检查通过: ../Wan2.1-T2V-1.3B"

# 启动Gradio界面
cd gradio
python t2v_1.3B_singleGPU.py \
    --ckpt_dir ../Wan2.1-T2V-1.3B \
    --offload_model \
    --sample_shift 8 \
    --sample_guide_scale 6
