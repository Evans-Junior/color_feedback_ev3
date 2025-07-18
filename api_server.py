from flask import Flask, request, jsonify
from flask_cors import CORS
from config import API_TOKEN
from collections import deque
from typing import Optional

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})  # allow all origins

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


@app.route('/reward-feedback', methods=['POST'])
def receive_reward_feedback():
    """
    Accepts reward data sent from frontend including:
    teamName, reward, timestamp, level, gameNumber, destination
    """
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    # Validate required fields
    required_fields = ['teamName', 'reward', 'timestamp', 'level', 'gameNumber']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing one or more required fields"}), 400

    payload = {
        "team": data["teamName"],
        "color": data["reward"],  # Mapping reward to color field for queue compatibility
        "timestamp": data["timestamp"],
        "level": data["level"],
        "gameNumber": data["gameNumber"],
        "destination": data.get("destination")  # Optional
    }

    color_queue.append(payload)
    print(f"Queued reward '{payload['color']}' for team '{payload['team']}' at game {payload['gameNumber']}")

    return jsonify({"status": "Reward queued"}), 200

@app.route('/peek', methods=['GET'])
def peek_team_payload():
    """
    GET /peek?team=alpha
    Returns the most recent payload for a specific team (without removing it)
    """
    team_filter = request.args.get("team")
    if not team_filter:
        return jsonify({"error": "Missing 'team' query parameter"}), 400

    # Iterate in reverse to get the most recent item
    for item in reversed(color_queue):
        if item.get("team") == team_filter:
            return jsonify(item), 200

    return jsonify({"team": team_filter, "destination": None, "message": "No pending data"}), 200


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


@app.route('/rewards/last', methods=['GET'])
def get_last_reward():
    """
    GET /rewards/last?team=team_name
    Returns the last reward for a specific team or the most recent reward from any team
    """
    team_filter = request.args.get("team")
    
    if team_filter:
        # Find the most recent reward for the specified team
        team_rewards = [item for item in reversed(color_queue) if item.get("team") == team_filter]
        if not team_rewards:
            return jsonify({"error": "No rewards found for this team"}), 404
        return jsonify(team_rewards[0])
    else:
        # Return the most recent reward from any team
        if not color_queue:
            return jsonify({"message": "No data available"}), 200
        return jsonify(color_queue[-1])


@app.route('/rewards', methods=['GET'])
def get_all_rewards():
    """
    GET /rewards?team=team_name
    Returns all rewards or all rewards for a specific team
    """
    team_filter = request.args.get("team")
    
    if team_filter:
        team_rewards = [item for item in color_queue if item.get("team") == team_filter]
        return jsonify(team_rewards)
    else:
        return jsonify(list(color_queue))


@app.route('/rewards/<team_name>', methods=['DELETE'])
def clear_team_rewards(team_name):
    print("Deleting rewards for team:", team_name)  # Debug log

    try:
        if not is_authorized(request):
            return jsonify({"error": "Unauthorized"}), 401

        initial_length = len(color_queue)
        color_queue[:] = [item for item in color_queue if item.get("team") != team_name]
        removed_count = initial_length - len(color_queue)

        if removed_count == 0:
            return jsonify({"error": "No rewards found for this team"}), 404

        return jsonify({"status": f"Cleared {removed_count} rewards for team '{team_name}'"})
    except Exception as e:
        import traceback
        traceback.print_exc()  # Logs full error
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route('/queue', methods=['GET'])
def view_queue():
    return jsonify(list(color_queue)), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)