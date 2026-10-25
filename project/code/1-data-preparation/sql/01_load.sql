-- 01_load.sql
-- Memuat CSV mentah apa adanya (semua kolom sebagai teks) ke churn_raw. Tidak ada perubahan nilai.
-- Jalur relatif terhadap folder project/ (skrip 02_build_tables.py berpindah ke folder itu lebih dulu).

CREATE OR REPLACE TABLE churn_raw AS
SELECT * FROM read_csv('data/raw/telco_churn.csv', header = true, all_varchar = true);
