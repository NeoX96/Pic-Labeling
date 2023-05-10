import cv2
import numpy as np
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

class VideoCapture(tk.Frame):
    """
    A Tkinter Frame widget that displays video feed from a camera using OpenCV.
    The frame can be resized based on the user's input and the video feed can be cropped using the mouse. 
    """

    def __init__(self, master, bg='black'):
        tk.Frame.__init__(self, master, bg=bg)
        self.master = master
        self.is_running = False
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
        """Start the video feed update loop."""
        self.is_running = True
        self.update()

    def stop_update(self):
        """Stop the video feed update loop."""
        self.is_running = False
        self.cap.release()
        cv2.destroyAllWindows()
    
    def update(self):
        """Update the video feed in the canvas."""
        if self.is_running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    # flip frame to mirror the video feed
                    frame = cv2.flip(frame, 1)

                    # get the width and height of the frame
                    original_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    original_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    width_entry_value = self.master.width_entry.get()
                    height_entry_value = self.master.height_entry.get()

                    # get color pick from input field
                    self.color = self.master.color_format_variable.get()

                    # switch case for color format
                    match self.color:
                        case 'RGB':
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        case 'Grayscale':
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        case 'Black/White':
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)[1]

                        case _: # default
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # resize the frame if the user has entered valid values in the width and height entry fields
                    if width_entry_value.isdigit() and height_entry_value.isdigit() and int(width_entry_value) > 19 and int(height_entry_value) > 10:
                        width = int(width_entry_value)
                        height = int(height_entry_value)
                        frame = cv2.resize(frame, (width, height))
                        
                        # save processed frame
                        self.processed_frame = frame

                        # if cropping is enabled, draw a rectangle on the frame
                        if self.cropping:
                            self.cropped_frame = frame[
                                int(self.y1 * height / original_height)+1:int(self.y2 * height / original_height)-1,
                                int(self.x1 * width / original_width)+1:int(self.x2 * width / original_width)-1
                            ]
                            if not self.cropping:
                                cv2.rectangle(frame, (int(self.x1 * width / original_width), int(self.y1 * height / original_height)), 
                                            (int(self.x2 * width / original_width), int(self.y2 * height / original_height)), (0, 0, 0), 1)
                            else:
                                cv2.rectangle(frame, (int(self.x1 * width / original_width), int(self.y1 * height / original_height)), 
                                            (int(self.x2 * width / original_width), int(self.y2 * height / original_height)), (0, 255, 0), 1)
                                
                                # swap the coordinates if the user drags the mouse from bottom right to top left
                                if self.x1 > self.x2:
                                    self.x1, self.x2 = self.x2, self.x1
                                if self.y1 > self.y2:
                                    self.y1, self.y2 = self.y2, self.y1

                    # convert the frame to a PIL image and resize it to fit the canvas
                    frame = np.array(frame)
                    frame = Image.fromarray(frame)
                    frame = frame.resize((self.canvas_width, self.canvas_height), Image.ANTIALIAS)
                    frame = ImageTk.PhotoImage(frame)

                    # update the video feed in the canvas
                    self.canvas.itemconfig(self.video_feed, image=frame)
                    self.canvas.image = frame

            # call this function again in 30 milliseconds
            self.after(30, self.update)


    def reset_crop(self):
        """ Resets the cropping variables to their default values """
        self.cropping = False
        self.x1, self.y1, self.x2, self.y2 = None, None, None, None


    def on_mouse_down(self, event):
        """ Handles the event when the mouse button is pressed down in the canvas widget.
            Sets the x1 and y1 coordinates to the location of the mouse click in the canvas widget, converted to the corresponding coordinates in the frame
        """
        self.x1 = int(event.x * (self.width / self.canvas_width))
        self.y1 = int(event.y * (self.height / self.canvas_height))

    def on_mouse_move(self, event):
        """ Handles the event when the mouse is moved while the mouse button is pressed down in the canvas widget.
            Sets the x2 and y2 coordinates to the location of the mouse click in the canvas widget, converted to the corresponding coordinates in the frame
        """
        self.x2 = int(event.x * (self.width / self.canvas_width))
        self.y2 = int(event.y * (self.height / self.canvas_height))

    def on_mouse_up(self, event):
        """
        Handles the event when the mouse button is released in the canvas widget
        Sets the x2 and y2 coordinates to the location of the mouse in the canvas widget, converted to the corresponding coordinates in the frame
        Sets the cropping flag to True, indicating that the user has selected a region to be cropped
        """

        self.x2 = int(event.x * (self.width / self.canvas_width))
        self.y2 = int(event.y * (self.height / self.canvas_height))
        self.cropping = True
