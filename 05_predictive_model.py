"""
Phase 4: Predictive model.

Compares Logistic Regression against Random Forest on a time-ordered
split, evaluated on three things: ROC-AUC, precision at the top 20% of
customers by predicted risk (a stand-in for "how many customers can a
retention team realistically contact"), and a qualitative note on
explainability.

Split method: the dataset has no signup date, only tenure. Customers
with higher tenure joined earlier; customers with lower tenure joined
more recently. Sorting by tenure and training on the longer-tenured
80% while testing on the most recent 20% is a reasonable time-ordered
proxy split, consistent with how tenure was already used as a cohort
proxy in the SQL phase. This is disclosed here rather than treated as
a real chronological split, since it isn't one.

Decision rule, stated before running anything: if the ROC-AUC gap
between the two models is small, prefer Logistic Regression for its
explainability. If Random Forest meaningfully outperforms, that's a
legitimate reason to choose it instead.

Run with:
    python 05_predictive_model.py

Requires the same environment variables as the loader scripts:
    GCP_PROJECT_ID, BQ_DATASET
"""

import os
import pandas as pd
import numpy as np
from google.cloud import bigquery
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

REQUIRED_ENV_VARS = ["GCP_PROJECT_ID", "BQ_DATASET"]

CATEGORICAL_FEATURES = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]
TOP_PCT_FOR_CAPACITY_METRIC = 0.20


def load_data() -> pd.DataFrame:
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {missing}")

    client = bigquery.Client(project=os.environ["GCP_PROJECT_ID"])
    dataset = os.environ["BQ_DATASET"]
    query = f"SELECT * FROM `{client.project}.{dataset}.customers`"
    return client.query(query).to_dataframe()


def prepare_features(df: pd.DataFrame):
    df = df.copy()
    df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"])
    df["churn_label"] = (df["Churn"] == "Yes").astype(int)
    return df


def time_ordered_split(df: pd.DataFrame):
    # Highest tenure = joined earliest. Sort descending, train on the
    # first 80%, test on the most recent 20%.
    #
    # IMPORTANT: do NOT reset_index here. The original row index is
    # needed afterward to look up the matching rows in the one-hot
    # encoded dataframe. Resetting it silently breaks that lookup —
    # it still runs without error, it just pulls the wrong rows.
    df_sorted = df.sort_values("tenure", ascending=False)
    split_idx = int(len(df_sorted) * 0.8)
    train = df_sorted.iloc[:split_idx]
    test = df_sorted.iloc[split_idx:]
    return train, test


def precision_at_top_pct(y_true: np.ndarray, y_scores: np.ndarray, pct: float) -> float:
    n_top = max(1, int(len(y_scores) * pct))
    top_indices = np.argsort(y_scores)[::-1][:n_top]
    return y_true[top_indices].mean()


if __name__ == "__main__":
    print("Loading data from BigQuery...")
    df = load_data()
    df = prepare_features(df)

    train_df, test_df = time_ordered_split(df)
    print(f"Train: {len(train_df)} customers (higher tenure / earlier joiners)")
    print(f"Test:  {len(test_df)} customers (lower tenure / more recent joiners)")

    # One-hot encode categoricals across the full dataset first, so
    # train and test end up with identical columns even if a category
    # only appears in one split.
    df_encoded = pd.get_dummies(df, columns=CATEGORICAL_FEATURES, drop_first=True)
    feature_cols = [c for c in df_encoded.columns if c not in
                     ("customerID", "Churn", "churn_label")]

    train_encoded = df_encoded.loc[train_df.index]
    test_encoded = df_encoded.loc[test_df.index]

    X_train = train_encoded[feature_cols]
    y_train = train_encoded["churn_label"].values
    X_test = test_encoded[feature_cols]
    y_test = test_encoded["churn_label"].values

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}

    print("\nTraining Logistic Regression...")
    log_reg = LogisticRegression(max_iter=1000, random_state=42)
    log_reg.fit(X_train_scaled, y_train)
    log_reg_scores = log_reg.predict_proba(X_test_scaled)[:, 1]
    results["Logistic Regression"] = {
        "roc_auc": roc_auc_score(y_test, log_reg_scores),
        "precision_at_top_20pct": precision_at_top_pct(y_test, log_reg_scores, TOP_PCT_FOR_CAPACITY_METRIC),
    }

    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    rf.fit(X_train, y_train)
    rf_scores = rf.predict_proba(X_test)[:, 1]
    results["Random Forest"] = {
        "roc_auc": roc_auc_score(y_test, rf_scores),
        "precision_at_top_20pct": precision_at_top_pct(y_test, rf_scores, TOP_PCT_FOR_CAPACITY_METRIC),
    }

    print("\n--- Results ---")
    for name, metrics in results.items():
        print(f"{name}: ROC-AUC={metrics['roc_auc']:.3f}, "
              f"Precision@top20%={metrics['precision_at_top_20pct']:.3f}")

    auc_gap = abs(results["Logistic Regression"]["roc_auc"] - results["Random Forest"]["roc_auc"])
    print(f"\nROC-AUC gap: {auc_gap:.3f}")
    if auc_gap < 0.03:
        print("Decision: gap is small (<0.03) -> Logistic Regression selected for explainability.")
    else:
        print("Decision: gap is meaningful (>=0.03) -> Random Forest selected on performance.")

    print("\nFull Logistic Regression coefficient table, sorted by strength:")
    coef_df = pd.DataFrame({
        "feature": feature_cols,
        "coefficient": log_reg.coef_[0],
    }).sort_values("coefficient", key=abs, ascending=False).reset_index(drop=True)
    coef_df.index += 1
    print(coef_df.to_string())

    addon_features = [f for f in feature_cols if "OnlineSecurity" in f or "TechSupport" in f]
    print("\nAdd-on related coefficients specifically, wherever they rank:")
    print(coef_df[coef_df["feature"].isin(addon_features)].to_string())
