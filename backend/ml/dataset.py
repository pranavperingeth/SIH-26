import os
import pandas as pd
from typing import Tuple
from sklearn.model_selection import train_test_split

# Elliptic labels: "1" = illicit, "2" = licit, "unknown" = unlabelled
LABEL_MAPPING = {
    "1": 1,  # Illicit / Fraud
    "2": 0   # Licit / Normal
}

def load_elliptic_dataset(data_dir: str) -> pd.DataFrame:
    """
    Loads and merges elliptic_txs_features.csv and elliptic_txs_classes.csv.
    """
    features_path = os.path.join(data_dir, "elliptic_txs_features.csv")
    classes_path = os.path.join(data_dir, "elliptic_txs_classes.csv")

    if not os.path.exists(features_path) or not os.path.exists(classes_path):
        raise FileNotFoundError(f"Missing Elliptic files in {data_dir}")

    # Column 0: txId, Column 1: time_step, Column 2..167: 165 local and aggregate features
    feature_cols = ["txId", "time_step"] + [f"feat_{i}" for i in range(1, 166)]
    df_features = pd.read_csv(features_path, header=None, names=feature_cols)
    df_classes = pd.read_csv(classes_path)

    # Merge on txId
    df = pd.merge(df_features, df_classes, on="txId")
    return df

def preprocess_elliptic(
    df: pd.DataFrame, 
    drop_unknown: bool = True
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Cleans classes, maps binary labels (illicit=1, licit=0), and separates X and y.
    """
    if drop_unknown:
        df = df[df["class"] != "unknown"].copy()

    df["target"] = df["class"].map(LABEL_MAPPING)
    
    # Feature matrix: drop identifiers and target columns
    X = df.drop(columns=["txId", "time_step", "class", "target"])
    y = df["target"].astype(int)

    return X, y

def get_train_test_splits(
    data_dir: str, 
    test_size: float = 0.2, 
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Stratified split into training and testing sets.
    """
    df = load_elliptic_dataset(data_dir)
    X, y = preprocess_elliptic(df, drop_unknown=True)
    
    return train_test_split(
        X, y, 
        test_size=test_size, 
        random_state=random_state, 
        stratify=y
    )