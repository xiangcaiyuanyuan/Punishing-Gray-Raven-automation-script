import time

import pyautogui

from KyrieAuto.src.utils.helpers import *
from KyrieAuto.src.core.executor import *
from src.core.task_builder import TaskBuilder
pyautogui.PAUSE = 2
time.sleep(2)
t=0
while t<13:
    pyautogui.click(575,645),
    pyautogui.click(2260,1490),
    TaskBuilder.wait(r'D:\PythonProject\KyrieAuto\tests\img.png')
    TaskBuilder.click(r'D:\PythonProject\KyrieAuto\tests\img.png')
    t=t+1
