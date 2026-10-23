[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 2: Customer Churn Driver Analysis (Telco)

**Status: Design (rancangan).** Halaman rancangan ada di [`index.html`](index.html). Analisis, dashboard, dan angka hasil belum dikerjakan, sehingga bagian Analysis, Recommendation, dan Impact di bawah masih kosong.

**Tujuan:** membangun analisis dan dashboard yang menunjukkan segmen pelanggan (tipe kontrak, lama berlangganan, layanan, dan metode bayar) dengan churn dan revenue hilang terbesar, sehingga program retensi dapat difokuskan pada segmen yang paling berharga untuk dipertahankan.

| | |
|---|---|
| Kategori | Telekomunikasi (Tech / Energi) |
| Tingkat | Mudah |
| Data | Dataset publik IBM Telco Customer Churn (Kaggle) |
| Tools | DuckDB + SQL, Python (pandas), Streamlit + Plotly. Excel opsional untuk cek silang |

## 1. Problem

**Pertanyaan utama:** Segmen pelanggan mana (tipe kontrak, tenure, layanan, metode bayar) yang paling banyak churn, dan berapa revenue bulanan yang hilang dari segmen tersebut?

Rancangan memecahnya menjadi 14 pertanyaan (9 Utama, 4 Pendukung, 1 Tambahan) dalam 5 tema: churn, segmen, revenue, dampak, serta validitas data. Daftar lengkap ada di bagian 2 halaman rancangan.

## 2. Data

- Sumber: dataset Telco Customer Churn dari IBM, tersedia di Kaggle.
- Ukuran (perkiraan, **belum diverifikasi**): ±7.043 pelanggan, 21 kolom, 1 file CSV. Tidak ada kolom tanggal; pola waktu dibaca dari tenure (±0–72 bulan). Angka ini dicek saat data diunduh.
- Lisensi dan sitasi: dicek di halaman dataset sebelum project dipublikasikan.
- Data mentah tidak di-commit ke repository. Cara mengunduhnya akan ditulis di `data/README.md`.
- Rencana tabel: `customers`, `accounts`, `services`, `dim_tenure_bucket`.
- Catatan awal cleaning: TotalCharges tersimpan sebagai teks dengan beberapa baris kosong, SeniorCitizen memakai 0/1, dan nilai "No internet service" perlu diputuskan. Setiap keputusan dicatat di log cleaning.

## 3. Analysis

Belum dikerjakan. Rencana langkah (12 langkah, tahap A sampai D) ada di bagian 6 halaman rancangan. Semua angka nanti dihitung dari data dengan SQL dan dicek silang dengan Excel atau pandas.

Hipotesis yang akan diuji (belum terbukti):
1. Kontrak Month-to-month jauh lebih sering churn daripada kontrak tahunan.
2. Churn paling tinggi di 12 bulan pertama berlangganan.
3. Pelanggan Fiber optic dan Electronic check lebih sering churn.
4. Pelanggan dengan Online Security dan Tech Support lebih jarang churn.
5. Sebagian besar revenue yang hilang berasal dari sedikit segmen.

## 4. Recommendation

Belum dikerjakan. Output yang direncanakan: daftar segmen sasaran program retensi, diurutkan menurut churn rate dan revenue hilang, dengan batas minimal jumlah pelanggan per segmen.

## 5. Impact

Belum dikerjakan. Rumus yang akan dipakai (semua hasil diberi label `estimated`):

```
Revenue terselamatkan per tahun = (churn lama − churn baru) × pelanggan segmen × ARPU × 12
```

Asumsi awal: ARPU = monthly charges, mata uang USD sesuai dataset.

## Batasan yang sudah diketahui

- Data adalah satu potret waktu, sehingga kurva retensi hanya pendekatan dari tenure.
- Pola belum tentu penyebab. Metode bayar bisa saja hanya menyertai tipe kontrak.
- Segmen dengan sedikit pelanggan mudah tampak ekstrem; jumlah pelanggan selalu ditampilkan.
- Dataset buatan IBM, polanya bisa lebih rapi daripada data perusahaan sebenarnya.

## Struktur repository

```
index.html   Halaman rancangan project (bisa dibuka di browser atau lewat GitHub Pages)
README.md    Dokumen ini
```

Folder `docs/`, `data/`, `scripts/`, `sql/`, `notebooks/`, `dashboard/`, dan `outputs/` ditambahkan saat pengerjaan dimulai.
