import os

# Impostazioni del logo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, "images", "logo_SADA_.png")

# Impostazioni dell'immagine
IMAGE_MAX_SIZE = (800, 600)

# Mappa dei colori
COLOR_MAP = {
    "Red": [255, 0, 0],
    "White": [255, 255, 255],
    "Blue": [0, 0, 255],
    "Green": [0, 255, 0],
    "Black": [0, 0, 0]
}