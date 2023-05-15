import os
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as filedialog
import threading
import tensorflow as tf
from tensorflow import keras
from keras.applications import ResNet50
from keras.layers import Dense, GlobalAveragePooling2D, Flatten
from keras.preprocessing.image import ImageDataGenerator
from PIL import Image

class Trainer:
    def __init__(self, master):
        self.master = master
        self.train_thread = None
        self.labels_file = "labels.txt"
        self.model_file = "trained_model.h5"

    def select_dataset_folder(self):
        folder_path = filedialog.askdirectory()
        self.master.dataset_variable.set(folder_path)

    def start_training(self):
        self.master.start_training_button.configure(text="Training ...", state="disabled")
        self.train_thread = threading.Thread(target=self.train)
        self.train_thread.start()

    def train(self):
        # Apply configurations
        batch_size = int(self.master.batch_size_variable.get())
        epochs = int(self.master.epochs_slider.get())
        learning_rate = float(self.master.learning_rate_slider.get())
        self.master.update_epochs_progress(0)

        # Load dataset and create labels
        dataset_folder = self.master.dataset_variable.get()

        if not os.path.isdir(dataset_folder):
            messagebox.showerror("Error", "Please select a valid dataset folder.")
            self.training_in_progress = False
            self.master.start_training_button.configure(text="Start Training", state="normal")
            return

        labels = os.listdir(dataset_folder)
        with open(self.labels_file, "w") as f:
            for index, label in enumerate(labels):
                f.write(f"{index} {label}\n")

        # Derive input shape from images
        sample_image_path = os.path.join(dataset_folder, labels[0], os.listdir(os.path.join(dataset_folder, labels[0]))[0])
        sample_image = Image.open(sample_image_path)
        input_shape = sample_image.size + (3,)  # Add channel dimension

        # Data processing and augmentation
        # Data processing and augmentation
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True
        )

        # Load training data from directories
        train_set = train_datagen.flow_from_directory(
            dataset_folder,
            target_size=input_shape[:2],
            batch_size=batch_size,
            class_mode='categorical',
            shuffle=True
        )

        # Load pre-trained ResNet50 model 
        base_model = tf.keras.applications.ResNet50(weights="imagenet", include_top=False, input_shape=input_shape)

        # Add custom classification layers
        x = base_model.output
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Flatten()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        predictions = tf.keras.layers.Dense(len(labels), activation='softmax')(x)

        # Create the final model
        model = tf.keras.models.Model(inputs=base_model.input, outputs=predictions)

        # Compile the model
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        # Calculate steps per epoch
        steps_per_epoch = max(len(train_set) // batch_size, 5)

        print("TrainSet laenge: ", len(train_set))

        # Configure GPU options
        gpus = tf.config.experimental.list_physical_devices('GPU')
        print ("GPU: ", gpus)
        if gpus:
            tf.config.experimental.set_memory_growth(gpus[0], True)
            tf.config.experimental.set_visible_devices(gpus[0], 'GPU')


        # Convert the ImageDataGenerator to tf.data.Dataset
        train_dataset = tf.data.Dataset.from_generator(
            lambda: train_set,
            output_signature=(
                tf.TensorSpec(shape=(None, *input_shape), dtype=tf.float32),
                tf.TensorSpec(shape=(None, len(labels)), dtype=tf.float32)
            )
        )

        # Optimize data pipeline
        train_dataset = train_dataset.cache().prefetch(tf.data.AUTOTUNE)

        # Train the model
        model.fit(train_dataset, epochs=epochs, steps_per_epoch=steps_per_epoch)

        # Update progress in GUI
        self.master.update_epochs_progress(100)

        # Save the trained model
        model.save(self.model_file)

        print("Training completed.")
        self.master.start_training_button.configure(text="Start Training", state="normal")

        # End the train_thread
        self.train_thread = None
