from flask import Flask, jsonify
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
    return jsonify({
        "message": "Registration endpoint working",
        "status": "test_mode"
    })

if __name__ == '__main__':
    app.run(debug=True)
