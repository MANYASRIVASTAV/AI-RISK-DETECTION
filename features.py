import pandas as pd


def load_data(path):
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def add_time_features(df):
    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    return df


def add_user_behavior_features(df):
    df = df.sort_values(["user_id", "timestamp"])

    txn_counts = []

    for user_id, group in df.groupby("user_id"):
        times = group["timestamp"].values

        for i in range(len(times)):
            # count transactions in last 24 hours
            count = 0
            for j in range(i, -1, -1):
                if (times[i] - times[j]).astype("timedelta64[h]") <= 24:
                    count += 1
                else:
                    break
            txn_counts.append(count)

    df["txn_count_last_24h"] = txn_counts
    return df


def add_amount_deviation(df):
    # ✅ PAST-ONLY average (no future leakage)
    df["user_avg_amount"] = (
        df.groupby("user_id")["amount"]
        .transform(lambda x: x.expanding().mean().shift())
    )

    df["amount_deviation"] = df["amount"] / df["user_avg_amount"]

    # clean NaNs (first txn per user)
    df.fillna(0, inplace=True)

    return df


def build_features(csv_path):
    df = load_data(csv_path)

    df = add_time_features(df)
    df = add_user_behavior_features(df)
    df = add_amount_deviation(df)
    df = add_amount_velocity(df)

    feature_cols = [
        "amount",
        "hour_of_day",
        "day_of_week",
        "amount_deviation",
        "txn_count_last_24h",
        'amount_velocity'
    ]

    return df, feature_cols


def add_amount_velocity(df, window=3):
    """
    Computes spending velocity per user as rate of change
    over recent transactions.
    """
    df = df.sort_values(["user_id", "timestamp"])

    velocities = []

    for user_id, group in df.groupby("user_id"):
        amounts = group["amount"].values

        for i in range(len(amounts)):
            if i < window:
                velocities.append(0.0)
            else:
                prev_avg = amounts[i-window:i].mean()
                curr = amounts[i]
                velocity = (curr - prev_avg) / max(prev_avg, 1)
                velocities.append(round(velocity, 2))

    df["amount_velocity"] = velocities
    return df
