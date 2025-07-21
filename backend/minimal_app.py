from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/')
def home():
    return jsonify({
        "message": "Emergency Vehicle Detection Backend API",
        "status": "operational",
        "version": "1.0.0"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Backend is running successfully"
    })

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
        
    try:
        data = request.get_json() or {}
        
        username = data.get('username', '')
        email = data.get('email', '')
        password = data.get('password', '')
        
        if not all([username, email, password]):
            return jsonify({"error": "Missing required fields: username, email, password"}), 400
            
        # Simplified registration - just return success
        return jsonify({
            "message": "User registered successfully",
            "success": True,
            "user": {
                "username": username,
                "email": email,
                "id": "test_user_123"
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
        
    try:
        data = request.get_json() or {}
        
        email = data.get('email', '')
        password = data.get('password', '')
        
        if not all([email, password]):
            return jsonify({"error": "Missing required fields: email, password"}), 400
            
        # Simplified login - just return success
        return jsonify({
            "message": "Login successful",
            "success": True,
            "user": {
                "email": email,
                "username": "testuser",
                "id": "test_user_123"
            },
            "token": "test_jwt_token_123"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# For Vercel deployment
handler = app
