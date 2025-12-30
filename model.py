import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class RiskModel:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42
        )
        self.is_trained = False

    def train(self, df, feature_cols):
        X = df[feature_cols].values
        X_scaled = self.scaler.fit_transform(X)

        self.model.fit(X_scaled)
        self.is_trained = True

    def score(self, df, feature_cols):
        if not self.is_trained:
            raise Exception("Model not trained yet")

        X = df[feature_cols].values
        X_scaled = self.scaler.transform(X)

        # Isolation Forest: -1 = anomaly, 1 = normal
        raw_scores = self.model.decision_function(X_scaled)

        # Normalize to 0–1 (higher = more risky)
        anomaly_scores = 1 - (
            (raw_scores - raw_scores.min()) /
            (raw_scores.max() - raw_scores.min())
        )

        return anomaly_scores
