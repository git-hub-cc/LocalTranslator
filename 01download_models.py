# 文件: download_models.py (修正版)

import os
import zipfile
from argostranslate import package

# --- 配置 ---
# 创建一个本地目录来存放模型
output_dir = "packages"
os.makedirs(output_dir, exist_ok=True)

# 定义你需要下载的语言模型 (from_code, to_code)
# 这里以 英->中 和 中->英 为例
models_to_download = [
    ("en", "zh"),
    ("zh", "en"),
]
# --- 配置结束 ---


def download_and_extract_model(pkg):
    """下载语言包并将其解压到本地目录"""
    print(f"正在下载模型: {pkg}...")
    download_path = pkg.download()
    print(f"下载完成，路径: {download_path}")

    # 解压 .argosmodel 文件 (它其实是一个zip文件)
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"模型已成功解压到 '{output_dir}' 目录")

    # 删除下载的临时 .argosmodel 文件
    os.remove(download_path)
    print("-" * 20)

def main():
    print("正在更新可用的语言包列表...")
    package.update_package_index()

    available_packages = package.get_available_packages()

    for from_code, to_code in models_to_download:
        print(f"正在查找模型 {from_code} -> {to_code}")

        # 筛选出匹配的包
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code,
                available_packages,
            ),
            None,
        )

        if package_to_install:
            download_and_extract_model(package_to_install)
        else:
            print(f"错误: 找不到模型 {from_code} -> {to_code}。请检查语言代码是否正确。")

if __name__ == "__main__":
    main()