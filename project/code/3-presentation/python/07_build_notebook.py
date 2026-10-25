"""Langkah 11: membuat results/3-presentation/analysis.ipynb dari results/2-analysis/*.csv.

Jalankan skrip ini, lalu eksekusi notebook:
    jupyter nbconvert --to notebook --execute --inplace results/3-presentation/analysis.ipynb
Notebook hanya membaca CSV hasil SQL (tidak menghitung ulang), jadi angkanya sama dengan dashboard dan README.
"""
import nbformat as nbf

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import RES_PRESENT

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

cells = [
    md("# Analisis churn pelanggan Telco (IBM sample data)\n\n"
       "Pertanyaan utama: **segmen pelanggan mana (kontrak, tenure, layanan, metode bayar) yang paling banyak churn, dan berapa revenue bulanan yang hilang?**\n\n"
       "Analisis deskriptif tanpa model prediksi. Semua angka dibaca dari `results/2-analysis/*.csv` (hasil SQL DuckDB yang sudah dicek silang dengan pandas). "
       "Pola adalah asosiasi, bukan sebab-akibat. Angka dampak berlabel *estimated*."),
    code("""from pathlib import Path
import pandas as pd, matplotlib.pyplot as plt
pd.options.display.float_format = '{:,.2f}'.format
plt.rcParams.update({'figure.dpi': 110, 'axes.spines.top': False, 'axes.spines.right': False})
R = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'results' / '2-analysis').exists()) / 'results' / '2-analysis'
rd = lambda f: pd.read_csv(R / f)
MIN_N = 30
def barh(df, label, val='churn_rate', n='n', title='', xmax=None):
    d = df.copy(); d = d[d[n] >= MIN_N]
    fig, ax = plt.subplots(figsize=(7, 0.45 * len(d) + 1))
    ax.barh(d[label].astype(str), d[val], color='#1A73E8'); ax.invert_yaxis()
    for i, (v, k) in enumerate(zip(d[val], d[n])): ax.text(v + 0.5, i, f'{v:.1f}% (n={k:,})', va='center', fontsize=8)
    ax.set_xlabel('Churn rate (%)'); ax.set_title(title); ax.set_xlim(0, xmax or d[val].max() * 1.35); plt.tight_layout(); plt.show()"""),
    md("## KPI"), code("rd('kpi_overall.csv')"),
    md("## Q1-Q2 Churn per kontrak dan per tenure"),
    code("barh(rd('churn_by_contract.csv'), 'contract', title='Churn rate per tipe kontrak')\nbarh(rd('churn_by_tenure.csv'), 'tenure_bucket', title='Churn rate per kelompok tenure')\nrd('churn_by_contract.csv')"),
    md("## Q3 Kurva retensi (Kaplan-Meier, pendekatan dari tenure)\nBukan kurva kohort sebenarnya; ujung kurva berbasis sedikit pelanggan."),
    code("km = rd('retention_curve.csv')\nfig, ax = plt.subplots(figsize=(7, 3.6))\nfor g, d in km.groupby('contract'): ax.plot(d.month, d.retention_pct, label=g, lw=2.2 if g != 'Semua' else 1.5, ls='--' if g == 'Semua' else '-')\nax.set_xlabel('Tenure (bulan)'); ax.set_ylabel('Retensi (%)'); ax.legend(frameon=False); plt.tight_layout(); plt.show()"),
    md("## Q4-Q5 Layanan dan bundling (pelanggan internet saja untuk layanan tambahan)"),
    code("s = rd('churn_by_service_internet.csv'); s = s[s.status.isin(['Yes', 'No'])]\np = s.pivot_table(index=['internet_service', 'service_name'], columns='status', values='churn_rate').reset_index()\np['selisih_pts'] = p['Yes'] - p['No']; p.sort_values(['internet_service', 'selisih_pts'])"),
    code("barh(rd('churn_by_addons.csv'), 'n_addons', title='Churn rate per jumlah layanan tambahan (pelanggan internet)')"),
    md("## Q6-Q7 Metode bayar, paperless, dan kombinasi segmen"),
    code("barh(rd('churn_by_payment.csv'), 'payment_method', title='Churn rate per metode bayar')\nrd('churn_payment_x_contract.csv').pivot(index='payment_method', columns='contract', values='churn_rate')"),
    code("seg = rd('segments.csv'); seg['ok_reco'] = seg.n >= 100\nseg.head(10)"),
    md("## Q8 Demografi"), code("rd('churn_by_demographics.csv')"),
    md("Setelah kontrak dikendalikan, perbedaan senior vs non-senior tetap ada tetapi mengecil:"), code("rd('churn_senior_x_contract.csv')"),
    md("## Q9 Lost MRR (Pareto)"),
    code("pa = rd('pareto_lost_mrr.csv').head(10); pa['segmen'] = pa.contract + ' | ' + pa.internet_service + ' | ' + pa.payment_method\nfig, ax = plt.subplots(figsize=(8, 4)); ax.barh(pa.segmen, pa.lost_mrr, color='#D93025'); ax.invert_yaxis()\nfor i, (v, c) in enumerate(zip(pa.lost_mrr, pa.cum_share_lost_mrr)): ax.text(v, i, f' ${v:,.0f} (kum. {c:.0f}%)', va='center', fontsize=8)\nax.set_xlabel('Lost MRR (US$ per bulan)'); ax.set_xlim(0, pa.lost_mrr.max() * 1.45); plt.tight_layout(); plt.show()"),
    md("## Q10 Tagihan bulanan: churn vs bertahan"), code("rd('monthly_charges_churn.csv')"),
    md("## Q11-Q12 Skenario program retensi (estimated)\nRevenue terselamatkan per tahun = (churn lama - churn baru) x pelanggan segmen x ARPU x 12. Batas biaya impas = revenue terselamatkan / pelanggan segmen."),
    code("sc = rd('breakeven.csv'); sc['segmen'] = sc.contract + ' | ' + sc.internet_service + ' | ' + sc.payment_method\nsc.pivot(index='segmen', columns='cut_pct', values='saved_revenue_year')"),
    code("sc.pivot(index='segmen', columns='cut_pct', values='breakeven_cost_per_customer_year')"),
    md("## Validasi\nSignifikansi dan kekuatan hubungan (Cramer's V), selisih mentah vs setelah kontrak dan tenure disamakan, sensitivitas, dan status hipotesis."),
    code("rd('significance.csv')"), code("rd('adjusted_gaps.csv')"), code("rd('sensitivity.csv')"), code("pd.set_option('display.max_colwidth', None); rd('hypotheses.csv')"),
    code("pd.set_option('display.max_colwidth', 80); rd('crosscheck.csv')[['check', 'status', 'max_abs_diff']]"),
]


def main() -> None:
    nb = nbf.v4.new_notebook()
    nb.cells = cells
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    RES_PRESENT.mkdir(parents=True, exist_ok=True)
    out = RES_PRESENT / "analysis.ipynb"
    nbf.write(nb, out)
    print("ditulis:", out)


if __name__ == "__main__":
    main()
