"""
按键时长监听器(优化版)
功能: 监听按键从按下到抬起的持续时间
依赖: pip install pynput
"""

import time
import threading
from typing import Callable, Optional, Dict, List
from pynput import keyboard


class KeyDurationListener:
    """按键时长监听器类"""

    def __init__(self, callback: Optional[Callable[[str, float], None]] = None):
        """
        初始化监听器

        Args:
            callback: 回调函数,接收参数 (按键名称, 持续时间秒)
                     例如: lambda key, duration: print(f"{key}: {duration:.3f}s")
        """
        self.callback = callback or self._default_callback
        self.key_press_times: Dict[str, float] = {}
        self.key_press_count: Dict[str, int] = {}  # 记录按键按下次数
        self.listener: Optional[keyboard.Listener] = None
        self.is_listening = False
        self._lock = threading.Lock()
        self.results: List[dict] = []  # 存储所有结果

    def _default_callback(self, key_name: str, duration: float):
        """默认回调函数"""
        print(f"按键: {key_name:15} | 持续时间: {duration:.3f} 秒")

    def on_press(self, key: keyboard.Key):
        """按键按下事件"""
        try:
            key_name = key.char if hasattr(key, 'char') and key.char else key.name
        except AttributeError:
            key_name = str(key)

        with self._lock:
            current_time = time.perf_counter()  # 使用更高精度的计时器

            # 如果按键已经在按下状态,不更新时间(处理操作系统重复事件)
            if key_name not in self.key_press_times:
                self.key_press_times[key_name] = current_time
                self.key_press_count[key_name] = 1
            else:
                self.key_press_count[key_name] += 1

    def on_release(self, key: keyboard.Key):
        """按键释放事件"""
        try:
            key_name = key.char if hasattr(key, 'char') and key.char else key.name
        except AttributeError:
            key_name = str(key)

        with self._lock:
            if key_name in self.key_press_times:
                press_time = self.key_press_times.pop(key_name)
                release_time = time.perf_counter()  # 使用高精度计时器
                duration = release_time - press_time

                # 只在第一次按下和最后一次释放之间计算时间
                if key_name in self.key_press_count:
                    del self.key_press_count[key_name]

                # 记录结果
                result = {
                    'key': key_name,
                    'duration': duration,
                    'timestamp': time.time(),
                    'press_count': self.key_press_count.get(key_name, 0)
                }
                self.results.append(result)

                # 调用回调函数
                self.callback(key_name, duration)

                return duration
        return None

    def start(self, blocking: bool = False):
        """
        开始监听

        Args:
            blocking: 是否阻塞主线程,True为阻塞模式
        """
        if self.is_listening:
            print("监听器已在运行")
            return

        self.is_listening = True
        self.results.clear()  # 清空之前的结果
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
            suppress=False  # 不阻止按键事件传递
        )
        self.listener.start()

        if blocking:
            try:
                self.listener.join()
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        """停止监听"""
        if self.listener:
            self.listener.stop()
            self.is_listening = False
            print(f"监听器已停止,共记录 {len(self.results)} 次按键")

    def get_results(self) -> List[dict]:
        """获取所有记录的结果"""
        return self.results.copy()

    def clear_results(self):
        """清空结果"""
        with self._lock:
            self.results.clear()


def simple_key_duration_monitor(target_key: Optional[str] = None):
    """
    简单版按键时长监听函数

    Args:
        target_key: 目标按键名称,None表示监听所有按键

    Returns:
        list: 包含按键信息的字典列表
    """
    results = []

    def custom_callback(key_name: str, duration: float):
        if target_key is None or key_name == target_key:
            result = {'key': key_name, 'duration': duration}
            results.append(result)
            print(f"✓ 按键: {key_name:10} | 按住时间: {duration:.3f}秒")

    listener = KeyDurationListener(callback=custom_callback)

    print(f"开始监听{' [' + target_key + ']' if target_key else ''}按键...")
    print("按 ESC 键退出监听\n")

    def check_esc(key):
        """检查是否按下ESC键"""
        if key == keyboard.Key.esc:
            listener.stop()
            return False
        return True

    # 包装on_release以添加ESC检测
    original_release = listener.on_release
    def combined_release(key):
        original_release(key)
        return check_esc(key)

    listener.on_release = combined_release
    listener.start(blocking=True)

    return results


def measure_single_key(key_name: str = "space") -> float:
    """
    测量单次按键时长(阻塞式)

    Args:
        key_name: 要测量的按键名称,默认为空格键

    Returns:
        float: 按键持续时间(秒)
    """
    print(f"请按下 [{key_name}] 键并释放...")

    event = threading.Event()
    result = [None]

    def measure_callback(k: str, d: float):
        if k == key_name and result[0] is None:  # 只记录第一次
            result[0] = d
            event.set()

    listener = KeyDurationListener(callback=measure_callback)
    listener.start()

    # 等待测量完成
    event.wait()
    listener.stop()

    print(f"✓ [{key_name}] 按键时长: {result[0]:.3f} 秒")
    return result[0]


def test_long_press():
    """测试长按功能的辅助函数"""
    print("=" * 60)
    print("长按测试模式")
    print("=" * 60)
    print("请尝试以下操作:")
    print("1. 短按任意键(< 0.5秒)")
    print("2. 长按任意键(> 2秒)")
    print("3. 快速连续按键")
    print("4. 按住不放然后释放")
    print("\n按 ESC 结束测试\n")

    results = simple_key_duration_monitor()

    # 分析结果
    if results:
        print("\n" + "=" * 60)
        print("测试结果分析:")
        print("=" * 60)

        durations = [r['duration'] for r in results]
        print(f"总按键次数: {len(results)}")
        print(f"最短按键: {min(durations):.3f} 秒")
        print(f"最长按键: {max(durations):.3f} 秒")
        print(f"平均时长: {sum(durations)/len(durations):.3f} 秒")

        # 分类统计
        short_presses = sum(1 for d in durations if d < 0.5)
        long_presses = sum(1 for d in durations if d >= 0.5)
        print(f"\n短按 (< 0.5s): {short_presses} 次")
        print(f"长按 (>= 0.5s): {long_presses} 次")


# ========== 使用示例 ==========

if __name__ == "__main__":
    print("=" * 50)
    print("按键时长监听器 - 演示程序")
    print("=" * 50)
    print("\n请选择模式:")
    print("1. 监听所有按键")
    print("2. 只监听特定按键(如 space)")
    print("3. 测量单次按键")
    print("4. 长按测试模式(推荐)")
    print("=" * 50)

    choice = input("\n请输入选项 (1/2/3/4): ").strip()

    if choice == "1":
        # 模式1: 监听所有按键
        results = simple_key_duration_monitor()
        print(f"\n共记录了 {len(results)} 次按键")

    elif choice == "2":
        # 模式2: 监听特定按键
        target = input("请输入要监听的按键名称 (如 space, a, enter): ").strip()
        results = simple_key_duration_monitor(target_key=target)
        print(f"\n共记录了 {len(results)} 次 [{target}] 按键")

    elif choice == "3":
        # 模式3: 测量单次按键
        key = input("请输入要测量的按键名称 (默认 space): ").strip() or "space"
        duration = measure_single_key(key)

    elif choice == "4":
        # 模式4: 长按测试
        test_long_press()

    else:
        print("无效的选项!")
