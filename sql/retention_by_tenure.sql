CREATE OR REPLACE VIEW telco_churn.retention_by_tenure AS
SELECT
  CASE
    WHEN tenure <= 6 THEN '0-6 months'
    WHEN tenure <= 12 THEN '7-12 months'
    WHEN tenure <= 24 THEN '13-24 months'
    WHEN tenure <= 48 THEN '25-48 months'
    ELSE '49+ months'
  END AS tenure_band,
  MIN(tenure) AS min_tenure_months,
  COUNT(*) AS customers,
  COUNTIF(Churn = 'Yes') AS churned,
  ROUND(COUNTIF(Churn = 'Yes') / COUNT(*) * 100, 1) AS churn_rate_pct
FROM telco_churn.customers
GROUP BY tenure_band
ORDER BY min_tenure_months