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
import serial
import serial.tools.list_ports
import time

class LoadModel:
    def __init__(self, master):
        """Initialize the LoadModel class."""
        self.master = master
        self.canvas = Canvas(self.master, bg="black", cursor='cross')

        self.cap = cv2.VideoCapture(0)
        self.video_feed = self.canvas.create_image(0, 0, image=None, anchor=tk.NW)

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.aspect_ratio = self.width / self.height

        self.canvas_width = 400
        self.canvas_height = int(self.canvas_width / self.aspect_ratio)
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        
        self.arduino_port = None
        self.connected = None


    def update(self):
        """Update the video feed in the canvas."""
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # flip frame to mirror the video feed
                frame = cv2.flip(frame, 1)

                # Calculate the remaining height of the window
                frame_height = self.master.back_button.winfo_height()
                frame_height += self.master.h5_frame.winfo_height()
                frame_height += self.master.txt_frame.winfo_height()
                frame_height += self.master.load_connect_frame.winfo_height()
                remaining_height = self.master.winfo_height() - frame_height - self.canvas_height + 80

                # Calculate the maximum frame height based on the aspect ratio
                max_frame_height = remaining_height

                # Calculate the maximum frame width based on the maximum frame height and aspect ratio
                max_frame_width = int(max_frame_height * self.aspect_ratio)

                # Resize the input image to the desired size
                resized_frame = cv2.resize(frame, (self.input_width, self.input_height), interpolation=cv2.INTER_LANCZOS4)
                resized_frame_canvas = cv2.resize(frame, (max_frame_width, max_frame_height), interpolation=cv2.INTER_LANCZOS4)

                # Convert the input image to a numpy array and normalize it
                normalized_frame = np.asarray(resized_frame, dtype=np.float32)
                normalized_frame = (normalized_frame / 127.5) - 1

                # Pass the input image to the model and get the predictions
                prediction = self.model.predict(normalized_frame[np.newaxis, ...], verbose=0)

                index = np.argmax(prediction)
                class_name = self.class_names[index]
                confidence_score = prediction[0][index]

                # Add label to the bottom right corner of the image
                frame_with_text = cv2.cvtColor(resized_frame_canvas, cv2.COLOR_BGR2RGB)
                cv2.putText(frame_with_text, f"{class_name[2:]}: {np.round(confidence_score * 100)}%",
                            (int(0.05 * max_frame_width), max_frame_height - int(0.05 * max_frame_height)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # Convert the frame to a PIL image and then to PhotoImage
                pil_image = Image.fromarray(frame_with_text)
                frame_for_canvas = ImageTk.PhotoImage(pil_image)

                # Update the canvas image
                self.canvas.config(width=max_frame_width, height=max_frame_height)
                self.canvas.itemconfig(self.video_feed, image=frame_for_canvas)
                self.canvas.image = frame_for_canvas

                if self.connected:
                    # if led is on, turn it off and vice-versa.
                    if self.arduino.readline() == b'1\r\n':
                        self.arduino.write(b'0')
                    else:
                        self.arduino.write(b'1')
                        print("Commands sent to Arduino with prediction")

        # Calculate the delay based on the current FPS of the camera
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps)  # Convert FPS to delay in milliseconds

        # Call this function again in 30 milliseconds
        self.master.after(delay, self.update)






    def stop_update(self):
        """Stop the video feed update loop."""
        self.cap.release()
        cv2.destroyAllWindows()

    def load_model(self):
        """Load the selected model. Check for the Com Port of the Arduino - self.arduino_port
            and if it is connected, enable the connect button.
        """
        print("Loading model...")
        self.master.load_model_button.configure(text="... Loading ....", fg_color="green")
        
        self.model = load_model(self.master.h5_variable.get(), compile=False)
        self.class_names = open(self.master.txt_variable.get(), "r").readlines()
        self.expected_input_shape = self.model.input_shape
        self.input_height, self.input_width, self.input_channels = self.expected_input_shape[1:]  # Extrahiere Höhe, Breite und Kanäle


        print("Model loaded.")

        # check if canvas pack does not exist
        if not self.canvas.winfo_ismapped():
            self.master.update()
            self.update()
            self.canvas.pack()
            
        self.disconnect_from_arduino()

        self.master.load_model_button.configure(text="Load Model", fg_color="#FF9000")
        self.master.connect_button.configure(state="normal", fg_color="#026c45")
        self.check_arduino_port()

    def check_arduino_port(self):
        self.myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        
        # if in myports is arduino than write it to arduino_port
        for port in self.myports:
            if "Arduino" in port[1]:
                self.arduino_port = port[0]
                self.master.connect_button.configure(text="Connect to Arduino", state="normal")

            else:
                self.arduino_port = None
                self.master.connect_button.configure(text="no Arduino connected", state="disabled")



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


    def connect_to_arduino(self):
        """Connect to Arduino and send data to it.
        If Arduino is not connected, disable the button.
        """

        self.master.connect_button.configure(text="Connecting to Arduino ...")
        self.myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]

        for port in self.myports:
            if "Arduino" in port[1]:
                self.arduino_port = port[0]
                self.master.connect_button.configure(text="Connect to Arduino", state="normal")
                self.arduino = serial.Serial(port=self.arduino_port, timeout=.5)

                # Handshake with Arduino
                self.arduino.setDTR(False)
                time.sleep(1)
                self.arduino.flushInput()
                self.arduino.setDTR(True)
                
                self.master.connect_button.configure(text="Connected", fg_color="green", state="normal")

                self.arduino.open()
                self.connected = self.arduino.is_open

            else:
                self.arduino_port = None
                self.master.connect_button.configure(text="no Arduino connected", state="disabled")
           
    def disconnect_from_arduino(self):
        """Disconnect from Arduino."""
    
        if self.arduino_port != None:
            self.arduino.close()

        self.master.connect_button.configure(text="Connect to Arduino", fg_color="#026c45", state="normal")
        self.connected = False