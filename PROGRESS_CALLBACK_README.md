# Wan2.1 进度回调功能说明

## 概述

我们已经成功为Wan2.1模型添加了进度回调功能，现在可以获取真实的扩散步骤进度，而不是基于时间的估算。

## 修改内容

### 1. 修改了 `wan/text2video.py`

- 在 `generate` 方法中添加了 `progress_callback` 参数
- 支持自定义进度回调函数
- 保持向后兼容性（如果不提供回调，仍使用默认的tqdm进度条）

### 2. 修改了 `gradio/t2v_1.3B_singleGPU.py`

- 移除了基于时间估算的进度监控
- 集成了真实的扩散步骤进度回调
- 简化了线程管理

## 使用方法

### 基本用法

```python
from wan import WanT2V

# 创建模型实例
wan_t2v = WanT2V(config, checkpoint_dir)

# 定义进度回调函数
def progress_callback(step, total_steps_count, current_timestep):
    progress = (step + 1) / total_steps_count * 100
    print(f"扩散步骤: {step + 1}/{total_steps_count} - 进度: {progress:.1f}%")

# 生成视频时使用回调
video = wan_t2v.generate(
    input_prompt="一只可爱的小猫",
    sampling_steps=50,
    progress_callback=progress_callback  # 新的进度回调参数
)
```

### 回调函数签名

```python
def progress_callback(step, total_steps_count, current_timestep):
    """
    进度回调函数
    
    Args:
        step (int): 当前步骤索引 (从0开始)
        total_steps_count (int): 总步骤数
        current_timestep (float): 当前时间步值
    """
    pass
```

### 在Gradio界面中的使用

现在Gradio界面会自动使用真实的扩散步骤进度，显示格式为：
```
扩散步骤 1/50 (时间步: 1000.00)
扩散步骤 2/50 (时间步: 980.00)
...
扩散步骤 50/50 (时间步: 20.00)
```

## 进度分布

新的进度分布更加合理：
- **2%**: 模型初始化
- **88%**: 扩散生成过程（基于真实步骤）
- **10%**: 视频保存

## 向后兼容性

- 如果不提供 `progress_callback` 参数，模型仍使用默认的tqdm进度条
- 现有的代码无需修改即可继续工作
- 新功能是可选的增强

## 错误处理

- 如果进度回调函数出错，会记录警告但不会中断生成过程
- 确保生成过程的稳定性

## 测试

运行测试脚本验证功能：
```bash
python test_progress_callback.py
```

运行变量名冲突修复测试：
```bash
python test_variable_conflict_fix.py
```

## 注意事项

1. 进度回调函数会在扩散循环的每一步被调用
2. 回调函数应该尽量轻量，避免影响生成性能
3. 如果不需要进度显示，可以不传递回调参数
4. 进度回调只在主进程（rank=0）中生效

## 优势

1. **真实进度**: 不再依赖时间估算，显示真实的扩散步骤
2. **精确控制**: 可以自定义进度显示格式和行为
3. **性能友好**: 回调机制轻量，不影响生成速度
4. **向后兼容**: 现有代码无需修改
5. **错误安全**: 回调错误不会中断生成过程

## Bug修复记录

### 变量名冲突修复 (已解决)

**问题描述**:
- 回调函数参数名 `total_steps` 与外部变量 `total_steps[0]` 冲突
- 赋值语句 `total_steps[0] = total_steps` 逻辑错误

**解决方案**:
- 参数重命名为 `total_steps_count`
- 赋值语句改为 `total_steps[0] = total_steps_count`
- 所有使用参数的地方都使用新名称

**修复验证**:
- ✅ 变量名冲突已解决
- ✅ 参数赋值逻辑正确
- ✅ 进度计算准确
- ✅ 外部状态更新正常

### Gradio进度条线程安全问题修复 (已解决)

**问题描述**:
- Gradio的`progress()`函数不能在后台线程中调用
- 进度回调函数在后台线程中执行，导致界面进度条无法更新
- 界面进度一直卡在10%，但控制台有进度打印

**解决方案**:
- 使用`queue.Queue`作为线程间通信桥梁
- 后台线程将进度信息放入队列
- 主线程从队列获取进度信息并更新Gradio进度条
- 添加专门的进度监控线程

**修复后的架构**:
```
后台线程 (Wan2.1) → 进度回调 → 队列 → 进度监控线程 → Gradio进度条
```

**关键代码**:
```python
# 使用队列来传递进度更新
progress_queue = queue.Queue()

def progress_callback(step, total_steps_count, current_timestep):
    # 将进度信息放入队列，而不是直接调用progress
    progress_queue.put((progress_value, desc))

def progress_monitor():
    # 在主线程中更新Gradio进度条
    while not generation_complete[0]:
        progress_update = progress_queue.get(timeout=0.1)
        progress_value, desc = progress_update
        progress(progress_value, desc)  # 在主线程中调用
```

**修复验证**:
- ✅ 进度队列机制正常工作
- ✅ 后台线程可以安全地放入进度信息
- ✅ 主线程可以正确接收和处理进度更新
- ✅ 线程间通信正常
- ✅ Gradio界面进度条现在可以正常更新

**测试命令**:
```bash
python test_progress_queue_fix.py
```
