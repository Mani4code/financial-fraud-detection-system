import random
import json
from pathlib import Path
import mysql.connector
from faker import Faker


TOTAL_CUSTOMERS = 1000
random.seed(42)

fake = Faker("en_IN")
Faker.seed(42)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "model" / "customer_profiles.json"

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mani@sql5825u",
    database="fraud_detection_final"
)

cursor = conn.cursor()



cities = [
    "Chennai",
    "Coimbatore",
    "Madurai",
    "Trichy",
    "Salem",
    "Bangalore",
    "Hyderabad",
    "Mumbai",
    "Pune",
    "Delhi",
    "Kolkata",
    "Kochi"
]

devices = [
    "Samsung S24",
    "Samsung A55",
    "Samsung S23",
    "Samsung M35",
    "iPhone 15",
    "iPhone 16",
    "Redmi Note 13",
    "Redmi Note 14",
    "OnePlus 13",
    "Realme GT",
    "Vivo V50",
    "Oppo Reno 12"
]

payment_methods = (
    ["UPI"] * 60 +
    ["Debit Card"] * 20 +
    ["Credit Card"] * 15 +
    ["Net Banking"] * 5
)



profiles = [
    ("Low", 35, (200, 1000)),
    ("Medium", 40, (1000, 5000)),
    ("High", 20, (5000, 15000)),
    ("Premium", 5, (15000, 50000))
]

profile_pool = []

for profile, weight, amount_range in profiles:
    profile_pool.extend([(profile, amount_range)] * weight)



insert_query = """
INSERT INTO customers
(
customer_name,
account_number,
phone_number,
home_city,
usual_device,
usual_payment_method
)
VALUES
(%s,%s,%s,%s,%s,%s)
"""

used_accounts = set()
used_phones = set()

customer_profiles = {}

print("Generating Customers...\n")



for _ in range(TOTAL_CUSTOMERS):

   
    while True:
        account = str(random.randint(100000000000, 999999999999))
        if account not in used_accounts:
            used_accounts.add(account)
            break

    

    while True:
        phone = str(random.randint(6000000000, 9999999999))
        if phone not in used_phones:
            used_phones.add(phone)
            break

    city = random.choice(cities)

    device = random.choice(devices)

    payment = random.choice(payment_methods)

    cursor.execute(
        insert_query,
        (
            fake.name(),
            account,
            phone,
            city,
            device,
            payment
        )
    )

    customer_id = cursor.lastrowid

  

    profile_name, amount_range = random.choice(profile_pool)

    average_amount = random.randint(
        amount_range[0],
        amount_range[1]
    )

    variation = round(
        random.uniform(0.10, 0.35),
        2
    )

    active_start = random.randint(6, 10)

    active_end = random.randint(20, 23)

    customer_profiles[str(customer_id)] = {

        "profile": profile_name,

        "average_amount": average_amount,

        "variation": variation,

        "active_hours": {

            "start": active_start,

            "end": active_end

        }

    }



conn.commit()



with open(OUTPUT_PATH, "w") as file:
    json.dump(customer_profiles, file, indent=4)


distribution = {}

for customer in customer_profiles.values():

    profile = customer["profile"]

    distribution[profile] = distribution.get(profile, 0) + 1

print("Customer Distribution")

for k, v in distribution.items():
    print(f"{k:<10}: {v}")

print()

print(f"Total Customers : {TOTAL_CUSTOMERS}")

print("customer_profiles.json created successfully.")

cursor.close()
conn.close()

print("\nCustomers inserted into MySQL successfully.")