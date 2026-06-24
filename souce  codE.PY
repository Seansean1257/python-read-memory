import tkinter as tk
from tkinter import ttk
import win32gui
import win32process

class WindowListApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("窗口列表 - 右键复制单个信息")
        self.root.geometry("800x1000")
        self.root.resizable(False, False)
        # ---------- 创建表格 ----------
        self.tree = ttk.Treeview(
            self.root,
            columns=('句柄', '类名', 'PID', '标题'),
            show='headings'
        )
        self.tree.heading('句柄', text='句柄 (十六进制)')
        self.tree.heading('类名', text='类名')
        self.tree.heading('PID', text='进程 ID')
        self.tree.heading('标题', text='窗口标题')

        self.tree.column('句柄', width=120, anchor='center')
        self.tree.column('类名', width=180)
        self.tree.column('PID', width=80, anchor='center')
        self.tree.column('标题', width=300)

        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,5), pady=5)

        # ---------- 底部按钮 ----------
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        btn_frame2 = tk.Frame(self.root)
        btn_frame2.pack(fill=tk.X, padx=5, pady=5)

        refresh_btn = tk.Button(btn_frame, text=" 手动刷新", command=self.refresh_list)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        exit_btn = tk.Button(btn_frame2, text="✖ 退出", command=self.root.quit)
        exit_btn.pack(side=tk.LEFT, padx=5)

        # ---------- 底部状态栏 ----------
        self.status_label = tk.Label(self.root, text="👉 右键点击任意行，可复制单个字段", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

        # ---------- 创建右键菜单 ----------
        self.popup_menu = tk.Menu(self.root, tearoff=0)
        self.popup_menu.add_command(label="复制句柄", command=self.copy_hwnd)
        self.popup_menu.add_command(label="复制类名", command=self.copy_class)
        self.popup_menu.add_command(label="复制 PID", command=self.copy_pid)
        self.popup_menu.add_command(label="复制标题", command=self.copy_title)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="复制整行（全部）", command=self.copy_all)

        # 绑定右键点击事件
        self.tree.bind("<Button-3>", self.show_popup)

        # 存储当前右键点击的行数据
        self.current_values = None

        # ---------- 初始化 ----------
        self.refresh_list()
        self.auto_refresh()

    def get_windows(self):
        """枚举所有可见窗口"""
        windows = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    except:
                        pid = 'N/A'
                    class_name = win32gui.GetClassName(hwnd)
                    windows.append((hwnd, class_name, pid, title))
            return True
        win32gui.EnumWindows(callback, None)
        return windows

    def refresh_list(self):
        """刷新表格"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        windows = self.get_windows()
        for hwnd, class_name, pid, title in windows:
            hwnd_str = f"0x{hwnd:X}"
            self.tree.insert('', 'end', values=(hwnd_str, class_name, pid, title))

        self.root.title(f"窗口列表 (共 {len(windows)} 个窗口) - 右键复制单个字段")

    def show_popup(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            # 选中该行
            self.tree.selection_set(item)
            # 获取该行的数据
            self.current_values = self.tree.item(item, 'values')
            # 在鼠标位置弹出菜单
            self.popup_menu.post(event.x_root, event.y_root)

    # ---------- 复制单个字段的方法 ----------
    def copy_hwnd(self):
        if self.current_values:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_values[0])
            self.status_label.config(text=f"✅ 已复制句柄: {self.current_values[0]}", fg='green')

    def copy_class(self):
        if self.current_values:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_values[1])
            self.status_label.config(text=f"✅ 已复制类名: {self.current_values[1]}", fg='green')

    def copy_pid(self):
        if self.current_values:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_values[2])
            self.status_label.config(text=f"✅ 已复制 PID: {self.current_values[2]}", fg='green')

    def copy_title(self):
        if self.current_values:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_values[3])
            self.status_label.config(text=f"✅ 已复制标题: {self.current_values[3]}", fg='green')

    def copy_all(self):
        """额外加一个复制整行的功能，方便你对比"""
        if self.current_values:
            info = f"句柄: {self.current_values[0]}\n类名: {self.current_values[1]}\nPID: {self.current_values[2]}\n标题: {self.current_values[3]}"
            self.root.clipboard_clear()
            self.root.clipboard_append(info)
            self.status_label.config(text=f"✅ 已复制整行信息", fg='green')

    def auto_refresh(self):
        self.refresh_list()
        self.root.after(3000, self.auto_refresh)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WindowListApp()
    app.run()
