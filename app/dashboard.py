import os

try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]
except ImportError:
    def load_dotenv():
        return False

load_dotenv()

import streamlit as st
import pandas as pd
import mysql.connector
from streamlit_autorefresh import st_autorefresh


st.set_page_config(
    page_title="Real-Time Fraud Monitoring",
    page_icon="🚨",
    layout="wide"
)

st_autorefresh(interval=1000, key="refresh")


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)



@st.cache_data(ttl=1)
def load_data():

    conn = get_connection()

    query = """
    SELECT

        lt.transaction_id,
        lt.customer_id,
        lt.amount,
        lt.probability,
        lt.city,
        lt.device,
        lt.payment_method,
        lt.transaction_time,
        lt.expected_avg,
        lt.growth_ratio,
        lt.amount_vs_max,

        c.customer_name,
        c.account_number,
        c.phone_number,
        c.home_city,
        c.usual_device,
        c.usual_payment_method

    FROM live_transactions lt
    JOIN customers c
    ON lt.customer_id = c.customer_id

    WHERE lt.fraud_label = 1

    ORDER BY lt.transaction_time DESC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


df = load_data()



if df.empty:
    st.title("🚨 Real-Time Fraud Monitoring Dashboard")
    st.success("✅ No fraud alerts at the moment.")
    st.stop()



selected = df.iloc[0]



if pd.isna(selected["probability"]):
    selected["probability"] = 0



st.markdown(
    """
    <h1 style='text-align:center;color:red;'>
    🚨 REAL-TIME FRAUD MONITORING DASHBOARD
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown("---")


st.error(f"""
## 🚨 NEW FRAUD DETECTED

Customer : {selected['customer_name']}

Transaction ID : {selected['transaction_id']}

Amount : ₹{selected['amount']:,.2f}

Fraud Probability : {selected['probability']*100:.2f}%

Transaction Time : {selected['transaction_time']}
""")

st.markdown("---")



st.subheader("📋 Recent Fraud Alerts")

table = df.copy()

table["Probability"] = (
    table["probability"]
    .fillna(0)
    .mul(100)
    .round(2)
    .astype(str) + "%"
)

table["Amount"] = table["amount"].map(
    lambda x: f"₹{x:,.2f}"
)

table["Time"] = pd.to_datetime(
    table["transaction_time"]
).dt.strftime("%d-%m-%Y %H:%M:%S")

st.dataframe(

    table[
        [
            "transaction_id",
            "customer_name",
            "Amount",
            "Probability",
            "Time"
        ]
    ],

    hide_index=True,

    use_container_width=True,

    height=250

)

st.markdown("---")


left, right = st.columns(2)


with left:

    st.subheader("👤 Customer Profile")

    st.write(f"**Customer Name:** {selected['customer_name']}")
    st.write(f"**Customer ID:** {selected['customer_id']}")
    st.write(f"**Account Number:** {selected['account_number']}")
    st.write(f"**Phone Number:** {selected['phone_number']}")
    st.write(f"**Home City:** {selected['home_city']}")
    st.write(f"**Usual Device:** {selected['usual_device']}")
    st.write(f"**Usual Payment:** {selected['usual_payment_method']}")



with right:

    st.subheader("💳 Fraud Transaction")

    prob = float(selected["probability"])

    if prob >= 0.95:
        risk = "🔴 CRITICAL"

    elif prob >= 0.80:
        risk = "🟠 HIGH"

    else:
        risk = "🟡 MEDIUM"

    st.write(f"**Risk Level:** {risk}")
    st.write(f"**Transaction ID:** {selected['transaction_id']}")
    st.write(f"**Amount:** ₹ {selected['amount']:,.2f}")
    st.write(f"**Fraud Probability:** {prob*100:.2f}%")
    st.write(f"**Transaction Time:** {selected['transaction_time']}")
    st.write(f"**Expected Average:** ₹ {selected['expected_avg']:,.2f}")
    st.write(f"**Growth Ratio:** {selected['growth_ratio']:.2f}x")
    st.write(f"**Amount vs Max:** {selected['amount_vs_max']:.2f}x")




st.markdown("---")
st.subheader("🧠 Behaviour Analysis")

c1, c2, c3 = st.columns(3)



with c1:

    changed = selected["city"] != selected["home_city"]

    st.info(f"""
### 🌍 City

Current

**{selected['city']}**

Home

**{selected['home_city']}**

Status

**{"❌ Changed" if changed else "✅ Normal"}**
""")




with c2:

    changed = selected["device"] != selected["usual_device"]

    st.info(f"""
### 📱 Device

Current

**{selected['device']}**

Usual

**{selected['usual_device']}**

Status

**{"❌ Changed" if changed else "✅ Normal"}**
""")



with c3:

    changed = (
        selected["payment_method"]
        !=
        selected["usual_payment_method"]
    )

    st.info(f"""
### 💳 Payment

Current

**{selected['payment_method']}**

Usual

**{selected['usual_payment_method']}**

Status

**{"❌ Changed" if changed else "✅ Normal"}**
""")




st.markdown("---")
st.subheader("📋 Last 10 Fraud Alerts")

last10 = df.head(10).copy()

last10["Amount"] = last10["amount"].map(
    lambda x: f"₹{x:,.2f}"
)

last10["Probability"] = (
    last10["probability"]
    .fillna(0)
    .mul(100)
    .round(2)
    .astype(str) + "%"
)

last10["Time"] = pd.to_datetime(
    last10["transaction_time"]
).dt.strftime("%d-%m-%Y %H:%M:%S")

st.dataframe(

    last10[
        [
            "transaction_id",
            "customer_name",
            "Amount",
            "Probability",
            "Time"
        ]
    ],

    hide_index=True,

    use_container_width=True

)

st.success("🟢 Dashboard Auto Refreshing Every Second")
