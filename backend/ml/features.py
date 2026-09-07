from typing import Dict, Any, List
import numpy as np

def extract_features(wallet_profile: Dict[str, Any]) -> Dict[str, float]:
    """
    Extracts statistical, structural, and temporal features from a WalletProfile
    (Contract 2) for downstream ML scoring.
    """
    transactions = wallet_profile.get("transactions", [])
    total_received = float(wallet_profile.get("total_received", 0.0))
    total_sent = float(wallet_profile.get("total_sent", 0.0))
    in_degree = int(wallet_profile.get("in_degree", 0))
    out_degree = int(wallet_profile.get("out_degree", 0))
    hop_distance = int(wallet_profile.get("hop_distance_from_suspect", 0))
    first_seen = wallet_profile.get("first_seen", 0)
    last_seen = wallet_profile.get("last_seen", 0)

    tx_count = len(transactions)
    values = [float(tx.get("value", 0.0)) for tx in transactions] if tx_count > 0 else [0.0]
    
    # Temporal calculations
    timestamps = sorted([tx.get("timestamp", 0) for tx in transactions if tx.get("timestamp")])
    time_deltas = [
        t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:])
    ] if len(timestamps) > 1 else [0.0]

    wallet_age_days = max((last_seen - first_seen) / 86400.0, 1.0 / 24.0)

    # Feature dictionary
    features = {
        "tx_count": float(tx_count),
        "total_received": total_received,
        "total_sent": total_sent,
        "balance_ratio": total_sent / max(total_received, 1e-4),
        "avg_tx_value": float(np.mean(values)),
        "max_tx_value": float(np.max(values)),
        "min_tx_value": float(np.min(values)),
        "std_tx_value": float(np.std(values)) if tx_count > 1 else 0.0,
        "tx_frequency": float(tx_count) / wallet_age_days,
        "avg_time_between_tx": float(np.mean(time_deltas)),
        "min_time_between_tx": float(np.min(time_deltas)),
        "in_degree": float(in_degree),
        "out_degree": float(out_degree),
        "degree_ratio": float(out_degree) / max(in_degree, 1),
        "hop_distance": float(hop_distance)
    }
    return features

def profile_to_feature_vector(wallet_profile: Dict[str, Any]) -> List[float]:
    """
    Returns ordered vector matching expected input layout for baseline models.
    """
    feature_dict = extract_features(wallet_profile)
    return list(feature_dict.values())