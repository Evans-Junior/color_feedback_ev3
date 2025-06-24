# api_server.py

from flask import Flask, request, jsonify
from mqtt_client import MqttPublisher
from config import MQTT_TOPIC, API_TOKEN
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

mqtt_publisher = MqttPublisher(MQTT_TOPIC)

def is_authorized(request):
    """Check if the request contains a valid API token."""
    token = request.headers.get('Authorization')
    return token == f"Bearer {API_TOKEN}"

@app.route('/color-feedback', methods=['POST'])
def receive_color_feedback():
    """
    Secured endpoint to receive color feedback.
    Requires Bearer token in Authorization header.
    """
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data or 'color' not in data:
        return jsonify({"error": "Missing 'color' in request body"}), 400

    color_code = data['color']
    mqtt_publisher.publish_color(color_code)
    return jsonify({"status": "Color code sent to EV3", "color": color_code}), 200


@app.route('/')
def index():
    """Simple index route to confirm the API is running."""
    return jsonify({"message": "EV3 Color Feedback API is running"}), 200