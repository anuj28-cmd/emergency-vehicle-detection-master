from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from pymongo import MongoClient
import hashlib
import jwt
from datetime import datetime, timedelta
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app, origins=["*"])

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://heyan0827:heyankumar@cluster0.eqwvb.mongodb.net/emergency_vehicle_db?retryWrites=true&w=majority')

# MongoDB connection
try:
    client = MongoClient(MONGODB_URI)
    db = client.emergency_vehicle_db
    users_collection = db.users
    detections_collection = db.detections
    print("✅ Connected to MongoDB successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    client = None
    db = None

@app.route('/')
def home():
    return jsonify({
        "message": "Emergency Vehicle Detection Backend API",
        "status": "operational",
        "version": "2.0.0",
        "database": "connected" if db else "disconnected"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Backend is running successfully",
        "database": "connected" if db else "disconnected"
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
            
        # Check if database is connected
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
            
        # Check if database is connected
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
            
        # Process image with PIL
        try:
            image = Image.open(image_file.stream)
            width, height = image.size
            
            # Simple mock detection (replace with actual ML model)
            mock_detection = {
                "detected": True,
                "vehicle_type": "ambulance",
                "confidence": 0.87,
                "coordinates": {"x": width//2, "y": height//2, "width": 100, "height": 80}
            }
            
            # Save detection to database if connected
            if db:
                detection_doc = {
                    "image_size": {"width": width, "height": height},
                    "detection_result": mock_detection,
                    "timestamp": datetime.utcnow(),
                    "processed": True
                }
                detections_collection.insert_one(detection_doc)
            
            return jsonify({
                "success": True,
                "message": "Detection completed successfully",
                "result": mock_detection,
                "image_info": {"width": width, "height": height}
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

# For deployment
handler = app
