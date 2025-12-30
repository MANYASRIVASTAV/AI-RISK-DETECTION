from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime
import os

from features import build_features
from model import RiskModel
from risk_logic import assign_risk_levels, apply_persistence, generate_risk_reason

app = Flask(__name__)
CORS(app)  # allow all origins

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "transactions.csv")


@app.route("/", methods=["GET"])
def home():
    return "RiskGuard API running"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/transaction", methods=["POST"])
def process_transaction():
    try:
        data = request.get_json()

        new_txn = {
            "transaction_id": f"T{int(datetime.now().timestamp())}",
            "user_id": data["user_id"],
            "amount": data["amount"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "merchant_category": data["merchant"],
            "device_type": data["device"]
        }

        # load existing data
        df = pd.read_csv(DATA_PATH)
        df = pd.concat([df, pd.DataFrame([new_txn])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)

        # run pipeline
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        df, feature_cols = build_features(DATA_PATH)

        model = RiskModel()
        model.train(df, feature_cols)

        df["anomaly_score"] = model.score(df, feature_cols)
        df = assign_risk_levels(df)
        df = apply_persistence(df)
        df["risk_reason"] = df.apply(generate_risk_reason, axis=1)

        latest = df.iloc[-1]

        return jsonify({
            "risk_level": latest["risk_level"],
            "reason": latest["risk_reason"],
            "baseline": "GLOBAL"
        })

    except Exception as e:
        # 🔥 THIS WILL SAVE YOU IN DEBUGGING
        print("BACKEND ERROR:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
