-- 02_clean.sql
-- Memecah tabel lebar menjadi 4 tabel yang terhubung lewat customer_id (lihat project/docs/data_dictionary.md).
-- Satu-satunya nilai yang diubah: TotalCharges berisi spasi pada 11 baris (tenure 0) -> NULL.
-- Setiap perubahan dicatat di results/1-data-preparation/cleaning_log.csv. Tidak ada imputasi dan tidak ada baris dibuang.

CREATE OR REPLACE TABLE dim_tenure_bucket AS
SELECT * FROM (VALUES
    (1, '0-6 bulan',   0,  6),
    (2, '7-12 bulan',  7, 12),
    (3, '13-24 bulan', 13, 24),
    (4, '25-48 bulan', 25, 48),
    (5, '49-72 bulan', 49, 72)
) AS t(bucket_id, label, min_month, max_month);

CREATE OR REPLACE TABLE customers AS
SELECT
    customerID                       AS customer_id,
    gender,
    CAST(SeniorCitizen AS INTEGER)   AS senior_citizen,
    Partner                          AS partner,
    Dependents                       AS dependents
FROM churn_raw;

CREATE OR REPLACE TABLE accounts AS
SELECT
    customerID                              AS customer_id,
    CAST(tenure AS INTEGER)                 AS tenure_months,
    Contract                                AS contract,
    PaperlessBilling                        AS paperless_billing,
    PaymentMethod                           AS payment_method,
    CAST(MonthlyCharges AS DOUBLE)          AS monthly_charges,
    TRY_CAST(trim(TotalCharges) AS DOUBLE)  AS total_charges,   -- spasi -> NULL
    Churn                                   AS churn,
    CASE Churn WHEN 'Yes' THEN 1 ELSE 0 END AS churn_i
FROM churn_raw;

-- satu baris per pelanggan per layanan (format panjang).
-- InternetService tetap DSL / Fiber optic / No; layanan lain: 'No internet service' dan 'No phone service' -> 'Not available'.
CREATE OR REPLACE TABLE services AS
SELECT customerID AS customer_id, service_name,
       CASE
            WHEN service_name = 'InternetService' THEN service_value
            WHEN service_value IN ('No internet service', 'No phone service') THEN 'Not available'
            ELSE service_value END AS status
FROM churn_raw
UNPIVOT (service_value FOR service_name IN
    (PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup,
     DeviceProtection, TechSupport, StreamingTV, StreamingMovies));

-- Tampilan lebar untuk query analisis: satu baris per pelanggan, dengan kolom turunan.
CREATE OR REPLACE VIEW v_customer AS
SELECT
    a.customer_id, a.tenure_months, a.contract, a.paperless_billing, a.payment_method,
    a.monthly_charges, a.total_charges, a.churn, a.churn_i,
    b.label AS tenure_bucket, b.bucket_id AS tenure_bucket_id,
    c.gender, c.senior_citizen, c.partner, c.dependents,
    i.status AS internet_service,
    coalesce(s.n_addons, 0) AS n_addons,
    CASE a.payment_method
         WHEN 'Bank transfer (automatic)' THEN 'Otomatis'
         WHEN 'Credit card (automatic)'   THEN 'Otomatis'
         ELSE 'Manual' END AS payment_mode
FROM accounts a
JOIN customers c USING (customer_id)
JOIN dim_tenure_bucket b ON a.tenure_months BETWEEN b.min_month AND b.max_month
JOIN services i ON i.customer_id = a.customer_id AND i.service_name = 'InternetService'
LEFT JOIN (
    SELECT customer_id, count(*) AS n_addons
    FROM services
    WHERE service_name IN ('OnlineSecurity','OnlineBackup','DeviceProtection','TechSupport','StreamingTV','StreamingMovies')
      AND status = 'Yes'
    GROUP BY customer_id
) s ON s.customer_id = a.customer_id;
