"""Langkah 6-9: menjalankan code/2-analysis/sql/03-06 dan mengekspor tabel hasil ke results/2-analysis/*.csv."""
import os

import duckdb

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import DB_PATH, RES_ANALYSIS, ROOT, SQL_ANALYSIS

# tabel di DuckDB -> (nama file CSV, urutan baris)
EXPORTS = {
    "q1_overall":              ("overall.csv",                   "n"),
    "q1_contract":             ("churn_by_contract.csv",         "contract"),
    "q2_tenure":               ("churn_by_tenure.csv",           "tenure_bucket_id"),
    "q2_tenure_contract":      ("churn_by_tenure_contract.csv",  "contract, tenure_bucket_id"),
    "q3_retention":            ("retention_curve.csv",           "contract, month"),
    "q4_service":              ("churn_by_service.csv",          "service_name, status"),
    "q4_internet":             ("churn_by_internet.csv",         "internet_service"),
    "q4_service_by_internet":  ("churn_by_service_internet.csv", "internet_service, service_name, status"),
    "q5_addons":               ("churn_by_addons.csv",           "n_addons"),
    "q5_addons_contract":      ("churn_by_addons_contract.csv",  "contract, addon_group"),
    "q6_payment":              ("churn_by_payment.csv",          "payment_method"),
    "q6_paperless":            ("churn_by_paperless.csv",        "paperless_billing"),
    "q6_payment_contract":     ("churn_payment_x_contract.csv",  "contract, payment_method"),
    "q6_payment_internet":     ("churn_payment_x_internet.csv",  "internet_service, payment_method"),
    "q7_segments":             ("segments.csv",                  "lost_mrr DESC, contract, internet_service, payment_method"),
    "q8_demographics":         ("churn_by_demographics.csv",     "factor, level"),
    "q8_senior_contract":      ("churn_senior_x_contract.csv",   "contract, senior_group"),
    "q9_pareto":               ("pareto_lost_mrr.csv",           "rank"),
    "q9_lost_by_factor":       ("lost_mrr_by_factor.csv",        "factor, lost_mrr DESC"),
    "q10_charges":             ("monthly_charges_churn.csv",     "churn"),
    "q10_charges_contract":    ("monthly_charges_churn_contract.csv", "contract, churn"),
    "q11_scenarios":           ("scenarios.csv",                 "rank_all, cut_pct"),
    "q12_breakeven":           ("breakeven.csv",                 "rank_all, cut_pct"),
    "kpi_overall":             ("kpi_overall.csv",               "kpi_id"),
}

CUBE_SQL = """
SELECT contract, internet_service, payment_method, tenure_bucket_id, tenure_bucket,
       count(*) AS n, sum(churn_i) AS churned,
       round(sum(monthly_charges), 2) AS sum_monthly,
       round(coalesce(sum(monthly_charges) FILTER (WHERE churn_i = 1), 0), 2) AS lost_mrr
FROM v_customer GROUP BY ALL ORDER BY contract, internet_service, payment_method, tenure_bucket_id
"""


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit("churn.duckdb belum ada. Jalankan project/code/1-data-preparation/python/02_build_tables.py dulu.")
    os.chdir(ROOT)
    RES_ANALYSIS.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    for f in sorted(SQL_ANALYSIS.glob("0[3-6]_*.sql")):
        con.execute(f.read_text(encoding="utf-8"))
        print("dijalankan:", f.name)
    for table, (fname, order) in EXPORTS.items():
        path = (RES_ANALYSIS / fname).as_posix()
        con.execute(f"COPY (SELECT * FROM {table} ORDER BY {order}) TO '{path}' (HEADER, DELIMITER ',')")
        n = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"  {fname:36s} {n:>6,} baris")
    # kubus agregat untuk dashboard (tanpa data per pelanggan)
    cube = (RES_ANALYSIS / "cube.csv").as_posix()
    con.execute(f"COPY ({CUBE_SQL}) TO '{cube}' (HEADER, DELIMITER ',')")
    print(f"  {'cube.csv':36s} {con.execute(f'SELECT count(*) FROM ({CUBE_SQL})').fetchone()[0]:>6,} baris")
    con.close()


if __name__ == "__main__":
    main()
