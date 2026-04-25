import torch
import torch.nn as nn
import torch.nn.functional as F


class UserTower(nn.Module):
    """
    User tower of the two-tower network.

    Takes a user index → learns a dense embedding →
    passes through MLP → outputs normalized 64-dim vector.

    This is exactly how YouTube and Spotify build their
    candidate generation models.
    """
    def __init__(self, num_users: int, embedding_dim: int = 32, output_dim: int = 64):
        super().__init__()
        self.embedding = nn.Embedding(num_users, embedding_dim)
        self.mlp = nn.Sequential(
            nn.Linear(embedding_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )

    def forward(self, user_idx: torch.Tensor) -> torch.Tensor:
        x = self.embedding(user_idx)
        x = self.mlp(x)
        return F.normalize(x, dim=-1)  # L2 normalize for cosine similarity


class ItemTower(nn.Module):
    """
    Item tower of the two-tower network.

    Takes an artist index + optional genre one-hot →
    learns a dense embedding → outputs normalized 64-dim vector.

    Separate from user tower so item embeddings can be
    pre-computed and indexed offline (key for serving at scale).
    """
    def __init__(self, num_items: int, num_genres: int = 10,
                 embedding_dim: int = 32, output_dim: int = 64):
        super().__init__()
        self.embedding  = nn.Embedding(num_items, embedding_dim)
        self.genre_proj = nn.Linear(num_genres, 16)
        self.mlp = nn.Sequential(
            nn.Linear(embedding_dim + 16, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )

    def forward(self, item_idx: torch.Tensor,
                genre_features: torch.Tensor) -> torch.Tensor:
        x_emb   = self.embedding(item_idx)
        x_genre = F.relu(self.genre_proj(genre_features))
        x = torch.cat([x_emb, x_genre], dim=-1)
        x = self.mlp(x)
        return F.normalize(x, dim=-1)


class TwoTowerModel(nn.Module):
    """
    Full two-tower model.

    At training time: both towers run, dot product gives score.
    At serving time: item tower runs offline to build FAISS index,
                     user tower runs online for each request.

    Loss: Binary Cross Entropy with negative sampling.
    For each positive (user, item) pair, we sample K random
    negative items the user hasn't interacted with.
    """
    def __init__(self, num_users: int, num_items: int,
                 num_genres: int = 10, output_dim: int = 64):
        super().__init__()
        self.user_tower = UserTower(num_users, output_dim=output_dim)
        self.item_tower = ItemTower(num_items, num_genres, output_dim=output_dim)
        self.num_items  = num_items

    def forward(self, user_idx: torch.Tensor,
                item_idx: torch.Tensor,
                genre_features: torch.Tensor) -> torch.Tensor:
        user_emb = self.user_tower(user_idx)
        item_emb = self.item_tower(item_idx, genre_features)
        # Dot product score (cosine similarity since both are L2 normalized)
        return (user_emb * item_emb).sum(dim=-1)

    def get_user_embedding(self, user_idx: torch.Tensor) -> torch.Tensor:
        return self.user_tower(user_idx)

    def get_item_embedding(self, item_idx: torch.Tensor,
                           genre_features: torch.Tensor) -> torch.Tensor:
        return self.item_tower(item_idx, genre_features)