import tkinter as tk
from tkinter import ttk, messagebox
import time
import sys
import os
import json
import pyautogui
import pygetwindow as gw

WINDOW_WIDTH = 460
WINDOW_HEIGHT = 340

# ── 配色方案 - 简约清新 ──
COLORS = {
    'bg': '#f5f7fa',            # 页面背景 - 极浅灰蓝
    'card_bg': '#ffffff',       # 卡片背景 - 纯白
    'border': '#e8ecf1',        # 边框 - 浅灰
    'fg': '#2d3436',            # 主文字 - 深灰
    'text_secondary': '#94a3b0', # 辅助文字 - 中灰
    'accent': '#5b8def',        # 主题色 - 清爽蓝
    'accent_hover': '#4a7de0',  # 主题悬浮 - 深一点蓝
    'accent_light': '#edf2ff',  # 主题浅色背景
    'success': '#00b894',       # 成功 - 薄荷绿
    'error': '#ff7675',         # 错误 - 珊瑚红
    'disabled_bg': '#f1f3f5',
    'disabled_fg': '#c8cfd6',
}


def get_progress_file_path():
    """获取进度文件的绝对路径，兼容开发环境和exe打包环境"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(current_dir)
    return os.path.normpath(os.path.join(base_dir, 'config', 'progress.json'))


def _get_icon_path():
    """获取窗口图标的路径，兼容开发和 exe 打包环境"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后：图标在 _MEIPASS 根目录（由 spec 的 datas 打包）
        base = sys._MEIPASS
    else:
        # 开发环境：icon.ico 在 src/ 目录（window.py 上一级）
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate = os.path.join(base, 'icon.ico')
    return candidate if os.path.exists(candidate) else None


class StatusWindow:
    """状态窗口类 - 简约清新风格"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kyrie")
        self.root.configure(bg=COLORS['bg'])

        try:
            icon_path = _get_icon_path()
            if icon_path and os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self._center_and_resize(self.root, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)

        self._setup_styles()

        self.selected_module = '日常任务'
        self.start_index = 0
        self.is_interrupted = False
        self.is_running = False
        self.is_paused = False
        self.pause_event = None

        self._create_widgets()

    # ── 样式 ──

    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure('.',
                        background=COLORS['bg'],
                        foreground=COLORS['fg'],
                        font=('Microsoft YaHei', 10))

        # 模块选择 - 简约标签式
        style.configure('Module.TRadiobutton',
                        font=('Microsoft YaHei', 10),
                        background=COLORS['card_bg'],
                        foreground=COLORS['text_secondary'],
                        indicatorrelief='flat',
                        indicatormargin=0,
                        padding=(10, 6))
        style.map('Module.TRadiobutton',
                  background=[('selected', COLORS['accent_light']),
                              ('active', '#f8faff')],
                  foreground=[('selected', COLORS['accent']),
                              ('active', COLORS['accent'])])

        # 进度条 - 细线风格
        style.configure('Active.Horizontal.TProgressbar',
                        background=COLORS['accent'],
                        troughcolor=COLORS['border'],
                        bordercolor=COLORS['border'],
                        lightcolor=COLORS['accent'],
                        darkcolor=COLORS['accent'],
                        thickness=6)

    def _flat_btn(self, btn, bg, fg, active_bg=None, active_fg=None):
        """统一扁平按钮样式"""
        btn.configure(bg=bg, fg=fg,
                      activebackground=active_bg or bg,
                      activeforeground=active_fg or fg,
                      relief='flat', bd=0, cursor='hand2')
        return btn

    # ── 窗口辅助 ──

    def _center_and_resize(self, window, width, height):
        screen_w = window.winfo_screenwidth()
        screen_h = window.winfo_screenheight()
        x = screen_w // 2 - width // 2
        y = screen_h // 2 - height // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _sep(self, parent):
        """极细分割线"""
        tk.Frame(parent, height=1, bg=COLORS['border']).pack(fill=tk.X, pady=10)

    # ── 控件构建 ──

    def _create_widgets(self):
        # 主容器 - 给左右留白
        root_frame = tk.Frame(self.root, bg=COLORS['bg'])
        root_frame.pack(fill=tk.BOTH, expand=True, padx=28, pady=(18, 20))

        # ═══ 标题 ═══
        tk.Label(root_frame,
                 text="干爆战双帕尼尼",
                 font=('Microsoft YaHei', 15, 'bold'),
                 fg=COLORS['fg'], bg=COLORS['bg']
                 ).pack(anchor=tk.W)

        tk.Label(root_frame,
                 text="自动化脚本 · 作者QQ:2976417128",
                 font=('Microsoft YaHei', 9),
                 fg=COLORS['text_secondary'], bg=COLORS['bg']
                 ).pack(anchor=tk.W, pady=(2, 0))

        self._sep(root_frame)

        # ═══ 模块选择 ═══
        sec = tk.Frame(root_frame, bg=COLORS['bg'])
        sec.pack(fill=tk.X)

        self.module_var = tk.StringVar(value='日常任务')

        from KyrieAuto.src.main import TASK_MODULES
        items = list(TASK_MODULES.items())
        n = len(items)
        rows = (n + 2) // 3

        # 白色卡片容器 - 带浅阴影效果
        card = tk.Frame(sec, bg=COLORS['card_bg'],
                        highlightbackground=COLORS['border'],
                        highlightthickness=1, padx=14, pady=10)
        card.pack(fill=tk.X)

        for idx, (key, info) in enumerate(items):
            r, c = idx // 3, idx % 3
            cell = tk.Frame(card, bg=COLORS['card_bg'], padx=3, pady=2)
            cell.grid(row=r, column=c, sticky='ew')

            ttk.Radiobutton(
                cell, text=info['name'],
                variable=self.module_var, value=key,
                command=self._on_module_change,
                style='Module.TRadiobutton'
            ).pack(fill=tk.X, padx=2, pady=1)

            card.columnconfigure(c, weight=1)

        # 动态高度
        extra = max(0, rows - 1) * 42
        new_h = WINDOW_HEIGHT + extra
        self._center_and_resize(self.root, WINDOW_WIDTH, new_h)

        # 提示：当前选中什么
        self.module_hint = tk.Label(sec,
                                     text="",
                                     font=('Microsoft YaHei', 8),
                                     fg=COLORS['text_secondary'],
                                     bg=COLORS['bg'])
        self.module_hint.pack(anchor=tk.W, pady=(4, 0))
        self._update_module_hint()

        self._sep(root_frame)

        # ═══ 启动按钮 ═══
        btn_box = tk.Frame(root_frame, bg=COLORS['bg'])
        btn_box.pack(fill=tk.X, pady=(2, 4))

        self.start_button = tk.Button(
            btn_box,
            text="开 始 运 行",
            command=self.start_script,
            font=('Microsoft YaHei', 11, 'bold'),
            padx=24, pady=7, border=0
        )
        self._flat_btn(self.start_button,
                        bg=COLORS['accent'], fg='#ffffff',
                        active_bg=COLORS['accent_hover'], active_fg='#ffffff')
        self.start_button.pack()

        self.start_button.bind('<Enter>', lambda e: self._on_start_enter())
        self.start_button.bind('<Leave>', lambda e: self._on_start_leave())

        # ═══ 状态显示 ═══
        status_section = tk.Frame(root_frame, bg=COLORS['bg'])
        status_section.pack(fill=tk.X, pady=(4, 2))

        # 状态标签行
        status_header = tk.Frame(status_section, bg=COLORS['bg'])
        status_header.pack(fill=tk.X, pady=(0, 5))

        # 指示灯 ↻
        self.status_dot = tk.Label(status_header, text="○",
                                    font=('Microsoft YaHei', 7),
                                    fg=COLORS['text_secondary'],
                                    bg=COLORS['bg'])
        self.status_dot.pack(side=tk.LEFT, padx=(0, 4))

        tk.Label(status_header,
                 text="状态",
                 font=('Microsoft YaHei', 9, 'bold'),
                 fg=COLORS['text_secondary'],
                 bg=COLORS['bg']).pack(side=tk.LEFT)

        # 状态文本
        self.status_label = tk.Label(
            status_section,
            text="等待启动",
            font=('Microsoft YaHei', 11),
            fg=COLORS['text_secondary'],
            bg=COLORS['card_bg'],
            anchor=tk.W, padx=14, pady=7
        )
        self.status_label.pack(fill=tk.X)

        # ═══ 进度条 ═══
        self.progress = ttk.Progressbar(
            root_frame,
            mode='indeterminate',
            style='Active.Horizontal.TProgressbar'
        )
        self.progress.pack(fill=tk.X, pady=(8, 6))

        # ═══ 底部提示 ═══
        tk.Label(root_frame,
                 text="Alt + E  可中断运行",
                 font=('Microsoft YaHei', 8),
                 fg=COLORS['text_secondary'],
                 bg=COLORS['bg']
                 ).pack(side=tk.BOTTOM, pady=(4, 0))

    # ── 模块提示 ──

    def _update_module_hint(self):
        from KyrieAuto.src.main import TASK_MODULES
        info = TASK_MODULES.get(self.selected_module, {})
        name = info.get('name', self.selected_module)
        self.module_hint.config(text=f"当前选择：{name}")

    # ── 按钮 Hover ──

    def _on_start_enter(self):
        if self.start_button['state'] != 'disabled':
            self.start_button.configure(bg=COLORS['accent_hover'])

    def _on_start_leave(self):
        if self.start_button['state'] != 'disabled':
            self.start_button.configure(bg=COLORS['accent'])

    # ── 模块切换 ──

    def _on_module_change(self):
        old = self.selected_module
        self.selected_module = self.module_var.get()
        self._update_module_hint()
        print(f"[调试] 模块切换: {old} -> {self.selected_module}")
        pf = get_progress_file_path()
        if not os.path.exists(pf):
            self.start_index = 0

    # ── 启动 ──

    def start_script(self):
        if self.is_running:
            return

        print(f"[调试] 点击开始按钮，当前选择模块: {self.selected_module}")

        self.is_interrupted = False
        self.start_index = 0
        pf = get_progress_file_path()

        print(f"[调试] 检查进度文件: {pf}")
        print(f"[调试] 文件是否存在: {os.path.exists(pf)}")

        if os.path.exists(pf):
            try:
                with open(pf, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                sm = saved.get('module')
                si = saved.get('index', 0)
                print(f"[调试] 读取到的数据: module={sm}, index={si}")

                if sm == self.selected_module and si > 0:
                    resp = messagebox.askyesno(
                        "发现未完成流程",
                        f"检测到上次中断在第 {si + 1} 步。\n是否尝试从中断处继续？"
                    )
                    if resp:
                        self.start_index = si
                        print(f"[调试] 从第 {si + 1} 步继续执行")
                    else:
                        os.remove(pf)
                        print(f"[调试] 用户选择重新开始，删除进度文件")
                else:
                    print(f"[调试] 模块不匹配或索引为0，不恢复进度")
            except Exception as e:
                print(f"[调试] 读取进度文件失败: {e}")

        self.is_running = True
        self.start_button.config(state='disabled',
                                  bg=COLORS['disabled_bg'],
                                  fg=COLORS['disabled_fg'],
                                  text='运 行 中 ...')
        self.show_running()
        self.root.after(500, self._start_automation)

    def _start_automation(self):
        self.root.iconify()
        time.sleep(0.5)

        try:
            win = gw.getWindowsWithTitle('战双帕弥什')
            if win:
                win[0].activate()
                time.sleep(0.5)
            else:
                pyautogui.click(pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)
        except Exception:
            pyautogui.click(pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)

        time.sleep(1)

        print(f"[调试] _start_automation 调用 run_automation，传递 module: {self.selected_module}")
        from KyrieAuto.src.main import run_automation
        run_automation(self, self.selected_module, self.start_index)

    # ── 状态更新 ──

    def update_status(self, status):
        self.status_label.config(text=status)

    def start_progress(self):
        self.progress.start(10)

    def stop_progress(self):
        self.progress.stop()

    def show_running(self):
        self.update_status("运行中 ...")
        self.status_dot.configure(text="●",
                                   fg=COLORS['success'])
        self.start_progress()
        self.root.update()

    # ── 结果弹窗 ──

    def _show_result_window(self, title, message, color, icon_text="", bg_light=""):
        self.stop_progress()
        self.status_dot.configure(text="○", fg=COLORS['text_secondary'])

        self.start_button.config(state='normal',
                                  bg=COLORS['accent'], fg='#ffffff',
                                  text='开 始 运 行')
        self.is_running = False
        self.update_status("等待启动")

        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

        mw = self.root.winfo_width()
        mh = self.root.winfo_height()
        if mw <= 1:
            mw = WINDOW_WIDTH
        if mh <= 1:
            mh = WINDOW_HEIGHT

        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg=COLORS['card_bg'])
        popup.resizable(False, False)
        popup.attributes('-topmost', True)

        # 结果窗口也使用同一图标
        try:
            ico = _get_icon_path()
            if ico:
                popup.iconbitmap(ico)
        except Exception:
            pass

        self._center_and_resize(popup, mw, mh)

        frame = tk.Frame(popup, bg=COLORS['card_bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=(28, 24))

        # 图标
        if icon_text:
            tk.Label(frame, text=icon_text,
                     font=('Segoe UI Emoji', 30),
                     fg=color, bg=COLORS['card_bg']).pack(pady=(0, 8))

        # 标题
        tk.Label(frame, text=title,
                 font=('Microsoft YaHei', 13, 'bold'),
                 fg=COLORS['fg'], bg=COLORS['card_bg']).pack(pady=(0, 8))

        # 消息
        tk.Label(frame, text=message,
                 font=('Microsoft YaHei', 10),
                 fg=COLORS['text_secondary'],
                 bg=COLORS['card_bg'],
                 wraplength=320, justify='left').pack(pady=4)

        tk.Label(frame, text="—",
                 font=('Microsoft YaHei', 9),
                 fg=COLORS['border'],
                 bg=COLORS['card_bg']).pack(pady=(10, 4))

        def _close():
            popup.destroy()

        ok_btn = tk.Button(frame, text="确 定", command=_close,
                            font=('Microsoft YaHei', 11, 'bold'),
                            padx=28, pady=5, border=0)
        self._flat_btn(ok_btn, bg=color, fg='#ffffff',
                        active_bg=color, active_fg='#ffffff')
        ok_btn.pack(pady=(2, 0))

        popup.protocol("WM_DELETE_WINDOW", _close)
        self.root.update()

    # ── 3 种结果 ──

    def show_interrupted(self):
        self._show_result_window("已中断",
                                 "按下了 Alt+E，程序已停止。",
                                 COLORS['error'], "⏸")

    def show_completed(self):
        pf = get_progress_file_path()
        if os.path.exists(pf):
            os.remove(pf)
        self._show_result_window("全部完成",
                                 "任务已成功执行完毕。",
                                 COLORS['success'], "✓")

    def show_failed(self, reason):
        self._show_result_window("执行失败",
                                 "日志详情请查看 exe 控制台窗口。",
                                 COLORS['error'], "✕")

    # ── 中断 / 暂停 ──

    def check_interrupt(self):
        return self.is_interrupted

    def wait_if_paused(self, timeout=15.0):
        if not self.pause_event:
            return

        if not self.pause_event.is_set():
            print("[等待] 检测到loading，等待游戏响应...")

        start = time.time()

        while not self.pause_event.is_set():
            elapsed = time.time() - start

            if elapsed > timeout:
                print(f"[警告] 等待超时({timeout}秒)，尝试ESC唤醒")

                old_pause = pyautogui.PAUSE
                pyautogui.PAUSE = 0
                try:
                    pyautogui.press('esc')
                    time.sleep(0.8)

                    from KyrieAuto.src.utils.helpers import find_image
                    still = any(find_image(img) is not None
                                for img in ['加载中', '升级'])

                    if not still:
                        print("[成功] ESC唤醒成功，恢复执行")
                        self.pause_event.set()
                        break
                    else:
                        print("[提示] 仍在loading，重置计时器继续等待...")
                        start = time.time()
                finally:
                    pyautogui.PAUSE = old_pause

            self.pause_event.wait(timeout=1.0)
