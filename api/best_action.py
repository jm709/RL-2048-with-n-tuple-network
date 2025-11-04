from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pickle
import os
import numpy as np

# Import your agent class
from nTupleAgent import nTupleNetwork

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your Vercel domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent variable (cached after first load)
agent = None


def load_agent():
    global agent
    if agent is None:
        # Adjust path based on your project structure
        model_path = os.path.join(os.path.dirname(__file__), '..', 'tmp', 'nTupleNetwork_63041games.pkl')
        print(f"Loading agent from: {model_path}")
        with open(model_path, 'rb') as f:
            n_games, loaded_agent = pickle.load(f)
            agent = loaded_agent
            print(f"Agent loaded successfully! Trained on {n_games} games")
    return agent


@app.get("/")
async def root():
    return {"message": "2048 AI API is running!"}


@app.post("/predict")  # Fixed: removed the dot
async def predict(request: Request):
    try:
        data = await request.json()
        board = np.array(data["board"])

        # Load agent and get prediction
        agent = load_agent()
        action = int(agent.best_action(board))  # Convert to int for JSON

        return {"action": action, "status": "success"}

    except Exception as e:
        return {"error": str(e), "status": "failed"}


@app.get("/health")
async def health():
    try:
        agent = load_agent()
        return {"status": "healthy", "agent_loaded": agent is not None}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}