# -*- coding: utf-8 -*-
"""
FloatPad — 桌面置顶速记小窗
无边框 / 始终置顶 / 可拖动 / 不进任务栏
Enter 保存到同目录 inbox.md，Shift+Enter 换行
"""
import os
import ctypes
import datetime
import tkinter as tk

BASE = os.path.dirname(os.path.abspath(__file__))
INBOX = os.path.join(BASE, "inbox.md")
GEOM = os.path.join(BASE, "_geom.txt")

BG = "#1b1d21"
BAR = "#25282e"
FG = "#e6e8eb"
MUT = "#7c828c"
ACCENT = "#4c8dff"
OKC = "#3fb950"
LINE = "#3a3f47"


def enable_dpi_awareness():
    """让窗口按物理像素绘制，避免高分屏被系统拉伸发虚"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class FloatPad:
    BASE_W, BASE_H, BASE_BAR = 396, 252, 36

    def __init__(self, root):
        self.root = root
        self.pinned = True
        self.collapsed = False
        self._drag = (0, 0)
        self._flash_job = None

        # DPI 缩放系数（96dpi 基准）
        try:
            self.k = max(1.0, root.winfo_fpixels("1i") / 96.0)
        except Exception:
            self.k = 1.0

        self.W = self.px(self.BASE_W)
        self.H = self.px(self.BASE_H)
        self.BAR_H = self.px(self.BASE_BAR)

        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.configure(bg=BG)

        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        x = sw - self.W - self.px(40)
        y = self.px(120)
        if y + self.H > sh - self.px(60):
            y = max(self.px(40), sh - self.H - self.px(100))
        root.geometry("%dx%d+%d+%d" % (self.W, self.H, x, y))

        self._build()
        self._round_corners()
        root.after(700, self._dump_geom)
        root.after(150, self._take_focus)

    def px(self, v):
        return int(round(v * self.k))

    # ---------------- UI ----------------
    def _build(self):
        self.outer = tk.Frame(self.root, bg=BG,
                              highlightbackground=LINE,
                              highlightthickness=self.px(1))
        self.outer.pack(fill="both", expand=True)

        bar = tk.Frame(self.outer, bg=BAR, height=self.BAR_H)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)
        self.bar = bar

        for txt, cmd, fg in (("\u2715", self.quit, MUT),
                             ("\u2014", self.toggle_collapse, MUT),
                             ("\U0001F4CC", self.toggle_pin, ACCENT)):
            b = tk.Label(bar, text=txt, bg=BAR, fg=fg, cursor="hand2",
                         font=("Microsoft YaHei UI", 9), padx=self.px(8))
            b.pack(side="right")
            b.bind("<Button-1>", lambda e, c=cmd: c())
            b.bind("<Enter>", lambda e, w=b: w.configure(bg="#343841"))
            b.bind("<Leave>", lambda e, w=b: w.configure(bg=BAR))

        self.grip = tk.Label(bar, text="\u2726  \u901f\u8bb0", bg=BAR, fg=FG,
                             anchor="w", padx=self.px(12), cursor="fleur",
                             font=("Microsoft YaHei UI", 9, "bold"))
        self.grip.pack(side="left", fill="x", expand=True)

        self.hint = tk.Label(self.grip, text="", bg=BAR, fg=OKC,
                             font=("Microsoft YaHei UI", 8))
        self.hint.place(relx=0.45, rely=0.5, anchor="w")

        for w in (bar, self.grip):
            w.bind("<Button-1>", self.drag_start)
            w.bind("<B1-Motion>", self.drag_move)
            w.bind("<Double-Button-1>", lambda e: self.raise_top())

        self.body = tk.Frame(self.outer, bg=BG)
        self.body.pack(fill="both", expand=True)

        self.foot = tk.Label(
            self.body,
            text="Enter \u4fdd\u5b58 \u00b7 Shift+Enter \u6362\u884c \u00b7 \u53cc\u51fb\u6807\u9898\u680f\u7f6e\u9876",
            bg=BG, fg=MUT, anchor="w",
            padx=self.px(13), pady=self.px(5),
            font=("Microsoft YaHei UI", 8))
        self.foot.pack(fill="x", side="bottom")

        self.txt = tk.Text(
            self.body, bg=BG, fg=FG, insertbackground=ACCENT,
            relief="flat", bd=0, wrap="word", undo=True, height=4,
            padx=self.px(13), pady=self.px(8), spacing1=self.px(2),
            font=("Microsoft YaHei UI", 10),
            selectbackground="#2f4f7a", selectforeground=FG)
        self.txt.pack(fill="both", expand=True)
        self.txt.bind("<Return>", self.on_enter)
        self.txt.bind("<Escape>", lambda e: self.quit())

    def _round_corners(self):
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if not hwnd:
                hwnd = self.root.winfo_id()
            pref = ctypes.c_int(2)  # DWMWCP_ROUND
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 33, ctypes.byref(pref), ctypes.sizeof(pref))
        except Exception:
            pass

    def _dump_geom(self):
        try:
            self.root.update_idletasks()
            with open(GEOM, "w", encoding="utf-8") as f:
                f.write("%d %d %d %d\n" % (self.root.winfo_x(), self.root.winfo_y(),
                                           self.root.winfo_width(),
                                           self.root.winfo_height()))
        except Exception:
            pass

    def _take_focus(self):
        try:
            self.root.lift()
            self.txt.focus_force()
        except Exception:
            pass

    # ---------------- 交互 ----------------
    def drag_start(self, e):
        self._drag = (e.x_root - self.root.winfo_x(),
                      e.y_root - self.root.winfo_y())

    def drag_move(self, e):
        self.root.geometry("+%d+%d" % (e.x_root - self._drag[0],
                                       e.y_root - self._drag[1]))

    def raise_top(self):
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.pinned = True
        self.flash("\u5df2\u7f6e\u9876")

    def toggle_pin(self):
        self.pinned = not self.pinned
        self.root.attributes("-topmost", self.pinned)
        self.flash("\u7f6e\u9876\u5f00" if self.pinned else "\u7f6e\u9876\u5173")

    def toggle_collapse(self):
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.body.pack_forget()
            self.root.geometry("%dx%d" % (self.W, self.BAR_H))
        else:
            self.body.pack(fill="both", expand=True)
            self.root.geometry("%dx%d" % (self.W, self.H))
            self.txt.focus_force()

    def on_enter(self, e):
        if e.state & 0x0001:  # Shift
            self.txt.insert("insert", "\n")
            return "break"
        self.save()
        return "break"

    # ---------------- 存储 ----------------
    def save(self):
        raw = self.txt.get("1.0", "end").strip()
        if not raw:
            return
        now = datetime.datetime.now()
        try:
            new_file = not os.path.exists(INBOX)
            with open(INBOX, "a", encoding="utf-8") as f:
                if new_file:
                    f.write("# Inbox\n\n")
                for line in raw.splitlines():
                    line = line.strip()
                    if line:
                        f.write("- [%s] %s\n" % (now.strftime("%m-%d %H:%M"), line))
            self.txt.delete("1.0", "end")
            self.flash("\u5df2\u4fdd\u5b58")
        except Exception:
            self.flash("\u4fdd\u5b58\u5931\u8d25")

    def flash(self, msg):
        self.hint.configure(text=msg)
        if self._flash_job:
            try:
                self.root.after_cancel(self._flash_job)
            except Exception:
                pass
        self._flash_job = self.root.after(
            1600, lambda: self.hint.configure(text=""))

    def quit(self):
        try:
            os.remove(GEOM)
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    enable_dpi_awareness()
    root = tk.Tk()
    FloatPad(root)
    root.mainloop()
