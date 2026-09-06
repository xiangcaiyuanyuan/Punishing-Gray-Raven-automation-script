"""
实时复现 find_image 的完整路径，确认 locateOnScreen 在真实画面上能否匹配。
匹配成功后，在截图上用红框标出匹配区域并自动打开。

用法：游戏停在能看到目标按钮的画面，然后运行：
    D:\\python\\Scripts\\python.exe D:\\PythonProject\\KyrieAuto\\tests\\live_test_find.py
    可选参数：图片名（不含 .png），默认测试 血清_1
    例：live_test_find.py 活动
"""
import sys
import os
import time

sys.path.insert(0, r'D:\PythonProject\KyrieAuto\src')

import pyautogui
from PIL import Image, ImageDraw
import numpy as np

import utils.helpers as helpers

# 目标图片（命令行参数，默认 血清_1）
img_name = sys.argv[1] if len(sys.argv) > 1 else '情报'
if '.' not in img_name:
    img_name += '.png'

print(f"3 秒后开始检测 [{img_name}]，请确保游戏前台并显示该按钮...")
time.sleep(1)

helpers.init_image_scale()
print(f"自动缩放系数: {helpers._scale_x:.4f}")

tpl = Image.open(helpers.resource_path(os.path.join('data', 'imgs', img_name)))
scaled = helpers._scaled_template(tpl)
np_tpl = np.array(scaled)
print(f"模板缩放后: {scaled.width}x{scaled.height}  阈值: {helpers.CONFIDENCE_THRESHOLD}")

found_box = None  # 记录最终命中的区域，用于画框

# ===== 路径1：完全模拟 find_image（实时 locateOnScreen）=====
try:
    res = pyautogui.locateOnScreen(np_tpl, confidence=helpers.CONFIDENCE_THRESHOLD)
    if res:
        print(f"路径1 locateOnScreen(实时): ✅ @{res.left},{res.top} 尺寸{res.width}x{res.height}")
        found_box = found_box or res
    else:
        print("路径1 locateOnScreen(实时): ❌ 未找到")
except pyautogui.ImageNotFoundException:
    print("路径1 locateOnScreen(实时): ❌ 未找到(异常)")

# ===== 路径2：先手动截图再 locate（对比实时与离线）=====
shot = pyautogui.screenshot()
shot_np = np.array(shot)
try:
    res2 = pyautogui.locate(np_tpl, shot_np, confidence=helpers.CONFIDENCE_THRESHOLD)
    if res2:
        print(f"路径2 先截图再locate:      ✅ @{res2.left},{res2.top} 尺寸{res2.width}x{res2.height}")
        found_box = found_box or res2   # 路径2直接对应 shot，优先用它画框
    else:
        print("路径2 先截图再locate:      ❌ 未找到")
except pyautogui.ImageNotFoundException:
    print("路径2 先截图再locate:      ❌ 未找到(异常)")

# ===== 框出匹配区域并保存/打开 =====
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug_live.png')
if found_box is not None:
    draw = ImageDraw.Draw(shot)
    box = found_box
    # 画一个显眼的红色方框（线宽 6），外加浅色底边角更清晰
    l, t = box.left, box.top
    r_, b = box.left + box.width, box.top + box.height
    draw.rectangle([l, t, r_, b], outline='red', width=6)
    draw.rectangle([l, t, r_, b], outline='yellow', width=2)  # 内层细线增强对比
    print(f"已在截图 ({l},{t})-({r_},{b}) 处画框")
else:
    print("未匹配到任何区域，无法画框")

shot.save(out_path)
print(f"已保存到 {out_path}")
