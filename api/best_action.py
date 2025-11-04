from http.server import BaseHTTPRequestHandler
import json
import pickle
import sys
import os
import numpy as np

# Add model directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'model'))

from nTupleAgent import nTupleNetwork

# Global agent variable (cached after first load)
agent = None


def load_agent():
    global agent
    if agent is None:
        model_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'trained_agent.pkl')
        with open(model_path, 'rb') as f:
            n_games, loaded_agent = pickle.load(f)
            agent = loaded_agent
    return agent


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Get board from request
            board = np.array(data['board'])

            # Load agent and get best action
            agent = load_agent()
            action = int(agent.best_action(board))

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = json.dumps({'action': action})
            self.wfile.write(response.encode())

        except Exception as e:
            # Error handling
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = json.dumps({'error': str(e), 'type': type(e).__name__})
            self.wfile.write(error_response.encode())

    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()