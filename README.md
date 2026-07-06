# 🚀 Real-Time Financial Fraud Detection System

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)

![XGBoost](https://img.shields.io/badge/Model-XGBoost-success?style=for-the-badge)

![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)

![MySQL](https://img.shields.io/badge/Database-MySQL-orange?style=for-the-badge&logo=mysql)

![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red?style=for-the-badge&logo=streamlit)

</p>

---

## 📌 Project Overview

This project is a **Real-Time Financial Fraud Detection System** that simulates banking transactions, detects fraudulent activities using a trained **XGBoost Machine Learning model**, and visualizes live transaction monitoring through an interactive **Streamlit dashboard**.

The system has been fully **Dockerized**, allowing the complete application—including **MySQL**, the **Live Transaction Simulator**, the **Fraud Detection Engine**, and the **Dashboard**—to be launched using a single Docker Compose command.

---

## 📸 Dashboard Preview

> *(We'll add your dashboard screenshot in the next step.)*

----

# ✨ Features

## 🔹 Real-Time Transaction Simulation
- Generates realistic banking transactions based on customer behavior profiles.
- Simulates spending patterns, device usage, payment methods, and locations.
- Injects rare fraudulent transactions using multiple fraud scenarios.

## 🔹 Machine Learning Fraud Detection
- Uses a trained **XGBoost** model to classify incoming transactions.
- Performs real-time feature engineering before prediction.
- Calculates fraud probability for every transaction.
- Updates the database instantly with prediction results.

## 🔹 Interactive Streamlit Dashboard
- Displays live transactions as they are generated.
- Highlights suspicious transactions in real time.
- Shows fraud probability and transaction details.
- Refreshes automatically without restarting the application.

## 🔹 MySQL Database
- Stores customer information.
- Maintains historical transaction data.
- Receives live simulated transactions.
- Stores fraud predictions and monitoring metrics.

## 🔹 Dockerized Deployment
- One-command deployment using Docker Compose.
- Automatically starts:
  - MySQL Database
  - Live Transaction Simulator
  - Fraud Detection Engine
  - Streamlit Dashboard

## 🔹 End-to-End Pipeline
- Historical Data Generation
- Customer Profile Creation
- Live Transaction Simulation
- Machine Learning Prediction
- Real-Time Dashboard Monitoring--

---

# ⚙️ Technology Stack

| Category | Technology |
|----------|------------|
| **Programming Language** | Python 3.11 |
| **Machine Learning** | XGBoost |
| **Database** | MySQL 8 |
| **Dashboard** | Streamlit |
| **Containerization** | Docker |
| **Container Orchestration** | Docker Compose |
| **Data Processing** | Pandas, NumPy |
| **Database Connector** | MySQL Connector/Python |
| **Model Persistence** | Joblib |
| **Environment Management** | python-dotenv |
| **Version Control** | Git & GitHub |

---

# 📂 Project Structure

```text
financial-fraud-detection-system/
│
├── app/
│   ├── dashboard.py              # Streamlit dashboard
│   ├── detector.py               # Real-time fraud detection engine
│   ├── live_simulator.py         # Live transaction simulator
│   └── __init__.py
│
├── assets/
│   ├── architecture.png
│   ├── dashboard.png
│   ├── dashboard_dark.png
│   └── demo.gif
│
├── database/
│   ├── init/
│   │   └── history_builder.sql   # Database initialization script
│   ├── history_builder.ipynb
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── api_documentation.md
│   └── project_report.pdf
│
├── model/
│   ├── customer_generator.py
│   ├── feature_engineering.py
│   ├── customer_profiles.json
│   ├── featured_transactions.csv
│   ├── fraud_detection_model.pkl
│   ├── fraud_model_training.ipynb
│   └── training_data_generator.ipynb
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .dockerignore
├── .gitignore
├── LICENSE
└── README.md
```

## 📑 Table of Contents

- Project Overview
- Features
- System Architecture
- Technology Stack
- Project Structure
- Machine Learning Pipeline
- Docker Architecture
- Installation
- Running the Project
- Dashboard
- Future Enhancements
- Author
- License
