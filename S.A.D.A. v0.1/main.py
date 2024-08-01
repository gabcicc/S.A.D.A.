import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def load_image(image_path):
    # Uploads an image from the specified path.
    return Image.open(image_path)

def find_anomalies(image, threshold=100):
    # Find the anomalies in the image, assuming that the darker areas      
      represent anomalies.
    image_array = np.array(image)
    anomalies = image_array[:, :, 0] < threshold
    return anomalies

def highlight_anomalies(image, anomalies):
    # Highlight anomalies in red on the image.
    highlighted_image = np.array(image).copy()
    highlighted_image[anomalies] = [255, 0, 0]
    return Image.fromarray(highlighted_image)

def display_image(image):
    # Display the image using matplotlib.
    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    plt.axis('off')
    plt.show()

def main(image_path):
    # Performs the entire process of image loading, anomaly detection  
      and result display
    image = load_image(image_path)
    anomalies = find_anomalies(image)
    highlighted_image = highlight_anomalies(image, anomalies)
    display_image(highlighted_image)

# Input image path
image_path = 'image_path/image.jpeg'
main(image_path)
