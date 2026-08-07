CREATE OR REPLACE VIEW telco_churn.driver_addons_by_contract AS
SELECT
  Contract AS contract_type,
  CASE
    WHEN InternetService = 'No' THEN 'No internet service'
    WHEN OnlineSecurity = 'Yes' AND TechSupport = 'Yes' THEN 'Has both security and support'
    WHEN OnlineSecurity = 'No' AND TechSupport = 'No' THEN 'Has neither'
    ELSE 'Has one of the two'
  END AS addon_bundle,
  COUNT(*) AS customers,
  COUNTIF(Churn = 'Yes') AS churned,
  ROUND(COUNTIF(Churn = 'Yes') / COUNT(*) * 100, 1) AS churn_rate_pct
FROM telco_churn.customers
GROUP BY contract_type, addon_bundle
ORDER BY contract_type, churn_rate_pct DESC