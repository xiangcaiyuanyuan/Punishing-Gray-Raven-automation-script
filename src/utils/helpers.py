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


def find_image(img_name):
    """在屏幕上查找图片，返回坐标区域或 None（自动补全 .png 后缀）"""
    # 非字符串（如 int）直接返回 None，防止 '.'
    if not isinstance(img_name, str):
        return None
    try:
        # 若未指定扩展名则自动补全 .png
        if '.' not in img_name:
            img_name = f'{img_name}.png'
        img_path = resource_path(os.path.join('data', 'imgs', img_name))

        # OpenCV 无法直接读取中文路径，改用 PIL + numpy
        pil_img = Image.open(img_path)
        np_img = np.array(pil_img)
        return pyautogui.locateOnScreen(np_img, confidence=CONFIDENCE_THRESHOLD)
    except pyautogui.ImageNotFoundException:
        return None
    except (OSError, ValueError) as e:
        print(f"[警告] 查找图片失败 {img_name}: {e}")
        return None
