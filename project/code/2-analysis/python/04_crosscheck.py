"""Langkah 7 (Q14): cek silang SQL vs pandas.

Semua angka dihitung ULANG dari CSV mentah memakai pandas (tanpa DuckDB), lalu dibandingkan dengan
file results/2-analysis/*.csv yang dihasilkan SQL. Jumlah baris dan hitungan (n, churned) harus sama persis.
Nilai pecahan boleh berbeda paling besar setengah digit pembulatan yang dipakai SQL (0,005).
Catatan: rancangan menyebut cek silang dengan Excel PivotTable (opsional). Di sini dipakai pandas; lembar Excel tidak dibuat.

Keluaran: results/2-analysis/crosscheck.csv. Skrip berhenti dengan kode 1 jika ada yang tidak cocok.
"""
import sys

import numpy as np
import pandas as pd

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import ADDON_SERVICES, RAW_CSV, RES_ANALYSIS, TENURE_BUCKETS, require_raw

RESULTS = []
TOL = 0.0051


def load() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip(), errors="coerce")
    df["churn_i"] = (df["Churn"] == "Yes").astype(int)
    edges = [(lo, hi, lab) for _, lab, lo, hi in TENURE_BUCKETS]
    df["bucket"] = df["tenure"].map(lambda t: next(l for lo, hi, l in edges if lo <= t <= hi))
    df["n_addons"] = (df[ADDON_SERVICES] == "Yes").sum(axis=1)
    return df


def agg(df, by):
    g = df.groupby(by, dropna=False)
    out = g.agg(n=("churn_i", "size"), churned=("churn_i", "sum"), rate=("churn_i", "mean"),
                sum_m=("MonthlyCharges", "sum"), arpu=("MonthlyCharges", "mean")).reset_index()
    out["rate"] = out["rate"] * 100
    lost = df[df.churn_i == 1].groupby(by)["MonthlyCharges"].sum().rename("lost").reset_index()
    out = out.merge(lost, on=by, how="left").fillna({"lost": 0.0})
    return out


def compare(name, sql_file, expected, keys, spec):
    """spec: kolom_sql -> kolom_pandas. Kolom 'n'/'churned' wajib sama persis."""
    got = pd.read_csv(RES_ANALYSIS / sql_file)
    status, max_diff, note = "PASS", 0.0, ""
    if len(got) != len(expected):
        status, note = "FAIL", f"jumlah baris SQL {len(got)} != pandas {len(expected)}"
    else:
        m = got.merge(expected, on=keys, how="outer", suffixes=("_sql", "_pd"), indicator=True)
        if (m["_merge"] != "both").any():
            status, note = "FAIL", "kunci baris tidak sama"
        else:
            for sc, pc in spec.items():
                a, b = m[sc + "_sql" if sc + "_sql" in m else sc], m[pc + "_pd" if pc + "_pd" in m else pc]
                d = float((a.astype(float) - b.astype(float)).abs().max())
                max_diff = max(max_diff, d)
                exact = sc in ("n", "churned", "at_risk", "churned_at_t")
                if (exact and d > 0) or d > TOL * (1 if sc != "lost_mrr" else 1):
                    status, note = "FAIL", f"kolom {sc}: selisih maks {d}"
    RESULTS.append({"check": name, "file": sql_file, "n_rows": len(got), "max_abs_diff": round(max_diff, 6), "status": status, "note": note})


def main() -> None:
    require_raw()
    df = load()
    v = df.assign(contract=df["Contract"], internet=df["InternetService"], payment=df["PaymentMethod"])

    a = agg(v, ["contract"]).rename(columns={"contract": "contract"})
    compare("Q1 churn per kontrak", "churn_by_contract.csv", a, ["contract"], {"n": "n", "churned": "churned", "churn_rate": "rate"})

    a = agg(v, ["bucket"]).rename(columns={"bucket": "tenure_bucket"})
    compare("Q2 churn per tenure bucket", "churn_by_tenure.csv", a, ["tenure_bucket"], {"n": "n", "churned": "churned", "churn_rate": "rate"})

    a = agg(v, ["contract", "bucket"]).rename(columns={"bucket": "tenure_bucket"})
    compare("Q2 tenure x kontrak", "churn_by_tenure_contract.csv", a, ["contract", "tenure_bucket"], {"n": "n", "churned": "churned", "churn_rate": "rate"})

    a = agg(v, ["internet"]).rename(columns={"internet": "internet_service"})
    a["internet_service"] = a["internet_service"].fillna("No")
    compare("Q4 churn per jenis internet", "churn_by_internet.csv", a, ["internet_service"], {"n": "n", "churned": "churned", "churn_rate": "rate", "arpu": "arpu"})

    rows = []
    for s in ADDON_SERVICES + ["PhoneService", "MultipleLines"]:
        t = agg(v, [s]).rename(columns={s: "status"})
        t["status"] = t["status"].replace({"No internet service": "Not available", "No phone service": "Not available"})
        t = t.groupby("status", as_index=False).agg(n=("n", "sum"), churned=("churned", "sum"))
        t["service_name"] = s
        t["rate"] = t["churned"] / t["n"] * 100
        rows.append(t)
    compare("Q4 churn per layanan", "churn_by_service.csv", pd.concat(rows), ["service_name", "status"], {"n": "n", "churned": "churned", "churn_rate": "rate"})

    a = agg(v[v.internet != "No"], ["n_addons"])
    compare("Q5 churn per jumlah layanan tambahan", "churn_by_addons.csv", a, ["n_addons"], {"n": "n", "churned": "churned", "churn_rate": "rate"})

    a = agg(v, ["payment"]).rename(columns={"payment": "payment_method"})
    compare("Q6 churn per metode bayar", "churn_by_payment.csv", a, ["payment_method"], {"n": "n", "churned": "churned", "churn_rate": "rate"})

    a = agg(v, ["PaperlessBilling"]).rename(columns={"PaperlessBilling": "paperless_billing"})
    compare("Q6 churn per paperless", "churn_by_paperless.csv", a, ["paperless_billing"], {"n": "n", "churned": "churned", "churn_rate": "rate"})

    a = agg(v, ["contract", "payment"]).rename(columns={"payment": "payment_method"})
    compare("Q6 kontrak x metode bayar", "churn_payment_x_contract.csv", a, ["contract", "payment_method"], {"n": "n", "churned": "churned", "churn_rate": "rate"})

    seg = agg(v, ["contract", "internet", "payment"]).rename(columns={"internet": "internet_service", "payment": "payment_method", "lost": "lost_mrr"})
    compare("Q7 segmen kontrak x internet x bayar", "segments.csv", seg, ["contract", "internet_service", "payment_method"],
            {"n": "n", "churned": "churned", "churn_rate": "rate", "arpu": "arpu", "lost_mrr": "lost_mrr"})

    dem = []
    for col, name in (("gender", "gender"), ("Partner", "partner"), ("Dependents", "dependents")):
        t = agg(v, [col]).rename(columns={col: "level"}); t["factor"] = name; dem.append(t)
    t = agg(v.assign(sc=np.where(v.SeniorCitizen == 1, "Senior", "Non-senior")), ["sc"]).rename(columns={"sc": "level"}); t["factor"] = "senior_citizen"; dem.append(t)
    compare("Q8 demografi", "churn_by_demographics.csv", pd.concat(dem), ["factor", "level"], {"n": "n", "churned": "churned", "churn_rate": "rate"})

    # Q9 Pareto: total lost MRR dan cum share di rank 5
    par = seg[seg.churned > 0].sort_values(["lost_mrr", "contract", "internet_service", "payment_method"], ascending=[False, True, True, True]).reset_index(drop=True)
    par["rank"] = par.index + 1
    par["share_lost_mrr"] = par["lost_mrr"] / par["lost_mrr"].sum() * 100
    par["cum_share_lost_mrr"] = par["share_lost_mrr"].cumsum()
    compare("Q9 Pareto lost MRR", "pareto_lost_mrr.csv", par, ["rank"],
            {"n": "n", "lost_mrr": "lost_mrr", "share_lost_mrr": "share_lost_mrr", "cum_share_lost_mrr": "cum_share_lost_mrr"})

    # Q10
    q = v.groupby("Churn")["MonthlyCharges"].agg(n="size", mean_charge="mean", median_charge="median", p25_charge=lambda s: s.quantile(.25), p75_charge=lambda s: s.quantile(.75)).reset_index().rename(columns={"Churn": "churn"})
    compare("Q10 tagihan churn vs bertahan", "monthly_charges_churn.csv", q, ["churn"],
            {"n": "n", "mean_charge": "mean_charge", "median_charge": "median_charge", "p25_charge": "p25_charge", "p75_charge": "p75_charge"})

    # Q3 Kaplan-Meier dihitung manual per kelompok
    km = []
    for grp, d in [(c, x) for c, x in v[v.tenure > 0].groupby("contract")] + [("Semua", v[v.tenure > 0])]:
        times = np.sort(d["tenure"].unique())
        s = 1.0
        for t in times:
            at = int((d.tenure >= t).sum()); ev = int(((d.tenure == t) & (d.churn_i == 1)).sum())
            s *= 1 - ev / at
            km.append({"contract": grp, "month": t, "at_risk": at, "churned_at_t": ev, "retention_pct": 100 * s})
    compare("Q3 kurva retensi Kaplan-Meier", "retention_curve.csv", pd.DataFrame(km), ["contract", "month"],
            {"at_risk": "at_risk", "churned_at_t": "churned_at_t", "retention_pct": "retention_pct"})

    # KPI
    kp = pd.read_csv(RES_ANALYSIS / "kpi_overall.csv").set_index("kpi_id")["value"]
    top = par[par.n >= 100].head(5)
    k5 = ((top.rate * 0.20) / 100 * top.n * top.arpu * 12).sum()
    exp = {"K1": df.churn_i.mean() * 100, "K2": 100 - df.churn_i.mean() * 100, "K3": df.loc[df.churn_i == 1, "MonthlyCharges"].sum(),
           "K4": df.MonthlyCharges.mean(), "K5": k5}
    for k, e in exp.items():
        tol = {"K3": 0.01, "K5": 60.0}.get(k, TOL)     # K5: SQL memakai churn rate dan ARPU yang sudah dibulatkan 2 desimal per segmen (selisih puluhan dolar dari 265 ribu)
        d = abs(float(kp[k]) - e)
        RESULTS.append({"check": f"KPI {k}", "file": "kpi_overall.csv", "n_rows": 1, "max_abs_diff": round(d, 6),
                        "status": "PASS" if d <= tol else "FAIL", "note": "" if d <= tol else f"SQL {kp[k]} vs pandas {e:.4f}"})

    out = pd.DataFrame(RESULTS)
    out.to_csv(RES_ANALYSIS / "crosscheck.csv", index=False)
    print(out.to_string(index=False))
    fails = (out.status != "PASS").sum()
    print(f"\n{len(out) - fails}/{len(out)} PASS")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
