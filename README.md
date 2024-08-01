<img src="https://github.com/gabcicc/S.A.D.A./blob/main/images/logo_SADA_.png" alt="Logo" width="25%">

# Smart Anomaly Detection Assistant (S.A.D.A.)

## Overview

The Smart Anomaly Detection Assistant (S.A.D.A.) is an advanced application designed to aid archaeologists in analyzing aerial and satellite imagery to detect potential archaeological anomalies. Developed using the capabilities of ChatGPT, S.A.D.A. leverages state-of-the-art image processing techniques and machine learning algorithms to identify and highlight anomalies in vegetation and soil patterns that may indicate hidden archaeological features.

## Key Features

1. **Image Loading and Display:**
   - Users can load aerial or satellite images directly into the application.
   - The loaded image is displayed on a dynamic canvas within the graphical user interface (GUI).

2. **Image Selection:**
   - Two methods of image selection are provided: Standard Rectangular Selection and Polygonal Selection.
   - Users can select specific areas of the image for detailed analysis.

3. **Anomaly Detection Algorithms:**
   - S.A.D.A. includes multiple methods for anomaly detection, such as:
     - Standard thresholding to detect darker or lighter pixels.
     - Principal Component Analysis (PCA) for statistical analysis.
     - Isolation Forest for outlier detection.
     - K-means clustering for grouping similar pixel values.
   - Users can choose the desired algorithm from a dropdown menu.

4. **Real-time Adjustments:**
   - Adjustable threshold slider allows real-time modification of detection sensitivity.
   - Brightness and contrast sliders enable real-time adjustments to image visibility and clarity.

5. **Zoom and Pan:**
   - Users can zoom in on selected areas or zoom out to view the entire image.
   - Panning functionality allows users to navigate across zoomed-in images.

6. **Undo/Redo Functionality:**
   - Users can easily undo or redo actions, providing flexibility in analysis and adjustments.

7. **Saving and Resetting:**
   - Processed images can be saved in various formats.
   - The application allows resetting to the original image state, clearing all selections and adjustments.

8. **User-friendly Interface:**
   - The GUI, built with Tkinter, is intuitive and easy to navigate.
   - Dropdown menus, buttons, and sliders are logically organized for efficient workflow.

## Development and Impact

S.A.D.A. was developed entirely through iterative interactions with ChatGPT, showcasing the potential of generative AI in software development. The process involved generating and refining Python code, incorporating user feedback, and addressing errors. This collaboration highlights how non-programmers can create sophisticated applications by leveraging AI tools.
