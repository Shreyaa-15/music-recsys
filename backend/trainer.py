import os
import json
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

from model import TwoTowerModel
from data_loader import prepare_training_data

CHECKPOINT_DIR = "checkpoints"
GENRES = [
    "rock", "pop", "hip-hop", "electronic", "jazz",
    "classical", "metal", "indie", "r&b", "folk"
]
GENRE2IDX = {g: i for i, g in enumerate(GENRES)}


class InteractionDataset(Dataset):
    """
    Dataset for two-tower training with negative sampling.

    Each sample: (user_idx, pos_item_idx, neg_item_idx, genre_features)
    Negative items are sampled randomly from items the user
    hasn't interacted with — standard practice for implicit feedback.
    """
    def __init__(self, df: pd.DataFrame, artists_df: pd.DataFrame,
                 num_items: int, neg_samples: int = 4):
        self.df          = df.reset_index(drop=True)
        self.num_items   = num_items
        self.neg_samples = neg_samples

        # Build user → set of positive items (for negative sampling)
        self.user_positives = (
            df.groupby("user_idx")["artist_idx"]
            .apply(set).to_dict()
        )

        # Build genre feature matrix
        genre_map = artists_df.set_index("artist_id")["genre"].to_dict()
        self.genre_features = np.zeros((num_items, len(GENRES)), dtype=np.float32)
        for artist_id, genre in genre_map.items():
            if genre in GENRE2IDX and artist_id < num_items:
                self.genre_features[artist_id, GENRE2IDX[genre]] = 1.0

    def __len__(self):
        return len(self.df) * self.neg_samples

    def __getitem__(self, idx):
        row_idx  = idx % len(self.df)
        row      = self.df.iloc[row_idx]
        user_idx = int(row["user_idx"])
        pos_item = int(row["artist_idx"])
        weight   = float(row["confidence_norm"])

        # Sample a negative item
        pos_set = self.user_positives.get(user_idx, set())
        while True:
            neg_item = np.random.randint(0, self.num_items)
            if neg_item not in pos_set:
                break

        return {
            "user_idx":       torch.tensor(user_idx, dtype=torch.long),
            "pos_item":       torch.tensor(pos_item, dtype=torch.long),
            "neg_item":       torch.tensor(neg_item, dtype=torch.long),
            "pos_genre":      torch.tensor(self.genre_features[pos_item]),
            "neg_genre":      torch.tensor(self.genre_features[neg_item]),
            "weight":         torch.tensor(weight, dtype=torch.float32),
        }


def compute_recall_at_k(model, test_df, genre_features_tensor,
                         num_items, k=10, device="cpu", max_users=200):
    """
    Recall@K — what fraction of held-out items appear in top-K recommendations.
    Standard evaluation metric for recommendation systems.
    """
    model.eval()
    recalls = []

    # Pre-compute all item embeddings
    all_items  = torch.arange(num_items, device=device)
    all_genres = genre_features_tensor.to(device)

    with torch.no_grad():
        all_item_embs = model.get_item_embedding(all_items, all_genres)

    users = test_df["user_idx"].unique()[:max_users]

    for user_idx in users:
        user_tensor = torch.tensor([user_idx], device=device)

        with torch.no_grad():
            user_emb = model.get_user_embedding(user_tensor)
            scores   = (user_emb @ all_item_embs.T).squeeze()

        top_k = scores.topk(k).indices.cpu().numpy().tolist()

        positives = set(
            test_df[test_df["user_idx"] == user_idx]["artist_idx"].tolist()
        )
        if not positives:
            continue

        hit   = len(set(top_k) & positives)
        recall = hit / len(positives)
        recalls.append(recall)

    return float(np.mean(recalls)) if recalls else 0.0


def train(epochs=15, batch_size=512, lr=1e-3, output_dim=64):
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Training on {device}")

    # Load data
    train_df, test_df, user2idx, artist2idx, idx2user, idx2artist, artists_df = \
        prepare_training_data()

    num_users = len(user2idx)
    num_items = len(artist2idx)

    # Build dataset
    dataset = InteractionDataset(train_df, artists_df, num_items)
    loader  = DataLoader(dataset, batch_size=batch_size,
                         shuffle=True, num_workers=0)

    # Genre features tensor for evaluation
    genre_features = torch.tensor(dataset.genre_features)

    # Model + optimizer
    model     = TwoTowerModel(num_users, num_items, output_dim=output_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    best_recall = 0.0
    history     = []

    print(f"\nModel: {sum(p.numel() for p in model.parameters()):,} parameters")
    print(f"Training {epochs} epochs...\n")

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        batches    = 0

        for batch in tqdm(loader, desc=f"Epoch {epoch}/{epochs}"):
            user_idx  = batch["user_idx"].to(device)
            pos_item  = batch["pos_item"].to(device)
            neg_item  = batch["neg_item"].to(device)
            pos_genre = batch["pos_genre"].to(device)
            neg_genre = batch["neg_genre"].to(device)
            weight    = batch["weight"].to(device)

            # Positive scores
            pos_scores = model(user_idx, pos_item, pos_genre)
            # Negative scores
            neg_scores = model(user_idx, neg_item, neg_genre)

            # BPR loss (Bayesian Personalized Ranking)
            # Pushes positive scores above negative scores
            loss = -torch.log(torch.sigmoid(pos_scores - neg_scores) + 1e-8)
            loss = (loss * weight).mean()

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            batches    += 1

        scheduler.step()
        avg_loss = total_loss / batches

        # Evaluate every 3 epochs
        if epoch % 3 == 0 or epoch == epochs:
            recall = compute_recall_at_k(
                model, test_df, genre_features,
                num_items, k=10, device=device
            )
            print(f"  Epoch {epoch:2d} | Loss: {avg_loss:.4f} | Recall@10: {recall:.4f}")
            history.append({"epoch": epoch, "loss": avg_loss, "recall_at_10": recall})

            if recall > best_recall:
                best_recall = recall
                torch.save({
                    "model_state":  model.state_dict(),
                    "user2idx":     user2idx,
                    "artist2idx":   artist2idx,
                    "idx2user":     idx2user,
                    "idx2artist":   idx2artist,
                    "num_users":    num_users,
                    "num_items":    num_items,
                    "output_dim":   output_dim,
                    "genre_features": dataset.genre_features.tolist(),
                }, os.path.join(CHECKPOINT_DIR, "best_model.pt"))
                print(f"  Saved best model (Recall@10: {best_recall:.4f})")
        else:
            print(f"  Epoch {epoch:2d} | Loss: {avg_loss:.4f}")

    # Save training history
    with open(os.path.join(CHECKPOINT_DIR, "history.json"), "w") as f:
        json.dump(history, f, indent=2)

    print(f"\nTraining done. Best Recall@10: {best_recall:.4f}")
    return model, history


if __name__ == "__main__":
    train()