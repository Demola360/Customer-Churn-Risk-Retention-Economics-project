"""
Diagnostic: checks how correlated the add-on flags (OnlineSecurity,
TechSupport) are with InternetService type. High correlation between
predictors is a common reason a variable's real effect gets absorbed
into a correlated variable's coefficient instead of showing up on its
own — the model can't fully tell the two apart, so it puts most of the
weight on whichever one happens to capture the pattern slightly better,
even if both matter.

Run with:
    python 07_addons_correlation_check.py

Requires the same environment variables as the other scripts.
"""

import os
import pandas as pd
from google.cloud import bigquery

REQUIRED_ENV_VARS = ["GCP_PROJECT_ID", "BQ_DATASET"]


def load_data() -> pd.DataFrame:
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {missing}")
    client = bigquery.Client(project=os.environ["GCP_PROJECT_ID"])
    dataset = os.environ["BQ_DATASET"]
    query = f"SELECT * FROM `{client.project}.{dataset}.customers`"
    return client.query(query).to_dataframe()


if __name__ == "__main__":
    df = load_data()

    df["has_fiber"] = (df["InternetService"] == "Fiber optic").astype(int)
    df["has_security"] = (df["OnlineSecurity"] == "Yes").astype(int)
    df["has_support"] = (df["TechSupport"] == "Yes").astype(int)
    df["no_internet"] = (df["InternetService"] == "No").astype(int)

    corr = df[["has_fiber", "has_security", "has_support", "no_internet"]].corr()
    print("Correlation matrix:")
    print(corr.round(3))

    print("\nWhat share of each internet service type has security/support:")
    summary = df.groupby("InternetService").agg(
        customers=("customerID", "count"),
        pct_with_security=("has_security", "mean"),
        pct_with_support=("has_support", "mean"),
    )
    summary["pct_with_security"] = (summary["pct_with_security"] * 100).round(1)
    summary["pct_with_support"] = (summary["pct_with_support"] * 100).round(1)
    print(summary)
