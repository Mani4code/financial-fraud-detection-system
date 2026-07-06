import os
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]
except ImportError:
    def load_dotenv():
        return False

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

import random
import json
import time
import mysql.connector
from datetime import datetime


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

FRAUD_RATE = 0.03      
SLEEP_TIME = 1          

random.seed()

import time

while True:
    try:
        conn = mysql.connector.connect(**DB_CONFIG, autocommit=True)
        cursor = conn.cursor(dictionary=True)
        print("✅ Connected to MySQL")
        break
    except mysql.connector.Error:
        print("⏳ Waiting for MySQL...")
        time.sleep(5)

print("Clearing previous live transactions...")

cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("TRUNCATE TABLE live_transactions")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

print("✓ live_transactions table cleared.\n")

cursor.execute("SELECT * FROM customers")
customers = cursor.fetchall()
print(f"Loaded {len(customers)} customers")

PROFILES_PATH = PROJECT_ROOT / "model" / "customer_profiles.json"
with open(PROFILES_PATH, "r") as f:
    customer_profiles = json.load(f)
print(f"Loaded {len(customer_profiles)} customer profiles")


cities = ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem", "Erode", "Tiruppur", "Bangalore", "Hyderabad", "Mumbai", "Pune", "Kochi"]
devices = ["Samsung S24", "Samsung A55", "Samsung M35", "Redmi Note 13", "Redmi Note 14", "OnePlus 13", "Vivo V50", "iPhone 15", "iPhone 16"]
payment_methods = ["UPI", "Debit Card", "Credit Card", "Net Banking"]


def generate_amount(profile):
    avg = profile["average_amount"]
    variation = profile["variation"]
    amount = random.uniform(avg * (1 - variation), avg * (1 + variation))
    if random.random() < 0.015:
        amount *= random.uniform(1.5, 2.5)
    return round(max(10, amount), 2)

def choose_city(customer, profile):
    if random.random() < profile["travel_probability"]:
        return random.choice(cities)
    return customer["home_city"]

def choose_device(customer, profile):
    if random.random() < profile["device_change_probability"]:
        return random.choice(devices)
    return customer["usual_device"]

def choose_payment(customer, profile):
    if random.random() < profile["payment_change_probability"]:
        return random.choice(payment_methods)
    return customer["usual_payment_method"]

def generate_time(profile):
    return datetime.now().replace(microsecond=0)

def generate_normal_transaction(customer):
    profile = customer_profiles[str(customer["customer_id"])]
    return {
        "customer_id": customer["customer_id"],
        "transaction_time": generate_time(profile),
        "amount": generate_amount(profile),
        "payment_method": choose_payment(customer, profile),
        "city": choose_city(customer, profile),
        "device": choose_device(customer, profile),
        "fraud_label": 0
    }



def inject_fraud(tx, customer):

    if random.random() > FRAUD_RATE:
        return tx

    profile = customer_profiles[str(customer["customer_id"])]
    avg = profile["average_amount"]

    scenario = random.choices(
        ["amount_spike", "device_change", "city_change", "combo", "extreme"],
        weights=[20, 15, 15, 35, 15],
        k=1
    )[0]

  
    if scenario == "amount_spike":

        tx["amount"] = round(avg * random.uniform(15, 30), 2)

     
        if random.random() < 0.30:
            tx["city"] = random.choice(
                [c for c in cities if c != customer["home_city"]]
            )

    elif scenario == "device_change":

        tx["device"] = random.choice(
            [d for d in devices if d != customer["usual_device"]]
        )

        tx["amount"] = round(avg * random.uniform(8, 15), 2)

        if random.random() < 0.40:
            tx["city"] = random.choice(
                [c for c in cities if c != customer["home_city"]]
            )

   
    elif scenario == "city_change":

        tx["city"] = random.choice(
            [c for c in cities if c != customer["home_city"]]
        )

        tx["amount"] = round(avg * random.uniform(8, 15), 2)

      
        if random.random() < 0.40:
            tx["device"] = random.choice(
                [d for d in devices if d != customer["usual_device"]]
            )

    elif scenario == "combo":

        tx["amount"] = round(avg * random.uniform(25, 45), 2)

        tx["device"] = random.choice(
            [d for d in devices if d != customer["usual_device"]]
        )

        tx["city"] = random.choice(
            [c for c in cities if c != customer["home_city"]]
        )

        tx["payment_method"] = random.choice(
            [p for p in payment_methods if p != customer["usual_payment_method"]]
        )

    
    elif scenario == "extreme":

        tx["amount"] = round(avg * random.uniform(45, 65), 2)

        tx["device"] = random.choice(
            [d for d in devices if d != customer["usual_device"]]
        )

        tx["city"] = random.choice(
            [c for c in cities if c != customer["home_city"]]
        )

        tx["payment_method"] = "Credit Card"

    tx["fraud_label"] = 0

    return tx


def insert_live_transaction(tx):
    cursor.execute("""
        INSERT INTO live_transactions (customer_id, transaction_time, amount, payment_method, city, device, fraud_label)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (tx["customer_id"], tx["transaction_time"], tx["amount"], tx["payment_method"], tx["city"], tx["device"], tx["fraud_label"]))
    conn.commit()


customer_pool = []
for customer in customers:
    profile = customer_profiles[str(customer["customer_id"])]
    weight = max(1, profile["transactions_per_day"])
    customer_pool.extend([customer] * weight)

if __name__ == "__main__":
    print("\n========================================")
    print(" 💥 MODEL-WEIGHT ALIGNED SIMULATOR RUNNING 💥 ")
    print("========================================\n")
    tx_count = 0
    try:
        while True:
            customer = random.choice(customer_pool)
            tx = generate_normal_transaction(customer)
            tx = inject_fraud(tx, customer)
            insert_live_transaction(tx)
            tx_count += 1

            print(
                f"[{tx_count:06}] "
                f"Cust:{tx['customer_id']} | "
                f"₹{tx['amount']:10.2f} | "
                f"{tx['city']:<12} | "
                f"{tx['device']}"
            )

            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")
    finally:
        cursor.close()
        conn.close()