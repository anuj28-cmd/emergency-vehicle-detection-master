from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import numpy as np
from PIL import Image
import tensorflow as tf
from datetime import datetime
import jwt
import hashlib
from pymongo import MongoClient
import base64
import io

app = Flask(__name__)
CORS(app, origins=["*"])

# Configuration
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'ENWZ7e9zkFxl+88xHRaaq0tl4CaVEe9EmPVkQhTgTXg=')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://Admin:Admin123@evdetect.fhoj3tp.mongodb.net/emergency_vehicle_detection?retryWrites=true&w=majority&appName=EVDetect')

# Model configuration
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'emergency_vehicle_model.h5')
CLASS_NAMES = {0: 'Emergency Vehicle', 1: 'Normal Vehicle'}
IMG_SIZE = (224, 224)  # Adjust based on your model

# Global model variable
model = None

# MongoDB connection
try:
    client = MongoClient(MONGODB_URI)
    db = client.emergency_vehicle_detection
    users_collection = db.users
    detections_collection = db.detections
    print("✅ Connected to MongoDB successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    client = None
    db = None

def load_model():
    """Load the trained model"""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            model = tf.keras.models.load_model(MODEL_PATH)
            print(f"✅ Model loaded successfully from {MODEL_PATH}")
            return True
        else:
            print(f"❌ Model file not found at {MODEL_PATH}")
            return False
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def preprocess_image(image):
    """Preprocess image for model prediction"""
    try:
        # Resize image to model input size
        image = image.resize(IMG_SIZE)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array and normalize
        img_array = np.array(image)
        img_array = img_array / 255.0  # Normalize to [0,1]
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        raise Exception(f"Image preprocessing failed: {str(e)}")

def predict_emergency_vehicle(image):
    """Make prediction using the loaded model"""
    global model
    
    if model is None:
        # Try to load model if not loaded
        if not load_model():
            # Fallback to mock prediction
            return mock_prediction()
    
    try:
        # Preprocess image
        processed_image = preprocess_image(image)
        
        # Make prediction
        predictions = model.predict(processed_image)
        
        # Get prediction results
        if len(predictions.shape) > 1 and predictions.shape[1] > 1:
            # Multi-class prediction
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class]) * 100
        else:
            # Binary prediction
            confidence = float(predictions[0][0]) * 100
            predicted_class = 1 if confidence > 50 else 0
        
        class_name = CLASS_NAMES.get(predicted_class, 'Unknown')
        
        # Create bounding box (mock coordinates - replace with actual detection if available)
        bbox = {
            "x": IMG_SIZE[0] // 4,
            "y": IMG_SIZE[1] // 4,
            "width": IMG_SIZE[0] // 2,
            "height": IMG_SIZE[1] // 2
        }
        
        return {
            "class": class_name,
            "confidence": confidence,
            "class_id": int(predicted_class),
            "coordinates": bbox,
            "model_used": "emergency_vehicle_model.h5"
        }
        
    except Exception as e:
        print(f"Model prediction error: {e}")
        # Fallback to mock prediction
        return mock_prediction()

def mock_prediction():
    """Fallback mock prediction when model is not available"""
    return {
        "class": "Emergency Vehicle",
        "confidence": 85.0,
        "class_id": 0,
        "coordinates": {"x": 56, "y": 42, "width": 112, "height": 84},
        "model_used": "mock_fallback"
    }

@app.route('/')
def home():
    return jsonify({
        "message": "Emergency Vehicle Detection API",
        "status": "operational",
        "model_loaded": model is not None,
        "database": "connected" if db else "disconnected",
        "version": "2.0.0"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "model_status": "loaded" if model else "not_loaded",
        "database_status": "connected" if db else "disconnected"
    })

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
        
    try:
        data = request.get_json() or {}
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not all([username, email, password]):
            return jsonify({"error": "Missing required fields: username, email, password"}), 400
            
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400
            
        if not db:
            return jsonify({"error": "Database connection unavailable"}), 500
            
        # Check if user already exists
        if users_collection.find_one({"email": email}):
            return jsonify({"error": "User with this email already exists"}), 409
            
        if users_collection.find_one({"username": username}):
            return jsonify({"error": "Username already taken"}), 409
            
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user document
        user_doc = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user
        result = users_collection.insert_one(user_doc)
        
        # Generate JWT token
        token_payload = {
            "user_id": str(result.inserted_id),
            "email": email,
            "username": username,
            "exp": datetime.utcnow().timestamp() + (7 * 24 * 60 * 60)  # 7 days
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "message": "User registered successfully",
            "success": True,
            "user": {
                "id": str(result.inserted_id),
                "username": username,
                "email": email
            },
            "token": token
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
        
    try:
        data = request.get_json() or {}
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not all([email, password]):
            return jsonify({"error": "Missing required fields: email, password"}), 400
            
        if not db:
            return jsonify({"error": "Database connection unavailable"}), 500
            
        # Find user
        user = users_collection.find_one({"email": email})
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
            
        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user['password_hash'] != password_hash:
            return jsonify({"error": "Invalid email or password"}), 401
            
        # Generate JWT token
        token_payload = {
            "user_id": str(user['_id']),
            "email": user['email'],
            "username": user['username'],
            "exp": datetime.utcnow().timestamp() + (7 * 24 * 60 * 60)  # 7 days
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "message": "Login successful",
            "success": True,
            "user": {
                "id": str(user['_id']),
                "username": user['username'],
                "email": user['email']
            },
            "token": token
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@app.route('/api/detect', methods=['POST', 'OPTIONS'])
def detect():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
        
    try:
        # Check if image file is provided
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
            
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No image file selected"}), 400
            
        # Process image
        try:
            image = Image.open(image_file.stream)
            original_size = image.size
            
            # Make prediction using the actual model
            prediction_result = predict_emergency_vehicle(image)
            
            # Save detection to database if connected
            if db:
                detection_doc = {
                    "filename": image_file.filename,
                    "original_size": {"width": original_size[0], "height": original_size[1]},
                    "prediction": prediction_result,
                    "timestamp": datetime.utcnow(),
                    "processed": True
                }
                result = detections_collection.insert_one(detection_doc)
                detection_id = str(result.inserted_id)
            else:
                detection_id = "no_db_connection"
            
            return jsonify({
                "success": True,
                "message": "Detection completed successfully",
                "detection_id": detection_id,
                "result": {
                    "vehicle_type": prediction_result["class"],
                    "confidence": prediction_result["confidence"],
                    "coordinates": prediction_result["coordinates"],
                    "is_emergency": prediction_result["class"] == "Emergency Vehicle",
                    "model_used": prediction_result["model_used"]
                },
                "image_info": {
                    "filename": image_file.filename,
                    "original_size": original_size
                }
            }), 200
            
        except Exception as img_error:
            return jsonify({"error": f"Image processing failed: {str(img_error)}"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Detection failed: {str(e)}"}), 500

@app.route('/api/history', methods=['GET', 'OPTIONS'])
def get_history():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
        
    try:
        if not db:
            return jsonify({"error": "Database connection unavailable"}), 500
            
        # Get recent detections
        detections = list(detections_collection.find().sort("timestamp", -1).limit(10))
        
        # Convert ObjectId to string for JSON serialization
        for detection in detections:
            detection['_id'] = str(detection['_id'])
            detection['timestamp'] = detection['timestamp'].isoformat()
            
        return jsonify({
            "success": True,
            "detections": detections,
            "count": len(detections)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch history: {str(e)}"}), 500

# Load model on startup
print("🚀 Starting Emergency Vehicle Detection API...")
load_model()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

# For deployment
handler = app
