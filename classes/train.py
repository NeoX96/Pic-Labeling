import os
import tkinter as tk
import tkinter.filedialog as filedialog
import threading
from keras.applications import ResNet50
from keras.layers import Dense, GlobalAveragePooling2D
from keras.models import Model
from keras.optimizers import Adam
from PIL import Image
from keras.preprocessing.image import ImageDataGenerator


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
        batch_size = self.master.batch_size_slider.get()
        epochs = self.master.epochs_slider.get()
        learning_rate = self.master.learning_rate_slider.get()

        # Load dataset and create labels
        dataset_folder = self.master.dataset_variable.get()
        labels = os.listdir(dataset_folder)
        with open(self.labels_file, "w") as f:
            f.write("\n".join(labels))

        # Derive input shape from images
        sample_image_path = os.path.join(dataset_folder, labels[0], os.listdir(os.path.join(dataset_folder, labels[0]))[0])
        sample_image = Image.open(sample_image_path)
        input_shape = sample_image.size + (3,)  # Add channel dimension

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
        base_model = ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)

        # Add custom classification layers
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(256, activation='relu')(x)
        predictions = Dense(len(labels), activation='softmax')(x)

        # Create the final model
        model = Model(inputs=base_model.input, outputs=predictions)

        # Compile the model
        model.compile(optimizer=Adam(learning_rate=learning_rate),
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        # Train the model
        model.fit(train_set, epochs=epochs)

        # Save the trained model
        model.save(self.model_file)

        print("Training completed.")
        self.master.start_training_button.configure(text="Start Training", state="normal")

        # End the train_thread
        self.train_thread = None
