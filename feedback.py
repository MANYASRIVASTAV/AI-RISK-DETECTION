import pandas as pd
import os
from datetime import datetime, timedelta

FEEDBACK_FILE = "feedback.csv"
COOLDOWN_HOURS = 24


def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        return pd.read_csv(FEEDBACK_FILE)
    return pd.DataFrame(
        columns=["transaction_id", "user_id", "user_confirmed", "verified_at"]
    )


def save_feedback(df):
    df.to_csv(FEEDBACK_FILE, index=False)


def is_in_cooldown(user_id, feedback_df):
    if feedback_df.empty:
        return False

    user_logs = feedback_df[feedback_df["user_id"] == user_id]
    if user_logs.empty:
        return False

    last_time = pd.to_datetime(user_logs["verified_at"].max())
    return datetime.now() - last_time < timedelta(hours=COOLDOWN_HOURS)


def verify_transaction(row):
    # Only HIGH risk needs verification
    if row["risk_level"] != "HIGH":
        return "SKIP"

    feedback_df = load_feedback()

    # Cooldown check
    if is_in_cooldown(row["user_id"], feedback_df):
        return "COOLDOWN_SKIP"

    # Already verified transaction
    existing = feedback_df[
        feedback_df["transaction_id"] == row["transaction_id"]
    ]
    if not existing.empty:
        return existing.iloc[0]["user_confirmed"]

    # Ask user
    print("\n--- VERIFY TRANSACTION ---")
    print(f"Transaction ID: {row['transaction_id']}")
    print(f"Amount: {row['amount']}")
    print(f"Reason: {row['risk_reason']}")

    resp = input("Is this transaction yours? (y/n): ").strip().lower()
    result = "YES" if resp == "y" else "NO"

    # Save feedback
    feedback_df = pd.concat(
        [
            feedback_df,
            pd.DataFrame(
                [{
                    "transaction_id": row["transaction_id"],
                    "user_id": row["user_id"],
                    "user_confirmed": result,
                    "verified_at": datetime.now()
                }]
            )
        ],
        ignore_index=True
    )

    save_feedback(feedback_df)
    return result
