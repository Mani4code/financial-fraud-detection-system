from pathlib import Path
import mysql.connector
import pandas as pd
import numpy as np



PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "model" / "featured_transactions.csv"

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mani@sql5825u",
    database="fraud_detection_final"
)


transactions = pd.read_sql("""
SELECT *
FROM transactions
""", conn)

customers = pd.read_sql("""
SELECT *
FROM customers
""", conn)

conn.close()


df = transactions.merge(
    customers,
    on="customer_id",
    how="left"
)



df["transaction_time"] = pd.to_datetime(df["transaction_time"])

df = df.sort_values(
    ["customer_id", "transaction_time"]
).reset_index(drop=True)


df["device_changed"] = (
    df["device"] != df["usual_device"]
).astype(int)

df["city_changed"] = (
    df["city"] != df["home_city"]
).astype(int)

df["payment_method_changed"] = (
    df["payment_method"] != df["usual_payment_method"]
).astype(int)



df["hour"] = df["transaction_time"].dt.hour

df["day_of_week"] = df["transaction_time"].dt.dayofweek

df["weekend_flag"] = (
    df["day_of_week"] >= 5
).astype(int)

df["night_flag"] = (
    df["hour"].between(0, 5)
).astype(int)


g = df.groupby("customer_id")

df["transaction_number"] = g.cumcount() + 1

df["previous_transaction_amount"] = g["amount"].shift(1)

df["customer_avg_amount"] = (
    g["amount"]
    .expanding()
    .mean()
    .shift(1)
    .reset_index(level=0, drop=True)
)

df["customer_max_amount"] = (
    g["amount"]
    .cummax()
    .shift(1)
)



df["amount_deviation"] = (
    df["amount"] -
    df["customer_avg_amount"]
)

df["amount_growth_ratio"] = (
    df["amount"] /
    df["customer_avg_amount"]
)

df["amount_vs_max"] = (
    df["amount"] /
    df["customer_max_amount"]
)



df["transaction_count_last_24h"] = 0

for customer_id, group in df.groupby("customer_id"):

    idx = group.index

    times = group["transaction_time"]

    counts = []

    for t in times:

        counts.append(
            (
                (times < t) &
                (times >= t - pd.Timedelta(hours=24))
            ).sum()
        )

    df.loc[idx, "transaction_count_last_24h"] = counts



df["previous_transaction_amount"] = df["previous_transaction_amount"].fillna(df["amount"])

df["customer_avg_amount"] = df["customer_avg_amount"].fillna(df["amount"])

df["customer_max_amount"] = df["customer_max_amount"].fillna(df["amount"])

df["amount_deviation"] = df["amount_deviation"].fillna(0)

df["amount_growth_ratio"] = df["amount_growth_ratio"].fillna(1)

df["amount_vs_max"] = df["amount_vs_max"].fillna(1)



df = df.drop(columns=[
    "transaction_id",
    "customer_name",
    "account_number",
    "phone_number",
    "home_city",
    "usual_device",
    "usual_payment_method",
    "transaction_time",
    "payment_method",
    "city",
    "device"
])



df.to_csv(
    OUTPUT_PATH,
    index=False
)

print(df.head())

print("\nShape:", df.shape)

print("\nFeature engineering completed successfully.")