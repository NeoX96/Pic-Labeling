import cv2
import numpy as np
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

class VideoCapture(tk.Frame):
    def __init__(self, master, bg='black'):
        tk.Frame.__init__(self, master, bg=bg)
        self.master = master
        self.width = None
        self.height = None
        self.bg = bg
        self.cap = None
        self.video_feed = None
        self.cropping = False
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None
        self.cropped_frame = None
        
        self.canvas = Canvas(self, bg=self.bg, cursor='cross')


        self.cap = cv2.VideoCapture(0)
        self.video_feed = self.canvas.create_image(0, 0, image=None, anchor=tk.NW)

        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.canvas.config(width=self.width, height=self.height)

        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        self.update()

    
    def update(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                if self.cropping:
                    self.cropped_frame = frame[self.y1+2:self.y2-2, self.x1+2:self.x2-2]
                    cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0), 2)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.array(frame)
                frame = Image.fromarray(frame)
                frame = ImageTk.PhotoImage(frame)
                self.canvas.itemconfig(self.video_feed, image=frame)
                self.canvas.image = frame
        self.after(30, self.update)

    def on_mouse_down(self, event):
        self.x1 = event.x
        self.y1 = event.y

    def on_mouse_move(self, event):
        self.x2 = event.x
        self.y2 = event.y

    def on_mouse_up(self, event):
        self.x2 = event.x
        self.y2 = event.y
        self.cropping = True
