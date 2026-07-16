import time

from KyrieAuto.src.utils.helpers import *
time.sleep(2)
temp = find_image("奖励")
print(temp)
pyautogui.click(temp)