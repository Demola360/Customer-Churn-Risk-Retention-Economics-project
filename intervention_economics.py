"""
Phase 6: Intervention economics.

Answers the real question this project is built around: for each
customer, is contacting them to prevent churn actually worth the cost,
given what's known about their risk and value?

Assumptions, stated explicitly rather than left implicit:
  - Cost to contact one customer: GBP 25-30, midpoint GBP 27.50
  - Retention intervention success rate: 30-35%, midpoint 32.5%
  - Retention horizon: 12 months of forward value if retained

None of these are measured. There is no real intervention campaign to
observe. They are stated, defensible assumptions, and the calculation
is run three times (low, base, high) rather than once, since presenting
a single point estimate would overstate how certain any of this is.

Expected retained value per customer = churn_probability x success_rate
x MonthlyCharges x retention_horizon_months

Net expected value = expected retained value - cost_per_contact

Intervention is recommended only where net expected value is positive.

Run with:
    python intervention_economics.py

Requires customer_segments.csv, produced by risk_value_segmentation.py.
"""

import pandas as pd

INPUT_FILE = "customer_segments.csv"
RETENTION_HORIZON_MONTHS = 12

SCENARIOS = {
    "Low (conservative)": {"cost_per_contact": 30.0, "success_rate": 0.30},
    "Base (midpoint)": {"cost_per_contact": 27.5, "success_rate": 0.325},
    "High (optimistic)": {"cost_per_contact": 25.0, "success_rate": 0.35},
}


def calculate_expected_value(df: pd.DataFrame, cost_per_contact: float, success_rate: float) -> pd.DataFrame:
    df = df.copy()
    df["expected_retained_value"] = (
        df["churn_probability"] * success_rate * df["MonthlyCharges"] * RETENTION_HORIZON_MONTHS
    )
    df["net_expected_value"] = df["expected_retained_value"] - cost_per_contact
    df["recommend_intervention"] = df["net_expected_value"] > 0
    return df


def summarise_scenario(df: pd.DataFrame, cost_per_contact: float) -> dict:
    recommended = df[df["recommend_intervention"]]
    return {
        "customers_recommended": len(recommended),
        "total_contact_cost": len(recommended) * cost_per_contact,
        "total_expected_retained_value": recommended["expected_retained_value"].sum(),
        "net_portfolio_value": recommended["net_expected_value"].sum(),
    }


if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} scored customers from {INPUT_FILE}\n")

    scenario_results = {}
    base_df_for_export = None

    for scenario_name, params in SCENARIOS.items():
        scored = calculate_expected_value(df, params["cost_per_contact"], params["success_rate"])
        summary = summarise_scenario(scored, params["cost_per_contact"])
        scenario_results[scenario_name] = summary

        if scenario_name == "Base (midpoint)":
            base_df_for_export = scored

    print("Scenario comparison (whole customer base):")
    results_df = pd.DataFrame(scenario_results).T
    results_df["total_contact_cost"] = results_df["total_contact_cost"].round(0)
    results_df["total_expected_retained_value"] = results_df["total_expected_retained_value"].round(0)
    results_df["net_portfolio_value"] = results_df["net_portfolio_value"].round(0)
    print(results_df.to_string())

    print("\nBase scenario, broken down by segment:")
    segment_summary = base_df_for_export.groupby("segment").agg(
        customers=("customerID", "count"),
        recommended=("recommend_intervention", "sum"),
        avg_net_expected_value=("net_expected_value", "mean"),
        total_net_expected_value=("net_expected_value", lambda x: x[x > 0].sum()),
    ).round(2)
    print(segment_summary.to_string())

    # Breakeven alone tends to recommend most of the customer base, since
    # a 12-month revenue horizon comfortably clears a one-time contact
    # cost even at modest risk. That's not useful for a team with a real,
    # fixed capacity. This view instead ranks customers by net expected
    # value and shows what a realistic weekly capacity constraint would
    # actually prioritise.
    WEEKLY_CAPACITY_OPTIONS = [50, 100, 250]
    print("\nCapacity-constrained view (base scenario, ranked by net expected value):")
    ranked = base_df_for_export.sort_values("net_expected_value", ascending=False)
    for capacity in WEEKLY_CAPACITY_OPTIONS:
        top_n = ranked.head(capacity)
        print(f"  Top {capacity} contacted -> "
              f"total net value \u00a3{top_n['net_expected_value'].sum():,.0f}, "
              f"avg churn probability {top_n['churn_probability'].mean():.2f}, "
              f"segments: {top_n['segment'].value_counts().to_dict()}")

    base_df_for_export.to_csv("customer_intervention_recommendations.csv", index=False)
    print(f"\nSaved base-scenario recommendations to customer_intervention_recommendations.csv")
