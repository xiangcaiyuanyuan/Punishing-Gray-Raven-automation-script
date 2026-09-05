import sys
import os
import time
import pyautogui
import pygetwindow as gw
from PIL import Image
import numpy as np

CONFIDENCE_THRESHOLD = 0.7

# 模板截图时的参考分辨率（data/imgs 的图片在此分辨率下截取）
REFERENCE_WIDTH = 2560
REFERENCE_HEIGHT = 1600

# 全局缩放系数（由 init_image_scale 启动时计算，默认 1.0 表示不缩放）
_scale_x = 1.0
_scale_y = 1.0

# 手动指定游戏窗口尺寸（元组 (宽, 高)）。自动检测找不到游戏窗口时，
# 可在这里填上实际的窗口尺寸绕过检测，例如 MANUAL_WINDOW_SIZE = (1920, 1200)
MANUAL_WINDOW_SIZE = None


def resource_path(relative_path):
    """获取资源文件的绝对路径（支持打包后的程序）"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)


# 缩放系数合理范围（超出则视为异常，避免模板缩得无法识别）
_MIN_SCALE = 0.4
_MAX_SCALE = 2.5


def _get_client_size(hwnd):
    """获取窗口客户区尺寸 (w, h)（不含标题栏/边框的渲染区域）。

    用 ctypes 调用 Windows API GetClientRect，无需额外安装 pywin32。
    """
    try:
        import ctypes
        from ctypes import wintypes
        rect = wintypes.RECT()
        user32 = ctypes.windll.user32
        if user32.GetClientRect(ctypes.c_void_p(hwnd), ctypes.byref(rect)) == 0:
            return None
        return rect.right - rect.left, rect.bottom - rect.top
    except Exception:
        return None


def _find_game_window(title_key='战双帕弥什'):
    """查找游戏窗口，返回客户区尺寸 (width, height)；找不到返回 (None, None)。

    处理逻辑：
    1. 标题含关键字的窗口中，优先选「未最小化且面积最大」的；
    2. 全部最小化时，选第一个并先 restore() 还原，再读取尺寸
       （最小化窗口 pygetwindow 报 237x39 之类的无效尺寸）；
    3. 读取「客户区」尺寸（渲染区域），而非含标题栏/边框的外框尺寸
       —— 外框尺寸会让缩放系数偏大约 1-2%，导致模板匹配置信度不足；
    4. 都没找到则打印可见窗口标题便于排查。
    """
    try:
        wins = gw.getWindowsWithTitle(title_key)
        if wins:
            normal = [w for w in wins if not w.isMinimized]
            candidates = normal if normal else wins
            # 面积最大者（同标题下游戏窗口通常大于启动器）
            w = max(candidates, key=lambda x: x.width * x.height)

            if w.isMinimized:
                # 最小化 → 还原后窗口尺寸才有效
                try:
                    w.restore()
                    time.sleep(0.5)
                except Exception:
                    pass

            # 优先用客户区尺寸（真实渲染分辨率）
            try:
                client = _get_client_size(w._hWnd)
                if client and client[0] > 0 and client[1] > 0:
                    return client
            except Exception:
                pass
            return w.width, w.height
    except Exception as e:
        print(f"[图像] 窗口检测异常: {e}")

    # 未找到 → 打印可见窗口标题，便于排查匹配问题
    try:
        all_wins = [x.title for x in gw.getAllWindows() if x.title.strip()]
        print(f"[图像] 未找到标题含「{title_key}」的窗口，"
              f"当前可见窗口: {all_wins[:10]}")
    except Exception:
        pass
    return None, None


def init_image_scale(window_title='战双帕弥什'):
    """启动时检测游戏窗口分辨率，计算模板缩放系数。

    若找到游戏窗口则以窗口尺寸为基准，找不到则退回全屏尺寸。
    分辨率与参考分辨率一致时系数为 1.0（不缩放）。
    """
    global _scale_x, _scale_y

    # 手动指定游戏窗口尺寸（自动检测失败时可直接设置，如 MANUAL_WINDOW_SIZE = (1920, 1200)）
    if MANUAL_WINDOW_SIZE:
        cur_w, cur_h = MANUAL_WINDOW_SIZE
        source = '手动指定'
    else:
        # 优先用游戏窗口尺寸
        cur_w, cur_h = _find_game_window(window_title)
        source = '游戏窗口' if cur_w else None

    # 窗口未找到或尺寸异常（如最小化时接近 0）→ 退回全屏尺寸
    min_valid = 640   # 小于此宽度视为无效窗口（最小化/误检测）
    if not cur_w or cur_w < min_valid:
        source = '屏幕(未找到游戏窗口)'
        cur_w = cur_h = None
        try:
            cur_w, cur_h = pyautogui.size()
        except Exception:
            _scale_x = _scale_y = 1.0
            print("[图像] 无法检测窗口，缩放系数保持 1.0")
            return

    raw_x = cur_w / REFERENCE_WIDTH
    raw_y = cur_h / REFERENCE_HEIGHT

    # 强制等比缩放：窗口外框含标题栏/边框，两轴原始比例会不一致，
    # 模板若用 x/y 两个不同系数缩放会变形导致匹配失败。
    # 以宽度为基准（横向边框最薄，最接近真实渲染分辨率）。
    _scale_x = _scale_y = raw_x

    # 接近 1.0 时归为 1.0，避免不必要的图片缩放
    if abs(_scale_x - 1.0) < 0.01:
        _scale_x = _scale_y = 1.0

    # 两轴原始比例差异过大说明非参考宽高比（16:10），等比按宽度可能仍不准
    if abs(raw_y - raw_x) / raw_x > 0.03:
        print(f"[图像] 提示：窗口宽高比与参考差异较大"
              f"(x={raw_x:.3f} y={raw_y:.3f})，若非全屏请确认游戏渲染分辨率")

    # 超出合理范围则回退为不缩放并提示（可能不是游戏全屏）
    if not (_MIN_SCALE <= _scale_x <= _MAX_SCALE):
        _scale_x = _scale_y = 1.0
        print(f"[图像] 检测分辨率 {cur_w}x{cur_h} 偏离参考过大，"
              f"本次不缩放（请确认游戏窗口尺寸正常）")
        return

    print(f"[图像] 使用{source} {cur_w}x{cur_h}，"
          f"等比缩放系数 {_scale_x:.3f}"
          f"（参考 {REFERENCE_WIDTH}x{REFERENCE_HEIGHT}）")


def _scaled_template(pil_img):
    """按全局缩放系数放大/缩小模板图片"""
    global _scale_x, _scale_y
    if _scale_x == 1.0 and _scale_y == 1.0:
        return pil_img
    new_w = max(1, round(pil_img.width * _scale_x))
    new_h = max(1, round(pil_img.height * _scale_y))
    return pil_img.resize((new_w, new_h), Image.LANCZOS)


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
            # 根据当前窗口分辨率缩放模板，再交给屏幕匹配
            pil_img = _scaled_template(pil_img)
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
