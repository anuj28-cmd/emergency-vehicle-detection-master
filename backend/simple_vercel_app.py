from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import base64
import os
import json
import datetime
import tensorflow as tf

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Mock data for emergency vehicles
MOCK_DETECTIONS = [
    {"id": "1", "timestamp": "2025-06-15T08:30:00", "location": "Main St & 5th Ave", "emergency_detected": True, "confidence": 0.95, "vehicle_type": "ambulance"},
    {"id": "2", "timestamp": "2025-06-15T09:45:00", "location": "Highway 101, Mile 23", "emergency_detected": True, "confidence": 0.92, "vehicle_type": "police"},
    {"id": "3", "timestamp": "2025-06-16T14:20:00", "location": "Central Park West", "emergency_detected": False, "confidence": 0.78, "vehicle_type": "civilian"},
    {"id": "4", "timestamp": "2025-06-17T11:05:00", "location": "Downtown, 3rd Street", "emergency_detected": True, "confidence": 0.88, "vehicle_type": "fire_truck"},
    {"id": "5", "timestamp": "2025-06-18T16:40:00", "location": "Industrial Zone", "emergency_detected": False, "confidence": 0.71, "vehicle_type": "civilian"}
]

class SimpleEmergencyVehicleDetector:
    def __init__(self):
        self.model = None
        self.config = {
            "model_type": "mobilenetv2",
            "task": "image-classification",
            "framework": "tensorflow",
            "input_size": [224, 224, 3],
            "num_classes": 2,
            "classes": ["no_emergency", "emergency_vehicle"],
            "preprocessing": {
                "resize": [224, 224],
                "normalize": {
                    "mean": [0.485, 0.456, 0.406],
                    "std": [0.229, 0.224, 0.225]
                }
            }
        }
        
    def load_model(self):
        if self.model is None:
            # We won't actually load a model, just simulate its behavior
            print("Model simulation initialized")
            
    def preprocess_image(self, image):
        # Get preprocessing config
        input_size = self.config["input_size"]
        
        # Resize image
        image = image.resize((input_size[0], input_size[1]))
        
        # Convert to array and normalize
        image_array = np.array(image) / 255.0
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    def predict(self, image):
        self.load_model()  # Ensure "model" is initialized
        
        # Preprocess image
        processed_image = self.preprocess_image(image)
        
        # Instead of using a real model, we'll use simple logic based on image properties
        # This is just a simulation for demonstration purposes
        
        # Calculate average brightness as a simple feature
        brightness = np.mean(processed_image)
        
        # Simulate a model prediction based on brightness
        # Higher brightness often correlates with emergency vehicle lights
        if brightness > 0.6:
            # Simulate high confidence for emergency vehicle
            return np.array([[0.2, 0.8]])
        elif brightness > 0.45:
            # Simulate medium confidence
            return np.array([[0.4, 0.6]])
        else:
            # Simulate low confidence - probably not an emergency vehicle
            return np.array([[0.7, 0.3]])

# Global detector instance
detector = SimpleEmergencyVehicleDetector()

# Routes
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Emergency Vehicle Detection API',
        'status': 'running',
        'endpoints': {
            'detect': '/detect',
            'health': '/health',
            'history': '/history'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'model_loaded': True,
        'version': '1.0.0',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/detect', methods=['POST'])
def detect_emergency_vehicle():
    try:
        # Get image from request
        image = None
        
        if 'image' in request.files:
            # Handle file upload
            image_file = request.files['image']
            image = Image.open(image_file.stream)
        elif request.json and 'image_data' in request.json:
            # Handle base64 encoded image
            image_data = request.json['image_data']
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            return jsonify({'error': 'No image provided. Send as file or base64 in JSON'}), 400
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Run detection
        predictions = detector.predict(image)
        
        # Process predictions
        classes = detector.config["classes"]
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class = classes[predicted_class_idx]
        confidence = float(predictions[0][predicted_class_idx])
        
        # Determine if emergency vehicle is detected
        emergency_detected = predicted_class == 'emergency_vehicle'
        
        return jsonify({
            'emergency_vehicle_detected': emergency_detected,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_predictions': {
                classes[i]: float(predictions[0][i]) for i in range(len(classes))
            },
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Detection failed: {str(e)}'}), 500

@app.route('/history', methods=['GET'])
def get_detection_history():
    # Return mock detection history
    return jsonify({
        'detections': MOCK_DETECTIONS,
        'count': len(MOCK_DETECTIONS)
    })

@app.route('/model-info', methods=['GET'])
def model_info():
    return jsonify({
        'model_config': detector.config,
        'model_type': 'simulated' 
    })

# For local development
if __name__ == '__main__':
    app.run(debug=True)
