# classes/loadmodel.py
import os
import tkinter as tk
import tkinter.filedialog as filedialog
from tensorflow.keras.models import load_model
import customtkinter as ctk


class LoadModel:
    def __init__(self, master):
        self.master = master

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
    
    def load_model(self):
        """Load the selected model."""
        print ("Loading model...")
        self.master.model = load_model(self.master.h5_variable.get())
        print ("Model loaded.")

