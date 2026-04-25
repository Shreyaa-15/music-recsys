import torch
import numpy as np
from model import TwoTowerModel
from indexer import load_index, load_checkpoint

_model = None
_index = None
_meta  = None


def load_model():
    global _model, _index, _meta
    if _model is not None:
        return

    print("Loading model + FAISS index...")
    _index, _meta = load_index()

    ckpt = load_checkpoint()
    _model = TwoTowerModel(
        _meta["num_users"],
        _meta["num_items"],
        output_dim=_meta["output_dim"]
    )
    _model.load_state_dict(ckpt["model_state"])
    _model.eval()
    print("Ready.")


def get_recommendations(user_id: int, top_k: int = 10,
                        exclude_seen: bool = True) -> list[dict]:
    """
    Online serving path:
    1. Look up user index
    2. Run user tower → 64-dim vector
    3. FAISS ANN search → top-K artists
    4. Return ranked list with scores
    """
    load_model()

    user2idx  = _meta["user2idx"]
    idx2artist = _meta["idx2artist"]

    # Handle unknown users — return popular items
    user_idx_str = str(user_id)
    if user_idx_str not in {str(v): v for v in user2idx.values()}:
        return get_popular_items(top_k)

    user_idx = user2idx.get(str(user_id), user2idx.get(user_id))
    if user_idx is None:
        return get_popular_items(top_k)

    user_tensor = torch.tensor([user_idx], dtype=torch.long)

    with torch.no_grad():
        user_emb = _model.get_user_embedding(user_tensor)
        user_vec = user_emb.numpy().astype("float32")

    # FAISS search
    scores, indices = _index.search(user_vec, top_k + 20)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        artist_id = idx2artist.get(str(idx), idx)
        results.append({
            "artist_id": int(artist_id),
            "score":     float(score),
            "rank":      len(results) + 1
        })
        if len(results) >= top_k:
            break

    return results


def get_popular_items(top_k: int = 10) -> list[dict]:
    """Fallback for cold-start users."""
    load_model()
    return [
        {"artist_id": i, "score": 1.0 - i * 0.05, "rank": i + 1}
        for i in range(min(top_k, _meta["num_items"]))
    ]


def get_user_embedding(user_id: int) -> list[float]:
    """Return raw user embedding for visualization."""
    load_model()
    user2idx = _meta["user2idx"]
    user_idx = user2idx.get(str(user_id), user2idx.get(user_id, 0))
    user_tensor = torch.tensor([user_idx], dtype=torch.long)
    with torch.no_grad():
        emb = _model.get_user_embedding(user_tensor)
    return emb.squeeze().tolist()


def get_all_item_embeddings() -> list[dict]:
    """Return all item embeddings for 2D visualization."""
    load_model()
    idx2artist = _meta["idx2artist"]
    num_items  = _meta["num_items"]
    genre_feat = torch.tensor(_meta["genre_features"], dtype=torch.float32)
    all_items  = torch.arange(num_items)

    with torch.no_grad():
        embs = _model.get_item_embedding(all_items, genre_feat)

    return [
        {
            "artist_id": idx2artist.get(str(i), i),
            "embedding": embs[i].tolist()
        }
        for i in range(num_items)
    ]