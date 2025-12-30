import os
from baseline import get_effective_baseline

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

CSV_PATH = os.path.join(PROJECT_ROOT, "data", "transactions.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "risk_output.csv")

# ---------------- IMPORTS ----------------
from features import build_features
from model import RiskModel
from risk_logic import (
    assign_risk_levels,
    apply_persistence,
    generate_risk_reason
)
from feedback import verify_transaction


def run_pipeline():
    # 1. Feature engineering
    df, feature_cols = build_features(CSV_PATH)

    # 2. Baseline assignment (cold start fix)
    df["baseline_type"] = df["user_id"].apply(
        lambda u: get_effective_baseline(df, u)["type"]
    )

    # 3. Train ML model
    model = RiskModel()
    model.train(df, feature_cols)

    # 4. Anomaly scoring
    df["anomaly_score"] = model.score(df, feature_cols)

    # 5. Risk logic
    df = assign_risk_levels(df)
    df = apply_persistence(df)

    # 6. Explainability
    df["risk_reason"] = df.apply(generate_risk_reason, axis=1)

    # 7. User verification
    df["user_confirmed"] = df.apply(verify_transaction, axis=1)

    return df


if __name__ == "__main__":
    print("=== PIPELINE STARTED ===")
    print(f"Reading data from: {CSV_PATH}")

    result = run_pipeline()

    print("\n=== DEBUG OUTPUT ===")
    print(result[["transaction_id", "amount", "anomaly_score", "risk_level"]])

    print("\n=== BASELINE TYPES ===")
    print(result[["transaction_id", "user_id", "baseline_type"]])

    result.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved output to: {OUTPUT_PATH}")
