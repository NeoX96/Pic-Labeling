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
        self.canvas_height = None
        self.canvas_width = None
        self.cropped_frame = None
        
        self.canvas = Canvas(self, bg=self.bg, cursor='cross')


        self.cap = cv2.VideoCapture(0)
        self.video_feed = self.canvas.create_image(0, 0, image=None, anchor=tk.NW)

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        aspect_ratio = self.width / self.height

        self.canvas_width = 600
        self.canvas_height = int(self.canvas_width / aspect_ratio)
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)

        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def start_update(self):
        self.update()
    
    def update(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                original_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                original_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                width_entry_value = self.master.width_entry.get()
                height_entry_value = self.master.height_entry.get()
                if width_entry_value.isdigit() and height_entry_value.isdigit() and int(width_entry_value) > 20 and int(height_entry_value) > 10:
                    width = int(width_entry_value)
                    height = int(height_entry_value)
                    frame = cv2.resize(frame, (width, height))

                    if self.cropping:
                        self.cropped_frame = frame[
                            int(self.y1 * height / original_height)+2:int(self.y2 * height / original_height)-2,
                            int(self.x1 * width / original_width)+2:int(self.x2 * width / original_width)-2
                        ]
                        cv2.rectangle(frame, (int(self.x1 * width / original_width), int(self.y1 * height / original_height)), 
                              (int(self.x2 * width / original_width), int(self.y2 * height / original_height)), (0, 255, 0), 2)
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.array(frame)
                frame = Image.fromarray(frame)
                frame = frame.resize((self.canvas_width, self.canvas_height), Image.ANTIALIAS)
                frame = ImageTk.PhotoImage(frame)

                self.canvas.itemconfig(self.video_feed, image=frame)
                self.canvas.image = frame
        self.after(30, self.update)



    def on_mouse_down(self, event):
        self.x1 = int(event.x * (self.width / self.canvas_width))
        self.y1 = int(event.y * (self.height / self.canvas_height))

    def on_mouse_move(self, event):
        self.x2 = int(event.x * (self.width / self.canvas_width))
        self.y2 = int(event.y * (self.height / self.canvas_height))

    def on_mouse_up(self, event):
        self.x2 = int(event.x * (self.width / self.canvas_width))
        self.y2 = int(event.y * (self.height / self.canvas_height))
        self.cropping = True
