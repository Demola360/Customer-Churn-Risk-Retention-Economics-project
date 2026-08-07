CREATE OR REPLACE VIEW telco_churn.driver_addons_by_internet_service AS
SELECT
  InternetService AS internet_service,
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
GROUP BY internet_service, addon_bundle
ORDER BY internet_service, churn_rate_pct DESC;