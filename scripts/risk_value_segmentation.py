"""
Phase 5: Risk x value segmentation.

Scores every customer with the Logistic Regression model selected in
Phase 4, then crosses predicted churn risk against monthly revenue
value to produce a simple 2x2 segmentation: High/Low risk by median
predicted probability, High/Low value by median MonthlyCharges.

Note on methodology: Phase 4 evaluated the model properly on a held-out
test set, and that evaluation stands as-is. This script refits the same
model on the FULL dataset before scoring, which is standard practice
once a model has been selected and evaluated - the deployed scoring
model uses all available historical data, rather than deliberately
withholding 20% from the customers it's actually meant to score.
Evaluating and deploying are two different jobs; this script only does
the second one.

Run with:
    python risk_value_segmentation.py

Requires the same environment variables as the other scripts.
"""

import os
import pandas as pd
from google.cloud import bigquery
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

REQUIRED_ENV_VARS = ["GCP_PROJECT_ID", "BQ_DATASET"]

CATEGORICAL_FEATURES = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]


def load_data() -> pd.DataFrame:
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {missing}")
    client = bigquery.Client(project=os.environ["GCP_PROJECT_ID"])
    dataset = os.environ["BQ_DATASET"]
    query = f"SELECT * FROM `{client.project}.{dataset}.customers`"
    return client.query(query).to_dataframe()


def score_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"])
    df["churn_label"] = (df["Churn"] == "Yes").astype(int)

    df_encoded = pd.get_dummies(df, columns=CATEGORICAL_FEATURES, drop_first=True)
    feature_cols = [c for c in df_encoded.columns if c not in
                     ("customerID", "Churn", "churn_label")]

    X = df_encoded[feature_cols]
    y = df_encoded["churn_label"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_scaled, y)

    df["churn_probability"] = model.predict_proba(X_scaled)[:, 1]
    return df


def segment(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    risk_median = df["churn_probability"].median()
    value_median = df["MonthlyCharges"].median()

    df["risk_tier"] = df["churn_probability"].apply(
        lambda p: "High Risk" if p >= risk_median else "Low Risk"
    )
    df["value_tier"] = df["MonthlyCharges"].apply(
        lambda v: "High Value" if v >= value_median else "Low Value"
    )
    df["segment"] = df["risk_tier"] + " / " + df["value_tier"]
    return df


if __name__ == "__main__":
    print("Loading data from BigQuery...")
    df = load_data()

    print("Scoring customers with the Logistic Regression model...")
    df_scored = score_customers(df)
    df_segmented = segment(df_scored)

    print("\nSegment summary:")
    summary = df_segmented.groupby("segment").agg(
        customers=("customerID", "count"),
        avg_churn_probability=("churn_probability", "mean"),
        total_monthly_revenue=("MonthlyCharges", "sum"),
        actual_churn_rate=("churn_label", "mean"),
    ).round(3)
    print(summary.to_string())

    output_cols = [
        "customerID", "churn_probability", "risk_tier", "MonthlyCharges",
        "value_tier", "segment", "Contract", "tenure",
    ]
    df_segmented[output_cols].to_csv("customer_segments.csv", index=False)
    print(f"\nSaved {len(df_segmented)} scored, segmented customers to customer_segments.csv")
