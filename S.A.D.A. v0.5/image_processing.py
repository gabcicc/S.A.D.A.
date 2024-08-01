import numpy as np
from PIL import Image, ImageDraw

def find_anomalies(image, threshold):
    """
    Trova le anomalie nell'immagine, assumendo che le aree più scure rappresentino anomalie.
    """
    image_array = np.array(image)
    anomalies = image_array[:, :, 0] < threshold
    return anomalies

def highlight_anomalies(image, anomalies, color):
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

def create_mask(width, height, polygon_points):
    """
    Crea una maschera basata sul poligono selezionato.
    """
    mask = Image.new('L', (width, height), 0)
    ImageDraw.Draw(mask).polygon(polygon_points, outline=1, fill=1)
    return np.array(mask)