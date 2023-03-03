import tkinter as tk
from tkinter import messagebox
from classes.videocapture import VideoCapture
from classes.imageprocessing import ImageProcessing

class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Image Capture Tool")
        self.config(bg='#2E2E2E')
        
        self.video_capture = VideoCapture(self)
        self.image_processing = ImageProcessing(self)

        self.label_image = tk.Label(self, text="Enter Image Label:", bg='#2E2E2E', fg='white')
        self.entry_image = tk.Entry(self, bg='#333333', fg='white')
        self.label_interval = tk.Label(self, text="Enter Capture Interval (ms):", bg='#2E2E2E', fg='white')
        self.entry_interval = tk.Entry(self, bg='#333333', fg='white')
        self.button = tk.Button(self, text="Start Capture", command=self.start_capture, bg='#00FF00', fg='black')
        
        self.label_image.pack(pady=10)
        self.entry_image.pack(pady=10)
        self.label_interval.pack(pady=10)
        self.entry_interval.pack(pady=10)
        self.button.pack(pady=10)

        self.video_capture.pack(pady=10)

    def start_capture(self):
        label = self.entry_image.get()
        if label:
            interval = self.entry_interval.get()
            if interval:
                self.image_processing.interval = int(interval)
            self.image_processing.label = label
            self.image_processing.start_capture()
            self.button.config(text="Stop Capture", command=self.stop_capture, bg='#FF0000')
        else:
            messagebox.showerror("Error", "Please enter a label for the image.")

    def stop_capture(self):
        self.image_processing.stop_capture()
        self.button.config(text="Start Capture", command=self.start_capture, bg='#00FF00')

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
