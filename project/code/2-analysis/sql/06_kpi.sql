-- 06_kpi.sql
-- 5 ukuran kunci (KPI). Rumus ada di project/docs/definitions.md.
-- K5 memakai skenario yang ditetapkan di muka: churn 5 segmen teratas turun 20% relatif (bukan hasil memilih skenario terbaik).

CREATE OR REPLACE TABLE kpi_overall AS
SELECT 'K1' AS kpi_id, 'Churn rate (%)' AS kpi, churn_rate AS value, n FROM q1_overall
UNION ALL
SELECT 'K2', 'Retention rate (%)', round(100 - churn_rate, 2), n FROM q1_overall
UNION ALL
SELECT 'K3', 'Lost MRR: tagihan bulanan pelanggan churn (US$)', lost_mrr, churned FROM q1_overall
UNION ALL
SELECT 'K4', 'ARPU: rata-rata MonthlyCharges semua pelanggan (US$)', round(mrr_total / n, 2), n FROM q1_overall
UNION ALL
SELECT 'K5', 'Revenue terselamatkan per tahun, skenario churn 5 segmen teratas -20% (US$, estimated)',
       round(sum(saved_revenue_year), 2), sum(n) FROM q11_scenarios WHERE cut_pct = 20;
