import subprocess
import sys
import os
import time
import shutil


def clean_build_folders(src_dir):
    """清理旧的构建文件夹"""
    # 只清理 build 临时文件夹
    build_path = os.path.join(src_dir, 'build')
    if os.path.exists(build_path):
        try:
            shutil.rmtree(build_path)
            print(f"[信息] 已清理旧文件夹: build")
        except Exception as e:
            print(f"[警告] 清理文件夹 build 失败: {e}")
            return False

    return True


def create_config_folder(target_path):
    """在目标文件夹中创建 config 目录（每次都重新创建）"""
    config_path = os.path.join(target_path, 'config')

    # 如果已存在，先删除再重建（确保内容是最新的）
    if os.path.exists(config_path):
        try:
            shutil.rmtree(config_path)
            print(f"[信息] 已清理旧的 config 文件夹")
        except Exception as e:
            print(f"[警告] 清理 config 文件夹失败: {e}")
            print(f"       请确保程序未运行后重试")
            return False

    # 创建新的 config 文件夹
    try:
        os.makedirs(config_path, exist_ok=True)
        print(f"[✓] 已创建 config 文件夹: {config_path}")

    except Exception as e:
        print(f"[警告] 创建 config 文件夹失败: {e}")
        return False

    return True


def build_with_spec():
    """使用 spec 文件打包项目"""

    # spec 文件路径
    spec_file = "KyrieAuto.spec"

    # 检查 spec 文件是否存在
    if not os.path.exists(spec_file):
        print(f"[错误] 找不到 spec 文件: {spec_file}")
        print("请确保在正确的目录下运行此脚本")
        input("\n按回车键退出...")
        return False

    print("=" * 50)
    print("    KyrieAuto 自动打包工具")
    print("=" * 50)
    print()
    print(f"[信息] 使用 spec 文件: {spec_file}")

    # 获取源码目录
    src_dir = os.path.dirname(os.path.abspath(__file__))

    # 清理旧的构建文件
    print(f"[信息] 清理旧的构建文件...")
    if not clean_build_folders(src_dir):
        input("\n按回车键退出...")
        return False

    # 设置输出目录名称
    output_dir = '干爆战双帕尼尼'
    print(f"[信息] 输出目录: {output_dir}")

    # ── 关闭正在运行的程序 ──
    exe_name = f'{output_dir}.exe'
    result = subprocess.run(['taskkill', '/F', '/IM', exe_name],
                           capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[✓] 已关闭正在运行的程序: {exe_name}")
    else:
        print(f"[信息] 程序未在运行，无需关闭")

    print(f"[信息] 开始打包...")
    print()

    try:
        # 执行 pyinstaller 命令，直接指定输出目录
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", spec_file, "--distpath=" + output_dir],
            check=True,
            capture_output=False
        )

        print()
        print("=" * 50)
        print("[✓] 打包成功！")
        print("=" * 50)

        # 创建 config 文件夹（每次都重新创建）
        target_path = os.path.join(src_dir, output_dir)
        if os.path.exists(target_path):
            if create_config_folder(target_path):
                print(f"\n[信息] 输出位置: {target_path}")
            else:
                print(f"\n[警告] 创建 config 文件夹失败")
        else:
            print(f"\n[警告] 输出文件夹不存在，可能打包出现问题")

        # ── 压缩为 zip ──
        zip_path = os.path.join(src_dir, f'{output_dir}.zip')
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
                print(f"[信息] 已删除旧压缩包: {output_dir}.zip")
            except Exception as e:
                print(f"[警告] 删除旧压缩包失败: {e}")

        try:
            shutil.make_archive(os.path.join(src_dir, output_dir), 'zip', src_dir, output_dir)
            print(f"[✓] 已创建压缩包: {output_dir}.zip")
        except Exception as e:
            print(f"[警告] 创建压缩包失败: {e}")

        return True

    except subprocess.CalledProcessError as e:
        print()
        print("=" * 50)
        print(f"[错误] 打包失败！")
        print("=" * 50)
        print(f"\n错误信息: {e}")
        input("\n按回车键退出...")
        return False
    except FileNotFoundError:
        print()
        print("[错误] 未找到 PyInstaller")
        print("正在安装 PyInstaller...")

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("[✓] PyInstaller 安装成功")
            print("请重新运行此脚本进行打包")
        except Exception as install_error:
            print(f"[错误] PyInstaller 安装失败: {install_error}")

        input("\n按回车键退出...")
        return False


if __name__ == "__main__":
    build_with_spec()

