import os
import numpy as np
import pandas as pd
from tqdm import tqdm

DATA_DIR = "data"

GENRES = [
    "rock", "pop", "hip-hop", "electronic", "jazz",
    "classical", "metal", "indie", "r&b", "folk"
]

ARTISTS = [
    ("Radiohead", "rock"), ("Coldplay", "pop"), ("Kendrick Lamar", "hip-hop"),
    ("Daft Punk", "electronic"), ("Miles Davis", "jazz"),
    ("Bach", "classical"), ("Metallica", "metal"), ("Arctic Monkeys", "indie"),
    ("Frank Ocean", "r&b"), ("Fleet Foxes", "folk"),
    ("Portishead", "electronic"), ("The Beatles", "rock"), ("Drake", "hip-hop"),
    ("Aphex Twin", "electronic"), ("Coltrane", "jazz"),
    ("Pink Floyd", "rock"), ("Taylor Swift", "pop"), ("Kanye West", "hip-hop"),
    ("Brian Eno", "electronic"), ("Nick Drake", "folk"),
    ("Thom Yorke", "indie"), ("Billie Eilish", "pop"), ("Tyler the Creator", "hip-hop"),
    ("Four Tet", "electronic"), ("Bill Evans", "jazz"),
    ("Black Sabbath", "metal"), ("Bon Iver", "indie"), ("SZA", "r&b"),
    ("Sufjan Stevens", "folk"), ("LCD Soundsystem", "electronic"),
    ("The Strokes", "rock"), ("Lorde", "pop"), ("J. Cole", "hip-hop"),
    ("Burial", "electronic"), ("Thelonious Monk", "jazz"),
    ("Tool", "metal"), ("Vampire Weekend", "indie"), ("Solange", "r&b"),
    ("Iron & Wine", "folk"), ("Massive Attack", "electronic"),
    ("Joy Division", "rock"), ("Lana Del Rey", "pop"), ("Pusha T", "hip-hop"),
    ("Boards of Canada", "electronic"), ("Charles Mingus", "jazz"),
    ("Opeth", "metal"), ("Tame Impala", "indie"), ("Erykah Badu", "r&b"),
    ("Elliot Smith", "folk"), ("The Chemical Brothers", "electronic"),
]

NUM_USERS   = 1000
NUM_ARTISTS = len(ARTISTS)
SEED        = 42


def generate_data():
    """
    Generate synthetic LastFM-style implicit feedback data.

    User behaviour model:
    - Each user has 2-3 preferred genres (simulates real taste)
    - Users play artists from preferred genres 10x more
    - Play counts follow a power law (a few artists get most plays)
    - Adds noise so it's not perfectly clean
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    np.random.seed(SEED)

    print("Generating synthetic LastFM-style dataset...")

    # Build artist dataframe
    artists_df = pd.DataFrame([
        {"artist_id": i, "artist_name": name, "genre": genre}
        for i, (name, genre) in enumerate(ARTISTS)
    ])

    # Each user has 2-3 preferred genres
    user_genres = {}
    for u in range(NUM_USERS):
        n_pref = np.random.choice([2, 3], p=[0.6, 0.4])
        user_genres[u] = np.random.choice(GENRES, size=n_pref, replace=False).tolist()

    # Generate interactions
    records = []
    for user_id in tqdm(range(NUM_USERS), desc="Generating users"):
        preferred = user_genres[user_id]

        for artist_id, (name, genre) in enumerate(ARTISTS):
            # Base probability
            if genre in preferred:
                base_prob = 0.7   # high chance of listening
            else:
                base_prob = 0.07  # low but nonzero (discovery)

            if np.random.random() > base_prob:
                continue

            # Play count: power law (most artists get few plays, some get many)
            if genre in preferred:
                play_count = int(np.random.pareto(1.5) * 50) + 1
            else:
                play_count = int(np.random.pareto(2.5) * 10) + 1

            play_count = min(play_count, 5000)  # cap outliers

            records.append({
                "user_id":   user_id,
                "artist_id": artist_id,
                "play_count": play_count
            })

    ua_df = pd.DataFrame(records)
    print(f"Generated {len(ua_df)} interactions")
    print(f"Users: {ua_df['user_id'].nunique()}, Artists: {ua_df['artist_id'].nunique()}")

    # Save
    ua_df.to_csv(os.path.join(DATA_DIR, "user_artists.csv"), index=False)
    artists_df.to_csv(os.path.join(DATA_DIR, "artists.csv"), index=False)
    print(f"Saved to {DATA_DIR}/")

    return ua_df, artists_df


def compute_implicit_feedback(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw play counts to implicit confidence scores.
    Formula from Hu et al. (2008) — used by Spotify internally.
    confidence = 1 + alpha * log(1 + play_count)
    """
    df = df.copy()
    alpha = 40.0
    df["confidence"] = 1 + alpha * np.log1p(df["play_count"])
    df["preference"] = 1

    user_max = df.groupby("user_id")["confidence"].transform("max")
    df["confidence_norm"] = df["confidence"] / user_max
    return df


def build_id_maps(df: pd.DataFrame):
    users   = sorted(df["user_id"].unique())
    artists = sorted(df["artist_id"].unique())

    user2idx   = {u: i for i, u in enumerate(users)}
    artist2idx = {a: i for i, a in enumerate(artists)}
    idx2user   = {i: u for u, i in user2idx.items()}
    idx2artist = {i: a for a, i in artist2idx.items()}

    return user2idx, artist2idx, idx2user, idx2artist


def prepare_training_data():
    """Full pipeline: generate → process → split."""
    ua_path = os.path.join(DATA_DIR, "user_artists.csv")
    ar_path = os.path.join(DATA_DIR, "artists.csv")

    if os.path.exists(ua_path):
        print("Loading existing data...")
        ua_df      = pd.read_csv(ua_path)
        artists_df = pd.read_csv(ar_path)
    else:
        ua_df, artists_df = generate_data()

    ua_df = compute_implicit_feedback(ua_df)

    user2idx, artist2idx, idx2user, idx2artist = build_id_maps(ua_df)

    ua_df["user_idx"]   = ua_df["user_id"].map(user2idx)
    ua_df["artist_idx"] = ua_df["artist_id"].map(artist2idx)

    # Train/test split — hold out 20% per user
    ua_df = ua_df.sort_values(["user_id", "play_count"])

    def split_user(group):
        n     = len(group)
        split = max(1, int(n * 0.8))
        group = group.copy()
        group["split"] = "train"
        group.iloc[split:, group.columns.get_loc("split")] = "test"
        return group

    ua_df = ua_df.groupby("user_id", group_keys=False).apply(split_user)

    train_df = ua_df[ua_df["split"] == "train"].copy()
    test_df  = ua_df[ua_df["split"] == "test"].copy()

    print(f"\nReady to train:")
    print(f"  Users:   {len(user2idx)}")
    print(f"  Artists: {len(artist2idx)}")
    print(f"  Train:   {len(train_df)}")
    print(f"  Test:    {len(test_df)}")

    return train_df, test_df, user2idx, artist2idx, idx2user, idx2artist, artists_df


if __name__ == "__main__":
    prepare_training_data()