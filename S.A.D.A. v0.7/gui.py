import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from image_processing_gui import ImageProcessingGUI
from image_selection import ImageSelection
from config import METHODS, ANOMALY_TYPES, LOGO_PATH


class ImageAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Anomaly Detection Assistant (S.A.D.A.)")
        self.image_path = None
        self.image = None
        self.original_image = None

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

        button_frame = tk.Frame(self)
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
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Double-Button-1>", self.on_button_double_click)

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

if __name__ == "__main__":
    app = ImageAnalyzer()
    app.mainloop()