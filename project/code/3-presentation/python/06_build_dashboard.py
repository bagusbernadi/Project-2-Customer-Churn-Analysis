"""Langkah 11: membuat results/3-presentation/dashboard.html (satu file, tanpa library luar, bisa dibuka offline).

Data yang ditanam hanya agregat (cube.csv, kurva retensi, Pareto, skenario), tanpa data per pelanggan.
Filter di dashboard menghitung ulang KPI dari kubus agregat, sehingga rumusnya sama dengan SQL.
"""
import json

import pandas as pd

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import CODE, RES_ANALYSIS, RES_PRESENT

TEMPLATE = CODE / "3-presentation" / "html" / "dashboard_template.html"


def main() -> None:
    cube = pd.read_csv(RES_ANALYSIS / "cube.csv")
    cube = cube.rename(columns={"contract": "c", "internet_service": "i", "payment_method": "p", "tenure_bucket_id": "b",
                                "tenure_bucket": "bl", "churned": "ch", "sum_monthly": "sm", "lost_mrr": "lm"})
    km_df = pd.read_csv(RES_ANALYSIS / "retention_curve.csv")
    km = {g: [[int(m), float(r)] for m, r in zip(d["month"], d["retention_pct"])] for g, d in km_df.groupby("contract")}
    order = ["Month-to-month", "One year", "Two year", "Semua"]
    km = {g: km[g] for g in order}
    pareto = pd.read_csv(RES_ANALYSIS / "pareto_lost_mrr.csv")
    scen = pd.read_csv(RES_ANALYSIS / "scenarios.csv").drop_duplicates("rank_all")
    segs = scen[["contract", "internet_service", "payment_method", "n", "churn_rate", "arpu"]].to_dict("records")
    data = {"cube": cube.to_dict("records"), "km": km, "pareto": pareto.to_dict("records"), "segs": segs}
    html = TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    RES_PRESENT.mkdir(parents=True, exist_ok=True)
    out = RES_PRESENT / "dashboard.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out.name}: {len(html) / 1024:.0f} KB, {len(cube)} sel kubus, {len(pareto)} segmen, {len(segs)} segmen skenario")


if __name__ == "__main__":
    main()
