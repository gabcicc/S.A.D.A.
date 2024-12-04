from PIL import Image, ImageDraw
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.svm import OneClassSVM


def create_mask(size, points, normalize=False):
    if normalize:
        points = [(int(x * size[0]), int(y * size[1])) for x, y in points]
    mask = Image.new('L', size, 0)
    ImageDraw.Draw(mask).polygon(points, outline=1, fill=1)
    return np.array(mask)

def find_anomalies(image, threshold, anomaly_type, method="Standard", *args):
    if method == "PCA":
        n_components = args[0]  # Prendi solo il primo argomento per PCA
        return find_anomalies_pca(image, threshold, n_components)
    elif method == "K-means":
        max_clusters = args[0] if len(args) > 0 else 10  # Aggiungi max_clusters come argomento opzionale
        return find_anomalies_kmeans(image, threshold, max_clusters)
    elif method == "Isolation Forest":
        return find_anomalies_isolation_forest(image, threshold)
    elif method == "DBSCAN":
        return find_anomalies_dbscan(image, *args)
    elif method == "SVM":
        kernel = args[0] if len(args) > 0 else "rbf"
        C = args[1] if len(args) > 1 else 1.0
        return find_anomalies_svm(image, kernel, C)
    else:
        if anomaly_type == "Darker Pixels":
            return image[:, :, 0] < threshold
        else:
            return image[:, :, 0] > threshold


def find_anomalies_pca(image, threshold, n_components):
    reshaped = image.reshape(-1, image.shape[2])

    # Limita il numero di componenti al valore massimo possibile
    max_components = min(reshaped.shape[0], reshaped.shape[1])
    n_components = min(n_components, max_components)

    pca = PCA(n_components=n_components)
    transformed = pca.fit_transform(reshaped)

    # Media delle componenti principali per ogni pixel
    transformed_mean = np.mean(transformed, axis=1)

    # Calcola le anomalie usando la media delle componenti principali
    anomalies = np.abs(transformed_mean - np.mean(transformed_mean)) > threshold

    return anomalies.reshape(image.shape[:2])


from sklearn.cluster import KMeans
import numpy as np


def find_anomalies_kmeans(image, threshold, max_clusters=10):  # Puoi regolare max_clusters secondo le necessità
    reshaped = image.reshape(-1, image.shape[2])

    distortions = []
    K = range(2, max_clusters + 1)

    for k in K:
        kmeans = KMeans(n_clusters=k, n_init=5, random_state=0)  # Riduzione del numero di inizializzazioni a 5
        kmeans.fit(reshaped)
        distortions.append(kmeans.inertia_)  # Inertia rappresenta la somma delle distanze al quadrato

    # Verifica se ci sono abbastanza distorsioni per calcolare il diff_ratio
    if len(distortions) > 1:
        diff = np.diff(distortions)
        diff_ratio = diff[:-1] / diff[1:]
        if len(diff_ratio) > 0:
            optimal_k = np.argmin(diff_ratio) + 2  # +2 perché l'indice inizia da 0 e abbiamo calcolato le differenze
        else:
            optimal_k = 2  # Valore predefinito se diff_ratio è vuoto
    else:
        optimal_k = 2  # Valore predefinito se ci sono meno di 2 distorsioni

    # Esegui KMeans con il numero ottimale di cluster
    kmeans = KMeans(n_clusters=optimal_k, n_init=10, random_state=0)
    labels = kmeans.fit_predict(reshaped)
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


def find_anomalies_dbscan(image, eps=0.5, min_samples=5, apply_pca=True):
    # Converti l'immagine in un array 2D
    reshaped = image.reshape(-1, image.shape[2])

    # Riduzione della dimensionalità con PCA
    if apply_pca:
        max_components = min(reshaped.shape[0], reshaped.shape[1])
        n_components = min(10, max_components)  # Imposta il numero di componenti a 10 o il massimo possibile
        if n_components > 1:
            pca = PCA(n_components=n_components)
            reshaped = pca.fit_transform(reshaped)
        else:
            # Se il numero di componenti è troppo basso, salta la PCA
            pass

    # Esegui DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(reshaped)

    # I punti considerati "rumore" da DBSCAN avranno l'etichetta -1
    anomalies = labels == -1
    return anomalies.reshape(image.shape[:2])

def find_anomalies_svm(image, kernel="rbf", C=1.0, sampling_rate=0.1):
    # Assicurati che il kernel sia una stringa valida
    if kernel not in ["linear", "poly", "rbf", "sigmoid"]:
        raise ValueError(f"Invalid kernel: {kernel}. Must be one of ['linear', 'poly', 'rbf', 'sigmoid'].")

    reshaped = image.reshape(-1, image.shape[2])

    # Applica il campionamento casuale
    sample_size = int(reshaped.shape[0] * sampling_rate)
    indices = np.random.choice(reshaped.shape[0], sample_size, replace=False)
    sampled_reshaped = reshaped[indices]

    svm = OneClassSVM(kernel=kernel, nu=0.1, gamma='auto')
    svm.fit(sampled_reshaped)
    predictions = svm.predict(sampled_reshaped)

    anomalies = np.full(reshaped.shape[0], False)
    anomalies[indices] = predictions == -1

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