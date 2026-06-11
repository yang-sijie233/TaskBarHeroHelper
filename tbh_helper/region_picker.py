"""全屏拖拽框选屏幕区域（使用 Toplevel，不创建第二个 Tk 根窗口）。"""

from __future__ import annotations

import tkinter as tk

from .anchor import AnchorRect


class RegionPicker:
    def pick_overlay(self, parent: tk.Misc, hint: str) -> AnchorRect | None:
        self._result: AnchorRect | None = None
        self._start: tuple[int, int] | None = None
        self._rect_id: int | None = None

        overlay = tk.Toplevel(parent)
        overlay.title("框选区域")
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.35)
        overlay.configure(cursor="crosshair", bg="black")
        overlay.grab_set()

        screen_w = overlay.winfo_screenwidth()
        screen_h = overlay.winfo_screenheight()

        canvas = tk.Canvas(
            overlay,
            width=screen_w,
            height=screen_h,
            highlightthickness=0,
            bg="black",
        )
        canvas.pack(fill=tk.BOTH, expand=True)

        hint_id = canvas.create_text(
            screen_w // 2,
            40,
            text=hint,
            fill="yellow",
            font=("Microsoft YaHei UI", 16, "bold"),
        )

        def close_overlay():
            try:
                overlay.grab_release()
            except tk.TclError:
                pass
            overlay.destroy()

        def cancel(_event=None):
            self._result = None
            close_overlay()

        def on_press(event):
            self._start = (event.x_root, event.y_root)
            if self._rect_id is not None:
                canvas.delete(self._rect_id)
            self._rect_id = canvas.create_rectangle(
                event.x_root,
                event.y_root,
                event.x_root,
                event.y_root,
                outline="#00ff88",
                width=3,
            )

        def on_drag(event):
            if self._start is None or self._rect_id is None:
                return
            x0, y0 = self._start
            canvas.coords(self._rect_id, x0, y0, event.x_root, event.y_root)

        def on_release(event):
            if self._start is None:
                return
            x0, y0 = self._start
            x1, y1 = event.x_root, event.y_root
            left = min(x0, x1)
            top = min(y0, y1)
            width = abs(x1 - x0)
            height = abs(y1 - y0)
            if width < 20 or height < 20:
                canvas.itemconfig(hint_id, text="区域太小，请重新拖拽")
                self._start = None
                if self._rect_id is not None:
                    canvas.delete(self._rect_id)
                    self._rect_id = None
                return
            self._result = AnchorRect(left=left, top=top, width=width, height=height)
            close_overlay()

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        overlay.bind("<Escape>", cancel)

        parent.wait_window(overlay)
        return self._result


def _restore_parent(parent: tk.Misc) -> None:
    try:
        parent.deiconify()
        parent.lift()
        parent.focus_force()
        parent.update_idletasks()
    except tk.TclError:
        pass


def pick_region(hint: str | None = None, *, parent: tk.Misc | None = None) -> AnchorRect:
    hint = hint or "拖拽框选传送门面板，松开确认 | Esc 取消"
    picker = RegionPicker()

    if parent is not None:
        parent.withdraw()
        parent.update_idletasks()
        try:
            result = picker.pick_overlay(parent, hint)
            if result is None:
                raise RuntimeError("已取消框选")
            return result
        finally:
            _restore_parent(parent)

    # CLI 独立模式：临时根窗口，用完即毁
    root = tk.Tk()
    root.withdraw()
    try:
        result = picker.pick_overlay(root, hint)
        if result is None:
            raise RuntimeError("已取消框选")
        return result
    finally:
        root.destroy()


def pick_region_modal(parent: tk.Misc, hint: str | None = None) -> AnchorRect:
    """在已有 GUI 窗口上模态框选（不 hide 主窗口，仅盖一层 overlay）。"""
    hint = hint or "拖拽框选传送门面板，松开确认 | Esc 取消"
    result = RegionPicker().pick_overlay(parent, hint)
    if result is None:
        raise RuntimeError("已取消框选")
    parent.lift()
    parent.focus_force()
    return result
