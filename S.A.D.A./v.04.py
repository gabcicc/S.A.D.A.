import numpy as np
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

class ImageAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Anomaly Detection Assistant (S.A.D.A.)")
        self.image_path = None
        self.image = None
        self.original_image = None
        self.polygon_points = []
        self.poly_line = None

        self.history = []
        self.history_index = -1

        self.threshold = tk.IntVar(value=100)
        self.color = tk.StringVar(value="#FF0000")

        self.logo_image = None
        self.logo_id = None

        self.create_gui()
        self.load_logo()

    def load_logo(self):
        """
        Carica il logo e lo visualizza al centro del canvas.
        """
        script_dir = os.path.dirname(__file__)  # Directory del file di script
        logo_path = os.path.join(script_dir, "logo_SADA_.png")
        self.logo_image = Image.open(logo_path)
        self.root.after(100, self.resize_logo)  # Attendere un breve momento prima di ridimensionare il logo
        self.root.bind("<Configure>", self.on_resize)  # Bind resize event

    def move_logo_to_top_right(self):
        """
        Ridimensiona il logo a dimensioni precise e lo sposta in alto a destra della GUI.
        """
        if self.logo_image:
            logo_width = 100  # Larghezza fissa del logo in pixel
            logo_height = 100  # Altezza fissa del logo in pixel
            self.logo_image_resized = self.logo_image.resize((logo_width, logo_height), Image.LANCZOS)
            self.tk_logo_image = ImageTk.PhotoImage(self.logo_image_resized)

            # Rimuovi il logo precedente, se esiste
            self.logo_label.pack_forget()
            self.logo_label.config(image=self.tk_logo_image)
            self.logo_label.image = self.tk_logo_image  # Mantiene un riferimento all'immagine per evitare che venga garbage-collected
            self.logo_label.pack(side=tk.RIGHT, padx=10)  # Posiziona l'etichetta in alto a destra

    def hide_center_logo(self):
        """
        Nasconde il logo al centro del canvas.
        """
        if self.logo_id:
            self.canvas.delete(self.logo_id)
            self.logo_id = None
    def resize_logo(self):
        """
        Ridimensiona il logo in base alle dimensioni della finestra e lo visualizza al centro.
        """
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width > 0 and canvas_height > 0:
            logo_size = min(canvas_width, canvas_height) // 2
            if logo_size > 0:  # Assicurarsi che logo_size sia valido
                self.logo_image_resized = self.logo_image.resize((logo_size, logo_size), Image.LANCZOS)
                self.tk_logo_image = ImageTk.PhotoImage(self.logo_image_resized)

                if self.logo_id:
                    self.canvas.delete(self.logo_id)
                self.logo_id = self.canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    anchor=tk.CENTER, image=self.tk_logo_image
                )

    def on_resize(self, event):
        """
        Callback per l'evento di ridimensionamento della finestra.
        """
        if not self.image:  # Chiama resize_logo solo se non è stata ancora caricata un'immagine
            self.resize_logo()

    def create_gui(self):
        """
        Crea l'interfaccia grafica.
        """
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.select_button = tk.Button(top_frame, text="Select Image", command=self.load_image)
        self.select_button.pack(side=tk.LEFT, pady=10)

        self.logo_label = tk.Label(top_frame)  # Aggiungi un'etichetta per il logo
        self.logo_label.pack(side=tk.RIGHT, padx=10)
        self.logo_label.pack_forget()  # Nasconde il logo all'inizio

        config_frame = tk.Frame(self.root)
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(config_frame, text="Threshold:").pack(side=tk.LEFT)
        tk.Entry(config_frame, textvariable=self.threshold, width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(config_frame, text="Anomaly Color:").pack(side=tk.LEFT)

        # Dropdown per selezionare il colore
        color_options = ["Red", "White", "Blue", "Green", "Black"]
        self.color_combobox = ttk.Combobox(config_frame, textvariable=self.color, values=color_options,
                                           state="readonly")
        self.color_combobox.set("Red")  # Imposta il colore di default
        self.color_combobox.pack(side=tk.LEFT, padx=5)

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

        self.undo_button = tk.Button(button_frame, text="Undo", command=self.undo, state=tk.DISABLED)
        self.undo_button.pack(side=tk.LEFT, padx=5)

        self.redo_button = tk.Button(button_frame, text="Redo", command=self.redo, state=tk.DISABLED)
        self.redo_button.pack(side=tk.LEFT, padx=5)

        self.back_button = tk.Button(button_frame, text="Back", command=self.go_home, state=tk.DISABLED)
        self.back_button.pack(side=tk.LEFT, padx=5)

        self.zoom_in_button = tk.Button(button_frame, text="Zoom In", command=self.zoom_in, state=tk.DISABLED)
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)

        self.zoom_out_button = tk.Button(button_frame, text="Zoom Out", command=self.zoom_out, state=tk.DISABLED)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="black")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Double-Button-1>", self.on_button_double_click)

        self.status_bar = tk.Label(self.root, text="Status: Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.load_logo()  # Carica il logo all'inizio

    def update_status(self, message):
        self.status_bar.config(text=f"Status: {message}")

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
            self.zoom_in_button.config(state=tk.NORMAL)
            self.zoom_out_button.config(state=tk.NORMAL)
            self.update_status("Image loaded")

            # Nasconde il logo al centro e sposta il logo in alto a destra
            self.hide_center_logo()
            self.move_logo_to_top_right()

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

        # Rimuovi il logo precedente, se esiste
        if self.logo_id:
            self.canvas.delete(self.logo_id)
        self.logo_id = None

    def enable_selection(self):
        """
        Abilita la selezione dell'area.
        """
        self.polygon_points = []
        self.canvas.delete("all")  # Rimuove tutti i disegni dal canvas
        self.display_image_on_canvas(self.image)
        self.canvas.config(cursor="cross")
        self.update_status("Select area by clicking points, double-click to complete")

    def on_button_press(self, event):
        """
        Gestisce l'evento di pressione del mouse per iniziare o continuare la selezione del poligono.
        """
        if not self.canvas.config()['cursor'][-1] == "cross":
            return

        self.polygon_points.append((event.x, event.y))

        # Disegna un cerchio per ogni punto cliccato
        radius = 3
        self.canvas.create_oval(event.x - radius, event.y - radius, event.x + radius, event.y + radius, fill='red')

        if self.poly_line:
            self.canvas.delete(self.poly_line)

        if len(self.polygon_points) > 1:
            self.poly_line = self.canvas.create_line(
                *sum(self.polygon_points, ()),  # flatten the list of tuples
                fill='red'
            )

    def on_move_press(self, event):
        """
        Gestisce l'evento di movimento del mouse per aggiornare la selezione dell'area.
        """
        pass  # Non è necessario fare nulla durante il movimento del mouse per la selezione del poligono

    def on_button_release(self, event):
        """
        Gestisce l'evento di rilascio del mouse per completare la selezione dell'area.
        """
        pass  # Non è necessario fare nulla durante il rilascio del mouse per la selezione del poligono
    def on_button_double_click(self, event):
        """
        Gestisce il doppio clic del mouse per completare la selezione del poligono.
        """
        if len(self.polygon_points) > 2:
            self.canvas.create_polygon(self.polygon_points, outline='red', fill='', width=2)
            self.canvas.config(cursor="")
            self.update_status("Polygon area selected")

    def find_anomalies(self, image, threshold):
        """
        Trova le anomalie nell'immagine, assumendo che le aree più scure rappresentino anomalie.
        """
        image_array = np.array(image)
        anomalies = image_array[:, :, 0] < threshold
        return anomalies

    def highlight_anomalies(self, image, anomalies, color):
        """
        Evidenzia le anomalie nell'immagine con il colore selezionato.
        """
        color_map = {
            "Red": [255, 0, 0],
            "White": [255, 255, 255],
            "Blue": [0, 0, 255],
            "Green": [0, 255, 0],
            "Black": [0, 0, 0]
        }
        rgb_color = color_map[color]

        highlighted_image = np.array(image).copy()
        highlighted_image[anomalies] = rgb_color
        return Image.fromarray(highlighted_image)

    def analyze_image(self):
        """
        Esegue l'analisi delle anomalie sull'area selezionata o sull'intera immagine.
        """
        self.hide_center_logo()  # Nasconde il logo centrale

        threshold = self.threshold.get()
        color = self.color_combobox.get()  # Ottiene il colore selezionato

        color_map = {
            "Red": [255, 0, 0],
            "White": [255, 255, 255],
            "Blue": [0, 0, 255],
            "Green": [0, 255, 0],
            "Black": [0, 0, 0]
        }
        rgb_color = color_map[color]

        if self.polygon_points:
            # Creare una maschera basata sul poligono selezionato
            mask = Image.new('L', (self.original_image.width, self.original_image.height), 0)
            ImageDraw.Draw(mask).polygon(self.polygon_points, outline=1, fill=1)
            mask = np.array(mask)

            # Applicare la maschera all'immagine
            image_array = np.array(self.original_image)
            masked_image = image_array.copy()
            masked_image[mask == 0] = 0  # Maschera fuori dal poligono impostata a 0

            # Anomalie solo nell'area mascherata
            anomalies = self.find_anomalies(Image.fromarray(masked_image), threshold)

            # Creare un'immagine per evidenziare le anomalie solo all'interno del poligono
            highlighted_image = image_array.copy()
            highlighted_image[anomalies] = rgb_color  # Usa il colore selezionato
            highlighted_image[mask == 0] = image_array[mask == 0]  # Mantenere l'area esterna al poligono invariata

            self.image = Image.fromarray(highlighted_image)

            # Centra l'immagine elaborata nella GUI
            self.display_image_on_canvas(self.image)
        else:
            anomalies = self.find_anomalies(self.image, threshold)
            highlighted_image = self.highlight_anomalies(self.image, anomalies, color)
            self.image = highlighted_image
            self.display_image_on_canvas(self.image)

        self.save_button.config(state=tk.NORMAL)
        self.undo_button.config(state=tk.NORMAL)
        self.redo_button.config(state=tk.DISABLED)
        self.history.append(self.image.copy())
        self.history_index += 1
        self.update_status("Image analyzed")

        # Sposta il logo in alto a destra e riducilo
        self.move_logo_to_top_right()

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
            self.update_status(f"Image saved to {save_path}")

    def undo(self):
        """
        Annulla l'ultima operazione.
        """
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.history[self.history_index]
            self.display_image_on_canvas(self.image)
            self.redo_button.config(state=tk.NORMAL)
            if self.history_index == 0:
                self.undo_button.config(state=tk.DISABLED)
            self.update_status("Undo")

    def redo(self):
        """
        Ripete l'ultima operazione annullata.
        """
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.image = self.history[self.history_index]
            self.display_image_on_canvas(self.image)
            self.undo_button.config(state=tk.NORMAL)
            if self.history_index == len(self.history) - 1:
                self.redo_button.config(state=tk.DISABLED)
            self.update_status("Redo")

    def go_home(self):
        """
        Torna alla visualizzazione originale dell'immagine caricata.
        """
        self.hide_center_logo()  # Nasconde il logo centrale
        self.image = self.original_image.copy()
        self.selection = None
        self.polygon_points = []  # Resetta i punti del poligono
        self.canvas.delete("all")  # Rimuove tutti i disegni dal canvas
        self.display_image_on_canvas(self.image)
        self.canvas.config(cursor="")
        self.save_button.config(state=tk.DISABLED)
        self.undo_button.config(state=tk.DISABLED)
        self.redo_button.config(state=tk.DISABLED)
        self.update_status("Image reset to original")

        # Sposta il logo in alto a destra e riducilo
        self.move_logo_to_top_right()

    def zoom_in(self):
        """
        Esegue lo zoom in dell'immagine.
        """
        if self.image:
            width, height = self.image.size
            self.image = self.image.resize((int(width * 1.2), int(height * 1.2)), Image.LANCZOS)
            self.display_image_on_canvas(self.image)
            self.update_status("Zoomed in")

    def zoom_out(self):
        """
        Esegue lo zoom out dell'immagine.
        """
        if self.image:
            width, height = self.image.size
            self.image = self.image.resize((int(width / 1.2), int(height / 1.2)), Image.LANCZOS)
            self.display_image_on_canvas(self.image)
            self.update_status("Zoomed out")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    analyzer = ImageAnalyzer()
    analyzer.run()
