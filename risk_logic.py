import pandas as pd

LOW_THRESHOLD = 0.4
HIGH_THRESHOLD = 0.7


def assign_risk_levels(df, score_col='anomaly_score'):
    def map_risk(score):
        if score < LOW_THRESHOLD:
            return 'LOW'
        elif score < HIGH_THRESHOLD:
            return 'MEDIUM'
        else:
            return 'HIGH'

    df['risk_level_raw'] = df[score_col].apply(map_risk)
    return df


def apply_persistence(df):
    """
    HIGH risk only if 2 of last 3 transactions are HIGH for a user
    """
    df = df.sort_values(by=['user_id', 'timestamp'])

    final_risks = []

    for user_id, group in df.groupby('user_id'):
        recent = []

        for _, row in group.iterrows():
            recent.append(row['risk_level_raw'])
            if len(recent) > 3:
                recent.pop(0)

            if recent.count('HIGH') >= 2:
                final_risks.append('HIGH')
            else:
                final_risks.append(row['risk_level_raw'])

    df['risk_level'] = final_risks
    return df


def generate_risk_reason(row):
    reasons = []

    # Amount deviation (quantified)
    if row.get("amount_deviation", 1) > 1.5:
        multiplier = round(row["amount_deviation"], 2)
        baseline = row.get("baseline_type", "GLOBAL")
        avg_amt = round(row["amount"] / row["amount_deviation"], 2)

        reasons.append(
            f"Amount is {multiplier}× higher than your {baseline} baseline (₹{avg_amt} avg)"
        )

    # Unusual hour (quantified)
    if row.get("hour_of_day", 0) < 5:
        reasons.append(
            f"Transaction occurred at {row['hour_of_day']}:00, outside usual hours"
        )

    # Frequency spike (quantified)
    if row.get("txn_count_last_24h", 0) > 5:
        reasons.append(
            f"{int(row['txn_count_last_24h'])} transactions in last 24 hours (unusual frequency)"
        )
    # Velocity spike
    if row.get("amount_velocity", 0) > 1.0:
        reasons.append(
            f"Spending increased rapidly ({row['amount_velocity']}× over recent average)"
        )

    if not reasons:
        return "Normal behavior"

    return "; ".join(reasons[:2])  # limit to top 2 reasons
