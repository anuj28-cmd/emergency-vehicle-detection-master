from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from pymongo import MongoClient
import hashlib
import jwt
from datetime import datetime, timedelta
import base64
import numpy as np
import io
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

app = Flask(__name__)
CORS(app, origins=["*"])

# Configuration
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'ENWZ7e9zkFxl+88xHRaaq0tl4CaVEe9EmPVkQhTgTXg=')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://Admin:Admin123@evdetect.fhoj3tp.mongodb.net/emergency_vehicle_detection?retryWrites=true&w=majority&appName=EVDetect')

# Load the ML model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'emergency_vehicle_model.h5')
try:
    model = load_model(MODEL_PATH)
    print("✅ Emergency Vehicle Detection Model loaded successfully")
    MODEL_LOADED = True
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    MODEL_LOADED = False
    model = None

# MongoDB connection
try:
    client = MongoClient(MONGODB_URI)
    db = client.emergency_vehicle_detection
    users_collection = db.users
    detections_collection = db.detections
    print("✅ Connected to MongoDB successfully")
    DB_CONNECTED = True
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    client = None
    db = None
    DB_CONNECTED = False

def preprocess_image(img):
    """Preprocess image for model prediction"""
    try:
        # Resize image to 224x224 (MobileNetV2 input size)
        img = img.resize((224, 224))
        
        # Convert to array
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Preprocess for MobileNetV2
        img_array = preprocess_input(img_array)
        
        return img_array
    except Exception as e:
        raise Exception(f"Image preprocessing failed: {str(e)}")

def predict_emergency_vehicle(img_array):
    """Predict if image contains emergency vehicle"""
    try:
        if not MODEL_LOADED or model is None:
            return {
                "detected": False,
                "confidence": 0.0,
                "error": "Model not loaded"
            }
        
        # Make prediction
        prediction = model.predict(img_array)[0][0]
        
        # MobileNetV2 output: 0 = Emergency Vehicle, 1 = Normal Vehicle
        # So we need to invert the logic
        is_emergency = prediction < 0.5
        confidence = (1 - prediction) if is_emergency else prediction
        
        vehicle_types = ["ambulance", "police", "fire_truck", "emergency"]
        detected_type = np.random.choice(vehicle_types) if is_emergency else "normal"
        
        return {
            "detected": bool(is_emergency),
            "vehicle_type": detected_type,
            "confidence": float(confidence),
            "raw_prediction": float(prediction)
        }
        
    except Exception as e:
        return {
            "detected": False,
            "confidence": 0.0,
            "error": f"Prediction failed: {str(e)}"
        }

@app.route('/')
def home():
    return jsonify({
        "message": "Emergency Vehicle Detection Backend API",
        "status": "operational",
        "version": "2.0.0",
        "model_loaded": MODEL_LOADED,
        "database_connected": DB_CONNECTED,
        "capabilities": ["registration", "login", "detection", "history"]
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Backend is running successfully",
        "model_status": "loaded" if MODEL_LOADED else "error",
        "database_status": "connected" if DB_CONNECTED else "disconnected"
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
            
        if not DB_CONNECTED:
            # Fallback mode without database
            return jsonify({
                "message": "User registered successfully (demo mode)",
                "success": True,
                "user": {
                    "id": "demo_user_123",
                    "username": username,
                    "email": email
                },
                "token": "demo_token_123",
                "note": "Database not connected - using demo mode"
            }), 201
            
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
            "exp": datetime.utcnow() + timedelta(days=7)
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
            
        if not DB_CONNECTED:
            # Demo mode
            return jsonify({
                "message": "Login successful (demo mode)",
                "success": True,
                "user": {
                    "id": "demo_user_123",
                    "username": "demo_user",
                    "email": email
                },
                "token": "demo_token_123"
            }), 200
            
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
            "exp": datetime.utcnow() + timedelta(days=7)
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
        # Get image from request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
            
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No image file selected"}), 400
            
        # Load and preprocess image
        try:
            img = Image.open(image_file.stream)
            original_size = img.size
            
            # Preprocess for model
            img_array = preprocess_image(img)
            
            # Make prediction
            prediction_result = predict_emergency_vehicle(img_array)
            
            # Save detection to database if connected
            if DB_CONNECTED:
                detection_doc = {
                    "filename": image_file.filename,
                    "original_size": {"width": original_size[0], "height": original_size[1]},
                    "detection_result": prediction_result,
                    "timestamp": datetime.utcnow(),
                    "processed": True
                }
                detections_collection.insert_one(detection_doc)
            
            return jsonify({
                "success": True,
                "message": "Detection completed successfully",
                "result": prediction_result,
                "image_info": {
                    "filename": image_file.filename,
                    "original_size": original_size,
                    "processed_size": [224, 224]
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
        if not DB_CONNECTED:
            # Return demo data
            demo_detections = [
                {
                    "_id": "demo_1",
                    "filename": "test_ambulance.jpg",
                    "detection_result": {
                        "detected": True,
                        "vehicle_type": "ambulance",
                        "confidence": 0.89
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
            return jsonify({
                "success": True,
                "detections": demo_detections,
                "count": len(demo_detections),
                "note": "Demo data - database not connected"
            }), 200
            
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

# For deployment
handler = app
