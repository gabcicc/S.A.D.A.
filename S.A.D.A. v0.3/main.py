import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox


class ImageAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Detecting anomalies")
        self.image_path = None
        self.image = None
        self.original_image = None
        self.selection = None
        self.rect = None
        self.start_x = None
        self.start_y = None

        self.threshold = tk.IntVar(value=100)
        self.color = tk.StringVar(value="#FF0000")

        self.create_gui()

    def create_gui(self):
        """
        Crea l'interfaccia grafica.
        """
        self.select_button = tk.Button(self.root, text="Select Image", command=self.load_image)
        self.select_button.pack(side=tk.TOP, pady=10)

        config_frame = tk.Frame(self.root)
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(config_frame, text="Threshold:").pack(side=tk.LEFT)
        tk.Entry(config_frame, textvariable=self.threshold, width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(config_frame, text="Anomaly Color:").pack(side=tk.LEFT)
        tk.Entry(config_frame, textvariable=self.color, width=10).pack(side=tk.LEFT, padx=5)

        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.select_area_button = tk.Button(button_frame, text="Select Area", command=self.enable_selection,
                                            state=tk.DISABLED)
        self.select_area_button.pack(side=tk.LEFT, padx=5)

        self.analyze_button = tk.Button(button_frame, text="Analyze Image", command=self.analyze_image,
                                        state=tk.DISABLED)
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(button_frame, text="Save Image", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.back_button = tk.Button(button_frame, text="Back", command=self.go_home, state=tk.DISABLED)
        self.back_button.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="black")
        self.canvas.pack(expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def load_image(self):
        """
        Carica un'immagine dal percorso specificato.
        """
        self.image_path = filedialog.askopenfilename(filetypes=[
            ("JPEG files", "*.jpg;*.jpeg"),
            ("PNG files", "*.png"),
            ("BMP files", "*.bmp"),
            ("TIFF files", "*.tiff"),
            ("All files", "*.*")
        ])
        if not self.image_path:
            return

        try:
            self.image = Image.open(self.image_path)
            if self.image.mode == 'RGBA':
                self.image = self.image.convert('RGB')

            # Ridimensiona l'immagine per adattarla alla finestra della GUI
            max_size = (800, 600)
            self.image.thumbnail(max_size, Image.LANCZOS)
            self.original_image = self.image.copy()

            self.display_image_on_canvas(self.image)
            self.select_area_button.config(state=tk.NORMAL)
            self.analyze_button.config(state=tk.NORMAL)
            self.back_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

    def display_image_on_canvas(self, image):
        """
        Visualizza l'immagine nella GUI.
        """
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image((self.canvas.winfo_width() - image.width) // 2,
                                 (self.canvas.winfo_height() - image.height) // 2,
                                 anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def enable_selection(self):
        """
        Abilita la selezione dell'area.
        """
        self.selection = None
        self.canvas.config(cursor="cross")

    def on_button_press(self, event):
        """
        Gestisce l'evento di pressione del mouse per iniziare la selezione dell'area.
        """
        if not self.canvas.config()['cursor'][-1] == "cross":
            return
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_move_press(self, event):
        """
        Gestisce l'evento di movimento del mouse per aggiornare la selezione dell'area.
        """
        if not self.canvas.config()['cursor'][-1] == "cross":
            return
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        """
        Gestisce l'evento di rilascio del mouse per completare la selezione dell'area.
        """
        if not self.canvas.config()['cursor'][-1] == "cross":
            return
        self.selection = (self.start_x, self.start_y, event.x, event.y)
        self.canvas.config(cursor="")

    def find_anomalies(self, image, threshold):
        """
        Trova le anomalie nell'immagine, assumendo che le aree più scure rappresentino anomalie.
        """
        image_array = np.array(image)
        anomalies = image_array[:, :, 0] < threshold
        return anomalies

    def highlight_anomalies(self, image, anomalies, color):
        """
        Evidenzia le anomalie in rosso sull'immagine.
        """
        highlighted_image = np.array(image).copy()
        color = [int(color[i:i + 2], 16) for i in (1, 3, 5)]  # Convert hex color to RGB
        highlighted_image[anomalies] = color
        return Image.fromarray(highlighted_image)

    def analyze_image(self):
        """
        Esegue l'analisi delle anomalie sull'area selezionata o sull'intera immagine.
        """
        threshold = self.threshold.get()
        color = self.color.get()

        if self.selection:
            x1, y1, x2, y2 = self.selection
            cropped_image = self.original_image.crop((x1, y1, x2, y2))

            # Ridimensiona la parte selezionata per adattarla alla finestra della GUI
            max_size = (800, 600)
            cropped_image.thumbnail(max_size, Image.LANCZOS)

            anomalies = self.find_anomalies(cropped_image, threshold)
            highlighted_image = self.highlight_anomalies(cropped_image, anomalies, color)
            self.image = highlighted_image

            # Centra l'immagine elaborata nella GUI
            self.display_image_on_canvas(self.image)
        else:
            anomalies = self.find_anomalies(self.image, threshold)
            highlighted_image = self.highlight_anomalies(self.image, anomalies, color)
            self.image = highlighted_image
            self.display_image_on_canvas(self.image)

        self.save_button.config(state=tk.NORMAL)

    def save_image(self):
        """
        Salva l'immagine elaborata.
        """
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("BMP files", "*.bmp"),
            ("TIFF files", "*.tiff"),
            ("All files", "*.*")
        ])
        if save_path:
            self.image.save(save_path)
            messagebox.showinfo("Image Saved", f"Image saved to {save_path}")

    def go_home(self):
        """
        Torna alla visualizzazione originale dell'immagine caricata.
        """
        self.image = self.original_image.copy()
        self.selection = None
        self.display_image_on_canvas(self.image)
        self.canvas.config(cursor="")
        self.save_button.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    analyzer = ImageAnalyzer()
    analyzer.run()
