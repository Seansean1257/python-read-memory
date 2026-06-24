import tkinter as tk
from tkinter import messagebox
import win32gui


class WindowTracker:
    def __init__(self, target_hwnd):
        self.target_hwnd = target_hwnd
        self.running = True

        # 创建透明覆盖窗口
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # 无边框
        self.root.attributes('-topmost', True)  # 置顶
        self.root.attributes('-transparentcolor', 'gray')  # 灰色变透明

        # 画布
        self.canvas = tk.Canvas(self.root, bg='gray', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绘制初始图形（边框 + 标签）
        self.draw_overlay()

        # 绑定键盘退出（按 ESC 退出）
        self.root.bind('<Escape>', lambda e: self.stop())

        # 开始跟踪
        self.update_position()

        # 窗口关闭时停止
        self.root.protocol("WM_DELETE_WINDOW", self.stop)

    def draw_overlay(self):
        """在画布上绘制覆盖图形（边框和文字）"""
        # 先清除旧图形（如果有的话）
        self.canvas.delete('all')
        # 绘制一个虚线矩形边框（稍后会在更新中调整大小）
        self.rect_id = self.canvas.create_rectangle(
            0, 0, 100, 100, outline='red', width=3, dash=(5, 3)
        )
        self.label_id = self.canvas.create_text(
            20, 20, text='跟踪中', fill='red', font=('Arial', 12, 'bold'), anchor='nw'
        )

    def update_position(self):
        """定时更新覆盖窗口的位置和大小"""
        if not self.running:
            return

        try:
            # 获取目标窗口的矩形
            left, top, right, bottom = win32gui.GetWindowRect(self.target_hwnd)
            width = right - left
            height = bottom - top

            # 如果窗口尺寸为0，可能被最小化或关闭了
            if width == 0 or height == 0:
                # 隐藏覆盖窗口
                self.root.withdraw()
            else:
                # 更新覆盖窗口的几何属性
                self.root.geometry(f"{width}x{height}+{left}+{top}")
                # 更新画布上的矩形尺寸（留边距）
                padding = 5
                self.canvas.coords(self.rect_id, padding, padding, width - padding, height - padding)
                # 更新文字位置（保持在左上角）
                self.canvas.coords(self.label_id, 20, 20)
                # 确保窗口显示
                self.root.deiconify()

        except Exception as e:
            # 如果句柄无效（窗口已关闭），停止跟踪
            print("目标窗口已关闭，停止跟踪")
            self.stop()
            return

        # 每 50ms 检查一次
        self.root.after(1, self.update_position)

    def stop(self):
        """停止跟踪并关闭窗口"""
        self.running = False
        self.root.destroy()

    def run(self):
        """启动主循环"""
        self.root.mainloop()


# --- 使用示例 ---
if __name__ == "__main__":
    # 查找目标窗口（例如记事本）
    hwnd = win32gui.FindWindow(None, "新建文本文档 (2) - 记事本)
    if hwnd == 0:
        # 尝试用类名查找
        hwnd = win32gui.FindWindow("Notepad", None)

    if hwnd == 0:
        print("未找到目标窗口，请检查标题或类名")
        exit()

    # 启动跟踪器
    tracker = WindowTracker(hwnd)
    tracker.run()
