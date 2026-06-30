---
title: Digit Detector
emoji: 🔢
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---
# Digit Detector — Classical Machine Learning

A polished, modern handwritten digit recognition web application powered by **Histogram of Oriented Gradients (HOG)** feature extraction and a **Support Vector Machine (SVM)** classifier. 

Live Demo style mimics modern minimalist designs (Vercel, Linear, Stripe).

## Project Pipeline

1. **Grayscale Conversion**: Normalizes canvas drawings to 1-channel color space.
2. **Resizing & Inverting**: Converts 280x280 inputs down to 28x28 (MNIST size) and inverts pixels to match MNIST data layouts (white digit on black background).
3. **HOG Descriptor**: Computes local edge gradient directions to extract shape structures.
4. **SVM Classifier**: Radial Basis Function (RBF) kernel predicts digit class.

## Installation & Local Execution

1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask server:
   ```bash
   python app.py
   ```
4. Access the web interface at `http://127.0.0.1:7860`.
