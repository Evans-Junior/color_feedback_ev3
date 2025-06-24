# main.py

from api_server import app
from config import API_HOST, API_PORT

if __name__ == '__main__':
    print(f"Starting API server on http://{API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT)
