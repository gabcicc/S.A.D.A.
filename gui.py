import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
from image_processing_gui import ImageProcessingGUI, create_mask
from image_selection import ImageSelection
from config import METHODS, ANOMALY_TYPES, LOGO_PATH, PCA_COMPONENTS, SVM_KERNELS, SVM_DEFAULT_KERNEL, SVM_DEFAULT_C
from tooltip import get_tooltip
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return

        # Stampa di debug per verificare il testo
        print(f"Tooltip text: {self.text}")

        x, y, _cx, _cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # Configurazione del Label per il tooltip
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0",  # Colore di sfondo chiaro
                         foreground="#000000",  # Colore del testo nero
                         relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=5, ipady=5)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
class ImageAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Anomaly Detection Assistant (S.A.D.A.)")
        self.image_path = None
        self.image = None
        self.original_image = None
        self.analyzed_image = None
        self.zoomed_selection_coords = None
        self.zoomed_in = False

        self.history = []
        self.history_index = -1

        self.threshold = tk.IntVar(value=100)
        self.color = tk.StringVar(value="Red")
        self.anomaly_type = tk.StringVar(value="Darker Pixels")
        self.method = tk.StringVar(value="Standard")

        self.logo_image = None
        self.logo_id = None

        self.image_selection = ImageSelection(self)
        self.image_processing_gui = ImageProcessingGUI(self)

        self.create_gui()

        self.load_logo()
        self.update_anomaly_type_state()

        self.panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0

    def set_combobox_width(self, combobox, values):
        max_width = max(len(str(value)) for value in values)
        combobox.config(width=max_width)
    def load_logo(self):
        self.logo_image = Image.open(LOGO_PATH)
        self.after(100, self.resize_logo)
        self.bind("<Configure>", self.on_resize)

    def resize_logo(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width > 0 and canvas_height > 0:
            logo_size = min(canvas_width, canvas_height) // 2
            if logo_size > 0:
                self.logo_image_resized = self.logo_image.resize((logo_size, logo_size), Image.LANCZOS)
                self.tk_logo_image = ImageTk.PhotoImage(self.logo_image_resized)
                if self.logo_id:
                    self.canvas.delete(self.logo_id)
                self.logo_id = self.canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    anchor=tk.CENTER, image=self.tk_logo_image
                )

    def move_logo_to_top_right(self):
        if self.logo_image:
            logo_width = 100
            logo_height = 100
            self.logo_image_resized = self.logo_image.resize((logo_width, logo_height), Image.LANCZOS)
            self.tk_logo_image = ImageTk.PhotoImage(self.logo_image_resized)
            self.logo_label.pack_forget()
            self.logo_label.config(image=self.tk_logo_image)
            self.logo_label.image = self.tk_logo_image
            self.logo_label.pack(side=tk.RIGHT, padx=10)

    def hide_center_logo(self):
        if self.logo_id:
            self.canvas.delete(self.logo_id)
            self.logo_id = None

    def on_resize(self, event):
        if not self.image:
            self.resize_logo()
    def create_gui(self):
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.select_button = tk.Button(top_frame, text="Load Image", command=self.load_image)
        self.select_button.pack(side=tk.LEFT, pady=10)

        self.logo_label = tk.Label(top_frame)
        self.logo_label.pack(side=tk.RIGHT, padx=10)
        self.logo_label.pack_forget()

        config_frame = tk.Frame(self)
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(config_frame, text="Method:").pack(side=tk.LEFT)
        self.method_combobox = ttk.Combobox(config_frame, textvariable=self.method, values=METHODS, state="readonly")
        # Imposta la larghezza della combobox basata sulla lunghezza massima del termine più lungo
        max_width_methods = max(len(method) for method in METHODS)
        self.method_combobox.config(width=max_width_methods)
        self.method_combobox.set("Standard")
        self.method_combobox.pack(side=tk.LEFT, padx=5)
        self.method_combobox.bind("<<ComboboxSelected>>", self.update_anomaly_type_state)
        Tooltip(self.method_combobox, get_tooltip("method_combobox"))

        # Aggiungi la configurazione per i parametri PCA_Components:
        self.pca_label = tk.Label(config_frame, text="PCA Components:")
        self.pca_label.pack_forget()  # Nascondi di default
        self.pca_components_slider = tk.Scale(config_frame, from_=1, to=10, orient=tk.HORIZONTAL, state=tk.DISABLED)
        self.pca_components_slider.set(PCA_COMPONENTS)
        self.pca_components_slider.pack_forget()  # Nascondi di default
        Tooltip(self.pca_components_slider, get_tooltip("pca_slider"))

        # Aggiungi la configurazione per i parametri DBSCAN
        self.eps_label = tk.Label(config_frame, text="Eps:")
        self.eps_label.pack_forget()  # Nascondi di default
        self.eps_slider = tk.Scale(config_frame, from_=0.1, to=10, resolution=0.1, orient=tk.HORIZONTAL)
        self.eps_slider.set(0.5)  # Valore di default
        self.eps_slider.pack_forget()  # Nascondi di default
        Tooltip(self.eps_slider, get_tooltip("eps_slider"))

        self.min_samples_label = tk.Label(config_frame, text="Min Samples:")
        self.min_samples_label.pack_forget()  # Nascondi di default
        self.min_samples_slider = tk.Scale(config_frame, from_=1, to=20, orient=tk.HORIZONTAL)
        self.min_samples_slider.set(5)  # Valore di default
        self.min_samples_slider.pack_forget()  # Nascondi di default
        Tooltip(self.min_samples_slider, get_tooltip("min_samples_slider"))

        # Parametri SVM
        self.svm_kernel_label = tk.Label(config_frame, text="SVM Kernel:")
        self.svm_kernel_combobox = ttk.Combobox(config_frame, values=SVM_KERNELS, state="readonly")

        # Imposta la larghezza della combobox basata sulla lunghezza massima del termine più lungo
        max_width = max(len(kernel) for kernel in SVM_KERNELS)
        self.svm_kernel_combobox.config(width=max_width)
        self.svm_kernel_combobox.set(SVM_DEFAULT_KERNEL)

        self.svm_c_label = tk.Label(config_frame, text="SVM C:")
        self.svm_c_slider = tk.Scale(config_frame, from_=0.1, to=10.0, orient=tk.HORIZONTAL, resolution=0.1)
        self.svm_c_slider.set(SVM_DEFAULT_C)

        # Nascondere inizialmente i controlli SVM
        self.svm_kernel_label.pack_forget()
        self.svm_kernel_combobox.pack_forget()
        self.svm_c_label.pack_forget()
        self.svm_c_slider.pack_forget()
        Tooltip(self.svm_kernel_combobox, get_tooltip("svm_kernel"))
        Tooltip(self.svm_c_slider, get_tooltip("svm_c_slider"))
        tk.Label(config_frame, text="Threshold:").pack(side=tk.LEFT)
        self.threshold_slider = tk.Scale(config_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.threshold,
                                         state=tk.DISABLED, fg="gray", troughcolor="gray")  # Imposta lo stato iniziale su DISABLED e i colori per farlo sembrare spento
        self.threshold_slider.pack(side=tk.LEFT, padx=5)
        Tooltip(self.threshold_slider, get_tooltip("threshold_slider"))
        tk.Label(config_frame, text="Anomaly Type:").pack(side=tk.LEFT)
        self.anomaly_combobox = ttk.Combobox(config_frame, textvariable=self.anomaly_type, values=ANOMALY_TYPES,
                                             state="readonly")
        Tooltip(self.anomaly_combobox, get_tooltip("anomaly_combobox"))
        self.anomaly_combobox.set("Darker Pixels")
        self.set_combobox_width(self.anomaly_combobox, ANOMALY_TYPES)  # Imposta la larghezza in base alla lunghezza massima
        self.anomaly_combobox.pack(side=tk.LEFT, padx=5)

        color_options = ["Red", "White", "Blue", "Green", "Black"]
        self.color_combobox = ttk.Combobox(config_frame, textvariable=self.color, values=color_options,
                                           state="readonly")
        self.color_combobox.set("Red")
        self.set_combobox_width(self.color_combobox, color_options)  # Imposta la larghezza in base alla lunghezza massima
        self.color_combobox.pack(side=tk.LEFT, padx=5)
        Tooltip(self.color_combobox, get_tooltip("color_combobox"))

        tk.Label(config_frame, text="Brightness:").pack(side=tk.LEFT)
        self.brightness_slider = tk.Scale(config_frame, from_=0, to=200, orient=tk.HORIZONTAL,
                                          command=self.adjust_brightness)
        self.brightness_slider.set(100)
        self.brightness_slider.pack(side=tk.LEFT, padx=5)
        Tooltip(self.brightness_slider, get_tooltip("brightness_slider"))

        tk.Label(config_frame, text="Contrast:").pack(side=tk.LEFT)
        self.contrast_slider = tk.Scale(config_frame, from_=0, to=200, orient=tk.HORIZONTAL,
                                        command=self.adjust_contrast)
        self.contrast_slider.set(100)
        self.contrast_slider.pack(side=tk.LEFT, padx=5)
        Tooltip(self.contrast_slider, get_tooltip("contrast_slider"))

        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.select_area_button = tk.Button(button_frame, text="Select by points", command=self.enable_selection,
                                            state=tk.DISABLED)
        self.select_area_button.pack(side=tk.LEFT, padx=5)

        self.standard_selection_button = tk.Button(button_frame, text="Standard Selection",
                                                   command=self.enable_standard_selection, state=tk.DISABLED)
        self.standard_selection_button.pack(side=tk.LEFT, padx=5)

        self.analyze_button = tk.Button(button_frame, text="Analyze Image", command=self.analyze_image,
                                        state=tk.DISABLED)
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(button_frame, text="Save Image", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.undo_button = tk.Button(button_frame, text="Undo", command=self.undo, state=tk.DISABLED)
        self.undo_button.pack(side=tk.LEFT, padx=5)

        self.redo_button = tk.Button(button_frame, text="Redo", command=self.redo, state=tk.DISABLED)
        self.redo_button.pack(side=tk.LEFT, padx=5)

        self.back_button = tk.Button(button_frame, text="Reset", command=self.go_home, state=tk.DISABLED)
        self.back_button.pack(side=tk.LEFT, padx=5)

        self.zoom_in_button = tk.Button(button_frame, text="Zoom In", command=self.zoom_in, state=tk.DISABLED)
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)

        self.zoom_out_button = tk.Button(button_frame, text="Zoom Out", command=self.zoom_out, state=tk.DISABLED)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)

        self.zoom_to_selection_button = tk.Button(button_frame, text="Zoom to Selection",
                                                  command=self.zoom_to_selection,
                                                  state=tk.DISABLED)
        self.zoom_to_selection_button.pack(side=tk.LEFT, padx=5)

        self.pan_button = tk.Button(button_frame, text="Move", command=self.start_pan, state=tk.DISABLED)
        self.pan_button.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self, width=800, height=600, bg="black")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Double-Button-1>", self.on_button_double_click)

        self.status_bar = tk.Label(self, text="Status: Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.load_logo()
        self.update_anomaly_type_state()

    def update_status(self, message: object) -> object:
        self.status_bar.config(text=f"Status: {message}")

    def update_anomaly_type_state(self, *args):
        # Nascondi tutto di default (sia controlli che etichette)
        self.pca_label.pack_forget()
        self.pca_components_slider.pack_forget()
        self.eps_label.pack_forget()
        self.eps_slider.pack_forget()
        self.min_samples_label.pack_forget()
        self.min_samples_slider.pack_forget()
        self.svm_kernel_label.pack_forget()
        self.svm_kernel_combobox.pack_forget()
        self.svm_c_label.pack_forget()
        self.svm_c_slider.pack_forget()

        if self.method.get() == "Standard":
            self.anomaly_combobox.config(state="readonly")
        elif self.method.get() == "PCA":
            self.anomaly_combobox.config(state="readonly")
            self.pca_label.pack(side=tk.LEFT)  # Mostra l'etichetta per PCA
            self.pca_components_slider.config(state=tk.NORMAL)
            self.pca_components_slider.pack(side=tk.LEFT, padx=5)  # Mostra il controllo della PCA
        elif self.method.get() == "K-means":
            self.anomaly_combobox.config(state="disabled")
        elif self.method.get() == "DBSCAN":
            self.anomaly_combobox.config(state="disabled")
            self.eps_label.pack(side=tk.LEFT)  # Mostra l'etichetta per eps
            self.eps_slider.pack(side=tk.LEFT, padx=5)  # Mostra il controllo per eps
            self.min_samples_label.pack(side=tk.LEFT)  # Mostra l'etichetta per min_samples
            self.min_samples_slider.pack(side=tk.LEFT, padx=5)  # Mostra il controllo per min_samples
        elif self.method.get() == "SVM":
            self.anomaly_combobox.config(state="disabled")
            self.svm_kernel_label.pack(side=tk.LEFT)  # Mostra l'etichetta per SVM kernel
            self.svm_kernel_combobox.pack(side=tk.LEFT, padx=5)  # Mostra il controllo per SVM kernel
            self.svm_c_label.pack(side=tk.LEFT)  # Mostra l'etichetta per SVM C
            self.svm_c_slider.pack(side=tk.LEFT, padx=5)  # Mostra il controllo per SVM C

    def load_image(self):
        # Carica l'immagine
        self.image_selection.load_image()

        if self.image_selection.image is not None:
            # Reset dei parametri come se avessi cliccato su "Reset"
            self.go_home()

            # Assicura che la nuova immagine caricata venga visualizzata
            self.image_processing_gui.display_image_on_canvas(self.image_selection.image)

    def enable_selection(self):
        self.image_selection.enable_selection()
        self.pan_button.config(state=tk.DISABLED)

    def enable_standard_selection(self):
        self.image_selection.enable_standard_selection()
        self.pan_button.config(state=tk.DISABLED)

    def on_button_press(self, event):
        self.image_selection.on_button_press(event)

    def on_move_press(self, event):
        self.image_selection.on_move_press(event)

    def on_button_release(self, event):
        self.image_selection.on_button_release(event)

    def on_button_double_click(self, event):
        self.image_selection.on_button_double_click(event)

    def analyze_image(self):
        self.image_processing_gui.analyze_image()
        self.update_status("Image analyzed")

        # Mantieni aggiornata l'immagine analizzata
        self.analyzed_image = self.image.copy()

    def save_image(self):
        self.image_processing_gui.save_image()

    def undo(self):
        self.image_processing_gui.undo()

    def redo(self):
        self.image_processing_gui.redo()

    def go_home(self, reset_image=True):
        if reset_image:
            self.image_processing_gui.go_home()
        self.zoom_to_selection_button.config(state=tk.DISABLED)
        self.pan_button.config(state=tk.DISABLED)
        self.select_area_button.config(state=tk.NORMAL)  # Assicura che il pulsante "Select Area" sia attivo
        self.brightness_slider.set(100)  # Reimposta il valore di luminosità
        self.contrast_slider.set(100)  # Reimposta il valore di contrasto
        self.zoomed_in = False  # Resetta lo stato dello zoom

        # Ripristina lo stato della scala PCA components
        self.pca_components_slider.config(state=tk.NORMAL)  # Temporaneamente abilitata per impostare il valore
        self.pca_components_slider.set(1)  # Imposta il valore a 1
        self.update_idletasks()  # Assicura che il valore sia aggiornato
        self.pca_components_slider.config(state=tk.DISABLED)  # Disabilita la scala

        self.method.set("Standard")  # Torna al metodo standard
        self.update_anomaly_type_state()  # Assicura che gli altri controlli siano aggiornati
        self.update_status("Original image")

        # Disabilita e spegni il threshold slider
        self.threshold_slider.config(state=tk.DISABLED, fg="gray", troughcolor="gray")
        self.threshold.set(100)  # Reimposta il valore del threshold


    def zoom_in(self):
        self.image_processing_gui.zoom_in()
        self.pan_button.config(state=tk.NORMAL)  # Attiva il pulsante "Move" dopo lo zoom

    def zoom_out(self):
        self.image_processing_gui.zoom_out()
        self.pan_button.config(state=tk.NORMAL)  # Attiva il pulsante "Move" dopo lo zoom

    def zoom_to_selection(self):
        self.image_processing_gui.zoom_to_selection()
        self.pan_button.config(state=tk.NORMAL)  # Attiva il pulsante "Move" dopo zoom to selection
        self.zoomed_in = True  # Aggiorna lo stato dello zoom

    def start_pan(self):
        self.image_processing_gui.start_pan()

    def adjust_brightness(self, value):
        if self.original_image:
            factor = float(value) / 100
            base_image = self.original_image.copy() if self.analyzed_image is None else self.analyzed_image.copy()
            enhancer = ImageEnhance.Brightness(base_image)
            enhanced_image = enhancer.enhance(factor)

            if self.zoomed_in and self.zoomed_selection_coords:
                left, top, right, bottom = self.zoomed_selection_coords
                left = max(int(left), 0)
                right = min(int(right), self.original_image.width)
                top = max(int(top), 0)
                bottom = min(int(bottom), self.original_image.height)

                cropped_image = enhanced_image.crop((left, top, right, bottom))
                zoomed_image = cropped_image.resize(self.image.size, Image.LANCZOS)
                self.image = zoomed_image
            elif self.image_selection.polygon_points:
                x_coords, y_coords = zip(*self.image_selection.polygon_points)
                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)

                min_x = max(int(min_x - self.x_offset), 0)
                max_x = min(int(max_x - self.x_offset), self.original_image.width)
                min_y = max(int(min_y - self.y_offset), 0)
                max_y = min(int(max_y - self.y_offset), self.original_image.height)

                cropped_image = enhanced_image.crop((min_x, min_y, max_x, max_y))
                self.image.paste(cropped_image, (min_x, min_y))
            elif self.image_selection.rect_coords:
                left, top, right, bottom = self.image_selection.rect_coords
                left = max(int(left), 0)
                right = min(int(right), self.original_image.width)
                top = max(int(top), 0)
                bottom = min(int(bottom), self.original_image.height)

                cropped_image = enhanced_image.crop((left, top, right, bottom))
                self.image.paste(cropped_image, (left, top))
            else:
                self.image = enhanced_image

            self.image_processing_gui.display_image_on_canvas(self.image)
            self.update_status("Brightness adjusted")

    def adjust_contrast(self, value):
        if self.original_image:
            factor = float(value) / 100
            base_image = self.original_image.copy() if self.analyzed_image is None else self.analyzed_image.copy()
            enhancer = ImageEnhance.Contrast(base_image)
            enhanced_image = enhancer.enhance(factor)

            if self.zoomed_in and self.zoomed_selection_coords:
                left, top, right, bottom = self.zoomed_selection_coords
                left = max(int(left), 0)
                right = min(int(right), self.original_image.width)
                top = max(int(top), 0)
                bottom = min(int(bottom), self.original_image.height)

                cropped_image = enhanced_image.crop((left, top, right, bottom))
                zoomed_image = cropped_image.resize(self.image.size, Image.LANCZOS)
                self.image = zoomed_image
            elif self.image_selection.polygon_points:
                x_coords, y_coords = zip(*self.image_selection.polygon_points)
                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)

                min_x = max(int(min_x - self.x_offset), 0)
                max_x = min(int(max_x - self.x_offset), self.original_image.width)
                min_y = max(int(min_y - self.y_offset), 0)
                max_y = min(int(max_y - self.y_offset), self.original_image.height)

                cropped_image = enhanced_image.crop((min_x, min_y, max_x, max_y))
                self.image.paste(cropped_image, (min_x, min_y))
            elif self.image_selection.rect_coords:
                left, top, right, bottom = self.image_selection.rect_coords
                left = max(int(left), 0)
                right = min(int(right), self.original_image.width)
                top = max(int(top), 0)
                bottom = min(int(bottom), self.original_image.height)

                cropped_image = enhanced_image.crop((left, top, right, bottom))
                self.image.paste(cropped_image, (left, top))
            else:
                self.image = enhanced_image

            self.image_processing_gui.display_image_on_canvas(self.image)
            self.update_status("Contrast adjusted")

if __name__ == "__main__":
    app = ImageAnalyzer()
    app.mainloop()