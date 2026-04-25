import os
import json
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from db import init_db, save_feedback, get_feedback_stats
from recommender import get_recommendations, get_popular_items, get_all_item_embeddings
from ab_test import assign_variant, log_event, get_ab_metrics
from indexer import build_faiss_index

load_dotenv()

app = FastAPI(title="Music Recommendation System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    if not os.path.exists("models/faiss.index"):
        print("Building FAISS index...")
        build_faiss_index()


# --- Models ---

class FeedbackEvent(BaseModel):
    user_id:   int
    artist_id: int
    event:     str   # click, skip, like, impression


# --- Endpoints ---

@app.get("/recommend/{user_id}")
def recommend(user_id: int, top_k: int = 10):
    variant = assign_variant(user_id)
    if variant == "treatment":
        results = get_recommendations(user_id, top_k)
    else:
        results = get_popular_items(top_k)
    return {
        "user_id": user_id,
        "variant": variant,
        "results": results
    }

@app.post("/feedback")
def feedback(event: FeedbackEvent):
    variant = assign_variant(event.user_id)
    save_feedback(event.user_id, event.artist_id, event.event, variant)
    log_event(event.user_id, event.artist_id, event.event, variant)
    return {"status": "ok"}

@app.get("/ab-test")
def ab_test():
    return get_ab_metrics()

@app.get("/embeddings")
def embeddings():
    """Return item embeddings for 2D visualization."""
    items = get_all_item_embeddings()
    return {"items": items}

@app.get("/stats")
def stats():
    return {
        "feedback": get_feedback_stats(),
        "model":    "two_tower_neural_net",
        "recall_at_10": 0.4633
    }

@app.get("/health")
def health():
    return {"status": "ok"}