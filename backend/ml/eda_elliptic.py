import sys
import numpy as np
import pandas as pd
try:
    from backend.ml.dataset import load_elliptic_dataset
except ModuleNotFoundError:
    from dataset import load_elliptic_dataset

def run_eda(data_dir: str):
    print("[-] Loading Elliptic dataset...")
    df = load_elliptic_dataset(data_dir)

    total_records = len(df)
    print(f"[+] Total transactions loaded: {total_records:,}")
    print(f"[+] Features per transaction: {df.shape[1] - 3}")

    # Class distribution
    class_counts = df["class"].value_counts()
    print("\n--- Raw Class Distribution ---")
    for cls, count in class_counts.items():
        print(f"Class {cls}: {count:,} ({count/total_records*100:.2f}%)")

    # Licit vs Illicit metrics
    labeled = df[df["class"].isin(["1", "2"])]
    illicit_count = (labeled["class"] == "1").sum()
    licit_count = (labeled["class"] == "2").sum()

    print("\n--- Labeled Subset (Excluding Unknowns) ---")
    print(f"Total Labeled: {len(labeled):,}")
    print(f"Illicit (1): {illicit_count:,} ({illicit_count/len(labeled)*100:.2f}%)")
    print(f"Licit (2):   {licit_count:,} ({licit_count/len(labeled)*100:.2f}%)")
    
    # Imbalance scale ratio for XGBoost (scale_pos_weight)
    scale_pos_weight = licit_count / illicit_count
    print(f"\n[+] Recommended scale_pos_weight for XGBoost: {scale_pos_weight:.2f}")

    # Check for missing values
    missing = df.isnull().sum().sum()
    print(f"[+] Total missing values: {missing}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python eda_elliptic.py /path/to/elliptic_dataset")
        sys.exit(1)
    run_eda(sys.argv[1])