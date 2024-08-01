import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector


class ImageAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = self.load_image(image_path)
        self.selection = None
        self.fig, self.ax = plt.subplots()

    def load_image(self, image_path):
        """
        Carica un'immagine dal percorso specificato.
        """
        image = Image.open(image_path)
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        return image

    def find_anomalies(self, image, threshold=100):
        """
        Trova le anomalie nell'immagine, assumendo che le aree più scure rappresentino anomalie.
        """
        image_array = np.array(image)
        anomalies = image_array[:, :, 0] < threshold
        return anomalies

    def highlight_anomalies(self, image, anomalies):
        """
        Evidenzia le anomalie in rosso sull'immagine.
        """
        highlighted_image = np.array(image).copy()
        highlighted_image[anomalies] = [255, 0, 0]
        return Image.fromarray(highlighted_image)

    def display_image(self, image):
        """
        Visualizza l'immagine usando matplotlib.
        """
        fig, ax = plt.subplots()
        ax.imshow(image)
        plt.axis('off')
        plt.show()

    def onselect(self, eclick, erelease):
        """
        Gestisce la selezione del rettangolo.
        """
        self.selection = (int(eclick.xdata), int(eclick.ydata), int(erelease.xdata), int(erelease.ydata))
        print(f"Selected area: {self.selection}")
        plt.close(self.fig)

    def select_area(self):
        """
        Permette all'utente di selezionare un'area dell'immagine.
        """
        self.ax.imshow(self.image)
        self.rs = RectangleSelector(self.ax, self.onselect,
                                    useblit=True,
                                    button=[1],  # Left mouse button
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True)
        plt.show()

    def main(self):
        """
        Esegue l'intero processo di caricamento dell'immagine, rilevamento delle anomalie e visualizzazione del risultato.
        """
        self.select_area()

        if self.selection:
            x1, y1, x2, y2 = self.selection
            cropped_image = self.image.crop((x1, y1, x2, y2))
            anomalies = self.find_anomalies(cropped_image)
            highlighted_image = self.highlight_anomalies(cropped_image, anomalies)
        else:
            anomalies = self.find_anomalies(self.image)
            highlighted_image = self.highlight_anomalies(self.image, anomalies)

        self.display_image(highlighted_image)


# Percorso dell'immagine di input
image_path = '/image_path/Figure.png'
analyzer = ImageAnalyzer(image_path)
analyzer.main()
