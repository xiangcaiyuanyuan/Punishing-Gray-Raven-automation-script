import sys
import os
import pyautogui
from PIL import Image
import numpy as np

CONFIDENCE_THRESHOLD = 0.8


def resource_path(relative_path):
    """获取资源文件的绝对路径（支持打包后的程序）"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)


def find_image(img_names):
    """
    在屏幕上查找图片，支持单个字符串或字符串列表。
    返回第一个成功匹配的坐标区域 (left, top, width, height)，
    如果全部未找到则返回 None。
    自动补全 .png 后缀。
    """
    # 统一转为列表处理
    if isinstance(img_names, str):
        img_names = [img_names]
    elif not isinstance(img_names, list):
        return None   # 非法输入

    for name in img_names:
        if not isinstance(name, str):
            continue
        try:
            # 补全扩展名
            if '.' not in name:
                name = f'{name}.png'
            img_path = resource_path(os.path.join('data', 'imgs', name))
            pil_img = Image.open(img_path)
            np_img = np.array(pil_img)
            result = pyautogui.locateOnScreen(np_img, confidence=CONFIDENCE_THRESHOLD)
            if result is not None:
                return result   # 找到即返回
        except pyautogui.ImageNotFoundException:
            continue
        except (OSError, ValueError) as e:
            print(f"[警告] 查找图片失败 {name}: {e}")
            continue
    return None