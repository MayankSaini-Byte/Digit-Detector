import os
import base64
import io
import pickle
import joblib
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify, render_template
from skimage.feature import hog

app = Flask(__name__)

# Load SVM Model and HOG parameters
# Using absolute paths relative to app.py location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "svm_digit_model_compressed.pkl")
HOG_PATH = os.path.join(BASE_DIR, "models", "hog_params.pkl")

print("Loading SVM model and HOG parameters...")
try:
    model = joblib.load(MODEL_PATH)
    hog_params = joblib.load(HOG_PATH)
    print("Model and HOG parameters loaded successfully.")
except Exception as e:
    print(f"Error loading model/params: {e}")
    model = None
    hog_params = None

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/canvas")
def canvas():
    return render_template("canvas.html")

@app.route("/analysis")
def analysis():
    return render_template("analysis.html")

@app.route("/predict", methods=["POST"])
def predict():
    if model is None or hog_params is None:
        return jsonify({"error": "Model or HOG configuration is not loaded on server."}), 500

    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image data provided"}), 400

    try:
        # Decode base64 image data
        image_data = data["image"]
        if "," in image_data:
            image_data = image_data.split(",")[1]
        
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes))

        # Check background composition and handle transparency
        # The user draws a black line on a white canvas.
        # If there's an alpha channel, we blend it with a white background.
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3]) # paste using alpha channel as mask
            else:
                background.paste(img)
            img = background
        else:
            img = img.convert('RGB')

        # Convert to grayscale
        img_gray = img.convert("L")

        # Resize to 28x28 (MNIST standard size)
        img_resized = img_gray.resize((28, 28), Image.Resampling.BILINEAR)

        # Invert colors: canvas has black drawing on white background.
        # MNIST dataset has white digit stroke (255) on black background (0).
        # We invert so that white backgrounds become black, and black drawings become white.
        img_inverted = np.invert(np.array(img_resized))

        # Extract HOG features using identical parameters as the training script
        # orientations=9, pixels_per_cell=(4,4), cells_per_block=(2,2), block_norm='L2-Hys'
        features = hog(
            img_inverted,
            orientations=hog_params.get("orientations", 9),
            pixels_per_cell=hog_params.get("pixels_per_cell", (4, 4)),
            cells_per_block=hog_params.get("cells_per_block", (2, 2)),
            block_norm=hog_params.get("block_norm", "L2-Hys"),
            feature_vector=True
        )

        # Reshape for scikit-learn prediction (1 sample)
        features = features.reshape(1, -1)

        # Perform prediction
        prediction = int(model.predict(features)[0])

        # Compute confidence using softmax on decision function
        decision_values = model.decision_function(features)[0]
        exp_values = np.exp(decision_values - np.max(decision_values))
        probabilities = exp_values / np.sum(exp_values)
        confidence = float(probabilities[prediction])

        return jsonify({
            "prediction": prediction,
            "confidence": confidence
        })

    except Exception as e:
        print(f"Error during preprocessing or prediction: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Host on 0.0.0.0 and port 7860 as requested for Hugging Face Spaces deployment
    app.run(host="0.0.0.0", port=7860, debug=True)
