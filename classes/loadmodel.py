# classes/loadmodel.py
import os
import tkinter as tk
from tkinter import Canvas
import tkinter.filedialog as filedialog
from keras.models import load_model
import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk

class LoadModel:
    def __init__(self, master):
        self.master = master
        self.canvas = Canvas(self.master, bg="black", cursor='cross')

        self.cap = cv2.VideoCapture(0)
        self.video_feed = self.canvas.create_image(0, 0, image=None, anchor=tk.NW)

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.aspect_ratio = self.width / self.height

        self.canvas_width = 800
        self.canvas_height = int(self.canvas_width / self.aspect_ratio)
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        
        #


    def update(self):
        """Update the video feed in the canvas."""
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # resize the input image to (224, 224) using OpenCV
                resized_frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
                resized_frame_canvas = cv2.resize(frame, (self.canvas_width, self.canvas_height), interpolation=cv2.INTER_AREA)

                # convert the input image to a numpy array and normalize it
                normalized_frame = np.asarray(resized_frame, dtype=np.float32)
                normalized_frame = (normalized_frame / 127.5) - 1

                # pass the input image to the model and get the predictions
                prediction = self.model.predict(normalized_frame[np.newaxis, ...], verbose=0)

                index = np.argmax(prediction)
                class_name = self.class_names[index]
                confidence_score = prediction[0][index]

                # Add label to the bottom right corner of the image
                frame_with_text = cv2.cvtColor(resized_frame_canvas, cv2.COLOR_BGR2RGB)
                cv2.putText(frame_with_text, f"{class_name[2:]}: {np.round(confidence_score * 100)}%",
                            (int(0.05 * self.canvas_width), int(0.95 * self.canvas_height)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)


                # convert the frame to a PIL image and then to PhotoImage
                pil_image = Image.fromarray(frame_with_text)
                frame_for_canvas = ImageTk.PhotoImage(pil_image)

                # update the canvas image
                self.canvas.itemconfig(self.video_feed, image=frame_for_canvas)
                self.canvas.image = frame_for_canvas

        # call this function again in 30 milliseconds
        self.master.after(30, self.update)



    def stop_update(self):
        """Stop the video feed update loop."""
        self.cap.release()
        cv2.destroyAllWindows()

    def load_model(self):
        """Load the selected model."""
        print("Loading model...")
        self.master.load_model_button.configure(text="... Loading ....", fg_color="green")
        self.master.update()
        self.model = load_model(self.master.h5_variable.get(), compile=False)
        self.class_names = open(self.master.txt_variable.get(), "r").readlines()
        print("Model loaded.")
        self.update()
        self.canvas.pack(fill=tk.BOTH)
        self.master.load_model_button.configure(text="Load Model", fg_color="#FF9000")





    def browse_file_h5(self):
        """Open file dialog to browse for .h5 file"""
        filetypes = [("H5 files", "*.h5")]
        file_path = filedialog.askopenfilename(filetypes=filetypes, parent=self.master)
        if file_path:
            self.master.h5_files.append(file_path)
            self.master.h5_dropdown.configure(values=self.master.h5_files)
            self.master.h5_variable.set(file_path)
            self.master.load_model_button.configure(state="normal")

    def browse_file_txt(self):
        """Open file dialog to browse for .txt file"""
        filetypes = [("Text files", "*.txt")]
        file_path = filedialog.askopenfilename(filetypes=filetypes, parent=self.master)
        if file_path:
            self.master.txt_files.append(file_path)
            self.master.txt_dropdown.configure(values=self.master.txt_files)
            self.master.txt_variable.set(file_path)
            self.master.load_model_button.configure(state="normal")



