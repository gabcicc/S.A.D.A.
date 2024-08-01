import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
from image_processing_gui import ImageProcessingGUI, create_mask
from image_selection import ImageSelection
from config import METHODS, ANOMALY_TYPES, LOGO_PATH

class ImageAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Anomaly Detection Assistant (S.A.D.A.)")
        self.image_path = None
        self.image = None
        self.original_image = None
        self.analyzed_image = None  # Aggiungi questa riga
        self.zoomed_selection_coords = None  # Aggiungi questa riga

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

        self.select_button = tk.Button(top_frame, text="Select Image", command=self.load_image)
        self.select_button.pack(side=tk.LEFT, pady=10)

        self.logo_label = tk.Label(top_frame)
        self.logo_label.pack(side=tk.RIGHT, padx=10)
        self.logo_label.pack_forget()

        config_frame = tk.Frame(self)
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(config_frame, text="Method:").pack(side=tk.LEFT)
        self.method_combobox = ttk.Combobox(config_frame, textvariable=self.method, values=METHODS, state="readonly")
        self.method_combobox.set("Standard")
        self.method_combobox.pack(side=tk.LEFT, padx=5)
        self.method_combobox.bind("<<ComboboxSelected>>", self.update_anomaly_type_state)

        tk.Label(config_frame, text="Threshold:").pack(side=tk.LEFT)
        self.threshold_slider = tk.Scale(config_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.threshold,
                                         command=self.image_processing_gui.update_anomalies)
        self.threshold_slider.pack(side=tk.LEFT, padx=5)
        tk.Label(config_frame, text="Anomaly Type:").pack(side=tk.LEFT)
        self.anomaly_combobox = ttk.Combobox(config_frame, textvariable=self.anomaly_type, values=ANOMALY_TYPES,
                                             state="readonly")
        self.anomaly_combobox.set("Darker Pixels")
        self.anomaly_combobox.pack(side=tk.LEFT, padx=5)
        tk.Label(config_frame, text="Anomaly Color:").pack(side=tk.LEFT)

        color_options = ["Red", "White", "Blue", "Green", "Black"]
        self.color_combobox = ttk.Combobox(config_frame, textvariable=self.color, values=color_options,
                                           state="readonly")
        self.color_combobox.set("Red")
        self.color_combobox.pack(side=tk.LEFT, padx=5)

        tk.Label(config_frame, text="Brightness:").pack(side=tk.LEFT)
        self.brightness_slider = tk.Scale(config_frame, from_=0, to=200, orient=tk.HORIZONTAL,
                                          command=self.adjust_brightness)
        self.brightness_slider.set(100)
        self.brightness_slider.pack(side=tk.LEFT, padx=5)

        tk.Label(config_frame, text="Contrast:").pack(side=tk.LEFT)
        self.contrast_slider = tk.Scale(config_frame, from_=0, to=200, orient=tk.HORIZONTAL,
                                        command=self.adjust_contrast)
        self.contrast_slider.set(100)
        self.contrast_slider.pack(side=tk.LEFT, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.select_area_button = tk.Button(button_frame, text="Select Area", command=self.enable_selection,
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

    def update_status(self, message):
        self.status_bar.config(text=f"Status: {message}")

    def update_anomaly_type_state(self, *args):
        if self.method.get() == "Standard":
            self.anomaly_combobox.config(state="readonly")
        else:
            self.anomaly_combobox.config(state="disabled")

    def load_image(self):
        self.image_selection.load_image()

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

    def save_image(self):
        self.image_processing_gui.save_image()

    def undo(self):
        self.image_processing_gui.undo()

    def redo(self):
        self.image_processing_gui.redo()

    def go_home(self):
        self.image_processing_gui.go_home()
        self.zoom_to_selection_button.config(state=tk.DISABLED)
        self.pan_button.config(state=tk.DISABLED)
        self.select_area_button.config(state=tk.NORMAL)  # Assicura che il pulsante "Select Area" sia attivo
        self.brightness_slider.set(100)  # Reimposta il valore di luminosità
        self.contrast_slider.set(100)  # Reimposta il valore di contrasto

    def zoom_in(self):
        self.image_processing_gui.zoom_in()
        self.pan_button.config(state=tk.NORMAL)  # Attiva il pulsante "Move" dopo lo zoom

    def zoom_out(self):
        self.image_processing_gui.zoom_out()
        self.pan_button.config(state=tk.NORMAL)  # Attiva il pulsante "Move" dopo lo zoom

    def zoom_to_selection(self):
        self.image_processing_gui.zoom_to_selection()
        self.pan_button.config(state=tk.NORMAL)  # Attiva il pulsante "Move" dopo zoom to selection

    def start_pan(self):
        self.image_processing_gui.start_pan()

    def adjust_brightness(self, value):
        if self.original_image:
            factor = float(value) / 100
            base_image = self.original_image.copy() if self.analyzed_image is None else self.analyzed_image.copy()
            enhancer = ImageEnhance.Brightness(base_image)
            enhanced_image = enhancer.enhance(factor)

            if self.zoomed_selection_coords:
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
                zoomed_image = cropped_image.resize(self.image.size, Image.LANCZOS)
                self.image = zoomed_image
            elif self.image_selection.rect_coords:
                left, top, right, bottom = self.image_selection.rect_coords
                left = max(int(left - self.x_offset), 0)
                right = min(int(right - self.x_offset), self.original_image.width)
                top = max(int(top - self.y_offset), 0)
                bottom = min(int(bottom - self.y_offset), self.original_image.height)

                cropped_image = enhanced_image.crop((left, top, right, bottom))
                zoomed_image = cropped_image.resize(self.image.size, Image.LANCZOS)
                self.image = zoomed_image
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

            if self.zoomed_selection_coords:
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
                zoomed_image = cropped_image.resize(self.image.size, Image.LANCZOS)
                self.image = zoomed_image
            elif self.image_selection.rect_coords:
                left, top, right, bottom = self.image_selection.rect_coords
                left = max(int(left - self.x_offset), 0)
                right = min(int(right - self.x_offset), self.original_image.width)
                top = max(int(top - self.y_offset), 0)
                bottom = min(int(bottom - self.y_offset), self.original_image.height)

                cropped_image = enhanced_image.crop((left, top, right, bottom))
                zoomed_image = cropped_image.resize(self.image.size, Image.LANCZOS)
                self.image = zoomed_image
            else:
                self.image = enhanced_image

            self.image_processing_gui.display_image_on_canvas(self.image)
            self.update_status("Contrast adjusted")

if __name__ == "__main__":
    app = ImageAnalyzer()
    app.mainloop()