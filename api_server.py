from flask import Flask, request, jsonify
from flask_cors import CORS
from config import API_TOKEN
from collections import deque

app = Flask(__name__)
CORS(app)

# FIFO queue to store requests
color_queue = deque()

def is_authorized(req):
    token = req.headers.get("Authorization")
    return token == f"Bearer {API_TOKEN}"

@app.route('/color-feedback', methods=['POST'])
def receive_color_feedback():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data or 'color' not in data or 'team' not in data:
        return jsonify({"error": "Missing 'color' or 'team' in request body"}), 400

    payload = {
        "team": data['team'],
        "color": data['color']
    }

    color_queue.append(payload)
    print(f"Queued color '{payload['color']}' for team '{payload['team']}'")

    return jsonify({"status": "Color queued"}), 200

@app.route('/next', methods=['GET'])
def get_next_color():
    """
    GET /next or /next?team=alpha
    Pops and returns the next item globally or for a specific team.
    """
    team_filter = request.args.get("team")

    if team_filter:
        # Look for the first item matching the team
        for i, item in enumerate(color_queue):
            if item["team"] == team_filter:
                result = color_queue[i]
                del color_queue[i]  # Remove it from the queue
                return jsonify(result), 200
        return jsonify({"team": None, "color": None}), 200
    else:
        # No team filter — pop the next global item
        if color_queue:
            return jsonify(color_queue.popleft()), 200
        else:
            return jsonify({"team": None, "color": None}), 200

@app.route('/admin/clear-queue', methods=['POST'])
def clear_queue():
    """
    POST /admin/clear-queue
    Clears the queue (admin-only)
    """
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    cleared = len(color_queue)
    color_queue.clear()
    print(f"Admin cleared queue of {cleared} items.")

    return jsonify({"status": "Queue cleared", "items_removed": cleared}), 200

@app.route('/queue', methods=['GET'])
def view_queue():
    return jsonify(list(color_queue)), 200



# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
