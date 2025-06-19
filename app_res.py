import os
import shutil
from pathlib import Path


def rename_and_copy(source_root, target_root, original_pattern, new_name):
    """
    遍历源文件夹的子文件夹，重命名文件后复制到目标文件夹的同名子文件夹

    :param source_root: 源根目录（如 "A"）
    :param target_root: 目标根目录（如 "C"）
    :param original_pattern: 要匹配的文件名模式（如 "*.txt"）
    :param new_name: 新文件名（不含扩展名）
    """
    # 遍历源文件夹的子文件夹
    for subdir in Path(source_root).iterdir():
        if subdir.is_dir():
            subdir_name = subdir.name  # 子文件夹名（如 "B1"）
            target_subdir = Path(target_root) / subdir_name

            # 创建目标子文件夹（如果不存在）
            target_subdir.mkdir(parents=True, exist_ok=True)
            print(f"处理子文件夹: {subdir} → {target_subdir}")

            # 遍历子文件夹中的匹配文件
            for file_path in subdir.glob(original_pattern):
                old_name = file_path.name
                ext = file_path.suffix  # 文件扩展名（如 ".txt"）
                new_file_name = f"{new_name}{ext}"
                target_path = target_subdir / new_file_name

                # 处理文件名重复
                counter = 1
                while target_path.exists():
                    new_file_name = f"{new_name}_{counter}{ext}"
                    target_path = target_subdir / new_file_name
                    counter += 1

                # 复制并重命名文件
                shutil.copy2(file_path, target_path)
                print(f"已复制: {subdir_name}/{old_name} → {target_path}")


if __name__ == "__main__":
    # 参数设置
    source_root = r"D:\work\huoguo\chat-sdk-android\app-demo\src\main\组 96_slices"  # 源根目录
    target_root = r"D:\work\huoguo\chat-sdk-android\app-demo\src\main\res"
    original_pattern = "*.png"  # 匹配所有 .txt 文件
    new_name = "ic_redo_black"  # 新文件名（不含扩展名）

    # 执行操作
    rename_and_copy(source_root, target_root, original_pattern, new_name)
    print("操作完成！")