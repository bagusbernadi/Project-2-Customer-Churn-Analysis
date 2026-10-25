# Keputusan cleaning dan audit kualitas data (Q13)

Rincian pemeriksaan: `results/1-data-preparation/data_quality.csv`. Setiap nilai yang diubah: `results/1-data-preparation/cleaning_log.csv`.

## Yang diubah (1 jenis, 11 baris)
| Masalah | Keputusan | Alasan |
|---|---|---|
| `TotalCharges` berisi spasi pada 11 baris, semuanya `tenure = 0` | Diubah menjadi NULL. Baris **tidak dibuang** | Pelanggan baru yang belum ditagih. Total memang belum ada. Tidak diisi 0 agar tidak tampak sebagai pelanggan yang membayar nol. |

Kolom `TotalCharges` tidak dipakai pada KPI atau segmen (analisis memakai `MonthlyCharges`), jadi keputusan ini tidak mengubah angka utama.

## Yang diperiksa dan tidak perlu diubah
- `customerID` unik (0 duplikat); `Churn` hanya Yes/No; `SeniorCitizen` hanya 0/1 (disimpan sebagai angka, tidak diubah menjadi Yes/No).
- `tenure` 0-72 dan `MonthlyCharges` > 0 (18,25-118,75).
- Konsistensi layanan: semua 1.526 pelanggan tanpa internet berstatus `No internet service` pada 6 layanan tambahan, dan semua 682 pelanggan tanpa telepon berstatus `No phone service` pada MultipleLines (ketidakcocokan 0).
- `TotalCharges` terhadap `tenure x MonthlyCharges`: rasio median 1,000. 2 baris di luar rentang 0,5-1,5 (tarif bisa berubah selama berlangganan). Dicatat, tidak dibuang.

## Keputusan "No internet service" / "No phone service"
Dipetakan ke `Not available` pada tabel `services`. Alasan: nilai ini bukan jawaban pelanggan, melainkan akibat tidak punya layanan induk. Pada analisis layanan (Q4b, Q5) pelanggan internet dibandingkan sendiri agar "tidak punya Tech Support" tidak bercampur dengan "tidak punya internet" (churn hanya 7,4%).

## Uji sensitivitas (`results/2-analysis/sensitivity.csv`)
Mengeluarkan 11 baris tenure 0, atau 2 baris TotalCharges janggal, mengubah metrik utama paling besar sekitar 0,9% secara relatif (churn rate 26,54% menjadi 26,58-26,59%; churn kelompok 0-6 bulan 52,94% menjadi 53,33-53,41%). Lost MRR tidak berubah (pelanggan tenure 0 tidak churn). Segmen penyumbang terbesar tetap sama. Tidak ada metrik yang melewati ambang tinjau 2%.

## Tidak dilakukan
Tidak ada imputasi, tidak ada pembuangan baris, tidak ada penghapusan outlier pada MonthlyCharges (rentangnya wajar untuk tarif layanan).
