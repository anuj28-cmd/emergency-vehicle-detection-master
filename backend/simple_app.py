from flask import Flask, jsonify, request
from flask_cors import CORS

# Create a simple test app
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "message": "Emergency Vehicle Detection API is running",
        "version": "1.0.0"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "database": "connected"
    })

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({"error": "Missing required fields"}), 400
            
        # Simplified registration - just return success for now
        return jsonify({
            "message": "User registered successfully",
            "success": True,
            "user": {
                "username": username,
                "email": email
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
