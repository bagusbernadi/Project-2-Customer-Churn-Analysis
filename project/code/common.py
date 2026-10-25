"""Pengaturan bersama untuk semua skrip. Semua jalur relatif terhadap folder project/."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # folder project/
RAW_CSV = ROOT / "data" / "raw" / "telco_churn.csv"
DB_PATH = ROOT / "churn.duckdb"
CODE = ROOT / "code"
SQL_PREP = CODE / "1-data-preparation" / "sql"
SQL_ANALYSIS = CODE / "2-analysis" / "sql"
RES_PREP = ROOT / "results" / "1-data-preparation"
RES_ANALYSIS = ROOT / "results" / "2-analysis"
RES_PRESENT = ROOT / "results" / "3-presentation"
DOCS_DIR = ROOT / "docs"

MIN_N = 30            # di bawah ini rasio/persentase tidak ditampilkan
MIN_N_RECO = 100      # segmen di bawah ini tidak dijadikan rekomendasi utama
SCENARIOS = (0.10, 0.20, 0.30)   # penurunan churn relatif untuk Q11
TOP_SEGMENTS = 5

# kelompok tenure (bulan), sama dengan dim_tenure_bucket di SQL
TENURE_BUCKETS = [
    (1, "0-6 bulan", 0, 6),
    (2, "7-12 bulan", 7, 12),
    (3, "13-24 bulan", 13, 24),
    (4, "25-48 bulan", 25, 48),
    (5, "49-72 bulan", 49, 72),
]

ADDON_SERVICES = ["OnlineSecurity", "OnlineBackup", "DeviceProtection",
                  "TechSupport", "StreamingTV", "StreamingMovies"]
ALL_SERVICES = ["PhoneService", "MultipleLines", "InternetService"] + ADDON_SERVICES


def require_raw():
    if not RAW_CSV.exists():
        raise SystemExit(f"File tidak ditemukan: {RAW_CSV}\nUnduh dulu, lihat project/data/README.md")
