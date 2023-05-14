import os
import tkinter as tk
import tkinter.filedialog as filedialog
import threading


class Trainer:
    def __init__(self, master):
        self.master = master

    def select_dataset_folder(self):
        folder_path = filedialog.askdirectory()
        self.master.dataset_variable.set(folder_path)

    def start_training(self):
        self.master.start_training_button.configure(text="Training ...", state="disabled")
        self.train_thread = threading.Thread(target=self.train)
        self.train_thread.start()

    def train(self):
        """Train the model."""
        print("Training ...")
        self.master.start_training_button.configure(text="Training ...", state="disabled")