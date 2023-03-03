import os
import cv2


class Camera:
    def __init__(self, camera_index=0):
        self.video_capture = cv2.VideoCapture(camera_index)

    def __del__(self):
        self.video_capture.release()

    def get_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            return frame
        else:
            return None

def get_next_file_name(label, folder_path):
    """
    Returns the next available file name for a given label in a given folder
    """
    i = 1
    while True:
        file_name = os.path.join(folder_path, f"{label}_{i}.png")
        if not os.path.exists(file_name):
            return file_name
        i += 1


def save_image(image, file_name):
    """
    Saves an image to a file
    """
    cv2.imwrite(file_name, image)
