import cv2
import tkinter as tk


class Resizer(tk.Frame):
    def __init__(self, parent, resize_callback):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, bg="white", width=100, height=100)
        self.canvas.pack(expand=True, fill="both")

        self.bind("<B1-Motion>", self._resize)

        self.resize_callback = resize_callback

    def _resize(self, event):
        new_size = (event.x, event.y)
        self.canvas.configure(width=new_size[0], height=new_size[1])
        self.resize_callback()

    def resize_frame(self, frame):
        size = (self.canvas.winfo_width(), self.canvas.winfo_height())
        if size[0] == 0 or size[1] == 0:
            return frame
        return cv2.resize(frame, size)
