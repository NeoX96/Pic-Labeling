import tkinter as tk
from tkinter import messagebox
import cv2
from classes.videocapture import VideoCapture
from classes.imageprocessing import ImageProcessing

class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Image Capture Tool")
        self.config(bg='#2E2E2E')

        # set minimum size of window (width, height)
        self.minsize(550, 550)
        
        self.video_capture = VideoCapture(self)
        self.image_processing = ImageProcessing(self)

        # Image label entry
        self.label_image = tk.Label(self, text="Enter Image Label:", bg='#2E2E2E', fg='white')
        self.entry_image = tk.Entry(self, bg='#333333', fg='white')
        

        self.label_interval = tk.Label(self, text="Enter Capture Interval (ms):", bg='#2E2E2E', fg='white')
        self.entry_interval = tk.Entry(self, bg='#333333', fg='white')

        # Start capture button
        self.start_capture_frame = tk.Frame(self, bg='#2E2E2E')
        self.button = tk.Button(self.start_capture_frame, text="Start Capture", command=self.start_capture, bg='#00FF00', fg='black')


        # Options frame

        # Resolution
        self.options_frame = tk.Frame(self, bg='#2E2E2E')
        self.resolution_label = tk.Label(self.options_frame, text="Resolution:", bg='#2E2E2E', fg='white')
        self.width_entry = tk.Entry(self.options_frame, bg='#333333', fg='white', width=5)
        self.width_entry.config(validate="key", validatecommand=(self.register(self.validate_resolution_callback), '%P'))

        self.height_entry = tk.Entry(self.options_frame, bg='#333333', fg='black', width=5)
        self.height_entry.config(validate="key", validatecommand=(self.register(self.validate_resolution_callback), '%P'))

        self.p_label = tk.Label(self.options_frame, text="p", bg='#2E2E2E', fg='white')
        self.x_label = tk.Label(self.options_frame, text="x", bg='#2E2E2E', fg='white')

        # File format
        self.file_format_label = tk.Label(self.options_frame, text="File format:", bg='#2E2E2E', fg='white')
        self.file_format_variable = tk.StringVar(self)
        self.file_format_variable.set("jpg") # default value
        self.file_format_options = tk.OptionMenu(self.options_frame, self.file_format_variable, "jpg", "jpeg", "png", "bmp", "tiff")

        # Color format, rgb, grayscale or black and white
        self.color_format_label = tk.Label(self.options_frame, text="Color format:", bg='#2E2E2E', fg='white')
        self.color_format_variable = tk.StringVar(self)
        self.color_format_variable.set("RGB") # default value
        self.color_format_options = tk.OptionMenu(self.options_frame, self.color_format_variable, "RGB", "Grayscale", "Black/White")




        # reset crop
        self.reset_button = tk.Button(self, text="Reset Crop", command=self.reset_crop, bg='#FFFF00', fg='black')
        
        
        # Pack the widgets
        self.label_image.pack(pady=(30, 1))
        self.entry_image.pack(pady=(0, 20))
        self.label_interval.pack(pady=0)
        self.entry_interval.pack(pady=0)
        self.button.pack(pady=30)
        self.reset_button.pack(pady=10)

        self.start_capture_frame.pack(pady=5)
        self.button.pack(side=tk.LEFT, padx=5)


        # options frame
        self.options_frame.pack(pady=5)

            # color format
        self.color_format_label.pack(side=tk.LEFT, padx=5)
        self.color_format_options.pack(side=tk.LEFT, padx=(5, 40))
        

          # resolution
        self.resolution_label.pack(side=tk.LEFT, padx=5)
        self.height_entry.pack(side=tk.LEFT, padx=0)
        self.x_label.pack(side=tk.LEFT, padx=0)
        self.width_entry.pack(side=tk.LEFT, padx=0)
        self.p_label.pack(side=tk.LEFT, padx=0)

          # file format
        self.file_format_options.pack(side=tk.RIGHT, padx=0)
        self.file_format_label.pack(side=tk.RIGHT, padx=(40, 5))


        
        

        # Pack the video capture widget
        self.video_capture.pack(pady=30, padx=30)
                
        # Bind the validate resolution callback function to the width entry widget
        self.width_entry.bind("<FocusOut>", self.validate_resolution_callback)

        # Insert the current frame width and height into the width and height entry widgets
        self.width_entry.insert(0, str(int(self.video_capture.cap.get(cv2.CAP_PROP_FRAME_WIDTH))))
        self.height_entry.insert(0, str(int(self.video_capture.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        # Insert a default value of 200 into the interval entry widget
        self.entry_interval.insert(0, "200")


        # Start updating the video capture widget
        self.video_capture.start_update()


    def reset_crop(self):
        self.video_capture.reset_crop()

    def update_counter(self):
        if not self.stop_counter:
            self.button.config(text="Stop Capture: " + str(self.image_processing.counter))
            self.after(200, self.update_counter)


    def validate_resolution_callback(self, *args):
        """Validate the entered width value and calculate the height based on the aspect ratio of the camera."""

        # Get the value entered in the width entry widget
        width_entry_value = self.width_entry.get()
        if width_entry_value.isdigit():
            width = int(width_entry_value)

            # Check if the entered width is valid
            if width <= self.video_capture.cap.get(cv2.CAP_PROP_FRAME_WIDTH) and width > 20:
                # Calculate the height based on the aspect ratio of the camera
                height = int(width / self.video_capture.cap.get(cv2.CAP_PROP_FRAME_WIDTH) * self.video_capture.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                # Make the height entry widget editable and insert the calculated height
                self.height_entry.config(state='normal')
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(height))
                # Make the height entry widget read-only
                self.height_entry.config(state='readonly')
                # Set the text color of the height entry widget to black
                self.height_entry.config(fg='black')
            else:
                # If the entered width is not valid, reset the width and height entry widgets to their previous values
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(int(self.video_capture.cap.get(cv2.CAP_PROP_FRAME_WIDTH))))
                self.height_entry.config(state='normal')
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(int(self.video_capture.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
                self.height_entry.config(state='readonly')
        else:
            # If the entered value is not a digit, reset the width entry widget to its previous value
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(int(self.video_capture.cap.get(cv2.CAP_PROP_FRAME_WIDTH))))



    def start_capture(self):
        """Start capturing images and save them to the images folder."""
        label = self.entry_image.get()
        self.stop_counter = False



        if label:
            interval = self.entry_interval.get()
            if interval:
                self.image_processing.interval = int(interval)
            self.image_processing.label = label
            self.image_processing.start_capture()
            self.button.config(text="Stop Capture: " + str(self.image_processing.counter), command=self.stop_capture, bg='#FF0000')
            self.update_counter()
        else:
            messagebox.showerror("Error", "Please enter a label for the image.")

    def stop_capture(self):
        """Stop capturing images."""
        self.image_processing.stop_capture()
        self.stop_counter = True
        self.button.config(text="Start Capture", command=self.start_capture, bg='#00FF00')


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

