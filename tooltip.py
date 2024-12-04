# Dizionario dei testi tooltip
TOOLTIPS = {
    "method_combobox": (
        "Select the method to analyze anomalies. Options include:\n"
        "- Standard: Basic anomaly detection using thresholds.\n"
        "- PCA: Principal Component Analysis to detect anomalies based on important features.\n"
        "- K-means: Clustering algorithm that identifies outliers as anomalies.\n"
        "- Isolation Forest: Detects anomalies by isolating data points through random partitioning.\n"
        "- DBSCAN: Density-Based Spatial Clustering with outliers as unclustered points.\n"
        "- SVM: Support Vector Machine separates anomalies from normal data."
    ),
    "pca_slider": "Set the number of PCA components for dimensionality reduction.",
    "eps_slider": (
        "Set the maximum distance between samples for them to be considered in the same neighborhood "
        "(DBSCAN parameter)."
    ),
    "min_samples_slider": (
        "Set the number of samples in a neighborhood for a point to be considered a core point "
        "(DBSCAN parameter)."
    ),
    "svm_kernel": (
        "Select the kernel type for SVM. Options include:\n"
        "- linear\n"
        "- polynomial\n"
        "- radial basis function (rbf)\n"
        "- sigmoid"
    ),
    "svm_c_slider": (
        "Set the regularization parameter for SVM. Smaller values create smoother decision boundaries, "
        "while larger values focus on classifying all training points correctly."
    ),
    "threshold_slider": (
        "Set the threshold value to control the sensitivity of anomaly detection. "
        "Higher values may detect fewer anomalies."
    ),
    "anomaly_combobox": (
        "Select the type of anomaly to detect in the Standard method:\n"
        "- Darker Pixels: Areas darker than the threshold.\n"
        "- Bright Pixels: Areas brighter than the threshold."
    ),
    "color_combobox": "Select the color to highlight detected anomalies in the image.",
    "brightness_slider": (
        "Adjust the brightness of the image before anomaly detection. Higher values increase brightness."
    ),
    "contrast_slider": (
        "Adjust the contrast of the image before anomaly detection. Higher values increase contrast."
    ),
}

# Funzione per ottenere il tooltip dal dizionario
def get_tooltip(key):
    """
    Ottieni il testo del tooltip per una determinata chiave.

    :param key: Chiave associata al tooltip (es: "method_combobox").
    :return: Testo del tooltip (stringa).
    """
    return TOOLTIPS.get(key, "No tooltip available for this item.")