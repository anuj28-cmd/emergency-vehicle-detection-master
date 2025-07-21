from flask import Flask, jsonify
from flask_cors import CORS
import os
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["*"])

# Use your actual MongoDB URI from .env.secure
MONGODB_URI = "mongodb+srv://Admin:Admin123@evdetect.fhoj3tp.mongodb.net/emergency_vehicle_detection?retryWrites=true&w=majority&appName=EVDetect"

@app.route('/')
def home():
    return jsonify({
        "message": "Database Connection Test",
        "status": "operational"
    })

@app.route('/api/test-db')
def test_database():
    try:
        # Try to connect to MongoDB
        client = MongoClient(MONGODB_URI)
        
        # Test the connection
        client.admin.command('ping')
        
        # Get database info
        db = client.emergency_vehicle_detection
        
        # Try to create a test document
        test_collection = db.connection_test
        test_doc = {
            "test": True,
            "timestamp": datetime.utcnow(),
            "message": "Connection successful from Vercel"
        }
        
        result = test_collection.insert_one(test_doc)
        
        # Try to read it back
        found_doc = test_collection.find_one({"_id": result.inserted_id})
        
        return jsonify({
            "database_status": "✅ CONNECTED",
            "connection": "success",
            "insert_test": "success",
            "read_test": "success",
            "document_id": str(result.inserted_id),
            "server_info": str(client.server_info().get('version', 'unknown'))
        }), 200
        
    except Exception as e:
        return jsonify({
            "database_status": "❌ FAILED", 
            "error": str(e),
            "error_type": type(e).__name__
        }), 500

@app.route('/api/register', methods=['POST'])
def register():
    return jsonify({
        "message": "Registration endpoint ready - testing database first",
        "status": "test_mode"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# For Vercel deployment
handler = app
