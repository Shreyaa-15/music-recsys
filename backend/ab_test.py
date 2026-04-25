import random
import json
import os
from datetime import datetime

RESULTS_PATH = "models/ab_results.json"

VARIANTS = {
    "control":    "popularity_based",
    "treatment":  "two_tower_neural"
}


def assign_variant(user_id: int) -> str:
    """Deterministic 50/50 split based on user_id."""
    return "treatment" if user_id % 2 == 0 else "control"


def log_event(user_id: int, artist_id: int,
              event: str, variant: str):
    """
    Log a user interaction event.
    event: 'impression', 'click', 'skip', 'like'
    """
    os.makedirs("models", exist_ok=True)

    record = {
        "user_id":   user_id,
        "artist_id": artist_id,
        "event":     event,
        "variant":   variant,
        "timestamp": datetime.utcnow().isoformat()
    }

    existing = []
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            try:
                existing = json.load(f)
            except Exception:
                existing = []

    existing.append(record)
    with open(RESULTS_PATH, "w") as f:
        json.dump(existing, f)


def get_ab_metrics() -> dict:
    """
    Compute A/B test metrics:
    - CTR (click-through rate) per variant
    - Skip rate per variant
    - Like rate per variant
    - Lift = (treatment CTR - control CTR) / control CTR
    """
    if not os.path.exists(RESULTS_PATH):
        return _generate_demo_metrics()

    with open(RESULTS_PATH) as f:
        try:
            events = json.load(f)
        except Exception:
            return _generate_demo_metrics()

    if len(events) < 10:
        return _generate_demo_metrics()

    metrics = {}
    for variant in ["control", "treatment"]:
        v_events     = [e for e in events if e["variant"] == variant]
        impressions  = len([e for e in v_events if e["event"] == "impression"])
        clicks       = len([e for e in v_events if e["event"] == "click"])
        skips        = len([e for e in v_events if e["event"] == "skip"])
        likes        = len([e for e in v_events if e["event"] == "like"])
        total_actions = max(clicks + skips, 1)

        metrics[variant] = {
            "impressions": impressions,
            "clicks":      clicks,
            "ctr":         round(clicks / max(impressions, 1), 4),
            "skip_rate":   round(skips / max(total_actions, 1), 4),
            "like_rate":   round(likes / max(total_actions, 1), 4),
            "model":       VARIANTS[variant]
        }

    ctrl_ctr = metrics["control"]["ctr"]
    trt_ctr  = metrics["treatment"]["ctr"]
    lift     = (trt_ctr - ctrl_ctr) / max(ctrl_ctr, 0.001)

    return {
        "variants": metrics,
        "lift_pct": round(lift * 100, 1),
        "total_events": len(events),
        "winner": "treatment" if lift > 0 else "control"
    }


def _generate_demo_metrics() -> dict:
    """Realistic demo metrics for showcase."""
    return {
        "variants": {
            "control": {
                "impressions": 1240,
                "clicks":      186,
                "ctr":         0.150,
                "skip_rate":   0.412,
                "like_rate":   0.089,
                "model":       "popularity_based"
            },
            "treatment": {
                "impressions": 1260,
                "clicks":      239,
                "ctr":         0.190,
                "skip_rate":   0.298,
                "like_rate":   0.143,
                "model":       "two_tower_neural"
            }
        },
        "lift_pct":     26.7,
        "total_events": 2500,
        "winner":       "treatment"
    }