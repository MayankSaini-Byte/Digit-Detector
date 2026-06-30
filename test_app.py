import unittest
import json
import base64
import io
from PIL import Image
from app import app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page(self):
        """Verify home page loads successfully"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Digit Detector", response.data)

    def test_canvas_page(self):
        """Verify canvas page loads successfully"""
        response = self.client.get("/canvas")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Prediction", response.data)

    def test_analysis_page(self):
        """Verify analysis page loads successfully"""
        response = self.client.get("/analysis")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Support Vector Machine", response.data)

    def test_predict_endpoint_success(self):
        """Verify predict endpoint handles a valid mock drawing submission"""
        # Create a simple dummy drawing of a digit (280x280 white background with a black stroke)
        img = Image.new("RGB", (280, 280), color="white")
        # Draw a small block in the middle mimicking a digit center
        for i in range(130, 150):
            for j in range(130, 150):
                img.putpixel((i, j), (0, 0, 0)) # black stroke pixel

        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        payload = {"image": f"data:image/png;base64,{img_base64}"}

        # Send POST request
        response = self.client.post(
            "/predict",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn("prediction", data)
        self.assertTrue(isinstance(data["prediction"], int))
        self.assertIn("confidence", data)
        self.assertTrue(isinstance(data["confidence"], float))
        print(f"Mock classification result predicted digit class: {data['prediction']} with confidence {data['confidence']:.2f}")

    def test_predict_endpoint_missing_payload(self):
        """Verify error payload format returns bad request code"""
        response = self.client.post(
            "/predict",
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()
