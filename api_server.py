from flask import Flask, request, jsonify
from mqtt_client import MqttPublisher
from config import MQTT_TOPIC, API_TOKEN
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

mqtt_publisher = MqttPublisher(MQTT_TOPIC)
last_received_color = None  # Store last color received

def is_authorized(request):
    """Check if the request contains a valid API token."""
    token = request.headers.get('Authorization')
    return token == f"Bearer {API_TOKEN}"

@app.route('/color-feedback', methods=['POST'])
def receive_color_feedback():
    """Secured POST endpoint to receive and publish color feedback."""
    global last_received_color

    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data or 'color' not in data:
        return jsonify({"error": "Missing 'color' in request body"}), 400

    color_code = data['color']
    # if last_received_color does not have  : old message, then add it
    if last_received_color is None or last_received_color != color_code:
        last_received_color = color_code + ' : old message'
    mqtt_publisher.publish_color(color_code)
    return jsonify({"status": "Color code sent to VEX", "color": color_code}), 200

@app.route('/color-feedback', methods=['GET'])
def get_last_color():
    # global last_received_color 
    """GET endpoint to return the last color received."""
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    if last_received_color is None or last_received_color == last_received_color + ' : old message':
        return jsonify({"message": "No color has been received yet."}), 200
    return jsonify({"color": last_received_color}), 200

@app.route('/')
def index():
    """Simple index route to confirm the API is running."""
    return jsonify({"message": "EV3 Color Feedback API is running"}), 200
