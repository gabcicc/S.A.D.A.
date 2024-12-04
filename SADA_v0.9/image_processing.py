import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from PIL import Image, ImageDraw

def create_mask(size, points, normalize=False):
    if normalize:
        points = [(int(x * size[0]), int(y * size[1])) for x, y in points]
    mask = Image.new('L', size, 0)
    ImageDraw.Draw(mask).polygon(points, outline=1, fill=1)
    return np.array(mask)

def find_anomalies(image, threshold, anomaly_type, method="Standard"):
    if method == "PCA":
        return find_anomalies_pca(image, threshold)
    elif method == "K-means":
        return find_anomalies_kmeans(image, threshold)
    elif method == "Isolation Forest":
        return find_anomalies_isolation_forest(image, threshold)
    else:
        if anomaly_type == "Darker Pixels":
            return image[:, :, 0] < threshold
        else:
            return image[:, :, 0] > threshold

def find_anomalies_pca(image, threshold):
    reshaped = image.reshape(-1, image.shape[2])
    pca = PCA(n_components=1)
    transformed = pca.fit_transform(reshaped)
    anomalies = np.abs(transformed - np.mean(transformed)) > threshold
    return anomalies.reshape(image.shape[:2])

def find_anomalies_kmeans(image, threshold):
    reshaped = image.reshape(-1, image.shape[2])
    kmeans = KMeans(n_clusters=2, random_state=0).fit(reshaped)
    labels = kmeans.labels_
    cluster_centers = kmeans.cluster_centers_

    # Calcola la distanza di ogni pixel dal centro del cluster
    distances = np.linalg.norm(reshaped - cluster_centers[labels], axis=1)

    # Utilizza la soglia per determinare il limite di distanza
    threshold_distance = np.percentile(distances, threshold)
    anomalies = distances > threshold_distance

    return anomalies.reshape(image.shape[:2])

def find_anomalies_isolation_forest(image, threshold):
    reshaped = image.reshape(-1, image.shape[2])
    isolation_forest = IsolationForest(contamination=0.1, random_state=0)
    isolation_forest.fit(reshaped)
    scores = isolation_forest.decision_function(reshaped)
    anomalies = scores < np.percentile(scores, 100 - threshold)
    return anomalies.reshape(image.shape[:2])

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
    anomalies = anomalies.astype(bool)
    highlighted_image[anomalies] = rgb_color
    return highlighted_image  # Restituisce la matrice numpy