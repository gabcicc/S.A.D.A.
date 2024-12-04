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

# Opzioni per il tipo di anomalia
ANOMALY_TYPES = ["Dark Pixels", "Bright Pixels"]

# Configurazione dei metodi di rilevamento anomalie
METHODS = ["Standard", "PCA", "K-means", "Isolation Forest", "DBSCAN", "SVM"]

# Parametri di default per SVM
SVM_KERNELS = ["linear", "poly", "rbf", "sigmoid"]  # I kernel supportati da SVM
SVM_DEFAULT_KERNEL = "rbf"  # Il kernel predefinito
SVM_DEFAULT_C = 1.0  # Il valore predefinito del parametro C per SVM

PCA_COMPONENTS = 1  # Default a 1, puoi cambiarlo in base alle tue esigenze