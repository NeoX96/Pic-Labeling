import os
import cv2

class ImageProcessing:
    def __init__(self, master):
        self.master = master
        self.label = ""
        self.counter = 1
        self.interval = 200
        self.should_stop_capture = False

    def start_capture(self):
        if not self.label:
            return
        
        if not os.path.exists(f"captures/{self.label}"):
            os.makedirs(f"captures/{self.label}")
        
        self.should_stop_capture = False
        self.capture_images()

    def capture_images(self):
        ret, frame = self.master.video_capture.cap.read()
        if ret:
            if self.should_stop_capture:
                return
            
            if self.master.video_capture.cropping:
                frame = self.master.video_capture.cropped_frame
            filename = f"{self.label}_{self.counter}.png"
            path = os.path.join("captures", self.label, filename)
            cv2.imwrite(path, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.counter += 1
            self.master.after(self.interval, self.capture_images)

    def stop_capture(self):
        self.should_stop_capture = True
        self.master.after_cancel(self.capture_images)
