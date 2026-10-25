"""Langkah 10: uji kewajaran temuan (validasi) sebelum menulis rekomendasi.

Menjawab: apakah perbedaan churn antar segmen cukup besar dibanding kebetulan (chi-square, Cramer's V, interval Wilson 95%),
apakah pola bertahan setelah faktor lain disamakan (standardisasi langsung pada strata kontrak x tenure bucket),
apakah hasil berubah jika baris bermasalah dikeluarkan (Q13), dan bagaimana lima hipotesis di rancangan terjawab.
Tidak ada model prediksi. Pola adalah asosiasi, bukan sebab-akibat.

Keluaran di results/2-analysis/: significance.csv, segment_ci.csv, adjusted_gaps.csv, sensitivity.csv, hypotheses.csv
"""
import numpy as np
import pandas as pd
from scipy import stats

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import ADDON_SERVICES, MIN_N_RECO, RAW_CSV, RES_ANALYSIS, TENURE_BUCKETS, require_raw


def load() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip(), errors="coerce")
    df["churn_i"] = (df["Churn"] == "Yes").astype(int)
    edges = [(lo, hi, lab) for _, lab, lo, hi in TENURE_BUCKETS]
    df["bucket"] = df["tenure"].map(lambda t: next(l for lo, hi, l in edges if lo <= t <= hi))
    df["n_addons"] = (df[ADDON_SERVICES] == "Yes").sum(axis=1)
    df["addon_group"] = pd.cut(df["n_addons"], [-1, 0, 2, 4, 6], labels=["0", "1-2", "3-4", "5-6"]).astype(str)
    df["Senior"] = np.where(df.SeniorCitizen == 1, "Senior", "Non-senior")
    return df


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    w = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - w) / den * 100, (c + w) / den * 100)


def chi_row(df, col, label, sub=None):
    d = df if sub is None else df[sub]
    tab = pd.crosstab(d[col], d["churn_i"])
    chi2, p, dof, _ = stats.chi2_contingency(tab, correction=False)
    n = tab.values.sum()
    v = np.sqrt(chi2 / (n * (min(tab.shape) - 1)))
    rates = d.groupby(col)["churn_i"].mean() * 100
    return {"factor": label, "n": int(n), "levels": tab.shape[0], "chi2": round(chi2, 1), "dof": dof,
            "p_value": float(f"{p:.3g}"), "cramers_v": round(v, 3),
            "rate_min": round(rates.min(), 2), "rate_max": round(rates.max(), 2), "gap_pts": round(rates.max() - rates.min(), 2)}


def std_gap(df, exposed_mask, strata=("Contract", "bucket"), min_n=10):
    """Selisih churn (terpapar - tidak terpapar) dalam tiap strata, dirata-rata berbobot jumlah pelanggan strata."""
    d = df.assign(exp=exposed_mask)
    gaps, weights = [], []
    for _, g in d.groupby(list(strata)):
        a, b = g[g.exp], g[~g.exp]
        if len(a) >= min_n and len(b) >= min_n:
            gaps.append((a.churn_i.mean() - b.churn_i.mean()) * 100)
            weights.append(len(g))
    raw = (d[d.exp].churn_i.mean() - d[~d.exp].churn_i.mean()) * 100
    return raw, float(np.average(gaps, weights=weights)), len(gaps)


def main() -> None:
    require_raw()
    df = load()
    net = df[df.InternetService != "No"]

    # 1. Signifikansi dan kekuatan hubungan
    sig = [chi_row(df, "Contract", "Tipe kontrak"), chi_row(df, "bucket", "Kelompok tenure"),
           chi_row(df, "InternetService", "Jenis internet"), chi_row(df, "PaymentMethod", "Metode bayar"),
           chi_row(df, "PaperlessBilling", "Paperless billing"), chi_row(net, "addon_group", "Jumlah layanan tambahan (pelanggan internet)"),
           chi_row(net, "OnlineSecurity", "Online Security (pelanggan internet)"), chi_row(net, "TechSupport", "Tech Support (pelanggan internet)"),
           chi_row(df, "Senior", "Senior citizen"), chi_row(df, "Partner", "Partner"), chi_row(df, "Dependents", "Dependents"),
           chi_row(df, "gender", "Gender")]
    sig = pd.DataFrame(sig).sort_values("cramers_v", ascending=False)
    sig.to_csv(RES_ANALYSIS / "significance.csv", index=False)

    # 2. Interval kepercayaan Wilson 95% untuk kontrak dan segmen teratas
    seg = (df.groupby(["Contract", "InternetService", "PaymentMethod"])
             .agg(n=("churn_i", "size"), churned=("churn_i", "sum"), lost_mrr=("MonthlyCharges", lambda s: s[df.loc[s.index, "churn_i"] == 1].sum()))
             .reset_index().sort_values("lost_mrr", ascending=False).head(10))
    rows = []
    for c, g in df.groupby("Contract"):
        lo, hi = wilson(g.churn_i.sum(), len(g))
        rows.append({"segment": f"Kontrak: {c}", "n": len(g), "churned": int(g.churn_i.sum()), "churn_rate": round(g.churn_i.mean() * 100, 2), "ci95_low": round(lo, 2), "ci95_high": round(hi, 2), "n_ok_reco": len(g) >= MIN_N_RECO})
    for r in seg.itertuples():
        lo, hi = wilson(r.churned, r.n)
        rows.append({"segment": f"{r.Contract} | {r.InternetService} | {r.PaymentMethod}", "n": r.n, "churned": int(r.churned),
                     "churn_rate": round(r.churned / r.n * 100, 2), "ci95_low": round(lo, 2), "ci95_high": round(hi, 2), "n_ok_reco": r.n >= MIN_N_RECO})
    pd.DataFrame(rows).to_csv(RES_ANALYSIS / "segment_ci.csv", index=False)

    # 3. Selisih mentah vs setelah faktor lain disamakan (strata kontrak x tenure bucket)
    tests = [("Electronic check vs metode lain", df.PaymentMethod == "Electronic check", df),
             ("Fiber optic vs DSL (pelanggan internet)", net.InternetService == "Fiber optic", net),
             ("Paperless billing vs tidak", df.PaperlessBilling == "Yes", df),
             ("Punya Online Security vs tidak (pelanggan internet)", net.OnlineSecurity == "Yes", net),
             ("Punya Tech Support vs tidak (pelanggan internet)", net.TechSupport == "Yes", net),
             ("Senior vs non-senior", df.Senior == "Senior", df),
             ("Punya partner vs tidak", df.Partner == "Yes", df)]
    adj = []
    for label, mask, d in tests:
        raw, std, k = std_gap(d, mask.values if hasattr(mask, "values") else mask)
        adj.append({"perbandingan": label, "selisih_mentah_pts": round(raw, 2), "selisih_setelah_strata_pts": round(std, 2),
                    "strata_dipakai": k, "bagian_selisih_yang_tersisa_pct": round(100 * std / raw, 1) if raw else np.nan})
    adj = pd.DataFrame(adj)
    adj.to_csv(RES_ANALYSIS / "adjusted_gaps.csv", index=False)

    # 4. Sensitivitas (Q13): hasil berubah jika baris bermasalah dikeluarkan / definisi diubah?
    base = df
    alt = df[df.tenure > 0]                         # keluarkan 11 baris TotalCharges kosong (tenure 0)
    alt2 = df[df["TotalCharges"].notna() & ((df.TotalCharges / (df.tenure.replace(0, np.nan) * df.MonthlyCharges)).between(0.5, 1.5) | (df.tenure == 0))]  # keluarkan baris TotalCharges janggal

    def metrics(d):
        m2m = d[d.Contract == "Month-to-month"].churn_i.mean() * 100
        two = d[d.Contract == "Two year"].churn_i.mean() * 100
        fib = d[d.InternetService == "Fiber optic"].churn_i.mean() * 100
        ech = d[d.PaymentMethod == "Electronic check"].churn_i.mean() * 100
        t1 = d[d.bucket == "0-6 bulan"].churn_i.mean() * 100
        lost = d.loc[d.churn_i == 1, "MonthlyCharges"].sum()
        top = (d[d.churn_i == 1].groupby(["Contract", "InternetService", "PaymentMethod"])["MonthlyCharges"].sum().sort_values(ascending=False))
        return {"churn_rate": d.churn_i.mean() * 100, "churn_M2M": m2m, "churn_TwoYear": two, "churn_Fiber": fib,
                "churn_ElectronicCheck": ech, "churn_tenure_0_6": t1, "lost_mrr": lost,
                "top1_share_lost_mrr": top.iloc[0] / lost * 100, "top1_segment": " | ".join(top.index[0])}

    mb, ma, mc = metrics(base), metrics(alt), metrics(alt2)
    sens = []
    for k in mb:
        if k == "top1_segment":
            sens.append({"metric": k, "dasar": mb[k], "tanpa_tenure_0": ma[k], "tanpa_totalcharges_janggal": mc[k], "diff_pct_tanpa_tenure_0": "", "flag_review": mb[k] != ma[k] or mb[k] != mc[k]})
            continue
        rel = (ma[k] - mb[k]) / mb[k] * 100
        sens.append({"metric": k, "dasar": round(mb[k], 3), "tanpa_tenure_0": round(ma[k], 3), "tanpa_totalcharges_janggal": round(mc[k], 3),
                     "diff_pct_tanpa_tenure_0": round(rel, 2), "flag_review": abs(rel) > 2 if k != "lost_mrr" else False})
    pd.DataFrame(sens).to_csv(RES_ANALYSIS / "sensitivity.csv", index=False)

    # 5. Hipotesis dari rancangan
    pc = pd.read_csv(RES_ANALYSIS / "pareto_lost_mrr.csv")
    byc = df.groupby("Contract").churn_i.mean() * 100
    byb = df.groupby("bucket").churn_i.mean() * 100
    ig = {r["perbandingan"]: r for r in adj.to_dict("records")}
    top5 = pc.head(5).share_lost_mrr.sum()
    top5_n = pc.head(5).n.sum() / len(df) * 100
    h = [
        ("H1", "Kontrak Month-to-month jauh lebih sering churn daripada kontrak tahunan",
         f"M2M {byc['Month-to-month']:.1f}% vs One year {byc['One year']:.1f}% vs Two year {byc['Two year']:.1f}%",
         "Didukung" if byc["Month-to-month"] > 3 * byc["One year"] else "Tidak didukung"),
        ("H2", "Churn paling tinggi di 12 bulan pertama",
         f"0-6 bulan {byb['0-6 bulan']:.1f}%, 7-12 bulan {byb['7-12 bulan']:.1f}%, 13-24 bulan {byb['13-24 bulan']:.1f}%",
         "Didukung" if byb.idxmax() == "0-6 bulan" and byb["7-12 bulan"] > byb["13-24 bulan"] else "Sebagian"),
        ("H3", "Fiber optic dan Electronic check lebih sering churn",
         f"Fiber vs DSL: mentah +{ig['Fiber optic vs DSL (pelanggan internet)']['selisih_mentah_pts']} poin, setelah strata +{ig['Fiber optic vs DSL (pelanggan internet)']['selisih_setelah_strata_pts']}; "
         f"Electronic check vs lain: mentah +{ig['Electronic check vs metode lain']['selisih_mentah_pts']}, setelah strata +{ig['Electronic check vs metode lain']['selisih_setelah_strata_pts']}",
         "Didukung (selisih mengecil setelah kontrol kontrak dan tenure, tetapi tetap ada)"
         if min(ig['Fiber optic vs DSL (pelanggan internet)']['selisih_setelah_strata_pts'], ig['Electronic check vs metode lain']['selisih_setelah_strata_pts']) > 3 else "Sebagian"),
        ("H4", "Pelanggan dengan Online Security dan Tech Support lebih jarang churn",
         f"Online Security: mentah {ig['Punya Online Security vs tidak (pelanggan internet)']['selisih_mentah_pts']} poin, setelah strata {ig['Punya Online Security vs tidak (pelanggan internet)']['selisih_setelah_strata_pts']}; "
         f"Tech Support: mentah {ig['Punya Tech Support vs tidak (pelanggan internet)']['selisih_mentah_pts']}, setelah strata {ig['Punya Tech Support vs tidak (pelanggan internet)']['selisih_setelah_strata_pts']}",
         "Didukung (selisih mengecil setelah kontrol, tetapi tetap negatif)"
         if max(ig['Punya Online Security vs tidak (pelanggan internet)']['selisih_setelah_strata_pts'], ig['Punya Tech Support vs tidak (pelanggan internet)']['selisih_setelah_strata_pts']) < -3 else "Sebagian"),
        ("H5", "Sebagian besar revenue hilang berasal dari sedikit segmen",
         f"5 dari {len(pc)} segmen menyumbang {top5:.1f}% lost MRR dengan {top5_n:.1f}% pelanggan; segmen teratas saja {pc.iloc[0].share_lost_mrr:.1f}%",
         "Didukung" if top5 >= 70 else "Sebagian"),
    ]
    pd.DataFrame(h, columns=["id", "hipotesis", "bukti", "kesimpulan"]).to_csv(RES_ANALYSIS / "hypotheses.csv", index=False)

    print(sig.to_string(index=False)); print()
    print(adj.to_string(index=False)); print()
    print(pd.DataFrame(sens).to_string(index=False)); print()
    for r in h:
        print(r[0], r[3], "|", r[2])


if __name__ == "__main__":
    main()
