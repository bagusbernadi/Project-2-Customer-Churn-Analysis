"""Langkah 3-4: profiling data mentah, audit kualitas (Q13), dan log cleaning.

Membaca data/raw/telco_churn.csv TANPA mengubahnya. Keluaran:
  results/1-data-preparation/profile_columns.csv   ringkasan tiap kolom
  results/1-data-preparation/data_quality.csv      hasil pemeriksaan (PASS / CATATAN)
  results/1-data-preparation/cleaning_log.csv      setiap nilai yang diubah, beserta alasan
  docs/profiling_summary.md
"""
import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
import pandas as pd

from common import ADDON_SERVICES, DOCS_DIR, RAW_CSV, RES_PREP, require_raw


def main() -> None:
    require_raw()
    RES_PREP.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RAW_CSV, dtype=str, keep_default_na=False)
    n = len(df)

    # --- profil kolom ---
    rows = []
    for c in df.columns:
        s = df[c]
        blank = int((s.str.strip() == "").sum())
        num = pd.to_numeric(s.replace("", pd.NA), errors="coerce")
        is_num = num.notna().sum() >= 0.9 * (n - blank)
        rows.append({
            "column": c,
            "kind": "numeric" if is_num else "text",
            "n_blank": blank,
            "n_unique": int(s.nunique()),
            "min": num.min() if is_num else "",
            "max": num.max() if is_num else "",
            "top_values": "" if is_num else "; ".join(f"{k} ({v})" for k, v in s.value_counts().head(5).items()),
        })
    prof = pd.DataFrame(rows)
    prof.to_csv(RES_PREP / "profile_columns.csv", index=False)

    # --- pemeriksaan kualitas ---
    checks = []

    def chk(name, ok, detail):
        checks.append({"check": name, "status": "PASS" if ok else "CATATAN", "detail": detail})

    chk("Jumlah baris", True, f"{n:,} baris, {df.shape[1]} kolom")
    dup = int(df["customerID"].duplicated().sum())
    chk("customerID unik", dup == 0, f"{dup} duplikat")
    blank_tc = df["TotalCharges"].str.strip() == ""
    chk("TotalCharges terisi", not blank_tc.any(),
        f"{int(blank_tc.sum())} baris kosong (teks spasi); semuanya tenure = {sorted(df.loc[blank_tc,'tenure'].unique())}")
    chk("Churn hanya Yes/No", set(df["Churn"]) <= {"Yes", "No"}, str(sorted(set(df["Churn"]))))
    chk("SeniorCitizen hanya 0/1", set(df["SeniorCitizen"]) <= {"0", "1"}, str(sorted(set(df["SeniorCitizen"]))))
    ten = pd.to_numeric(df["tenure"])
    chk("tenure 0-72", ten.between(0, 72).all(), f"min {ten.min()}, max {ten.max()}; baris tenure 0 = {int((ten==0).sum())}")
    mc = pd.to_numeric(df["MonthlyCharges"])
    chk("MonthlyCharges > 0", (mc > 0).all(), f"min {mc.min()}, max {mc.max()}")

    no_int = df["InternetService"] == "No"
    bad_int = int((df.loc[no_int, ADDON_SERVICES] != "No internet service").sum().sum())
    bad_int2 = int((df.loc[~no_int, ADDON_SERVICES] == "No internet service").sum().sum())
    chk("'No internet service' konsisten dengan InternetService = No", bad_int == 0 and bad_int2 == 0,
        f"{int(no_int.sum())} pelanggan tanpa internet; ketidakcocokan {bad_int + bad_int2}")
    no_ph = df["PhoneService"] == "No"
    bad_ph = int(((df["MultipleLines"] == "No phone service") != no_ph).sum())
    chk("'No phone service' konsisten dengan PhoneService = No", bad_ph == 0,
        f"{int(no_ph.sum())} pelanggan tanpa telepon; ketidakcocokan {bad_ph}")

    tc = pd.to_numeric(df["TotalCharges"].str.strip(), errors="coerce")
    ok = ~tc.isna() & (ten > 0)
    ratio = (tc[ok] / (ten[ok] * mc[ok]))
    off = int(((ratio < 0.5) | (ratio > 1.5)).sum())
    chk("TotalCharges masuk akal terhadap tenure x MonthlyCharges (rasio 0,5-1,5)", off == 0,
        f"rasio median {ratio.median():.3f}; {off} baris di luar rentang (tarif bisa berubah selama berlangganan)")
    qc = pd.DataFrame(checks)
    qc.to_csv(RES_PREP / "data_quality.csv", index=False)

    # --- log cleaning: setiap nilai yang berubah ---
    log = []
    for _, r in df[blank_tc].iterrows():
        log.append({"customerID": r.customerID, "column": "TotalCharges", "original": repr(r.TotalCharges),
                    "new": "NULL", "tenure": r.tenure, "churn": r.Churn,
                    "reason": "Teks kosong diubah menjadi NULL; baris tidak dibuang (pelanggan baru, tenure 0, belum ada tagihan)"})
    pd.DataFrame(log).to_csv(RES_PREP / "cleaning_log.csv", index=False)

    # --- ringkasan markdown ---
    churn = (df["Churn"] == "Yes").sum()
    md = [
        "# Ringkasan profiling data mentah", "",
        "Dihasilkan oleh `project/code/1-data-preparation/python/01_profile_audit.py`. Semua angka dihitung dari `project/data/raw/telco_churn.csv`.", "",
        f"- Baris: **{n:,}** | Kolom: **{df.shape[1]}** | customerID unik: **{df['customerID'].nunique():,}**",
        f"- Pelanggan churn: **{churn:,}** ({churn/n*100:.2f}%)",
        f"- Nilai kosong yang tersembunyi sebagai teks: TotalCharges **{int(blank_tc.sum())}** baris (semuanya tenure 0)", "",
        "## Hasil pemeriksaan", "", "| Pemeriksaan | Status | Rincian |", "|---|---|---|",
    ]
    md += [f"| {r.check} | {r.status} | {r.detail} |" for r in qc.itertuples()]
    md += ["", "## Profil kolom", "", "| Kolom | Jenis | Kosong | Unik | Min | Maks | Nilai teratas |", "|---|---|---|---|---|---|---|"]
    md += [f"| {r.column} | {r.kind} | {r.n_blank} | {r.n_unique} | {r.min} | {r.max} | {r.top_values} |" for r in prof.itertuples()]
    (DOCS_DIR).mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "profiling_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(qc.to_string(index=False))
    print(f"\ncleaning_log: {len(log)} baris diubah")


if __name__ == "__main__":
    main()
