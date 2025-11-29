from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from mongoengine import connect
from mongoengine.connection import get_connection
from dotenv import load_dotenv
from datetime import timedelta
import os
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Secure JWT secret
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

# Connect to MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/InterviewAI')
connect(db='InterviewAI', host=MONGO_URI)

# Register blueprints
from routes.adminRoutes import admin_bp


app.register_blueprint(admin_bp, url_prefix='/api/admin')


@app.route('/api/health')
def index():
    return jsonify({'message': 'Backend Running at 01 December 2025!'}), 200

@app.route('/api/mongo-status')
def mongo_status():
    try:
        conn = get_connection()
        # Force a command to verify actual connectivity
        conn.admin.command('ping')
        return jsonify({
            'status': 'connected',
            'mongo_uri': MONGO_URI
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'disconnected',
            'error': str(e)
        }), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5055, use_reloader=False)
