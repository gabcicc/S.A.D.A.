from PIL import Image
from tkinter import filedialog, messagebox

class ImageSelection:
    def __init__(self, parent):
        self.parent = parent
        self.polygon_points = []
        self.poly_line = None
        self.rect_id = None
        self.rect_coords = None
        self.start_x = 0
        self.start_y = 0

    def load_image(self):
        self.parent.image_path = filedialog.askopenfilename(filetypes=[
            ("JPEG files", "*.jpg;*.jpeg"),
            ("PNG files", "*.png"),
            ("BMP files", "*.bmp"),
            ("TIFF files", "*.tiff"),
            ("All files", "*.*")
        ])
        if not self.parent.image_path:
            return

        try:
            self.parent.image = Image.open(self.parent.image_path)
            if self.parent.image.mode == 'RGBA':
                self.parent.image = self.parent.image.convert('RGB')

            max_size = (800, 600)
            self.parent.image.thumbnail(max_size, Image.LANCZOS)
            self.parent.original_image = self.parent.image.copy()

            self.parent.image_processing_gui.display_image_on_canvas(self.parent.image)
            self.parent.select_area_button.config(state="normal")
            self.parent.analyze_button.config(state="normal")
            self.parent.back_button.config(state="normal")
            self.parent.zoom_in_button.config(state="normal")
            self.parent.zoom_out_button.config(state="normal")
            self.parent.zoom_to_selection_button.config(state="normal")
            self.parent.pan_button.config(state="normal")
            self.parent.standard_selection_button.config(state="normal")
            self.parent.update_status("Image loaded")

            self.parent.hide_center_logo()
            self.parent.move_logo_to_top_right()

        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

    def enable_selection(self):
        self.polygon_points = []
        self.parent.canvas.delete("all")
        self.parent.image_processing_gui.display_image_on_canvas(self.parent.image)
        self.parent.canvas.config(cursor="cross")
        self.parent.update_status("Select area by clicking points, double-click to complete")
        self.parent.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.parent.canvas.bind("<B1-Motion>", self.on_move_press)
        self.parent.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.parent.canvas.bind("<Double-Button-1>", self.on_button_double_click)
        self.parent.zoom_to_selection_button.config(state="normal")  # Abilita il pulsante "Zoom to Selection"
        self.parent.pan_button.config(state="disabled")  # Disabilita il pulsante "Move"

    def enable_standard_selection(self):
        self.parent.canvas.bind("<ButtonPress-1>", self.start_standard_selection)
        self.parent.canvas.bind("<B1-Motion>", self.update_standard_selection)
        self.parent.canvas.bind("<ButtonRelease-1>", self.end_standard_selection)
        self.parent.update_status("Standard selection enabled")

    def on_button_press(self, event):
        if not self.parent.canvas.config()['cursor'][-1] == "cross":
            return

        self.polygon_points.append((event.x, event.y))

        radius = 3
        self.parent.canvas.create_oval(event.x - radius, event.y - radius, event.x + radius, event.y + radius,
                                       fill='red')

        if self.poly_line:
            self.parent.canvas.delete(self.poly_line)

        if len(self.polygon_points) > 1:
            self.poly_line = self.parent.canvas.create_line(
                *sum(self.polygon_points, ()),
                fill='red'
            )

    def on_move_press(self, event):
        pass

    def on_button_release(self, event):
        pass

    def on_button_double_click(self, event):
        if len(self.polygon_points) > 2:
            self.parent.canvas.create_polygon(self.polygon_points, outline='red', fill='', width=2)
            self.parent.canvas.config(cursor="")
            self.parent.update_status("Polygon area selected")
            self.parent.pan_button.config(state="normal")  # Abilita il pulsante "Move"

    def start_standard_selection(self, event):
        if self.rect_id:
            self.parent.canvas.delete(self.rect_id)
        self.start_x = event.x
        self.start_y = event.y
        self.rect_id = self.parent.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                           outline="red")

    def update_standard_selection(self, event):
        self.parent.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def end_standard_selection(self, event):
        canvas_width = self.parent.canvas.winfo_width()
        canvas_height = self.parent.canvas.winfo_height()
        img_width, img_height = self.parent.original_image.size

        x_offset = (canvas_width - img_width) // 2
        y_offset = (canvas_height - img_height) // 2

        self.end_x = event.x
        self.end_y = event.y
        self.parent.update_status("Area selected")
        self.parent.canvas.config(cursor="")
        self.parent.zoom_to_selection_button.config(state="normal")
        self.parent.pan_button.config(state="normal")
        self.rect_coords = (
            max(int(self.start_x - x_offset), 0),
            max(int(self.start_y - y_offset), 0),
            min(int(self.end_x - x_offset), img_width),
            min(int(self.end_y - y_offset), img_height)
        )
        self.parent.image_selection.rect_coords = self.rect_coords
        self.parent.zoomed_selection_coords = self.rect_coords  # Save the selection coordinates

    def update_status(self, message):
        self.parent.update_status(message)