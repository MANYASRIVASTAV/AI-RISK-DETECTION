import pandas as pd

# Threshold: how many txns before personal baseline activates
MIN_USER_TXNS = 30


def compute_global_baseline(df):
    """
    Used for cold-start users
    """
    return {
        "avg_amount": df["amount"].mean(),
        "common_hours": df["hour_of_day"].mode().tolist()
    }


def compute_user_baseline(df, user_id):
    """
    Personal baseline after enough history
    """
    user_df = df[df["user_id"] == user_id]

    return {
        "avg_amount": user_df["amount"].mean(),
        "common_hours": user_df["hour_of_day"].mode().tolist(),
        "txn_count": len(user_df)
    }


def get_effective_baseline(df, user_id):
    """
    Switch logic: global → personal
    """
    user_txns = df[df["user_id"] == user_id]

    if len(user_txns) < MIN_USER_TXNS:
        baseline = compute_global_baseline(df)
        baseline["type"] = "GLOBAL"
    else:
        baseline = compute_user_baseline(df, user_id)
        baseline["type"] = "USER"

    return baseline
