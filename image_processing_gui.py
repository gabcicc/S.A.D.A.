import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
from image_processing import find_anomalies, highlight_anomalies, create_mask



class ImageProcessingGUI:
    def __init__(self, parent):
        self.parent = parent
        self.panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0

    def display_image_on_canvas(self, image):
        self.parent.tk_image = ImageTk.PhotoImage(image)
        self.parent.canvas.delete("all")

        canvas_width = self.parent.canvas.winfo_width()
        canvas_height = self.parent.canvas.winfo_height()
        img_width, img_height = image.size

        x_offset = (canvas_width - img_width) // 2
        y_offset = (canvas_height - img_height) // 2

        self.canvas_image = self.parent.canvas.create_image(x_offset, y_offset, anchor=tk.NW,
                                                            image=self.parent.tk_image)
        self.parent.canvas.config(scrollregion=self.parent.canvas.bbox(tk.ALL))

        self.parent.x_offset = x_offset
        self.parent.y_offset = y_offset

        if self.parent.logo_id:
            self.parent.canvas.delete(self.parent.logo_id)
        self.parent.logo_id = None

        self.reset_pan()  # Resetta la posizione di pan

    def update_anomalies(self, *args):
        threshold = self.parent.threshold.get()
        color = self.parent.color.get()

        canvas_width = self.parent.canvas.winfo_width()
        canvas_height = self.parent.canvas.winfo_height()
        img_width, img_height = self.parent.original_image.size

        x_offset = (canvas_width - img_width) // 2
        y_offset = (canvas_height - img_height) // 2

        base_image = self.parent.original_image.copy() if self.parent.analyzed_image is None else self.parent.analyzed_image.copy()
        image_array = np.array(base_image)

        if self.parent.image_selection.polygon_points:
            normalized_polygon_points = [((x - x_offset) / img_width, (y - y_offset) / img_height)
                                         for x, y in self.parent.image_selection.polygon_points]

            mask = create_mask(self.parent.original_image.size, normalized_polygon_points, normalize=True)

            masked_image = image_array.copy()
            masked_image[mask == 0] = 0

            anomalies = find_anomalies(masked_image, threshold, self.parent.anomaly_type.get(),
                                       self.parent.method.get())

            highlighted_image = image_array.copy()
            if self.parent.method.get() == "Standard":
                highlighted_image[mask == 1] = highlight_anomalies(image_array, anomalies, color)[mask == 1]
            else:
                highlighted_image = highlight_anomalies(image_array, anomalies, color)
                highlighted_image[mask == 0] = image_array[mask == 0]

            self.parent.image = Image.fromarray(highlighted_image)
            self.display_image_on_canvas(self.parent.image)
        elif self.parent.image_selection.rect_coords:
            left, top, right, bottom = self.parent.image_selection.rect_coords

            left = max(int(left), 0)
            right = min(int(right), img_width)
            top = max(int(top), 0)
            bottom = min(int(bottom), img_height)

            mask = np.zeros((img_height, img_width), dtype=np.uint8)
            mask[top:bottom, left:right] = 1

            masked_image = image_array.copy()
            masked_image[mask == 0] = 0

            anomalies = find_anomalies(masked_image, threshold, self.parent.anomaly_type.get(),
                                       self.parent.method.get())

            highlighted_image = image_array.copy()
            highlighted_image[mask == 1] = highlight_anomalies(image_array, anomalies, color)[mask == 1]

            # Combina l'immagine evidenziata con l'immagine originale
            combined_image = image_array.copy()
            combined_image[mask == 1] = highlighted_image[mask == 1]

            self.parent.image = Image.fromarray(combined_image)
            self.display_image_on_canvas(self.parent.image)
        else:
            anomalies = find_anomalies(image_array, threshold, self.parent.anomaly_type.get(), self.parent.method.get())
            highlighted_image = highlight_anomalies(image_array, anomalies, color)
            self.parent.image = Image.fromarray(highlighted_image)
            self.display_image_on_canvas(self.parent.image)

        self.parent.update_status("Threshold adjusted")

    def analyze_image(self):
        self.parent.hide_center_logo()

        self.update_threshold_slider()

        threshold = self.parent.threshold.get()
        color = self.parent.color.get()
        n_components = self.parent.pca_components_slider.get()
        eps = self.parent.eps_slider.get()
        min_samples = int(self.parent.min_samples_slider.get())  # Assicurati che sia un intero

        # Converti l'immagine in un array NumPy
        image_array = np.array(self.parent.original_image)

        # Se il metodo selezionato è SVM, ottieni i parametri kernel e C dalla GUI
        if self.parent.method.get() == "SVM":
            kernel = self.parent.svm_kernel_combobox.get()  # Ottieni il kernel selezionato
            C = self.parent.svm_c_slider.get()  # Ottieni il valore di C dalla GUI
            anomalies = find_anomalies(image_array, threshold, self.parent.anomaly_type.get(),
                                       self.parent.method.get(), kernel, C)
        elif self.parent.method.get() == "DBSCAN":
            anomalies = find_anomalies(image_array, threshold, self.parent.anomaly_type.get(),
                                       self.parent.method.get(), eps, min_samples)
        else:
            anomalies = find_anomalies(image_array, threshold, self.parent.anomaly_type.get(),
                                       self.parent.method.get(), n_components, eps, min_samples)

        canvas_width = self.parent.canvas.winfo_width()
        canvas_height = self.parent.canvas.winfo_height()
        img_width, img_height = self.parent.original_image.size

        x_offset = (canvas_width - img_width) // 2
        y_offset = (canvas_height - img_height) // 2

        if self.parent.image_selection.polygon_points:
            normalized_polygon_points = [((x - x_offset) / img_width, (y - y_offset) / img_height)
                                         for x, y in self.parent.image_selection.polygon_points]

            mask = create_mask(self.parent.original_image.size, normalized_polygon_points, normalize=True)

            masked_image = image_array.copy()
            masked_image[mask == 0] = 0

            highlighted_image = image_array.copy()
            if self.parent.method.get() == "Standard":
                highlighted_image[mask == 1] = highlight_anomalies(image_array, anomalies, color)[mask == 1]
            else:
                highlighted_image = highlight_anomalies(image_array, anomalies, color)
                highlighted_image[mask == 0] = image_array[mask == 0]

            self.parent.image = Image.fromarray(highlighted_image)

            self.display_image_on_canvas(self.parent.image)
            self.parent.zoomed_selection_coords = None  # Assicura che le coordinate dello zoom siano resettate
        elif self.parent.image_selection.rect_coords:
            left, top, right, bottom = self.parent.image_selection.rect_coords

            left = max(int(left), 0)
            right = min(int(right), img_width)
            top = max(int(top), 0)
            bottom = min(int(bottom), img_height)

            mask = np.zeros((img_height, img_width), dtype=np.uint8)
            mask[top:bottom, left:right] = 1

            masked_image = image_array.copy()
            masked_image[mask == 0] = 0

            highlighted_image = image_array.copy()
            highlighted_image[mask == 1] = highlight_anomalies(image_array, anomalies, color)[mask == 1]

            self.parent.image = Image.fromarray(highlighted_image)

            self.display_image_on_canvas(self.parent.image)
            self.parent.zoomed_selection_coords = (left, top, right, bottom)  # Salva le coordinate della selezione
        else:
            highlighted_image = highlight_anomalies(image_array, anomalies, color)
            self.parent.image = Image.fromarray(highlighted_image)
            self.display_image_on_canvas(self.parent.image)

            # Abilita il threshold slider e associa l'aggiornamento dell'immagine alla modifica del valore
        self.parent.threshold_slider.config(state=tk.NORMAL, command=self.update_anomalies, fg="white", troughcolor="light gray")

        self.parent.save_button.config(state=tk.NORMAL)
        self.parent.undo_button.config(state=tk.NORMAL)
        self.parent.redo_button.config(state=tk.DISABLED)
        self.parent.history.append(self.parent.image.copy())
        self.parent.history_index += 1
        self.parent.update_status("Image analyzed")

        self.parent.analyzed_image = self.parent.image.copy()
        self.parent.move_logo_to_top_right()

    def update_threshold_slider(self, event=None):
        method = self.parent.method.get()
        if method == "Isolation Forest" or method == "K-means":
            self.parent.threshold_slider.config(from_=0, to=100)
            self.parent.threshold.set(50)
        else:
            self.parent.threshold_slider.config(from_=0, to=255)
            self.parent.threshold.set(100)

    def save_image(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("BMP files", "*.bmp"),
            ("TIFF files", "*.tiff"),
            ("All files", "*.*")
        ])
        if save_path:
            self.parent.image.save(save_path)
            messagebox.showinfo("Image Saved", f"Image saved to {save_path}")
            self.parent.update_status(f"Image saved to {save_path}")

    def undo(self):
        if self.parent.history_index > 0:
            self.parent.history_index -= 1
            self.parent.image = self.parent.history[self.parent.history_index]
            self.display_image_on_canvas(self.parent.image)
            self.parent.redo_button.config(state=tk.NORMAL)
            if self.parent.history_index == 0:
                self.parent.undo_button.config(state=tk.DISABLED)
            self.parent.update_status("Undo")

    def redo(self):
        if self.parent.history_index < len(self.parent.history) - 1:
            self.parent.history_index += 1
            self.parent.image = self.parent.history[self.parent.history_index]
            self.display_image_on_canvas(self.parent.image)
            self.parent.undo_button.config(state=tk.NORMAL)
            if self.parent.history_index == len(self.parent.history) - 1:
                self.parent.redo_button.config(state=tk.DISABLED)
            self.parent.update_status("Redo")

    def go_home(self):
        self.parent.hide_center_logo()
        self.parent.image = self.parent.original_image.copy()
        self.parent.analyzed_image = None  # Resetta l'immagine analizzata
        self.parent.selection = None
        self.parent.image_selection.polygon_points = []
        self.parent.image_selection.rect_coords = None  # Resetta le coordinate del rettangolo di selezione
        self.parent.zoomed_selection_coords = None  # Resetta le coordinate della selezione zoomata
        if self.parent.image_selection.rect_id:
            self.parent.canvas.delete(self.parent.image_selection.rect_id)
            self.parent.image_selection.rect_id = None
        self.parent.canvas.delete("all")
        self.display_image_on_canvas(self.parent.image)
        self.parent.canvas.config(cursor="")
        self.parent.save_button.config(state=tk.DISABLED)
        self.parent.undo_button.config(state=tk.DISABLED)
        self.parent.redo_button.config(state=tk.DISABLED)
        self.parent.method.set("Standard")
        self.parent.threshold.set(100)
        self.parent.anomaly_combobox.set("Darker Pixels")
        self.parent.color_combobox.set("Red")
        self.parent.brightness_slider.set(100)
        self.parent.contrast_slider.set(100)
        self.parent.update_status("Image reset to original")
        self.parent.move_logo_to_top_right()
        self.parent.update_anomaly_type_state()
        self.reset_selection()  # Abilita nuovamente la selezione dell'area
        self.parent.select_area_button.config(state=tk.NORMAL)  # Assicura che il pulsante "Select Area" sia attivo
        self.parent.standard_selection_button.config(
            state=tk.NORMAL)  # Assicura che il pulsante "Standard Selection" sia attivo
        self.reset_pan()  # Resetta la posizione di pan

    def zoom_in(self):
        if self.parent.image:
            width, height = self.parent.image.size
            self.parent.image = self.parent.image.resize((int(width * 1.2), int(height * 1.2)), Image.LANCZOS)
            self.display_image_on_canvas(self.parent.image)
            self.parent.update_status("Zoomed in")
            self.parent.pan_button.config(state=tk.NORMAL)  # Attiva il pulsante "Move"

    def zoom_out(self):
        if self.parent.image:
            width, height = self.parent.image.size
            self.parent.image = self.parent.image.resize((int(width / 1.2), int(height / 1.2)), Image.LANCZOS)
            self.display_image_on_canvas(self.parent.image)
            self.parent.update_status("Zoomed out")
            self.parent.pan_button.config(state=tk.NORMAL)  # Attiva il pulsante "Move"

    def zoom_to_selection(self):
        if self.parent.image_selection.polygon_points:
            x_coords, y_coords = zip(*(self.parent.image_selection.polygon_points))
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)

            # Adjust the coordinates to account for the offset and ensure they are within bounds
            min_x = max(int(min_x - self.parent.x_offset), 0)
            max_x = min(int(max_x - self.parent.x_offset), self.parent.original_image.width)
            min_y = max(int(min_y - self.parent.y_offset), 0)
            max_y = min(int(max_y - self.parent.y_offset), self.parent.original_image.height)

            roi = self.parent.image.crop((min_x, min_y, max_x, max_y))
            roi_width, roi_height = roi.size

            # Resize the ROI to fit the canvas
            canvas_width = self.parent.canvas.winfo_width()
            canvas_height = self.parent.canvas.winfo_height()
            scale = min(canvas_width / roi_width, canvas_height / roi_height)
            new_size = (int(roi_width * scale), int(roi_height * scale))
            zoomed_image = roi.resize(new_size, Image.LANCZOS)

            self.parent.image = zoomed_image
            self.display_image_on_canvas(self.parent.image)
            self.parent.update_status("Zoomed to selection")
            self.parent.pan_button.config(state=tk.NORMAL)
            self.parent.zoomed_selection_coords = (min_x, min_y, max_x, max_y)
        elif self.parent.zoomed_selection_coords:
            left, top, right, bottom = self.parent.zoomed_selection_coords

            roi = self.parent.image.crop((left, top, right, bottom))
            roi_width, roi_height = roi.size

            # Resize the ROI to fit the canvas
            canvas_width = self.parent.canvas.winfo_width()
            canvas_height = self.parent.canvas.winfo_height()
            scale = min(canvas_width / roi_width, canvas_height / roi_height)
            new_size = (int(roi_width * scale), int(roi_height * scale))
            zoomed_image = roi.resize(new_size, Image.LANCZOS)

            self.parent.image = zoomed_image
            self.display_image_on_canvas(self.parent.image)
            self.parent.update_status("Zoomed to selection")
            self.parent.pan_button.config(state=tk.NORMAL)
        else:
            self.parent.update_status("No valid selection to zoom")
    def start_pan(self):
        self.parent.canvas.config(cursor="fleur")
        self.parent.canvas.bind("<ButtonPress-1>", self.start_pan_drag)
        self.parent.canvas.bind("<B1-Motion>", self.pan_image)
        self.parent.canvas.bind("<ButtonRelease-1>", self.end_pan)

    def start_pan_drag(self, event):
        self.panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def pan_image(self, event):
        if self.panning:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.parent.canvas.move(self.canvas_image, dx, dy)
            self.pan_start_x = event.x
            self.pan_start_y = event.y

    def end_pan(self, event):
        self.panning = False

    def reset_pan(self):
        self.panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.parent.canvas.scan_mark(0, 0)
        self.parent.canvas.scan_dragto(0, 0, gain=1)
        self.parent.canvas.unbind("<ButtonPress-1>")
        self.parent.canvas.unbind("<B1-Motion>")
        self.parent.canvas.unbind("<ButtonRelease-1>")

    def reset_selection(self):
        self.parent.canvas.bind("<ButtonPress-1>", self.parent.image_selection.on_button_press)
        self.parent.canvas.bind("<B1-Motion>", self.parent.image_selection.on_move_press)
        self.parent.canvas.bind("<ButtonRelease-1>", self.parent.image_selection.on_button_release)
        self.parent.canvas.bind("<Double-Button-1>", self.parent.image_selection.on_button_double_click)
        self.parent.select_area_button.config(state=tk.NORMAL)
        self.parent.image_selection.polygon_points = []
        self.parent.image_selection.rect_coords = None  # Resetta le coordinate della selezione rettangolare
        if self.parent.image_selection.rect_id:
            self.parent.canvas.delete(self.parent.image_selection.rect_id)
            self.parent.image_selection.rect_id = None