# 🚀 Gradio命令运行指南

## 🎯 概述

现在你可以使用 `gradio` 命令来运行文生视频应用，享受热加载代码的便利！

## ✨ 主要优势

### 🔥 **热加载功能**
- 修改代码后自动重新加载
- 无需重启应用
- 开发调试更高效

### ⚙️ **配置管理**
- 支持环境变量配置
- 支持JSON配置文件
- 无需命令行参数

## 🚀 运行方式

### 1. **使用Gradio命令（推荐）**
```bash
# 基本运行
gradio gradio/t2v_1.3B_singleGPU.py

# 指定端口
gradio gradio/t2v_1.3B_singleGPU.py --port 7860

# 允许外部访问
gradio gradio/t2v_1.3B_singleGPU.py --server-name 0.0.0.0 --port 7860

# 启用分享功能
gradio gradio/t2v_1.3B_singleGPU.py --share
```

### 2. **传统Python运行**
```bash
python gradio/t2v_1.3B_singleGPU.py
```

## ⚙️ 配置方式

### 🌍 **环境变量配置**
```bash
# 设置环境变量
export WAN_CKPT_DIR="../Wan2.1-T2V-1.3B"
export WAN_OFFLOAD_MODEL="true"
export WAN_T5_CPU="true"
export WAN_SAMPLE_SHIFT="8.0"
export WAN_SAMPLE_GUIDE_SCALE="6.0"

# 然后运行
gradio gradio/t2v_1.3B_singleGPU.py
```

### 📄 **配置文件方式**
```bash
# 使用默认配置文件 wan_config.json
gradio gradio/t2v_1.3B_singleGPU.py

# 指定配置文件
export WAN_CONFIG_FILE="my_config.json"
gradio gradio/t2v_1.3B_singleGPU.py
```

### 🔧 **配置参数说明**

| 参数 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| `ckpt_dir` | `WAN_CKPT_DIR` | `../Wan2.1-T2V-1.3B` | 模型检查点目录 |
| `offload_model` | `WAN_OFFLOAD_MODEL` | `true` | 是否卸载模型到CPU |
| `t5_cpu` | `WAN_T5_CPU` | `true` | T5模型是否在CPU运行 |
| `sample_shift` | `WAN_SAMPLE_SHIFT` | `8.0` | 时间偏移强度 |
| `sample_guide_scale` | `WAN_SAMPLE_GUIDE_SCALE` | `6.0` | 文本引导比例 |

## 🎨 热加载开发

### 📝 **代码修改**
```python
# 修改任何代码后，保存文件
# Gradio会自动检测并重新加载
# 无需重启应用！
```

### 🔍 **实时调试**
- 修改UI组件
- 调整样式
- 更新函数逻辑
- 所有更改立即生效

## 📁 文件结构

```
Wan2.1/
├── gradio/
│   └── t2v_1.3B_singleGPU.py    # 主应用文件（已适配）
├── wan_config.json               # 配置文件示例
├── GRADIO_COMMAND_README.md      # 本文档
└── ...
```

## 🚨 注意事项

### ⚠️ **依赖要求**
- Gradio 3.0+
- Python 3.7+
- 相关模型依赖

### 🔧 **配置优先级**
1. 环境变量（最高优先级）
2. 配置文件
3. 默认值（最低优先级）

### 🌐 **网络配置**
- 默认端口：7860
- 默认地址：127.0.0.1
- 外部访问：使用 `--server-name 0.0.0.0`

## 🎯 使用场景

### 💻 **开发调试**
```bash
# 开发模式，启用热加载
gradio gradio/t2v_1.3B_singleGPU.py --port 7860
```

### 🚀 **生产部署**
```bash
# 生产模式，外部访问
gradio gradio/t2v_1.3B_singleGPU.py --server-name 0.0.0.0 --port 7860
```

### 🔗 **分享演示**
```bash
# 启用分享功能
gradio gradio/t2v_1.3B_singleGPU.py --share
```

## 🎉 开始使用

1. **确保依赖安装**
   ```bash
   pip install gradio
   ```

2. **配置参数**（可选）
   ```bash
   # 方式1：环境变量
   export WAN_CKPT_DIR="../Wan2.1-T2V-1.3B"
   
   # 方式2：配置文件
   cp wan_config.json my_config.json
   # 编辑 my_config.json
   ```

3. **运行应用**
   ```bash
   gradio gradio/t2v_1.3B_singleGPU.py
   ```

4. **享受热加载**
   - 修改代码
   - 保存文件
   - 自动重新加载！

## 🔍 故障排除

### ❌ **常见问题**

1. **端口被占用**
   ```bash
   gradio gradio/t2v_1.3B_singleGPU.py --port 7861
   ```

2. **配置文件错误**
   ```bash
   # 检查JSON格式
   python -m json.tool wan_config.json
   ```

3. **权限问题**
   ```bash
   # 使用sudo（如果需要）
   sudo gradio gradio/t2v_1.3B_singleGPU.py --server-name 0.0.0.0
   ```

### 📞 **获取帮助**
```bash
# Gradio帮助
gradio --help

# 查看版本
gradio --version
```

---

**🎬 现在你可以使用 `gradio` 命令享受热加载的开发体验了！**
