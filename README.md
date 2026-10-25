[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 2: Customer Churn Driver Analysis (Telco)

**Status: Selesai (versi 1).** Rancangan dan laporan ada di [`design-and-report/index.html`](design-and-report/index.html), tab *Design Project* dan *Report Project* (laporan versi 2, 7 bagian evaluasi). Dashboard interaktif: [`project/results/3-presentation/dashboard.html`](project/results/3-presentation/dashboard.html).

**Tujuan:** membangun analisis dan dashboard yang menunjukkan segmen pelanggan (tipe kontrak, lama berlangganan, layanan, dan metode bayar) dengan churn dan revenue hilang terbesar, sehingga program retensi dapat difokuskan pada segmen yang paling berharga untuk dipertahankan.

| | |
|---|---|
| Kategori | Telekomunikasi (Tech / Energi) |
| Tingkat | Mudah |
| Data | Dataset sampel IBM Telco Customer Churn (7.043 pelanggan, 21 kolom) |
| Tools | DuckDB + SQL, Python (pandas, scipy), dashboard HTML statis, Streamlit + Plotly (opsional). Excel tidak dibuat (cek silang memakai pandas) |

## 1. Problem

**Pertanyaan utama:** Segmen pelanggan mana (tipe kontrak, tenure, layanan, metode bayar) yang paling banyak churn, dan berapa revenue bulanan yang hilang dari segmen tersebut?

Rancangan memecahnya menjadi 14 pertanyaan (9 Utama, 4 Pendukung, 1 Tambahan) dalam 5 tema: churn, segmen, revenue, dampak, serta validitas data. Semuanya terjawab (lihat tab *Report Project*).

## 2. Data

- Sumber: Telco Customer Churn (IBM sample data). Rancangan merujuk [Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) (diakses 23 Oktober 2026); file yang dipakai diunduh 25 Oktober 2026 dari salinan IBM di GitHub (cara dan catatan lisensi: `project/data/README.md`).
- Ukuran (terverifikasi): 7.043 pelanggan, 21 kolom, `customerID` unik, tanpa kolom tanggal (waktu dibaca dari tenure 0-72 bulan). Churn 1.869 pelanggan (26,54%).
- Cleaning: hanya `TotalCharges` kosong (spasi) pada 11 baris tenure 0, diubah menjadi NULL; baris tidak dibuang, tidak ada imputasi. "No internet service" dipetakan ke `Not available`. Rincian: `project/docs/cleaning_decisions.md`.
- Empat tabel (`customers`, `accounts`, `services`, `dim_tenure_bucket`) plus tampilan `v_customer`. File mentah tidak di-commit.

## 3. Analysis

Pipeline: SQL (DuckDB) membuat tabel dan query, pandas menghitung ulang secara independen sebagai crosscheck (19 dari 19 PASS), skrip validasi menguji kewajaran, dashboard menghitung ulang KPI sesuai filter dari kubus agregat.

Temuan utama (angka dari `project/results/`):
- **Kontrak:** churn 26,5% keseluruhan. Month-to-month 42,7%, One year 11,3%, Two year 2,8%. Kontrak bulanan = 55% pelanggan tetapi 88,6% dari semua churn.
- **Tenure:** churn 52,9% pada 0-6 bulan, turun menjadi 9,5% pada 49-72 bulan. 12 bulan pertama = 55,5% dari semua churn.
- **Layanan:** Fiber optic 41,9% vs DSL 19,0%; dengan Online Security 14,6% vs tanpa 41,8% (pelanggan internet). Setelah kontrak dan tenure disamakan, selisih Online Security dan Tech Support mengecil sekitar separuh.
- **Metode bayar:** Electronic check 45,3% vs 15,2-19,1% metode lain (setelah strata: +14,8 poin dari +28,2).
- **Demografi:** gender tidak berpengaruh (p=0,47); senior 41,7% vs 23,6%; selisih partner hilang setelah kontrak dan tenure disamakan.
- **Revenue hilang:** lost MRR US$ 139.131 per bulan (30,5% dari MRR). Segmen **Month-to-month · Fiber optic · Electronic check** (n=1.307, churn 60,4%) menyumbang 49,1%; lima segmen teratas 78,5% dengan 36,9% pelanggan.

Hipotesis pada rancangan (H1-H5):

| ID | Hipotesis | Bukti | Kesimpulan |
|---|---|---|---|
| H1 | Kontrak Month-to-month jauh lebih sering churn daripada kontrak tahunan | M2M 42,7% vs One year 11,3% vs Two year 2,8% | Didukung |
| H2 | Churn paling tinggi di 12 bulan pertama | 0-6 bulan 52,9%, 7-12 bulan 35,9%, 13-24 bulan 28,7% | Didukung |
| H3 | Fiber optic dan Electronic check lebih sering churn | Fiber vs DSL: mentah +22,93 poin, setelah strata +19,64; Electronic check vs lain: mentah +28,23, setelah strata +14,84 | Didukung (selisih mengecil setelah kontrol kontrak dan tenure, tetapi tetap ada) |
| H4 | Pelanggan dengan Online Security dan Tech Support lebih jarang churn | Online Security: mentah -27,16 poin, setelah strata -12,85; Tech Support: mentah -26,47, setelah strata -10,56 | Didukung (selisih mengecil setelah kontrol, tetapi tetap negatif) |
| H5 | Sebagian besar revenue hilang berasal dari sedikit segmen | 5 dari 34 segmen menyumbang 78,5% lost MRR dengan 36,9% pelanggan; segmen teratas saja 49,1% | Didukung |

Kesimpulan "Didukung" berarti pola ada di data ini dan lolos uji kewajaran, bukan bukti sebab-akibat.

Seberapa kuat polanya setelah faktor lain disamakan (selisih churn di dalam strata kontrak × kelompok tenure, dirata-rata berbobot):

| Perbandingan | Selisih mentah (poin) | Setelah strata (poin) |
|---|---|---|
| Electronic check vs metode lain | +28,2 | +14,8 |
| Fiber optic vs DSL (pelanggan internet) | +22,9 | +19,6 |
| Paperless billing vs tidak | +17,2 | +12,9 |
| Punya Online Security vs tidak (pelanggan internet) | −27,2 | −12,8 |
| Punya Tech Support vs tidak (pelanggan internet) | −26,5 | −10,6 |
| Senior vs non-senior | +18,1 | +12,6 |
| Punya partner vs tidak | −13,3 | +0,4 |

Ukuran hubungan (Cramer's V, semua p < 0,001 kecuali gender): kontrak 0,41; tenure 0,36; jenis internet 0,32; metode bayar 0,30; Online Security 0,28; Tech Support 0,27. Ini asosiasi, bukan model prediksi.

File hasil:

- [Dashboard interaktif](project/results/3-presentation/dashboard.html) (satu file HTML, tanpa library luar) dan dashboard Streamlit opsional.
- `project/results/3-presentation/analysis.ipynb`: notebook Q1 sampai Q14 dengan grafik.
- `project/results/2-analysis/`: CSV hasil SQL, `crosscheck.csv`, `significance.csv`, `adjusted_gaps.csv`, `sensitivity.csv`, `hypotheses.csv`.

## 4. Recommendation

1. Fokuskan program retensi pada segmen Month-to-month · Fiber optic · Electronic check (hampir setengah revenue hilang). Usulan tindakan, belum teruji: tawaran pindah ke pembayaran otomatis dan kontrak 12 bulan.
2. Segmen 2-5 (kontrak bulanan, Fiber atau DSL, n 201-474) menyusul.
3. Garap 12 bulan pertama pelanggan kontrak bulanan.
4. Dorong Online Security dan Tech Support pada pelanggan Fiber optic, tetapi uji dulu efeknya.
5. Jangan memakai gender atau status partner sebagai dasar sasaran. Segmen n < 100 tidak direkomendasikan.
6. Uji lewat A/B test sebelum diperluas.

## 5. Impact

```
Revenue terselamatkan per tahun = (churn lama − churn baru) × pelanggan segmen × ARPU × 12
```

Semua hasil berlabel `estimated`; asumsi: ARPU = rata-rata MonthlyCharges segmen, USD, penurunan churn merata, efek program belum teruji.

| Churn turun (relatif) | Segmen 1 saja | 5 segmen teratas |
|---|---|---|
| 10% | US$ 82.546 / tahun | US$ 132.664 / tahun |
| **20% (K5, ditetapkan di muka)** | **US$ 165.092 / tahun** | **US$ 265.327 / tahun** |
| 30% | US$ 247.637 / tahun | US$ 397.991 / tahun |

Batas biaya impas (skenario 20%, segmen 1): sekitar US$ 126 per pelanggan segmen per tahun. Detail: `project/results/2-analysis/breakeven.csv`.

## Batasan

- Satu potret waktu tanpa tanggal; kurva retensi (Kaplan-Meier) hanya pendekatan dari tenure, memakai kontrak saat ini, dan ujungnya berbasis sedikit pelanggan.
- Pola bukan sebab-akibat: selisih mengecil setelah faktor lain disamakan, dan Fiber optic lebih mahal sehingga harga ikut bercampur.
- Segmen kecil mudah tampak ekstrem (n < 30 tidak dibaca, n < 100 tidak direkomendasikan).
- Angka dampak adalah skenario; efek program belum teruji.
- Dataset sampel buatan IBM; hasil menggambarkan dataset ini, bukan perusahaan tertentu.
- Lisensi dataset belum diverifikasi. File IBM sudah dibandingkan dengan file Kaggle (`WA_Fn-UseC_-Telco-Customer-Churn.csv`, 25 Oktober 2026): 7.043 baris × 21 kolom, 0 sel berbeda; hanya akhir baris berbeda (Kaggle CRLF, IBM LF), hash identik setelah CR dibuang.
- Belum dibuat: lembar cek silang Excel (diganti pandas), one-sheet, slide wawancara, publikasi dashboard Streamlit ke link publik.

## Menjalankan
Semua perintah dari folder `project/`. Skrip membaca dan menulis dengan jalur relatif.
```
cd project
pip install -r requirements.txt
# taruh telco_churn.csv di data/raw/ (lihat project/data/README.md)
python code/1-data-preparation/python/01_profile_audit.py   # profiling, audit kualitas, cleaning log
python code/1-data-preparation/python/02_build_tables.py    # churn.duckdb (SQL 01-02)
python code/2-analysis/python/03_run_queries.py             # SQL 03-06 -> results/2-analysis/*.csv
python code/2-analysis/python/04_crosscheck.py              # SQL vs pandas (harus semua PASS)
python code/2-analysis/python/05_validation.py              # signifikansi, strata, sensitivitas, hipotesis
python code/3-presentation/python/06_build_dashboard.py     # results/3-presentation/dashboard.html
python code/3-presentation/python/07_build_notebook.py
jupyter nbconvert --to notebook --execute --inplace results/3-presentation/analysis.ipynb
# opsional: streamlit run code/3-presentation/streamlit/app.py
cd ..
python design-and-report/src/build_report_v2.py              # design-and-report/index.html (angka dari CSV, diaudit otomatis)
```
Catatan: nama skrip dan folder berbeda dari usulan awal di halaman rancangan (`scripts/clean_load.py`, `dashboard/app.py`, dan seterusnya); mengikuti struktur Project 1 (kode dan hasil dipisah per tahap).

## Struktur repository
Sama dengan Project 1: halaman, kode, dan hasil dipisah. Di dalam `project/` kode dan hasil dipisah lagi per tahap (1 data-preparation, 2 analysis, 3 presentation).
```
README.md                      ringkasan project (file ini)
index.html                     pengalihan ke design-and-report/ (agar URL GitHub Pages tetap)
design-and-report/
  index.html                   halaman Design Project dan Report Project (v2)
  src/                         sumber halaman: design_base.html (rancangan), report_v2.css, build_report_v2.py
project/
  code/                        PROGRAM
    common.py                  jalur dan konstanta bersama
    1-data-preparation/        python/ (01, 02)   sql/ (01_load, 02_clean)
    2-analysis/                python/ (03, 04, 05)   sql/ (03-06)
    3-presentation/            python/ (06, 07)   html/ (template dashboard)   streamlit/ (app.py)
  results/                     HASIL ANALISIS
    1-data-preparation/        csv profiling, kualitas data, cleaning log
    2-analysis/                csv hasil query, crosscheck, validasi, skenario
    3-presentation/            dashboard.html, analysis.ipynb
  data/                        raw/ (tidak di-commit), README.md
  docs/                        definisi, kamus data, keputusan cleaning, ringkasan profiling
  requirements.txt
```
