"""
Loads the Telco Customer Churn CSV into BigQuery.

Before running:
  1. Download WA_Fn-UseC_-Telco-Customer-Churn.csv from
     https://www.kaggle.com/datasets/blastchar/telco-customer-churn
     and place it in this project folder.
  2. Set up a BigQuery project the same way as the last project (Sandbox,
     no credit card): https://console.cloud.google.com/bigquery
  3. gcloud auth application-default login
  4. Set GCP_PROJECT_ID and BQ_DATASET as usual.

Run with:
    python load_telco_data.py
"""

import os
import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

REQUIRED_ENV_VARS = ["GCP_PROJECT_ID", "BQ_DATASET"]
CSV_PATH = "WA_Fn-UseC_-Telco-Customer-Churn.csv"
TABLE_NAME = "customers"


def get_client() -> bigquery.Client:
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {missing}")
    return bigquery.Client(project=os.environ["GCP_PROJECT_ID"])


def ensure_dataset(client: bigquery.Client, dataset_id: str):
    full_id = f"{client.project}.{dataset_id}"
    try:
        client.get_dataset(full_id)
    except NotFound:
        print(f"Dataset {full_id} not found, creating it...")
        dataset = bigquery.Dataset(full_id)
        dataset.location = "US"
        client.create_dataset(dataset)


def clean_telco_data(df: pd.DataFrame) -> pd.DataFrame:
    # TotalCharges is loaded by pandas as a string in the raw file — a
    # handful of rows (customers with 0 tenure) have blank values here,
    # which need converting to numeric with those blanks as NULL, not 0.
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    return df


if __name__ == "__main__":
    client = get_client()
    dataset_id = os.environ["BQ_DATASET"]
    ensure_dataset(client, dataset_id)

    df = pd.read_csv(CSV_PATH)
    df = clean_telco_data(df)

    table_id = f"{client.project}.{dataset_id}.{TABLE_NAME}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE", autodetect=True)
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows -> {table_id}")
