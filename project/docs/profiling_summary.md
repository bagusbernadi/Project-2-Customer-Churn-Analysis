# Ringkasan profiling data mentah

Dihasilkan oleh `project/code/1-data-preparation/python/01_profile_audit.py`. Semua angka dihitung dari `project/data/raw/telco_churn.csv`.

- Baris: **7,043** | Kolom: **21** | customerID unik: **7,043**
- Pelanggan churn: **1,869** (26.54%)
- Nilai kosong yang tersembunyi sebagai teks: TotalCharges **11** baris (semuanya tenure 0)

## Hasil pemeriksaan

| Pemeriksaan | Status | Rincian |
|---|---|---|
| Jumlah baris | PASS | 7,043 baris, 21 kolom |
| customerID unik | PASS | 0 duplikat |
| TotalCharges terisi | CATATAN | 11 baris kosong (teks spasi); semuanya tenure = ['0'] |
| Churn hanya Yes/No | PASS | ['No', 'Yes'] |
| SeniorCitizen hanya 0/1 | PASS | ['0', '1'] |
| tenure 0-72 | PASS | min 0, max 72; baris tenure 0 = 11 |
| MonthlyCharges > 0 | PASS | min 18.25, max 118.75 |
| 'No internet service' konsisten dengan InternetService = No | PASS | 1526 pelanggan tanpa internet; ketidakcocokan 0 |
| 'No phone service' konsisten dengan PhoneService = No | PASS | 682 pelanggan tanpa telepon; ketidakcocokan 0 |
| TotalCharges masuk akal terhadap tenure x MonthlyCharges (rasio 0,5-1,5) | CATATAN | rasio median 1.000; 2 baris di luar rentang (tarif bisa berubah selama berlangganan) |

## Profil kolom

| Kolom | Jenis | Kosong | Unik | Min | Maks | Nilai teratas |
|---|---|---|---|---|---|---|
| customerID | text | 0 | 7043 |  |  | 7590-VHVEG (1); 5575-GNVDE (1); 3668-QPYBK (1); 7795-CFOCW (1); 9237-HQITU (1) |
| gender | text | 0 | 2 |  |  | Male (3555); Female (3488) |
| SeniorCitizen | numeric | 0 | 2 | 0 | 1 |  |
| Partner | text | 0 | 2 |  |  | No (3641); Yes (3402) |
| Dependents | text | 0 | 2 |  |  | No (4933); Yes (2110) |
| tenure | numeric | 0 | 73 | 0 | 72 |  |
| PhoneService | text | 0 | 2 |  |  | Yes (6361); No (682) |
| MultipleLines | text | 0 | 3 |  |  | No (3390); Yes (2971); No phone service (682) |
| InternetService | text | 0 | 3 |  |  | Fiber optic (3096); DSL (2421); No (1526) |
| OnlineSecurity | text | 0 | 3 |  |  | No (3498); Yes (2019); No internet service (1526) |
| OnlineBackup | text | 0 | 3 |  |  | No (3088); Yes (2429); No internet service (1526) |
| DeviceProtection | text | 0 | 3 |  |  | No (3095); Yes (2422); No internet service (1526) |
| TechSupport | text | 0 | 3 |  |  | No (3473); Yes (2044); No internet service (1526) |
| StreamingTV | text | 0 | 3 |  |  | No (2810); Yes (2707); No internet service (1526) |
| StreamingMovies | text | 0 | 3 |  |  | No (2785); Yes (2732); No internet service (1526) |
| Contract | text | 0 | 3 |  |  | Month-to-month (3875); Two year (1695); One year (1473) |
| PaperlessBilling | text | 0 | 2 |  |  | Yes (4171); No (2872) |
| PaymentMethod | text | 0 | 4 |  |  | Electronic check (2365); Mailed check (1612); Bank transfer (automatic) (1544); Credit card (automatic) (1522) |
| MonthlyCharges | numeric | 0 | 1585 | 18.25 | 118.75 |  |
| TotalCharges | numeric | 11 | 6531 | 18.8 | 8684.8 |  |
| Churn | text | 0 | 2 |  |  | No (5174); Yes (1869) |
