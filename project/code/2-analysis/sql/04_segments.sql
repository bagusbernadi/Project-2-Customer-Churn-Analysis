-- 04_segments.sql  (Q4-Q8)

-- Q4: layanan (ada vs tidak ada). Status 'Not available' = pelanggan tidak punya layanan induk (internet/telepon).
CREATE OR REPLACE TABLE q4_service AS
SELECT s.service_name, s.status, count(*) AS n, sum(a.churn_i) AS churned,
       round(100.0 * avg(a.churn_i), 2) AS churn_rate
FROM services s JOIN accounts a USING (customer_id)
WHERE s.service_name <> 'InternetService'
GROUP BY s.service_name, s.status;

CREATE OR REPLACE TABLE q4_internet AS
SELECT internet_service, count(*) AS n, sum(churn_i) AS churned,
       round(100.0 * avg(churn_i), 2) AS churn_rate,
       round(avg(monthly_charges), 2) AS arpu
FROM v_customer GROUP BY internet_service;

-- Q4b: layanan di antara pelanggan internet saja, dipisah per jenis internet (mengendalikan DSL vs Fiber).
CREATE OR REPLACE TABLE q4_service_by_internet AS
SELECT v.internet_service, s.service_name, s.status, count(*) AS n, sum(v.churn_i) AS churned,
       round(100.0 * avg(v.churn_i), 2) AS churn_rate
FROM services s JOIN v_customer v USING (customer_id)
WHERE v.internet_service <> 'No'
  AND s.service_name IN ('OnlineSecurity','OnlineBackup','DeviceProtection','TechSupport','StreamingTV','StreamingMovies')
GROUP BY v.internet_service, s.service_name, s.status;

-- Q5: jumlah layanan tambahan (bundling), hanya pelanggan internet
CREATE OR REPLACE TABLE q5_addons AS
SELECT n_addons, count(*) AS n, sum(churn_i) AS churned,
       round(100.0 * avg(churn_i), 2) AS churn_rate
FROM v_customer WHERE internet_service <> 'No' GROUP BY n_addons;

CREATE OR REPLACE TABLE q5_addons_contract AS
SELECT contract,
       CASE WHEN n_addons = 0 THEN '0' WHEN n_addons <= 2 THEN '1-2' WHEN n_addons <= 4 THEN '3-4' ELSE '5-6' END AS addon_group,
       count(*) AS n, sum(churn_i) AS churned, round(100.0 * avg(churn_i), 2) AS churn_rate
FROM v_customer WHERE internet_service <> 'No' GROUP BY 1, 2;

-- Q6: metode bayar dan paperless; tabel silang dengan kontrak dan internet
CREATE OR REPLACE TABLE q6_payment AS
SELECT payment_method, count(*) AS n, sum(churn_i) AS churned, round(100.0 * avg(churn_i), 2) AS churn_rate
FROM v_customer GROUP BY payment_method;

CREATE OR REPLACE TABLE q6_paperless AS
SELECT paperless_billing, count(*) AS n, sum(churn_i) AS churned, round(100.0 * avg(churn_i), 2) AS churn_rate
FROM v_customer GROUP BY paperless_billing;

CREATE OR REPLACE TABLE q6_payment_contract AS
SELECT contract, payment_method, count(*) AS n, sum(churn_i) AS churned, round(100.0 * avg(churn_i), 2) AS churn_rate
FROM v_customer GROUP BY contract, payment_method;

CREATE OR REPLACE TABLE q6_payment_internet AS
SELECT internet_service, payment_method, count(*) AS n, sum(churn_i) AS churned, round(100.0 * avg(churn_i), 2) AS churn_rate
FROM v_customer GROUP BY internet_service, payment_method;

-- Q7: kombinasi kontrak x internet x metode bayar
CREATE OR REPLACE TABLE q7_segments AS
SELECT contract, internet_service, payment_method, count(*) AS n, sum(churn_i) AS churned,
       round(100.0 * avg(churn_i), 2) AS churn_rate,
       round(avg(monthly_charges), 2) AS arpu,
       round(coalesce(sum(monthly_charges) FILTER (WHERE churn_i = 1), 0), 2) AS lost_mrr
FROM v_customer GROUP BY contract, internet_service, payment_method;

-- Q8: demografi
CREATE OR REPLACE TABLE q8_demographics AS
SELECT 'gender' AS factor, gender AS level, count(*) AS n, sum(churn_i) AS churned, round(100.0 * avg(churn_i), 2) AS churn_rate FROM v_customer GROUP BY gender
UNION ALL
SELECT 'senior_citizen', CASE senior_citizen WHEN 1 THEN 'Senior' ELSE 'Non-senior' END, count(*), sum(churn_i), round(100.0 * avg(churn_i), 2) FROM v_customer GROUP BY senior_citizen
UNION ALL
SELECT 'partner', partner, count(*), sum(churn_i), round(100.0 * avg(churn_i), 2) FROM v_customer GROUP BY partner
UNION ALL
SELECT 'dependents', dependents, count(*), sum(churn_i), round(100.0 * avg(churn_i), 2) FROM v_customer GROUP BY dependents;

-- Q8b: senior dengan kontrak dikendalikan (apakah pengaruh senior hanya ikut kontrak?)
CREATE OR REPLACE TABLE q8_senior_contract AS
SELECT contract, CASE senior_citizen WHEN 1 THEN 'Senior' ELSE 'Non-senior' END AS senior_group,
       count(*) AS n, sum(churn_i) AS churned, round(100.0 * avg(churn_i), 2) AS churn_rate
FROM v_customer GROUP BY contract, senior_citizen;
