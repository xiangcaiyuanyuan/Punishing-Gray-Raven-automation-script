import pyautogui
import time
import sys
import os
import json
import threading
import traceback
from pynput import keyboard as kb_listener
from tasks.task_modules import TASK_MODULES
from core.window import StatusWindow
from core.executor import execute_task
from utils.helpers import find_image
from utils.logger import get_logger

logger = get_logger()

pyautogui.PAUSE = 1
pyautogui.FAILSAFE = False

# 进度文件保存在 config 文件夹
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

PROGRESS_FILE = os.path.normpath(os.path.join(base_dir, 'config', 'progress.json'))


def pause_monitor(window, pause_images):
    """监控暂停状态，检测 loading 画面时暂停任务"""

    consecutive_loading = 0
    consecutive_normal = 0
    threshold = 2

    while not window.is_interrupted:
        try:
            is_loading = any(find_image(img) is not None for img in pause_images)

            if is_loading:
                consecutive_loading += 1
                consecutive_normal = 0

                if consecutive_loading >= threshold and not window.is_paused:
                    window.is_paused = True
                    window.pause_event.clear()
            else:
                consecutive_normal += 1
                consecutive_loading = 0

                if consecutive_normal >= threshold and window.is_paused:
                    window.is_paused = False
                    window.pause_event.set()

        except pyautogui.ImageNotFoundException:
            consecutive_loading = 0
        except Exception as e:
            pass

        time.sleep(0.1)


def run_automation(window, module_key='日常任务', start_index=0):
    """执行自动化任务"""
    pause_image = ['加载中', '升级']
    monitor_thread = threading.Thread(target=pause_monitor, args=(window, pause_image), daemon=True)
    monitor_thread.start()

    try:
        module_info = TASK_MODULES.get(module_key, TASK_MODULES['日常任务'])
        module_name = module_info['name']
        tasks = module_info['tasks']

        logger.debug(f"run_automation 接收到的 module_key: {module_key}")
        logger.debug(f"解析后的 module_name: {module_name}")

        window.root.after(0, lambda: window.update_status(f"✅ 正在运行: {module_name}"))

        if not tasks:
            window.root.after(0, lambda: window.show_failed(f"模块 '{module_name}' 的任务尚未配置"))
            return

        logger.info(f"========== 开始执行 {module_name} ==========")
        logger.info(f"总任务数: {len(tasks)}")
        logger.info(f"起始索引: {start_index}")
        logger.info(f"进度文件路径: {PROGRESS_FILE}")

        for i in range(start_index, len(tasks)):
            if window.check_interrupt():
                logger.warning(f"在步骤 {i + 1} 被用户中断")
                logger.debug(f"保存进度 - module_key: {module_key}, index: {i}")
                save_progress(module_key, i, is_completed=False)
                window.root.after(0, lambda: window.show_interrupted())
                return

            task = tasks[i]
            task_desc = get_task_description(task, i)

            logger.info(f"步骤 {i + 1}/{len(tasks)}: {task_desc}")
            logger.debug(f"任务详情: {task}")
            window.root.after(0,
                              lambda idx=i + 1, desc=task_desc: window.update_status(f" {desc} ({idx}/{len(tasks)})"))

            success = execute_task(task, window, should_exit=False)

            if success:
                logger.info(f"步骤 {i + 1} 执行完成")
                if task.get('type') != 'loop':
                    logger.debug(f"保存进度 - module_key: {module_key}, index: {i}")
                    save_progress(module_key, i, is_completed=True)
                else:
                    logger.debug("loop任务完成，不保存进度")
            else:
                logger.error(f"步骤 {i + 1} 执行失败")
                logger.debug(f"任务详情: {task}")
                logger.debug(f"保存进度 - module_key: {module_key}, index: {i}")
                save_progress(module_key, i, is_completed=False)
                window.root.after(0, lambda t=task, d=task_desc: window.show_failed(
                    f"步骤 {i + 1}/{len(tasks)} 执行失败\n"
                    f"任务描述: {d}\n"
                    f"任务详情: {t}"
                ))
                return

        if not window.check_interrupt():
            logger.info(f"========== {module_name} 执行完成 ==========")
            if os.path.exists(PROGRESS_FILE):
                os.remove(PROGRESS_FILE)
            window.root.after(0, window.show_completed)
        elif tasks and tasks[-1].get('type') == 'loop':
            logger.info(f"========== {module_name} 循环任务被中断 ==========")
            if os.path.exists(PROGRESS_FILE):
                os.remove(PROGRESS_FILE)
            window.root.after(0, window.show_completed)

    except Exception as e:
        logger.error(f"发生未知错误: {e}")
        traceback.print_exc()
        error_msg = str(e)
        window.root.after(0, lambda msg=error_msg: window.show_failed(f"发生未知错误：{msg}"))


def save_progress(module_key, index, is_completed=False):
    """保存当前进度到 JSON 文件"""
    data = {
        'module': module_key,
        'index': index,
        'completed': is_completed,
        'timestamp': time.time()
    }
    try:
        progress_dir = os.path.dirname(PROGRESS_FILE)
        os.makedirs(progress_dir, exist_ok=True)
        logger.debug(f"准备保存 - module: {module_key}, index: {index}, completed: {is_completed}")
        logger.info(f"保存进度到: {PROGRESS_FILE}")
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.debug("进度保存成功")
    except Exception as e:
        logger.error(f"保存进度失败: {e}")
        traceback.print_exc()


def get_task_description(task, index):
    """获取任务的描述信息"""
    if isinstance(task, dict):
        task_type = task.get('type', 'click')

        if task_type == 'click':
            img = task.get('image', 'unknown')
            clicks = task.get('clicks', 1)
            return f"点击 [{img}] x{clicks}"
        elif task_type == 'key_press':
            key = task.get('key', 'esc')
            times = task.get('press_times', 1)
            return f"按键 [{key}] x{times}"
        elif task_type == 'offset_click':
            img = task.get('image', 'unknown')
            offset_x = task.get('offset_x', 0)
            offset_y = task.get('offset_y', 0)
            return f"偏移点击 [{img}] (+{offset_x},+{offset_y})"
        elif task_type == 'move':
            return "移动角色"
        elif task_type == 'choice':
            options = task.get('options', [])
            return f"选择分支 ({len(options)}个选项)"
        elif task_type == 'combo':
            sub_tasks = task.get('tasks', [])
            return f"组合任务 ({len(sub_tasks)}个子任务)"
        elif task_type == 'scroll':
            amount = task.get('amount', 0)
            img = task.get('image', '')
            return f"滚动 {amount} (目标: {img or '当前位置'})"
        elif task_type == 'check':
            img = task.get('image', 'unknown')
            return f"检测 [{img}]"
        elif task_type == 'wait':
            img = task.get('image', 'unknown')
            timeout = task.get('timeout', 30)
            return f"等待 [{img}] (超时{timeout}秒)"
        elif task_type == 'key_press_until_image':
            key = task.get('key', 'f')
            target = task.get('target_image', '?')
            return f"按键 [{key}] 直到 [{target}] 出现"
        else:
            return f"未知任务类型: {task_type}"
    elif isinstance(task, list):
        return f"多选一 ({len(task)}个候选)"
    else:
        return f"步骤 {index + 1}"


if __name__ == '__main__':
    status_window = StatusWindow()
    status_window._alt_pressed = False

    # 初始化pause_event
    status_window.pause_event = threading.Event()
    status_window.pause_event.set()


    def on_press(key):
        try:
            if key == kb_listener.Key.alt_l or key == kb_listener.Key.alt_r:
                status_window._alt_pressed = True
            elif status_window._alt_pressed:
                if hasattr(key, 'char') and key.char == 'e':
                    if not status_window.check_interrupt() and status_window.is_running:
                        status_window.is_interrupted = True
                        logger.warning("收到 Alt+E 信号，等待当前步骤完成后停止...")
                status_window._alt_pressed = False
        except Exception as e:
            logger.error(f"键盘监听异常: {e}")


    def on_release(key):
        try:
            if key == kb_listener.Key.alt_l or key == kb_listener.Key.alt_r:
                status_window._alt_pressed = False
        except Exception as e:
            logger.error(f"键盘释放监听异常: {e}")


    listener = kb_listener.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    status_window.root.mainloop()
    listener.stop()