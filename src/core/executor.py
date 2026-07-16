import time
import random
import pyautogui
from utils.helpers import find_image

# 鼠标点击后偏移量（避免遮挡识别区域）
MOVE_OFFSET = 20
# 点击位置随机噪声范围（±px，模拟人类点击防止脚本检测）
CLICK_NOISE = 5


def execute_mouse_action(img_name, click_times=1, interval=1, offset_x=0, offset_y=0,
                         window=None, should_exit=True, noise=CLICK_NOISE):
    """执行鼠标操作"""
    if window:
        window.wait_if_paused()

    address = find_image(img_name)
    if address:
        center_x = address.left + address.width // 2
        center_y = address.top + address.height // 2

        # 基础偏移 + 随机噪声（模拟真实人类点击）
        target_x = center_x + offset_x + random.randint(-noise, noise)
        target_y = center_y + offset_y + random.randint(-noise, noise)

        if click_times >= 0:
            # 一步到位：移动到目标并点击（不单独调用 moveTo）
            pyautogui.click(target_x, target_y, clicks=click_times, interval=interval)
            pyautogui.moveRel(MOVE_OFFSET, MOVE_OFFSET)
        return True

    if window and should_exit:
        window.root.after(0, lambda: window.show_failed(f"未检索到图片: {img_name}"))
    return False


def execute_click(imgs, click_times=1, window=None, should_exit=True):
    """执行点击操作"""
    if window:
        window.wait_if_paused()

    img_list = imgs if isinstance(imgs, list) else [imgs]

    for img in img_list:
        if execute_mouse_action(img, click_times=click_times, window=window, should_exit=False):
            return True

    if window and should_exit:
        window.root.after(0, lambda: window.show_failed(f"未检索到图片: {img_list[0]}"))
    return False


def execute_key_press(key, press_times=1, interval=1, window=None, should_exit=True):
    """执行按键操作"""
    if window:
        window.wait_if_paused()

    if isinstance(key, list):
        key_list = [str(k).strip().lower() for k in key]
        old_pause = pyautogui.PAUSE
        pyautogui.PAUSE = 0
        try:
            pyautogui.hotkey(*key_list)
        finally:
            pyautogui.PAUSE = old_pause
    else:
        pyautogui.press(key, presses=press_times, interval=interval)
    return True


def execute_offset_click(img_name, click_times=1, offset_x=0, offset_y=0, window=None, should_exit=True):
    """执行偏移点击"""
    return execute_mouse_action(
        img_name,
        click_times=click_times,
        offset_x=offset_x,
        offset_y=offset_y,
        window=window,
        should_exit=should_exit
    )


def move_character(time_a, time_w, time_d, time_s):
    """移动角色"""
    def move(key, seconds):
        if seconds <= 0:
            return
        old_pause = pyautogui.PAUSE
        pyautogui.PAUSE = 0
        try:
            pyautogui.keyDown(key)
            time.sleep(seconds)
            pyautogui.keyUp(key)
        finally:
            pyautogui.PAUSE = old_pause

    move('a', time_a)
    move('w', time_w)
    move('d', time_d)
    move('s', time_s)


def execute_scroll(amount, img_name=None, window=None, should_exit=True):
    """执行滚动操作"""
    if window:
        window.wait_if_paused()

    if img_name:
        address = find_image(img_name)
        if address:
            center_x = address.left + address.width // 2
            center_y = address.top + address.height // 2

            old_pause = pyautogui.PAUSE
            pyautogui.PAUSE = 0
            try:
                pyautogui.moveTo(center_x, center_y, duration=0)
            finally:
                pyautogui.PAUSE = old_pause
        else:
            if window and should_exit:
                window.root.after(0, lambda: window.show_failed(f"未检索到图片: {img_name}"))
            return False

    step = 50
    remaining = amount

    old_pause = pyautogui.PAUSE
    pyautogui.PAUSE = 0.1
    try:
        while abs(remaining) >= step:
            pyautogui.scroll(step if remaining > 0 else -step)
            remaining -= step if remaining > 0 else -step
        if remaining != 0:
            pyautogui.scroll(remaining)
    finally:
        pyautogui.PAUSE = old_pause

    return True


def execute_task(task, window, should_exit=True):
    """执行单个任务"""
    if task is None:
        return True

    if window and window.check_interrupt():
        return False

    if isinstance(task, dict):
        task_type = task.get('type', 'click')

        if task_type == 'reset_menu':
            max_attempts = 20
            for _ in range(max_attempts):
                if window.check_interrupt():
                    return False
                if find_image('活动'):
                    return True
                pyautogui.press('esc')
            return True

        elif task_type == 'click':
            return execute_mouse_action(
                task['image'],
                click_times=task.get('clicks', 1),
                interval=task.get('interval', 1),
                window=window,
                should_exit=should_exit
            )

        elif task_type == 'key_press':
            return execute_key_press(
                task.get('key', 'esc'),
                task.get('press_times', 1),
                task.get('interval', 1),
                window,
                should_exit
            )

        elif task_type == 'offset_click':
            return execute_offset_click(
                task['image'],
                task.get('clicks', 1),
                task.get('offset_x', 0),
                task.get('offset_y', 0),
                window,
                should_exit
            )

        elif task_type == 'move':
            for action in task['actions']:
                img_name, t_a, t_w, t_d, t_s = action
                if find_image(img_name):
                    move_character(t_a, t_w, t_d, t_s)
                    return True
            return False

        elif task_type == 'choice':
            options = task.get('options', [])
            for option in options:
                if execute_task(option, window, should_exit=False):
                    return True
            print(f"[提示] 选择分支的所有选项均未匹配,跳过此步骤")
            return True

        elif task_type == 'combo':
            for sub_task in task.get('tasks', []):
                if not execute_task(sub_task, window, should_exit):
                    return False
            return True

        elif task_type == 'scroll':
            return execute_scroll(
                task.get('amount', 0),
                task.get('image', None),
                window,
                should_exit
            )

        elif task_type == 'check':
            images = task.get('images', [])
            found = False
            for img in images:
                if find_image(img):
                    found = True
                    break
            if found:
                return execute_task(task.get('success'), window, should_exit)
            else:
                return execute_task(task.get('fail'), window, should_exit)

        elif task_type == 'wait':

            img_name = task.get('image')
            timeout = task.get('timeout', 60)
            interval = task.get('interval', 0.5)
            fail_on_timeout = task.get('fail_on_timeout', True)

            # image 不是字符串（None / 数字等）→ 纯延时等待
            if not isinstance(img_name, str):
                time.sleep(timeout)
                return True

            start_time = time.time()

            while time.time() - start_time < timeout:

                if window and window.check_interrupt():
                    return False

                if window:
                    window.wait_if_paused()

                if find_image(img_name):
                    return True

                time.sleep(interval)

            if fail_on_timeout:
                if should_exit and window:
                    error_msg = f"等待图片超时: {img_name} (超时{timeout}秒)"
                    window.root.after(0, lambda msg=error_msg: window.show_failed(msg))
                return False
            else:
                print(f"[提示] 等待图片超时: {img_name} (超时{timeout}秒)，继续执行")
                return True

        elif task_type == 'key_press_until_image':
            key = task.get('key', 'f')
            target = task.get('target_image')
            interval = task.get('interval', 0.5)
            pyautogui.PAUSE = 0
            while True:
                if window and window.check_interrupt():
                    return True
                if window:
                    window.wait_if_paused()

                if find_image(target):
                    pyautogui.PAUSE = 1
                    return True

                # 按一次键后等待 interval
                pyautogui.press(key)
                time.sleep(interval)

        elif task_type == 'loop':
            loop_task = task.get('task')
            if not loop_task:
                return True

            while True:
                if window and window.check_interrupt():
                    return True

                if not execute_task(loop_task, window, should_exit=False):
                    if window and window.check_interrupt():
                        return True
                    return False

        else:
            print(f"未知任务类型: {task_type}")
            return False

    elif isinstance(task, list):
        for sub_task in task:
            if window and window.check_interrupt():
                return False
            if execute_task(sub_task, window, should_exit=False):
                return True

        if should_exit and window:
            first_item = task[0]
            first_name = first_item.get('image', 'unknown') if isinstance(first_item, dict) else (
                first_item[0] if isinstance(first_item, tuple) else first_item
            )
            error_msg = f"未检索到图片: {first_name}"
            window.root.after(0, lambda msg=error_msg: window.show_failed(msg))
        return False

    else:
        print(f"无效任务格式: {type(task)}")
        return False