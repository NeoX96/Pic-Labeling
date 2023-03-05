import os
import cv2

class ImageProcessing:
    """
    Konstruktor, um eine Instanz der ImageProcessing-Klasse zu erstellen.
    @param master: Hauptfenster, in dem das Video angezeigt wird.
    """
    def __init__(self, master):
        self.master = master
        self.label = ""
        self.counter = 1
        self.interval = 200
        self.should_stop_capture = False
        self.width = 0
        self.height = 0


    def start_capture(self):
        """
        Startet den Bildaufnahmeprozess. Überprüft, ob ein Label für die Bilder eingegeben wurde und ob der Ordner für die Bilder bereits existiert. 
        """
        if not self.label:
            return
        
        if not os.path.exists(f"captures/{self.label}"):
            os.makedirs(f"captures/{self.label}")
            self.counter = 1
        
        self.should_stop_capture = False
        self.capture_images()

    def capture_images(self):
        """
        Speichert das aktuelle Bild in einem Ordner mit dem Label als Name.
        """

        frame = self.master.video_capture.processed_frame
        
        # Bug?? weil ich bereits in der Klasse VideoCapture das Bild in RGB umgewandelt habe, im Canvas wird es richtig angezeigt, aber hier nicht mehr
        if self.master.video_capture.color == "RGB":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if self.should_stop_capture:
            return
            
        self.width = int(self.master.width_entry.get())
        self.height = int(self.master.height_entry.get())




        if self.master.video_capture.cropping:
            frame = self.master.video_capture.cropped_frame
        else:
            frame = cv2.resize(frame, (self.width, self.height))


        selected_format = self.master.file_format_variable.get()
            
        # Speichert das Bild im ausgewählten Format, label und counter als Dateinamen
        filename = f"{self.label}_{self.counter}.{selected_format}"

        path = os.path.join("captures", self.label, filename)
        cv2.imwrite(path, frame)
        self.counter += 1
        self.master.after(self.interval, self.capture_images)

    def stop_capture(self):
        """
        Stoppt den Bildaufnahmeprozess.
        """
        self.should_stop_capture = True
        self.master.after_cancel(self.capture_images)
