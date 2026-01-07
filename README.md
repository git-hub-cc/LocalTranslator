# Local Translator Sidecar

本项目是一个基于 [Argos Translate](https://github.com/argosopentech/argos-translate) 的**完全离线、便携式**翻译引擎。

它经过特别修改，旨在作为 Sidecar（边车模式）集成到 Tauri、Electron 或其他应用程序中。它将模型文件与可执行文件放在同一目录下，不依赖系统的全局 Python 环境或全局配置路径。

## ✨ 核心特性

*   **📦 便携式模型管理**: 代码强制将模型路径指向程序同级目录的 `packages/` 文件夹，实现“绿色版”部署，不污染用户系统路径。
*   **🔌 离线运行**: 只要下载好模型，运行无需网络。
*   **🚀 JSON API**: 通过标准输入输出（Stdio）交互，输出 JSON 格式，易于任何语言解析。
*   **⚡ 硬件加速**: 支持 `ctranslate2` (CUDA/ROCm) 加速。

---

## 🛠️ 环境准备

### 1. 基础环境
*   **Python**: 3.10+
*   **系统**: Windows / macOS / Linux

### 2. 安装依赖

建议在虚拟环境中安装。根据你的硬件选择一种安装方式：

```bash
# 退出venv
# deactivate

# 创建并激活虚拟环境
python -m venv venv

# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
.\venv\Scripts\Activate

# 删除旧的打包输出和临时文件
# Remove-Item -Recurse -Force dist, build, *.spec -ErrorAction SilentlyContinue
# 卸载当前的 ctranslate2, 删除不干净，建议重建venv环境
# pip uninstall -y ctranslate2

# --- 选项 A: NVIDIA 显卡 (CUDA) [推荐] ---
pip install "ctranslate2[cuda]" argostranslate pyinstaller

# --- 选项 B: 无显卡 (CPU 模式) ---
pip install ctranslate2 argostranslate pyinstaller

# --- 选项 C: AMD 显卡 (ROCm) [仅 Linux 支持] ---
# 第一步：确保系统已安装 ROCm 依赖（以 Ubuntu 为例）
# sudo apt-get update && sudo apt-get install -y rocm-libs rocm-dev
# 第二步：安装适配 ROCm 的 ctranslate2
pip install "ctranslate2[rocm]" argostranslate pyinstaller
```

---

## 🚀 开发与使用流程

### 第一步：下载模型

运行脚本下载并解压模型到本地 `packages` 目录。

```bash
# 对应文件: 01download_models.py
python 01download_models.py
```

> **注意**: 运行结束后，项目根目录下会出现一个 `packages` 文件夹，里面包含了解压后的模型文件。

### 第二步：测试翻译

在开发环境下直接运行 Python 脚本进行测试。注意脚本会自动检测同级目录下的 `packages` 文件夹。

```bash
# 对应文件: 02translate.py
python 02translate.py --text "Hello World" --source "en" --target "zh"
```

**成功输出示例**:
```json
{"code": 200, "translated_text": "你好世界"}
```

---

## 📦 构建发布 (Build)

使用 `pyinstaller` 将脚本打包为独立 EXE。

### 1. 执行打包命令

```bash
pyinstaller --onefile --noconsole --name "translate_engine" `
    --hidden-import "argostranslate.definitions" `
    --hidden-import "argostranslate.networking" `
    --hidden-import "argostranslate.package" `
    --hidden-import "argostranslate.settings" `
    --hidden-import "argostranslate.translate" `
    02translate.py
```

```bash
# 注意：这里去掉了 --noconsole，或者你可以显式加上 --console
pyinstaller --onefile --console --name "translate_engine" --hidden-import "argostranslate.definitions" --hidden-import "argostranslate.networking" --hidden-import "argostranslate.package" --hidden-import "argostranslate.settings" --hidden-import "argostranslate.translate" 02translate.py
```


### 2. 🚨 关键步骤：迁移模型文件

由于代码中硬编码了模型路径逻辑，**你必须将 `packages` 文件夹复制到构建产物目录中**。

**目录结构必须如下所示**：

```text
部署目录/
├── translate_engine.exe   # (Linux下为 translate_engine)
└── packages/              # 必须与 exe 在同一级！
    ├── translate-en_zh-1_9/
    ├── translate-zh_en-1_9/
    └── ...
```

如果 `packages` 文件夹不存在于 exe 同级目录，程序将报错退出。

---

## 🔌 集成指南 (Tauri/Electron)

在你的主应用中调用此 Sidecar 时：

1.  **资源配置**: 将 `translate_engine.exe` 和 `packages/` 文件夹一同放入 Sidecar 资源目录。
2.  **调用方式**:
    *   **Command**: `translate_engine.exe`
    *   **Args**: `["--text", "要翻译的内容", "--source", "en", "--target", "zh"]`
3.  **错误处理**:
    *   脚本已做修改，即使发生 Python 级错误（如缺少依赖、路径错误），也会尝试以 JSON 格式打印错误信息到 Stdout，方便主进程捕获。
    *   错误码 `501`: 环境或导入错误。
    *   错误码 `500`: 翻译过程错误。

---

## 📄 常见问题

**Q: 为什么运行 exe 提示找不到 argostranslate?**
A: 请检查是否正确使用了 `--hidden-import` 参数进行打包。

**Q: 为什么提示 "找不到所需的语言模型"?**
A: 请确保 `packages` 文件夹位于 exe 文件的同一目录下。代码逻辑通过 `sys.executable` 获取当前路径并寻找 `packages` 子目录。

**Q: 支持更多语言吗？**
A: 修改 `01download_models.py` 中的 `models_to_download` 列表，添加对应的语言代码（如 `("ja", "zh")`），重新运行下载脚本即可。
