import os
import json
import torch
import numpy as np
import faiss

from model import TwoTowerModel

CHECKPOINT_DIR = "checkpoints"
INDEX_PATH     = "models/faiss.index"
META_PATH      = "models/meta.json"


def load_checkpoint():
    path = os.path.join(CHECKPOINT_DIR, "best_model.pt")
    ckpt = torch.load(path, map_location="cpu")
    return ckpt


def build_faiss_index():
    """
    Pre-compute all item embeddings and store in FAISS.
    This runs OFFLINE — once after training.
    At serving time, only the user tower runs online.
    """
    os.makedirs("models", exist_ok=True)
    print("Loading checkpoint...")
    ckpt = load_checkpoint()

    num_users      = ckpt["num_users"]
    num_items      = ckpt["num_items"]
    output_dim     = ckpt["output_dim"]
    genre_features = np.array(ckpt["genre_features"], dtype=np.float32)

    model = TwoTowerModel(num_users, num_items, output_dim=output_dim)
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    print(f"Computing embeddings for {num_items} items...")
    all_items  = torch.arange(num_items)
    all_genres = torch.tensor(genre_features)

    with torch.no_grad():
        item_embs = model.get_item_embedding(all_items, all_genres)
        item_embs = item_embs.numpy().astype("float32")

    # Build FAISS index — IndexFlatIP = exact inner product
    # (cosine similarity since embeddings are L2 normalized)
    dim   = item_embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(item_embs)

    faiss.write_index(index, INDEX_PATH)
    print(f"FAISS index built: {index.ntotal} vectors, dim={dim}")

    # Save metadata
    meta = {
        "num_users":    num_users,
        "num_items":    num_items,
        "output_dim":   output_dim,
        "user2idx":     {str(k): int(v) for k, v in ckpt["user2idx"].items()},
        "artist2idx":   {str(k): int(v) for k, v in ckpt["artist2idx"].items()},
        "idx2user":     {str(k): int(v) for k, v in ckpt["idx2user"].items()},
        "idx2artist":   {str(k): int(v) for k, v in ckpt["idx2artist"].items()},
        "genre_features": genre_features.tolist(),
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f)

    print(f"Metadata saved to {META_PATH}")
    return index, meta


def load_index():
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH) as f:
        meta = json.load(f)
    return index, meta


if __name__ == "__main__":
    build_faiss_index()