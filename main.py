import tkinter as tk
import os
import customtkinter as ctk
from customtkinter import set_default_color_theme
from tkinter import messagebox
import cv2
from classes.videocapture import VideoCapture
from classes.imageprocessing import ImageProcessing
from classes.loadmodel import LoadModel
from classes.train import Trainer

set_default_color_theme("dark-blue")

class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Image Capture Tool")
        self.config(bg='#2E2E2E')

        # set minimum size of window (width, height)
        self.minsize(680, 820)
        
        self.init_buttons()

    def init_buttons(self):
        # Add title label
        title_label = tk.Label(self, text="KI-MCR-Projekt", font=("Arial", 60))
        title_label.pack(pady=(100, 0))

        self.load_model_button = ctk.CTkButton(self, text="Load Model", command=self.init_loader_gui, font=("Arial", 40))
        self.capture_images_button = ctk.CTkButton(self, text="Capture Images", command=self.init_capture_gui, font=("Arial", 40))
        self.train_model_button = ctk.CTkButton(self, text="Train Model", command=self.init_trainer_gui, font=("Arial", 40))

        self.load_model_button.configure(
            corner_radius=15,
            border_width=2,
            border_spacing=2,
            border_color="black",
            font=("Arial", 40),
            hover=True,
            anchor="center"
        )

        self.capture_images_button.configure(
            corner_radius=15,
            border_width=2,
            border_spacing=2,
            border_color="black",
            font=("Arial", 40),
            hover=True,
            anchor="center"
        )

        self.train_model_button.configure(
            corner_radius=15,
            border_width=2,
            border_spacing=2,
            border_color="black",
            font=("Arial", 40),
            hover=True,
            anchor="center"
        )

        self.load_model_button.pack(pady=(200, 10))
        self.train_model_button.pack(pady=(10, 10))
        self.capture_images_button.pack(pady=(10, 10))
        


        # Add author label
        author_label = tk.Label(self, text="by Kulcsar, Schmid, Schießl, Würfel", font=("Arial", 12), fg="gray")
        author_label.pack(side=tk.RIGHT, padx=20, pady=10)


    def show_main_buttons(self):
        """ Show the main buttons and hide the capture buttons. """
        # if tkinter.tkapp has object video_capture, stop the video capture
        if hasattr(self, "video_capture"):
            self.video_capture.stop_update()
        
        # wenn self.loadmodel existiert, dann stoppe das laden des models
        if hasattr(self, "loadmodel"):
            self.loadmodel.stop_update()
            self.loadmodel.disconnect_from_arduino()

            
        for widget in self.winfo_children():
            widget.pack_forget()

        self.init_buttons()



    def init_capture_gui(self):
        self.load_model_button.pack_forget()
        self.capture_images_button.pack_forget()
        # forget titel label and author label
        for widget in self.winfo_children():
            widget.pack_forget()

        self.video_capture = VideoCapture(self)
        self.image_processing = ImageProcessing(self)

        # Back button
        self.back_button = ctk.CTkButton(self, text="← Back", command=self.show_main_buttons, fg_color="red")
        self.back_button.pack(side="top", anchor="nw", padx=10, pady=10)


        # Image label entry
        self.label_image = tk.Label(self, text="Enter Image Label:", bg='#2E2E2E', fg='white')
        self.entry_image = ctk.CTkEntry(self)
        

        self.label_interval = tk.Label(self, text="Enter Capture Interval (ms):", bg='#2E2E2E', fg='white')
        self.entry_interval = ctk.CTkEntry(self)

        # Start capture button
        self.start_capture_frame = tk.Frame(self, bg='#2E2E2E')
        self.button = ctk.CTkButton(self.start_capture_frame, text="Start Capture", command=self.start_capture, fg_color="green")


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
        self.file_format_label = ctk.CTkLabel(self.options_frame, text="File format:")
        self.file_format_variable = ctk.StringVar(value="jpg") # default value
        self.file_format_options = ctk.CTkOptionMenu(self.options_frame, variable=self.file_format_variable, values=["jpg", "jpeg", "png", "bmp", "tiff"])

        # Color format, rgb, grayscale or black and white
        self.color_format_label = ctk.CTkLabel(self.options_frame, text="Color format:")
        self.color_format_variable = ctk.StringVar(value="RGB") # default value
        self.color_format_options = ctk.CTkOptionMenu(self.options_frame, variable=self.color_format_variable, values=["RGB", "Grayscale", "Black/White"])




        # reset crop
        self.reset_button = ctk.CTkButton(self, text="Reset Crop", command=self.reset_crop, fg_color="#FF9000")
        
        
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

    def init_loader_gui(self):
        """Initialize the GUI for load Model with filesearch and load button."""
        for widget in self.winfo_children():
            widget.pack_forget()

        self.loadmodel = LoadModel(self)
        # Back button
        self.back_button = ctk.CTkButton(self, text="← Back", command=self.show_main_buttons, fg_color="red")
        self.back_button.pack(side="top", anchor="nw", padx=10, pady=10)


        # Find all .h5 and .txt files in directory
        self.h5_files = [] # empty list for .h5 files
        self.txt_files = [] # empty list for .txt files

        # search for .h5 and .txt files in the current directory
        for file in os.listdir():
            if file.endswith(".h5"):
                self.h5_files.append(file)
            elif file.endswith(".txt"):
                self.txt_files.append(file)

        self.load_connect_frame = ctk.CTkFrame(self)

        # create a label and a dropdown menu for selecting the .h5 file
        self.h5_frame = ctk.CTkFrame(self)
        self.h5_label = ctk.CTkLabel(self.h5_frame, text="Select .h5 file:")

        self.load_model_button = ctk.CTkButton(self.load_connect_frame, text="Load Model", command=self.loadmodel.load_model, state="disabled")
        self.connect_button = ctk.CTkButton(self.load_connect_frame, text="Connect to Arduino", command=self.loadmodel.connect_to_arduino, fg_color="orange", state="disabled")

        if len(self.h5_files) == 0:
            self.h5_variable = ctk.StringVar(value="  No .h5 files found.  ")
        else:
            self.h5_variable = ctk.StringVar(value=self.h5_files[0]) # set the default value to the first .h5 file in the list
        self.h5_dropdown = ctk.CTkOptionMenu(self.h5_frame, variable=self.h5_variable, values=self.h5_files)
        self.browse_h5_button = ctk.CTkButton(self.h5_frame, text="Browse", command=self.loadmodel.browse_file_h5)

        # create a label and a dropdown menu for selecting the .txt file
        self.txt_frame = ctk.CTkFrame(self)
        self.txt_label = ctk.CTkLabel(self.txt_frame, text="Select .txt file:")
        if len(self.txt_files) == 0:
            self.txt_variable = ctk.StringVar(value="No .txt files found.")
        else:
            self.txt_variable = ctk.StringVar(value=self.txt_files[0]) # set the default value to the first .txt file in the list
        self.txt_dropdown = ctk.CTkOptionMenu(self.txt_frame, variable=self.txt_variable, values=self.txt_files)
        self.browse_txt_button = ctk.CTkButton(self.txt_frame, text="Browse", command=self.loadmodel.browse_file_txt)

        if len(self.h5_files) == 0 or len(self.txt_files) == 0:
            self.load_model_button.configure(state="disabled", fg_color="#FF6000")
        else:
            self.load_model_button.configure(state="normal", fg_color="#026c45")

        # pack the widgets into the frames
        self.h5_label.pack(pady=10)
        self.h5_dropdown.pack(pady=10)
        self.browse_h5_button.pack(pady=10, padx=(10,0))

        self.txt_label.pack(pady=10)
        self.txt_dropdown.pack(pady=10)
        self.browse_txt_button.pack(pady=10, padx=(10,0))

        self.h5_frame.pack(padx=20, pady=10, fill="x")
        self.txt_frame.pack(padx=20, pady=10, fill="x")
        self.load_connect_frame.pack(padx=20, pady=10, fill="x")

        self.load_model_button.pack(pady=10)
        self.connect_button.pack(pady=10)



    def init_trainer_gui(self):
        """Initialize the GUI for the trainer."""
        for widget in self.winfo_children():
            widget.pack_forget()

        self.trainer = Trainer(self)

        # Back button
        self.back_button = ctk.CTkButton(self, text="← Back", command=self.show_main_buttons, fg_color="red")
        self.back_button.pack(side="top", anchor="nw", padx=10, pady=10)

        # Training parameters
        self.parameters_frame = ctk.CTkFrame(self)
        self.parameters_label = ctk.CTkLabel(self.parameters_frame, text="Training Parameters:")

        self.batch_size_label = ctk.CTkLabel(self.parameters_frame, text="Batch Size:")
        self.batch_size_slider = ctk.CTkSlider(self.parameters_frame, from_=16, to=256, orientation="horizontal", command=self.update_batch_size)
        self.batch_size_min_label = ctk.CTkLabel(self.parameters_frame, text="16")
        self.batch_size_max_label = ctk.CTkLabel(self.parameters_frame, text="256")
        self.batch_size_value_label = ctk.CTkLabel(self.parameters_frame, text="16")

        self.epochs_label = ctk.CTkLabel(self.parameters_frame, text="Epochs:")
        self.epochs_slider = ctk.CTkSlider(self.parameters_frame, from_=10, to=100, orientation="horizontal", command=self.update_epochs)
        self.epochs_min_label = ctk.CTkLabel(self.parameters_frame, text="10")
        self.epochs_max_label = ctk.CTkLabel(self.parameters_frame, text="100")
        self.epochs_value_label = ctk.CTkLabel(self.parameters_frame, text="10")

        self.learning_rate_label = ctk.CTkLabel(self.parameters_frame, text="Learning Rate:")
        self.learning_rate_slider = ctk.CTkSlider(self.parameters_frame, from_=0.01, to=1.00, orientation="horizontal", command=self.update_learning_rate)
        self.learning_rate_min_label = ctk.CTkLabel(self.parameters_frame, text="0.01")
        self.learning_rate_max_label = ctk.CTkLabel(self.parameters_frame, text="1.00")
        self.learning_rate_value_label = ctk.CTkLabel(self.parameters_frame, text="0.01")


        self.batch_size_slider.configure(number_of_steps=240)
        self.epochs_slider.configure(number_of_steps=90)
        self.learning_rate_slider.configure(number_of_steps=99)


        self.parameters_frame.pack(padx=20, pady=10, fill="x")
        self.parameters_label.grid(row=0, column=0, columnspan=4, pady=10)

        self.batch_size_label.grid(row=1, column=0, pady=10)
        self.batch_size_min_label.grid(row=1, column=1, padx=(0, 10))
        self.batch_size_slider.grid(row=1, column=2, padx=(0, 10))
        self.batch_size_max_label.grid(row=1, column=3)
        self.batch_size_value_label.grid(row=1, column=4, padx=(10, 0))

        self.epochs_label.grid(row=2, column=0, pady=10)
        self.epochs_min_label.grid(row=2, column=1, padx=(0, 10))
        self.epochs_slider.grid(row=2, column=2, padx=(0, 10))
        self.epochs_max_label.grid(row=2, column=3)
        self.epochs_value_label.grid(row=2, column=4, padx=(10, 0))

        self.learning_rate_label.grid(row=3, column=0, pady=10)
        self.learning_rate_min_label.grid(row=3, column=1, padx=(0, 10))
        self.learning_rate_slider.grid(row=3, column=2, padx=(0, 10))
        self.learning_rate_max_label.grid(row=3, column=3)
        self.learning_rate_value_label.grid(row=3, column=4, padx=(10, 0))

        # Dataset selection
        self.dataset_frame = ctk.CTkFrame(self)
        self.dataset_label = ctk.CTkLabel(self.dataset_frame, text="Select Dataset Folder:")
        self.dataset_variable = ctk.StringVar(value="  No Folder selected.  ")
        self.dataset_entry = ctk.CTkEntry(self.dataset_frame, textvariable=self.dataset_variable, state="disabled")
        self.browse_dataset_button = ctk.CTkButton(self.dataset_frame, text="Browse", command=self.trainer.select_dataset_folder)
        self.dataset_frame.pack(padx=20, pady=10, fill="x")
        self.dataset_label.pack(pady=10)
        self.dataset_entry.pack(pady=10)
        self.browse_dataset_button.pack(pady=10)

        # search in the current directory for the dataset folder captures/
        if os.path.isdir("captures"):
            self.dataset_variable.set("captures")

        # Progress bar
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Training Progress:")
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, orientation="horizontal")
        self.progress_frame.pack(padx=20, pady=10, fill="x")
        self.progress_label.pack(pady=10)
        self.progress_bar.pack(pady=10)

        # Start training button
        self.start_training_button = ctk.CTkButton(self, text="Start Training", command=self.trainer.start_training)
        self.start_training_button.pack(pady=10)

    def update_epochs_progress(self, progress):
        """Update the epochs progress."""
        self.progress_bar.set(progress)
        self.progress_bar.update()

    def update_batch_size(self, value):
        current_value = self.batch_size_slider.get()
        self.batch_size_value_label.configure(text=str(current_value))

    def update_epochs(self, value):
        current_value = self.epochs_slider.get()
        self.epochs_value_label.configure(text=str(current_value))
        
    def update_learning_rate(self, value):
        current_value = self.learning_rate_slider.get()
        self.learning_rate_value_label.configure(text="{:.4f}".format(current_value))




    


    def reset_crop(self):
        self.video_capture.reset_crop()

    def update_counter(self):
        if not self.stop_counter:
            self.button.configure(text="Stop Capture: " + str(self.image_processing.counter))
            self.after(200, self.update_counter)

    def validate_resolution_callback(self, *args):
        """Validate the entered width value and calculate the height based on the aspect ratio of the camera."""

        # Get the value entered in the width entry widget
        width_entry_value = self.width_entry.get()
        if width_entry_value.isdigit():
            width = int(width_entry_value)

            # Check if the entered width is valid
            if width <= self.video_capture.cap.get(cv2.CAP_PROP_FRAME_WIDTH) and width > 19:
                # Calculate the height based on the aspect ratio of the camera
                height = int(width / self.video_capture.cap.get(cv2.CAP_PROP_FRAME_WIDTH) * self.video_capture.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                # Make the height entry widget editable and insert the calculated height
                self.height_entry.configure(state='normal')
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(height))
                # Make the height entry widget read-only
                self.height_entry.configure(state='readonly')
                # Set the text color of the height entry widget to black
                self.height_entry.config(fg='black')
            else:
                # If the entered width is not valid, reset the width and height entry widgets to their previous values
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(int(self.video_capture.cap.get(cv2.CAP_PROP_FRAME_WIDTH))))
                self.height_entry.configure(state='normal')
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(int(self.video_capture.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
                self.height_entry.configure(state='readonly')
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
            self.button.configure(text="Stop Capture: " + str(self.image_processing.counter), command=self.stop_capture, fg_color='#FF0000')
            self.update_counter()
        else:
            messagebox.showerror("Error", "Please enter a label for the image.")

    def stop_capture(self):
        """Stop capturing images."""
        self.image_processing.stop_capture()
        self.stop_counter = True
        self.button.configure(text="Start Capture", command=self.start_capture, fg_color="green")




if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()



