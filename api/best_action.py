from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import pickle
import sys
import os
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later to your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add model directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tmp', 'nTupleNetwork_63041games.pkl'))

from nTupleAgent import nTupleNetwork

# Global agent variable (cached after first load)
agent = None


def load_agent():
    global agent
    if agent is None:
        model_path = os.path.join(os.path.dirname(__file__), '..', 'tmp', 'nTupleNetwork_63041games.pkl')
        with open(model_path, 'rb') as f:
            n_games, loaded_agent = pickle.load(f)
            agent = loaded_agent
    return agent

@app.post("./predict")
async def predict(request: Request):
    data = await request.json()
    board = np.array(data["board"])

    agent = load_agent()
    action = agent.best_action(board)

    return {'action': action}

