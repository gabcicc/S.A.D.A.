from PIL import Image
from tkinter import filedialog, messagebox

class ImageSelection:
    def __init__(self, parent):
        self.parent = parent
        self.polygon_points = []
        self.poly_line = None

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
            self.parent.zoom_to_selection_button.config(state="disabled")
            self.parent.pan_button.config(state="disabled")
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
        self.parent.zoom_to_selection_button.config(state="normal")  # Abilita il pulsante "Zoom to Selection"
        self.parent.pan_button.config(state="disabled")  # Disabilita il pulsante "Move"
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