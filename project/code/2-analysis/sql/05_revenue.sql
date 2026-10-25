-- 05_revenue.sql  (Q9-Q12)
-- Hasil dampak (Q11-Q12) adalah ESTIMASI: asumsi churn turun relatif, ARPU = rata-rata MonthlyCharges segmen.

-- Q9: revenue bulanan hilang (lost MRR) per segmen, dengan kontribusi dan kumulatif (Pareto)
CREATE OR REPLACE TABLE q9_pareto AS
WITH s AS (SELECT * FROM q7_segments WHERE churned > 0),
     t AS (SELECT sum(lost_mrr) AS total FROM s)
SELECT row_number() OVER (ORDER BY s.lost_mrr DESC, s.contract, s.internet_service, s.payment_method) AS rank,
       s.contract, s.internet_service, s.payment_method, s.n, s.churned, s.churn_rate, s.arpu, s.lost_mrr,
       round(100.0 * s.lost_mrr / t.total, 2) AS share_lost_mrr,
       round(100.0 * sum(s.lost_mrr) OVER (ORDER BY s.lost_mrr DESC, s.contract, s.internet_service, s.payment_method
                                           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / t.total, 2) AS cum_share_lost_mrr
FROM s, t;

CREATE OR REPLACE TABLE q9_lost_by_factor AS
SELECT 'contract' AS factor, contract AS level, sum(churn_i) AS churned,
       round(coalesce(sum(monthly_charges) FILTER (WHERE churn_i = 1), 0), 2) AS lost_mrr,
       round(100.0 * avg(churn_i), 2) AS churn_rate FROM v_customer GROUP BY contract
UNION ALL
SELECT 'internet_service', internet_service, sum(churn_i),
       round(coalesce(sum(monthly_charges) FILTER (WHERE churn_i = 1), 0), 2), round(100.0 * avg(churn_i), 2)
FROM v_customer GROUP BY internet_service
UNION ALL
SELECT 'payment_method', payment_method, sum(churn_i),
       round(coalesce(sum(monthly_charges) FILTER (WHERE churn_i = 1), 0), 2), round(100.0 * avg(churn_i), 2)
FROM v_customer GROUP BY payment_method
UNION ALL
SELECT 'tenure_bucket', tenure_bucket, sum(churn_i),
       round(coalesce(sum(monthly_charges) FILTER (WHERE churn_i = 1), 0), 2), round(100.0 * avg(churn_i), 2)
FROM v_customer GROUP BY tenure_bucket;

-- Q10: tagihan bulanan pelanggan churn vs bertahan
CREATE OR REPLACE TABLE q10_charges AS
SELECT churn, count(*) AS n, round(avg(monthly_charges), 2) AS mean_charge,
       round(quantile_cont(monthly_charges, 0.5), 2) AS median_charge,
       round(quantile_cont(monthly_charges, 0.25), 2) AS p25_charge,
       round(quantile_cont(monthly_charges, 0.75), 2) AS p75_charge
FROM v_customer GROUP BY churn;

CREATE OR REPLACE TABLE q10_charges_contract AS
SELECT contract, churn, count(*) AS n, round(avg(monthly_charges), 2) AS mean_charge,
       round(quantile_cont(monthly_charges, 0.5), 2) AS median_charge
FROM v_customer GROUP BY contract, churn;

-- Q11: skenario revenue terselamatkan per tahun untuk 5 segmen teratas (n >= 100, urut lost MRR)
-- Revenue terselamatkan/tahun = (churn lama - churn baru) x pelanggan segmen x ARPU x 12
CREATE OR REPLACE TABLE q11_scenarios AS
WITH top AS (
    SELECT * FROM q9_pareto WHERE n >= 100 ORDER BY lost_mrr DESC LIMIT 5
), sc AS (SELECT unnest([0.10, 0.20, 0.30]) AS cut)
SELECT t.rank AS rank_all, t.contract, t.internet_service, t.payment_method, t.n, t.churn_rate, t.arpu, t.lost_mrr,
       round(100 * sc.cut) AS cut_pct,
       round(t.churn_rate * (1 - sc.cut), 2) AS churn_rate_new,
       round((t.churn_rate - t.churn_rate * (1 - sc.cut)) / 100.0 * t.n, 1) AS customers_saved,
       round((t.churn_rate - t.churn_rate * (1 - sc.cut)) / 100.0 * t.n * t.arpu * 12, 2) AS saved_revenue_year
FROM top t, sc;

-- Q12: batas biaya program agar impas = revenue terselamatkan / pelanggan segmen (per tahun)
CREATE OR REPLACE TABLE q12_breakeven AS
SELECT rank_all, contract, internet_service, payment_method, n, cut_pct, saved_revenue_year,
       round(saved_revenue_year / n, 2) AS breakeven_cost_per_customer_year,
       round(saved_revenue_year / customers_saved, 2) AS breakeven_cost_per_saved_customer
FROM q11_scenarios;
