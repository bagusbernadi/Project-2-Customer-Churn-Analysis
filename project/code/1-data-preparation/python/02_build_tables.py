"""Langkah 5: membuat churn.duckdb berisi tabel customers, accounts, services, dim_tenure_bucket, churn_raw
dan tampilan v_customer. Berhenti jika pemeriksaan integritas gagal."""
import os

import duckdb

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import DB_PATH, ROOT, SQL_PREP, require_raw


def main() -> None:
    require_raw()
    os.chdir(ROOT)  # jalur di file SQL relatif terhadap root project
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = duckdb.connect(str(DB_PATH))
    for f in ("01_load.sql", "02_clean.sql"):
        con.execute((SQL_PREP / f).read_text(encoding="utf-8"))

    q = lambda sql: con.execute(sql).fetchone()[0]
    raw_n = q("SELECT count(*) FROM churn_raw")
    assert q("SELECT count(*) FROM customers") == raw_n, "customers != raw"
    assert q("SELECT count(*) FROM accounts") == raw_n, "accounts != raw"
    assert q("SELECT count(*) FROM services") == raw_n * 9, "services harus 9 baris per pelanggan"
    assert q("SELECT count(*) FROM v_customer") == raw_n, "v_customer menggandakan/menghilangkan baris (join tenure bucket?)"
    assert q("SELECT count(DISTINCT customer_id) FROM accounts") == raw_n, "customer_id tidak unik"
    assert q("SELECT count(*) FROM accounts WHERE total_charges IS NULL") == 11, "jumlah TotalCharges NULL tidak sesuai log cleaning"
    assert q("SELECT count(*) FROM churn_raw WHERE Churn = 'Yes'") == q("SELECT sum(churn_i) FROM accounts"), "jumlah churn berubah"
    for t in ("churn_raw", "customers", "accounts", "services", "dim_tenure_bucket", "v_customer"):
        print(f"{t:18s} {q(f'SELECT count(*) FROM {t}'):>8,} baris")
    con.close()


if __name__ == "__main__":
    main()
