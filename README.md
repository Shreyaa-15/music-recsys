# Real-Time Music Recommendation System

A production-style recommendation engine built with a two-tower neural network, FAISS approximate nearest neighbor search, implicit feedback modeling, and A/B test infrastructure.

Inspired by how Spotify, YouTube, and Instagram build their recommendation systems.

## Features
- Two-tower neural network (user tower + item tower) trained with BPR loss
- Implicit feedback modeling using Hu et al. (2008) confidence weighting
- FAISS IndexFlatIP for sub-millisecond ANN serving
- A/B test engine — two-tower vs popularity baseline with CTR/skip/like metrics
- Real-time feedback logging (click, skip, like, impression)
- Dark minimal dashboard showing training curves and live metrics

## Results
- Recall@10: 46.3% on held-out test set
- A/B test: +26.7% CTR lift over popularity baseline
- 10,870 user-artist interactions · 1,000 users · 50 artists

## Tech Stack
- **Model:** PyTorch two-tower neural network
- **Serving:** FAISS (IndexFlatIP) + FastAPI
- **Feedback:** Implicit confidence scoring (Hu et al. 2008)
- **Frontend:** React + Vite (dark minimal aesthetic)
- **Storage:** SQLite

## Architecture

### Two-Tower Model
User tower: Embedding(user_id) → MLP → 64-dim L2-normalized vector
Item tower: Embedding(artist_id) + genre features → MLP → 64-dim L2-normalized vector
Score: dot product (= cosine similarity after normalization)

### Serving Pipeline
1. Item embeddings pre-computed offline → stored in FAISS
2. At request time: user tower runs online → FAISS top-K retrieval
3. Results ranked by cosine similarity score

### Training
- Loss: BPR (Bayesian Personalized Ranking)
- Negative sampling: 4× per positive interaction
- Optimizer: Adam with StepLR scheduler
- Epochs: 15

## Run Locally

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate data + train model
python3 data_loader.py
python3 trainer.py

# Build FAISS index
python3 -c "from indexer import build_faiss_index; build_faiss_index()"

# Start API
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /recommend/{user_id} | Get personalized recommendations |
| POST | /feedback | Log click/skip/like/impression |
| GET | /ab-test | A/B test metrics and lift |
| GET | /stats | Model stats and feedback breakdown |
| GET | /embeddings | Raw item embeddings for visualization |