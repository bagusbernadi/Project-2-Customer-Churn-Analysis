# Definisi

## Churn
Pelanggan dengan `Churn = Yes` pada data (berhenti berlangganan). Semua persentase memakai seluruh 7.043 pelanggan sebagai penyebut (tidak ada nilai kosong pada kolom Churn). Persentase memakai poin persen, 2 desimal di tabel dan dibulatkan di tampilan.

## KPI (`code/2-analysis/sql/06_kpi.sql`, dihitung ulang di dashboard sesuai filter)
| ID | Rumus |
|---|---|
| K1 Churn rate | pelanggan churn / total pelanggan x 100 |
| K2 Retention rate | 100 - churn rate |
| K3 Lost MRR | jumlah MonthlyCharges pelanggan churn (US$ per bulan) |
| K4 ARPU | rata-rata MonthlyCharges (US$ per bulan). Untuk segmen: rata-rata di segmen itu |
| K5 Revenue terselamatkan per tahun (**estimated**) | (churn lama - churn baru) x pelanggan segmen x ARPU segmen x 12 |

Skenario K5 ditetapkan di muka: churn 5 segmen teratas turun 20% relatif (mis. 60,4% menjadi 48,3%). Skenario 10% dan 30% hanya pembanding, tidak dipilih dari hasil terbaik.

## Kelompok tenure (`dim_tenure_bucket`)
0-6, 7-12, 13-24, 25-48, 49-72 bulan. Tenure 0 (11 pelanggan baru, belum ditagih) masuk kelompok 0-6.

## Segmen
Kombinasi tipe kontrak x jenis internet x metode bayar (36 kombinasi, 34 di antaranya punya pelanggan churn). Aturan baca:
- n < 30: persentase tidak ditampilkan (`MIN_N`).
- n < 100: tidak dijadikan rekomendasi utama (`MIN_N_RECO`).
- Selalu tampilkan n di samping churn rate.

## Jumlah layanan tambahan (bundling)
Jumlah dari 6 layanan yang berstatus `Yes`: OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies. Hanya dihitung untuk pelanggan internet (pelanggan tanpa internet tidak bisa memilikinya).

## Status layanan
`No internet service` dan `No phone service` dipetakan ke `Not available` pada tabel `services`. Pelanggan tanpa internet tidak dibandingkan sebagai "tidak memakai layanan" pada Q4/Q5 karena memang tidak punya pilihan. Detail di `cleaning_decisions.md`.

## Kurva retensi (Q3)
Estimator Kaplan-Meier. Waktu = `tenure`, kejadian = churn, pelanggan yang tidak churn dianggap tersensor di tenure-nya. Pelanggan tenure 0 tidak ikut. Ini pendekatan, bukan kurva kohort sebenarnya: tidak ada tanggal bergabung/berhenti, kontrak adalah kontrak saat ini (bisa berubah selama berlangganan), dan pelanggan yang sudah lama pergi tidak ada di data.

## Perbandingan setelah faktor lain disamakan (validasi)
Standardisasi langsung: selisih churn (terpapar - tidak terpapar) dihitung di tiap strata kontrak x kelompok tenure (hanya strata dengan >= 10 pelanggan di kedua kelompok), lalu dirata-rata berbobot jumlah pelanggan strata. Ini bukan model sebab-akibat, hanya pemeriksaan apakah pola bertahan setelah kontrak dan tenure disamakan.

## Interval kepercayaan
Interval Wilson 95% untuk proporsi churn. Chi-square memakai tabel kontingensi tanpa koreksi kontinuitas; Cramer's V = akar(chi2 / (n x (min(baris, kolom) - 1))).
