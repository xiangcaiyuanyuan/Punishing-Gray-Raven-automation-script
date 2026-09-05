import time

import pyautogui

from KyrieAuto.src.utils.helpers import *
from KyrieAuto.src.core.executor import *
from src.core.task_builder import TaskBuilder
pyautogui.PAUSE = 2
time.sleep(2)
# TaskBuilder.offset_click('战略',offset_x=0,offset_y=100)

result = find_image('战略')   # 或传列表 ['公会', '签到']

if result:
    # 方法1：属性访问
    x, y = result.left, result.top
    w, h = result.width, result.height

    # 计算中心点
    center_x = result.left + result.width // 2
    center_y = result.top + result.height // 2

    pyautogui.click(center_x,center_y+220)
else:
    print("未找到图片")

