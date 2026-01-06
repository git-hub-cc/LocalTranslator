# 文件: translate.py (修正版)

import os
import sys
import json
import argparse

# --------------------------------------------------------------------------------
# 核心修复: 让打包后的EXE能找到模型文件
# --------------------------------------------------------------------------------
# 当脚本被 PyInstaller 打包成 --onefile 模式的 exe 后，
# `sys.executable` 会指向 exe 文件的路径。
# 如果是作为普通 .py 脚本运行, `__file__` 会指向脚本自身的路径。
# 我们优先使用 `sys.executable` 来确保在打包后也能正确工作。
if getattr(sys, 'frozen', False):
    # 如果是打包状态
    application_path = os.path.dirname(sys.executable)
else:
    # 如果是普通脚本运行状态
    application_path = os.path.dirname(os.path.abspath(__file__))

# 构建模型文件夹的绝对路径 (假设 'packages' 文件夹与 exe 在同一目录下)
packages_path = os.path.join(application_path, "packages")

# 强制 argostranslate 使用我们指定的模型路径
os.environ["ARGOS_PACKAGES_DIR"] = packages_path

# 只有在设置完路径后才能导入 argostranslate 的核心模块
try:
    from argostranslate import translate
except ImportError as e:
    # 捕获导入错误，这通常意味着路径设置有问题或依赖不完整
    error_result = {
        "code": 501,
        "error_message": f"无法导入 argostranslate 模块: {e}. 请检查依赖是否正确安装，以及 'packages' 目录是否存在于: {packages_path}"
    }
    print(json.dumps(error_result, ensure_ascii=False))
    sys.exit(1)
# --------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="本地翻译 Sidecar")
    parser.add_argument("--text", required=True, help="要翻译的文本")
    parser.add_argument("--source", required=True, help="源语言代码 (例如 'en')")
    parser.add_argument("--target", required=True, help="目标语言代码 (例如 'zh')")
    args = parser.parse_args()

    result = {}

    try:
        # 获取已安装的翻译模型
        installed_languages = translate.get_installed_languages()
        source_lang = next((lang for lang in installed_languages if lang.code == args.source), None)
        target_lang = next((lang for lang in installed_languages if lang.code == args.target), None)

        if not source_lang or not target_lang:
            raise ValueError(f"找不到所需的语言模型。源语言: '{args.source}', 目标语言: '{args.target}'. 请确保模型已下载并放置在 'packages' 目录中。")

        # 执行翻译
        translation = source_lang.get_translation(target_lang)
        if not translation:
            raise RuntimeError(f"无法创建从 '{args.source}' 到 '{args.target}' 的翻译通道。")

        translated_text = translation.translate(args.text)

        result = {
            "code": 200,
            "translated_text": translated_text
        }

    except Exception as e:
        result = {
            "code": 500,
            "error_message": str(e)
        }

    # 无论成功或失败，都以JSON格式输出结果
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()