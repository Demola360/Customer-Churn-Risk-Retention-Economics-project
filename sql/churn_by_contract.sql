CREATE OR REPLACE VIEW telco_churn.churn_by_contract AS
SELECT
  Contract AS contract_type,
  COUNT(*) AS customers,
  COUNTIF(Churn = 'Yes') AS churned,
  ROUND(COUNTIF(Churn = 'Yes') / COUNT(*) * 100, 1) AS churn_rate_pct,
  ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM telco_churn.customers
GROUP BY contract_type
ORDER BY churn_rate_pct DESC