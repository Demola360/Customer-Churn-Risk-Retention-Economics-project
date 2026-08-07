CREATE OR REPLACE VIEW telco_churn.driver_payment_churn_by_contract AS
SELECT
  Contract AS contract_type,
  PaymentMethod AS payment_method,
  COUNT(*) AS customers,
  COUNTIF(Churn = 'Yes') AS churned,
  ROUND(COUNTIF(Churn = 'Yes') / COUNT(*) * 100, 1) AS churn_rate_pct
FROM telco_churn.customers
GROUP BY contract_type, payment_method
ORDER BY contract_type, churn_rate_pct DESC