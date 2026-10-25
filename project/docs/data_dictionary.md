# Kamus data

Sumber: `data/raw/telco_churn.csv` (7.043 baris, 21 kolom, 1 baris per pelanggan, kunci `customerID`). Dimuat apa adanya ke `churn_raw`, lalu dipecah oleh `code/1-data-preparation/sql/02_clean.sql`.

## Hubungan tabel
```
customers (1) ---- (1) accounts (1) ---- (9) services        dim_tenure_bucket (referensi, 5 baris)
          \_________ customer_id _________/                  v_customer = tampilan lebar untuk query
```

## customers (7.043 baris)
| Kolom | Arti | Nilai |
|---|---|---|
| customer_id | Kunci pelanggan | teks unik |
| gender | Jenis kelamin | Female / Male |
| senior_citizen | Warga senior | 0 / 1 |
| partner | Punya pasangan | Yes / No |
| dependents | Punya tanggungan | Yes / No |

## accounts (7.043 baris)
| Kolom | Arti | Nilai |
|---|---|---|
| customer_id | Kunci | |
| tenure_months | Lama berlangganan (bulan) | 0-72 |
| contract | Tipe kontrak | Month-to-month / One year / Two year |
| paperless_billing | Tagihan tanpa kertas | Yes / No |
| payment_method | Metode bayar | Electronic check / Mailed check / Bank transfer (automatic) / Credit card (automatic) |
| monthly_charges | Tagihan bulanan (US$) | 18,25-118,75 |
| total_charges | Total tagihan sejak berlangganan (US$) | angka; **NULL pada 11 baris** (tenure 0) |
| churn | Berhenti berlangganan | Yes / No |
| churn_i | `churn` sebagai angka | 1 / 0 |

## services (63.387 baris = 7.043 x 9)
| Kolom | Arti | Nilai |
|---|---|---|
| customer_id | Kunci | |
| service_name | Nama layanan | PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies |
| status | Status layanan | Yes / No / **Not available** (tidak punya internet atau telepon). Khusus `InternetService`: DSL / Fiber optic / No |

## dim_tenure_bucket (5 baris)
`bucket_id`, `label`, `min_month`, `max_month`: 0-6, 7-12, 13-24, 25-48, 49-72 bulan.

## v_customer (tampilan, 7.043 baris)
Gabungan accounts + customers + `tenure_bucket` + `internet_service` + `n_addons` (jumlah layanan tambahan berstatus Yes) + `payment_mode` (Otomatis / Manual).

## File hasil
Daftar CSV di `results/2-analysis/` dan arti kolomnya mengikuti nama kolom di atas. Tambahan: `n` jumlah pelanggan, `churned` jumlah churn, `churn_rate` persen, `arpu` rata-rata MonthlyCharges, `lost_mrr` jumlah MonthlyCharges pelanggan churn, `cube.csv` agregat untuk dashboard (tanpa data per pelanggan).
