import tkinter as tk
import os
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from utils.camera import Camera, get_next_file_name, save_image


class App:
    def __init__(self, window, camera_index=0):
        self.window = window
        self.window.title("KI-Pic-Labeling")
        self.camera = Camera(camera_index)

        self.label_entry = ttk.Entry(self.window)
        self.label_entry.grid(row=0, column=0, padx=5, pady=5)
        self.label_entry.focus()

        self.capture_button = ttk.Button(self.window, text="Capture", command=self.start_capture)
        self.capture_button.grid(row=0, column=1, padx=5, pady=5)

        self.preview_label = ttk.Label(self.window)
        self.preview_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.is_capturing = False
        self.timer_id = None
        self.interval = 100 # Time between captures in ms

        # Display preview
        frame = self.camera.get_frame()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        self.photo = ImageTk.PhotoImage(image)
        self.preview_label.configure(image=self.photo)


    def start_capture(self):
        label = self.label_entry.get()
        folder_path = os.path.join("captures", label)

        # Create folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        self.is_capturing = True
        self.capture_button.configure(text="Stop Capture", command=self.stop_capture)

        def capture():
            frame = self.camera.get_frame()

            if frame is None:
                self.stop_capture()
                return

            file_name = get_next_file_name(label, folder_path)
            save_image(frame, file_name)

            # Display preview
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            self.photo = ImageTk.PhotoImage(image)
            self.preview_label.configure(image=self.photo)

            self.timer_id = self.window.after(self.interval, capture)

        capture()


    def stop_capture(self):
        self.is_capturing = False
        self.capture_button.configure(text="Capture", command=self.start_capture)

        if self.timer_id is not None:
            self.window.after_cancel(self.timer_id)
            self.timer_id = None


if __name__ == "__main__":
    window = tk.Tk()
    app = App(window)
    window.mainloop()
