import tkinter as tk
import cv2
from ..utils.camera import Camera


class CaptureWindow:
    def __init__(self, master, labeling_callback):
        self.master = master
        self.labeling_callback = labeling_callback
        self.camera = Camera()

        # create window
        self.window = tk.Toplevel(self.master)
        self.window.title("KI-Pic-Labeling")
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        # create canvas for video feed
        self.canvas = tk.Canvas(self.window, width=self.camera.width, height=self.camera.height)
        self.canvas.pack()

        # create button to capture images
        self.capture_button = tk.Button(self.window, text="Capture", command=self.capture)
        self.capture_button.pack()

        # start video feed
        self.update()

    def update(self):
        # get frame from camera
        ret, frame = self.camera.get_frame()

        if ret:
            # convert frame to tkinter image
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (self.camera.width, self.camera.height))
            img = tk.PhotoImage(data=cv2.imencode('.png', img)[1].tobytes())

            # update canvas with new image
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
            self.canvas.image = img

        # schedule next update
        self.window.after(100, self.update)

    def capture(self):
        # get current frame from camera
        ret, frame = self.camera.get_frame()

        if ret:
            # call labeling callback with captured frame
            self.labeling_callback(frame)

    def close(self):
        # release camera and destroy window
        self.camera.release()
        self.window.destroy()
