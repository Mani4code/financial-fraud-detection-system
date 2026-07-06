import os
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]
except ImportError:
    def load_dotenv():
        return False

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

import mysql.connector
import pandas as pd
import joblib
import time

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

MODEL_PATH = PROJECT_ROOT / "model" / "fraud_detection_model.pkl"
model = joblib.load(MODEL_PATH)
ALERT_THRESHOLD = 0.60


def build_features(tx, customer, history_txns):

    df = pd.DataFrame(history_txns)
    tx_amount = float(tx["amount"])

    if len(df) == 0:

        return pd.DataFrame([{
            "amount": tx_amount,
            "device_changed": 0,
            "city_changed": 0,
            "payment_method_changed": 0,
            "previous_transaction_amount": tx_amount,
            "customer_avg_amount": tx_amount,
            "customer_max_amount": tx_amount,
            "amount_deviation": 0.0,
            "amount_growth_ratio": 1.0,
            "amount_vs_max": 1.0,
            "transaction_count_last_24h": 1
        }])

    avg_amt = float(df["amount"].mean())
    max_amt = float(df["amount"].max())

    return pd.DataFrame([{

        "amount": tx_amount,

        "device_changed": int(tx["device"] != customer["usual_device"]),

        "city_changed": int(tx["city"] != customer["home_city"]),

        "payment_method_changed": int(
            tx["payment_method"] != customer["usual_payment_method"]
        ),

        "previous_transaction_amount": float(df.iloc[0]["amount"]),

        "customer_avg_amount": avg_amt,

        "customer_max_amount": max_amt,

        "amount_deviation": tx_amount - avg_amt,

        "amount_growth_ratio": tx_amount / (avg_amt + 1e-6),

        "amount_vs_max": tx_amount / (max_amt + 1e-6),

        "transaction_count_last_24h": len(df)

    }])


def run_detector():

    print("🚀 Detector Started")

    while True:

        conn = None

        try:

            conn = mysql.connector.connect(**DB_CONFIG)

            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
            SELECT *
            FROM live_transactions
            WHERE fraud_label = 0
            ORDER BY transaction_id
            LIMIT 1
            """)

            tx = cursor.fetchone()

            if tx is None:

                cursor.close()
                conn.close()
                time.sleep(0.5)
                continue

            cursor.execute(
                "SELECT * FROM customers WHERE customer_id=%s",
                (tx["customer_id"],)
            )

            customer = cursor.fetchone()

            cursor.execute("""
            SELECT *
            FROM transactions
            WHERE customer_id=%s
            ORDER BY transaction_time DESC
            LIMIT 30
            """,
            (tx["customer_id"],)
            )

            history = cursor.fetchall()

            X = build_features(tx, customer, history)
            print("\n==============================")
            print("Transaction ID:", tx["transaction_id"])
            print(X)
            print("==============================")

            prob = float(model.predict_proba(X)[0][1])
            print("Probability:", prob)

            label = 1 if prob >= ALERT_THRESHOLD else 2
            print("Label:", label)
             

            cursor.execute("""
            UPDATE live_transactions

                                         
            SET
                fraud_label=%s,
                probability=%s,
                expected_avg=%s,
                growth_ratio=%s,
                amount_vs_max=%s
            WHERE transaction_id=%s
            """,
            (
                label,
                prob,
                float(X["customer_avg_amount"].iloc[0]),
                float(X["amount_growth_ratio"].iloc[0]),
                float(X["amount_vs_max"].iloc[0]),
                tx["transaction_id"]
            ))

            if label == 1:
                print(f"🚨 FRAUD DETECTED | ID {tx['transaction_id']} | Score {prob:.3f}")
            else:
                print(f"✅ NORMAL | ID {tx['transaction_id']} | Score {prob:.3f}")

            conn.commit()

            cursor.close()
            conn.close()

            time.sleep(0.5)

        except Exception as e:

            print(e)

            if conn:
                conn.close()

            time.sleep(2)


if __name__ == "__main__":
    run_detector()