-- 03_churn_core.sql  (Q1-Q3)
-- Rumus ada di project/docs/definitions.md. churn_rate dalam persen (2 desimal).

-- Q1: churn keseluruhan dan per tipe kontrak
CREATE OR REPLACE TABLE q1_overall AS
SELECT count(*) AS n, sum(churn_i) AS churned,
       round(100.0 * avg(churn_i), 2) AS churn_rate,
       round(sum(monthly_charges), 2) AS mrr_total,
       round(sum(monthly_charges) FILTER (WHERE churn_i = 1), 2) AS lost_mrr
FROM v_customer;

CREATE OR REPLACE TABLE q1_contract AS
SELECT contract, count(*) AS n, sum(churn_i) AS churned,
       round(100.0 * avg(churn_i), 2) AS churn_rate,
       round(100.0 * sum(churn_i) / (SELECT sum(churn_i) FROM v_customer), 2) AS share_of_churners,
       round(100.0 * count(*) / (SELECT count(*) FROM v_customer), 2) AS share_of_customers
FROM v_customer GROUP BY contract;

-- Q2: churn per kelompok tenure
CREATE OR REPLACE TABLE q2_tenure AS
SELECT tenure_bucket_id, tenure_bucket, count(*) AS n, sum(churn_i) AS churned,
       round(100.0 * avg(churn_i), 2) AS churn_rate,
       round(100.0 * sum(churn_i) / (SELECT sum(churn_i) FROM v_customer), 2) AS share_of_churners
FROM v_customer GROUP BY tenure_bucket_id, tenure_bucket;

CREATE OR REPLACE TABLE q2_tenure_contract AS
SELECT contract, tenure_bucket_id, tenure_bucket, count(*) AS n, sum(churn_i) AS churned,
       round(100.0 * avg(churn_i), 2) AS churn_rate
FROM v_customer GROUP BY contract, tenure_bucket_id, tenure_bucket;

-- Q3: kurva retensi (Kaplan-Meier) dengan tenure sebagai waktu pengamatan dan churn sebagai kejadian.
-- Pelanggan yang tidak churn dianggap tersensor di tenure-nya. Pelanggan tenure 0 tidak ikut (belum diamati sebulan pun).
CREATE OR REPLACE TABLE q3_retention AS
WITH per_t AS (
    SELECT grp, t, count(*) AS c, sum(churn_i) AS d
    FROM (
        SELECT contract AS grp, tenure_months AS t, churn_i FROM v_customer WHERE tenure_months > 0
        UNION ALL
        SELECT 'Semua' AS grp, tenure_months AS t, churn_i FROM v_customer WHERE tenure_months > 0
    ) GROUP BY grp, t
), risk AS (
    SELECT grp, t, d,
           sum(c) OVER (PARTITION BY grp ORDER BY t DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS at_risk
    FROM per_t
)
SELECT grp AS contract, t AS month, at_risk, d AS churned_at_t,
       round(100.0 * exp(sum(ln(greatest(1.0 - d::DOUBLE / at_risk, 1e-12))) OVER (PARTITION BY grp ORDER BY t)), 2) AS retention_pct
FROM risk;
