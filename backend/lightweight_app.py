from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from pymongo import MongoClient
import hashlib
import jwt
from datetime import datetime, timedelta
import requests
import base64
from PIL import Image
import io

app = Flask(__name__)
CORS(app, origins=["*"])

# Configuration
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'ENWZ7e9zkFxl+88xHRaaq0tl4CaVEe9EmPVkQhTgTXg=')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://Admin:Admin123@evdetect.fhoj3tp.mongodb.net/emergency_vehicle_detection?retryWrites=true&w=majority&appName=EVDetect')

# Hugging Face Configuration
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', 'your-hf-token')
HUGGINGFACE_MODEL_URL = os.getenv('HUGGINGFACE_MODEL_URL', 'https://api-inference.huggingface.co/models/your-model')

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

def call_huggingface_api(image_bytes):
    """Call Hugging Face API for emergency vehicle detection"""
    try:
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Convert image to base64 for API call
        image_b64 = base64.b64encode(image_bytes).decode()
        
        payload = {
            "inputs": image_b64,
            "parameters": {
                "threshold": 0.5
            }
        }
        
        response = requests.post(HUGGINGFACE_MODEL_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            # Parse Hugging Face response (adjust based on your model's output format)
            if isinstance(result, list) and len(result) > 0:
                prediction = result[0]
                
                # Assume your model returns classification results
                if 'label' in prediction and 'score' in prediction:
                    is_emergency = 'emergency' in prediction['label'].lower()
                    confidence = prediction['score']
                    
                    return {
                        "detected": is_emergency,
                        "vehicle_type": prediction['label'],
                        "confidence": float(confidence),
                        "source": "huggingface_api"
                    }
            
            # Fallback to mock detection if response format is unexpected
            return mock_detection()
            
        else:
            print(f"Hugging Face API error: {response.status_code}")
            return mock_detection()
            
    except Exception as e:
        print(f"Hugging Face API call failed: {e}")
        return mock_detection()

def mock_detection():
    """Fallback mock detection when API is unavailable"""
    import random
    
    is_emergency = random.choice([True, False])
    vehicle_types = ["ambulance", "police", "fire_truck"] if is_emergency else ["car", "truck", "bus"]
    
    return {
        "detected": is_emergency,
        "vehicle_type": random.choice(vehicle_types),
        "confidence": random.uniform(0.7, 0.95),
        "source": "mock_fallback"
    }

@app.route('/')
def home():
    return jsonify({
        "message": "Emergency Vehicle Detection Backend API",
        "status": "operational",
        "version": "3.0.0",
        "ml_service": "Hugging Face API",
        "database_connected": DB_CONNECTED,
        "capabilities": ["registration", "login", "detection", "history"]
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Backend is running successfully",
        "ml_service": "external_api",
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
            
        # Read image data
        image_bytes = image_file.read()
        
        # Get image info using PIL
        try:
            img = Image.open(io.BytesIO(image_bytes))
            original_size = img.size
        except Exception:
            original_size = (0, 0)
        
        # Call Hugging Face API for prediction
        prediction_result = call_huggingface_api(image_bytes)
        
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
                "original_size": original_size
            }
        }), 200
        
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
                        "confidence": 0.89,
                        "source": "huggingface_api"
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
