import pyperclip
import time
import threading
import json
import os
import sys
from datetime import datetime
from pynput import mouse
from pynput.keyboard import Controller, Key
import tkinter as tk
from tkinter import ttk
import ctypes
from pystray import Icon, Menu, MenuItem
from PIL import Image

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

class ClipboardManager:
    def __init__(self, max_history=20):
        self.max_history = max_history
        self.clipboard_history = []
        self.last_clipboard = ""
        self.running = True
        self.keyboard = Controller()
        self.menu_window = None
        self.last_right_click_time = 0
        self.double_click_interval = 0.5
        self.previous_window = None  # 保存打开菜单前的窗口句柄
        self.tray_icon = None  # 系统托盘图标

        # 粘贴控制
        self.is_pasting = False  # 标记是否正在粘贴
        self.paste_lock = threading.Lock()  # 粘贴锁

        self.config_file = "clipboard_config.json"
        self.load_history()

        # 创建隐藏的主窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口

        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def load_history(self):
        """加载历史记录"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.clipboard_history = data.get('history', [])[:self.max_history]
            except:
                pass

    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({'history': self.clipboard_history}, f, ensure_ascii=False, indent=2)
        except:
            pass

    def monitor_clipboard(self):
        """监控剪贴板变化"""
        print("📋 剪贴板监控已启动...")
        while self.running:
            try:
                # 如果正在粘贴，跳过监控
                if self.is_pasting:
                    time.sleep(0.3)
                    continue

                current_clipboard = pyperclip.paste()

                if current_clipboard and current_clipboard != self.last_clipboard:
                    if current_clipboard not in self.clipboard_history:
                        self.clipboard_history.insert(0, current_clipboard)

                        if len(self.clipboard_history) > self.max_history:
                            self.clipboard_history = self.clipboard_history[:self.max_history]

                        timestamp = datetime.now().strftime('%H:%M:%S')
                        preview = current_clipboard[:50].replace('\n', ' ')
                        if len(current_clipboard) > 50:
                            preview += "..."
                        print(f"[{timestamp}] 新增复制内容: {preview}")

                        self.save_history()

                    self.last_clipboard = current_clipboard

            except Exception as e:
                pass

            time.sleep(0.3)

    def has_text_selection(self):
        """检测是否有文字被选中"""
        try:
            # 保存当前剪贴板内容
            old_clipboard = pyperclip.paste()

            # 模拟Ctrl+C尝试复制选中内容
            VK_CONTROL = 0x11
            VK_C = 0x43
            KEYEVENTF_KEYUP = 0x0002

            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
            time.sleep(0.01)
            ctypes.windll.user32.keybd_event(VK_C, 0, 0, 0)
            time.sleep(0.01)
            ctypes.windll.user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

            # 等待剪贴板更新
            time.sleep(0.05)

            # 检查剪贴板是否变化
            new_clipboard = pyperclip.paste()
            has_selection = (new_clipboard != old_clipboard and len(new_clipboard.strip()) > 0)

            # 如果没有选中，恢复原剪贴板内容
            if not has_selection:
                pyperclip.copy(old_clipboard)

            return has_selection

        except:
            return False

    def is_in_editable_field(self):
        """检测当前焦点是否在可编辑的输入框中"""
        try:
            # 获取前台窗口
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return False

            # 获取主窗口类名
            main_class_name = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(hwnd, main_class_name, 256)
            main_class_name_str = main_class_name.value.lower()

            # 获取窗口标题
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            window_title = buff.value.lower()

            # 调试信息
            print(f"🔍 窗口标题: {window_title}")
            print(f"🔍 主窗口类名: {main_class_name_str}")

            # 明确排除的窗口类型（桌面、资源管理器等）
            excluded_classes = [
                'progman',              # 桌面程序管理器
                'workerw',              # 桌面工作窗口
                'shell_traywnd',        # 任务栏
                'cabinetwclass',        # Windows资源管理器
                'explorerframe',        # 资源管理器框架
                '#32768',               # 右键菜单
                'tooltips_class32',     # 工具提示
                'button',               # 按钮
            ]

            # 检查主窗口是否在排除列表中
            for excluded in excluded_classes:
                if excluded in main_class_name_str:
                    print(f"✗ 排除的窗口类型: {main_class_name_str}")
                    return False

            # 如果窗口标题为空或是"程序管理器"，很可能是桌面
            if not window_title or window_title == 'program manager' or window_title == '程序管理器':
                print(f"✗ 检测到桌面窗口")
                return False

            # 获取焦点控件
            focus_hwnd = ctypes.windll.user32.GetFocus()

            # 如果没有焦点控件，检查是否是特殊的编辑器窗口
            if not focus_hwnd:
                # 某些现代编辑器（如VSCode）焦点可能在主窗口
                # 只有明确是编辑器时才允许
                editable_titles = [
                    'visual studio code',
                    'vscode',
                    'notepad++',
                    'sublime text',
                    'atom',
                    'pycharm',
                    'webstorm',
                    'intellij idea',
                    'eclipse',
                    'android studio',
                    'notepad',  # 记事本
                    'word',     # Word
                ]

                for editable_title in editable_titles:
                    if editable_title in window_title:
                        print(f"✓ 通过窗口标题识别为编辑器: {editable_title}")
                        return True

                print(f"✗ 无焦点控件且非编辑器")
                return False

            # 获取焦点控件的类名
            class_name = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(focus_hwnd, class_name, 256)
            class_name_str = class_name.value.lower()

            print(f"🔍 焦点控件类名: {class_name_str}")

            # 明确的可编辑控件类名（严格匹配）
            editable_classes = [
                'edit',                 # 标准文本框
                'richedit',             # 富文本框
                'richedit20',           # 富文本框2.0
                'richedit50',           # 富文本框5.0
                'consolewindowclass',   # 命令行窗口
                'scintilla',            # Scintilla编辑器
                'txtwndclass',          # 某些文本编辑器
            ]

            # 精确匹配可编辑控件
            for editable_class in editable_classes:
                if editable_class == class_name_str or class_name_str.startswith(editable_class):
                    print(f"✓ 检测到可编辑控件: {class_name_str}")
                    return True

            # 检查是否是浏览器的输入框（需要更谨慎）
            # Chrome/Edge等浏览器的输入框通常有特殊标识
            if 'chrome' in class_name_str or 'chrome' in main_class_name_str:
                # 只有当光标类型是文本光标时才认为是输入框
                # 或者可以尝试发送测试按键来判断
                print(f"⚠️  检测到Chrome窗口，需要进一步验证")
                # Chrome窗口比较复杂，暂时保守处理
                return False

            print(f"✗ 未识别为可编辑区域")
            return False

        except Exception as e:
            print(f"❌ 检测异常: {e}")
            return False

    def on_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        # 单击右键检测
        if button == mouse.Button.right and pressed:
            # 检测是否在可编辑输入框中
            if self.is_in_editable_field():
                # 检测是否有文字被选中
                if self.has_text_selection():
                    print("✓ 检测到选中文字，不弹出菜单（允许复制）")
                    return  # 不弹菜单，让系统右键菜单正常显示

                print("✓ 检测到输入框，显示粘贴菜单")
                self.show_menu()
            else:
                print("✗ 当前不在输入框中")

    def show_menu(self):
        """显示剪贴板历史菜单"""
        if not self.clipboard_history:
            return

        # 保存当前前台窗口句柄
        self.previous_window = ctypes.windll.user32.GetForegroundWindow()

        # 如果菜单已存在，先销毁
        if self.menu_window:
            try:
                self.menu_window.destroy()
            except:
                pass

        # 使用Toplevel创建菜单窗口
        self.menu_window = tk.Toplevel(self.root)
        self.menu_window.title("剪贴板历史")
        self.menu_window.attributes('-topmost', True)

        screen_width = self.menu_window.winfo_screenwidth()
        screen_height = self.menu_window.winfo_screenheight()

        menu_width = 500
        menu_height = min(400, len(self.clipboard_history) * 40 + 50)

        x = (screen_width - menu_width) // 2
        y = (screen_height - menu_height) // 2

        self.menu_window.geometry(f'{menu_width}x{menu_height}+{x}+{y}')

        frame = ttk.Frame(self.menu_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.menu_window.columnconfigure(0, weight=1)
        self.menu_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(frame, text="选择要粘贴的内容 (单击左键选择)",
                               font=('微软雅黑', 12, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)

        canvas = tk.Canvas(frame, height=menu_height-80)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 绑定鼠标滚轮事件
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # 当菜单关闭时解绑滚轮事件
        def on_destroy():
            canvas.unbind_all("<MouseWheel>")

        self.menu_window.protocol("WM_DELETE_WINDOW", lambda: (on_destroy(), self.menu_window.destroy()))

        for idx, content in enumerate(self.clipboard_history):
            self.create_item_button(scrollable_frame, idx, content)

        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        frame.rowconfigure(1, weight=1)

        close_btn = ttk.Button(frame, text="关闭 (ESC)",
                              command=lambda: (on_destroy(), self.menu_window.destroy()))
        close_btn.grid(row=2, column=0, pady=(10, 0))

        self.menu_window.bind('<Escape>', lambda e: (on_destroy(), self.menu_window.destroy()))
        self.menu_window.bind('<FocusOut>', lambda e: (on_destroy(), self.menu_window.destroy()))

    def create_item_button(self, parent, idx, content):
        """创建列表项按钮"""
        preview = content[:80].replace('\n', ' ')
        if len(content) > 80:
            preview += "..."

        # 使用tk.Frame而不是ttk.Frame，以支持背景色
        btn_frame = tk.Frame(parent, relief='raised', borderwidth=1, bg='white')
        btn_frame.grid(row=idx, column=0, sticky=(tk.W, tk.E), pady=2, padx=5)
        btn_frame.columnconfigure(1, weight=1)

        num_label = tk.Label(btn_frame, text=f"{idx+1}.",
                            font=('微软雅黑', 11, 'bold'),
                            width=3, bg='white')
        num_label.grid(row=0, column=0, padx=(8, 5))

        content_label = tk.Label(btn_frame, text=preview,
                                font=('微软雅黑', 11),
                                wraplength=420, bg='white', anchor='w', justify='left')
        content_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=8)

        def on_select(event=None):
            # 检查是否有粘贴正在进行
            if self.is_pasting:
                print("⚠️  请等待上一次粘贴完成")
                return

            # 在新线程中执行粘贴
            threading.Thread(target=lambda: self.paste_and_close_menu(content), daemon=True).start()

        # 只绑定单击左键
        btn_frame.bind('<Button-1>', on_select)
        num_label.bind('<Button-1>', on_select)
        content_label.bind('<Button-1>', on_select)

        def on_enter(event):
            # 深蓝色背景，白色文字，高对比度
            btn_frame.configure(relief='sunken', bg='#1E3A8A')
            num_label.configure(bg='#1E3A8A', foreground='white', font=('微软雅黑', 11, 'bold'))
            content_label.configure(bg='#1E3A8A', foreground='white', font=('微软雅黑', 11, 'bold'))

        def on_leave(event):
            # 恢复原样
            btn_frame.configure(relief='raised', bg='white')
            num_label.configure(bg='white', foreground='black', font=('微软雅黑', 11, 'bold'))
            content_label.configure(bg='white', foreground='black', font=('微软雅黑', 11))

        for widget in [btn_frame, num_label, content_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)

    def paste_and_close_menu(self, content):
        """粘贴内容并关闭菜单"""
        menu_to_destroy = self.menu_window

        try:
            # 隐藏菜单
            if menu_to_destroy and menu_to_destroy.winfo_exists():
                menu_to_destroy.withdraw()

            # 等待菜单隐藏
            time.sleep(0.1)

            # 主动恢复焦点到之前的窗口
            if self.previous_window:
                ctypes.windll.user32.SetForegroundWindow(self.previous_window)
                print(f"🔄 恢复焦点到窗口: {self.previous_window}")

            # 再等待焦点切换完成
            time.sleep(0.3)

            # 执行粘贴
            self.paste_content(content)

        finally:
            # 粘贴完成后销毁菜单
            if menu_to_destroy:
                try:
                    if menu_to_destroy.winfo_exists():
                        menu_to_destroy.destroy()
                except:
                    pass

    def paste_content_delayed(self, content):
        """延迟粘贴选中的内容"""
        time.sleep(0.3)  # 增加等待时间，确保焦点完全回到输入框
        self.paste_content(content)

    def paste_content(self, content):
        """粘贴选中的内容"""
        try:
            print(f"🔄 开始粘贴...")
            # 标记开始粘贴，暂停剪贴板监控
            self.is_pasting = True

            # 复制内容到剪贴板
            pyperclip.copy(content)
            # 等待剪贴板更新完成
            time.sleep(0.15)

            # 使用Windows API模拟按键，更稳定
            VK_CONTROL = 0x11
            VK_V = 0x56
            KEYEVENTF_KEYUP = 0x0002

            # 按下Ctrl
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
            time.sleep(0.05)
            # 按下V
            ctypes.windll.user32.keybd_event(VK_V, 0, 0, 0)
            time.sleep(0.05)
            # 释放V
            ctypes.windll.user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            # 释放Ctrl
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

            preview = content[:50].replace('\n', ' ')
            if len(content) > 50:
                preview += "..."
            print(f"✅ 已粘贴: {preview}")

            # 更新最后剪贴板内容，避免重复记录
            self.last_clipboard = content

            # 等待粘贴完成
            time.sleep(0.2)

        except Exception as e:
            print(f"❌ 粘贴失败: {e}")
        finally:
            # 恢复剪贴板监控
            self.is_pasting = False
            print(f"🔄 粘贴完成，恢复监控")

    def create_tray_icon(self):
        """创建系统托盘图标"""
        # 加载图标
        try:
            icon_image = Image.open("icon.ico")
        except:
            # 如果图标文件不存在，创建一个简单的图标
            icon_image = Image.new('RGB', (64, 64), color=(41, 128, 185))

        # 创建托盘菜单
        menu = Menu(
            MenuItem('剪贴板历史管理器', lambda: None, enabled=False),
            MenuItem('---', lambda: None, enabled=False),
            MenuItem('显示历史', self.show_menu_from_tray),
            MenuItem('清空历史', self.clear_history),
            MenuItem('---', lambda: None, enabled=False),
            MenuItem('退出', self.quit_app)
        )

        # 创建托盘图标
        self.tray_icon = Icon(
            "ClipboardManager",
            icon_image,
            "剪贴板历史管理器",
            menu
        )

    def show_menu_from_tray(self):
        """从系统托盘显示历史菜单"""
        if self.clipboard_history:
            self.show_menu()

    def clear_history(self):
        """清空历史记录"""
        self.clipboard_history = []
        self.save_history()
        print("✓ 历史记录已清空")

    def quit_app(self):
        """退出应用程序"""
        print("\n👋 正在退出程序...")
        self.running = False

        # 停止托盘图标
        if self.tray_icon:
            self.tray_icon.stop()

        # 关闭Tkinter
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

        os._exit(0)

    def start(self):
        """启动监控"""
        print("🚀 剪贴板历史管理器启动中...")
        print("💡 使用说明:")
        print("   1. 正常复制文本，会自动记录到历史")
        print("   2. 在任意输入框中 单击鼠标右键 调出历史菜单")
        print("   3. 单击鼠标左键 选择要粘贴的内容")
        print(f"   4. 最多保存 {self.max_history} 条历史记录")
        print("   5. 程序已驻留系统托盘，右键托盘图标可退出")
        print("-" * 60)

        # 启动剪贴板监控线程
        clipboard_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        clipboard_thread.start()

        # 启动鼠标监听线程
        def start_mouse_listener():
            with mouse.Listener(on_click=self.on_click) as listener:
                listener.join()

        mouse_thread = threading.Thread(target=start_mouse_listener, daemon=True)
        mouse_thread.start()

        # 创建并启动系统托盘图标
        self.create_tray_icon()

        # 在单独线程中运行托盘图标
        def run_tray():
            self.tray_icon.run()

        tray_thread = threading.Thread(target=run_tray, daemon=True)
        tray_thread.start()

        # 运行Tkinter主循环
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 程序已退出")
            self.quit_app()

if __name__ == "__main__":
    manager = ClipboardManager(max_history=20)
    manager.start()
