# Data

Dataset: **Telco Customer Churn** (IBM sample data), 7.043 baris, 21 kolom, 1 file CSV.

## Sumber
- Rancangan menyebut Kaggle: https://www.kaggle.com/datasets/blastchar/telco-customer-churn (Versi 1, diakses 23 Oktober 2026).
- File yang dipakai di repo ini diunduh pada 25 Oktober 2026 dari salinan IBM di GitHub (tanpa login): https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv (970.457 byte).
- Isi file diperiksa: 7.043 baris, 21 kolom, kolom sama dengan versi Kaggle. Dibandingkan dengan file Kaggle (`WA_Fn-UseC_-Telco-Customer-Churn.csv`, 977.501 byte, dari arsip yang diunduh pengguna, 25 Oktober 2026): kolom, urutan baris, dan seluruh 147.903 sel **identik**. Hanya akhir baris yang berbeda (Kaggle CRLF, salinan IBM LF), sehingga ukuran file berbeda 7.044 byte; hash MD5 sama setelah karakter CR dibuang.

## Cara memakai
1. Simpan file sebagai `project/data/raw/telco_churn.csv` (folder `raw/` ada di `.gitignore`, file mentah tidak di-commit).
2. Jalankan pipeline (lihat README utama).

## Yang perlu dicek sebelum publikasi
- **Lisensi dan ketentuan sitasi** dataset (halaman Kaggle dan repo IBM) belum diverifikasi dalam project ini. Cek dulu dan cantumkan atribusi sesuai ketentuan.
- Dataset adalah **data sampel buatan IBM** untuk latihan, bukan data pelanggan nyata. Temuan menggambarkan dataset ini, bukan perusahaan telekomunikasi tertentu.
