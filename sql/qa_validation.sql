-- QA check: confirm segment counts sum to the full customer base
-- and no key fields have unexpected nulls
SELECT
  'segment_totals' AS check_name,
  SUM(customers) AS total_customers,
  7043 AS expected_total,
  SUM(customers) = 7043 AS passes
FROM telco_churn.churn_by_contract

UNION ALL

SELECT
  'null_check' AS check_name,
  COUNT(*) AS rows_with_nulls,
  0 AS expected_total,
  COUNT(*) = 0 AS passes
FROM telco_churn.customers
WHERE customerID IS NULL
   OR Contract IS NULL
   OR PaymentMethod IS NULL
   OR MonthlyCharges IS NULL
   OR Churn IS NULL