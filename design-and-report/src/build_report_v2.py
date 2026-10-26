"""Langkah 12: membuat design-and-report/index.html (Design Project + Report Project versi 2, 7 bagian evaluasi).

Pane Design disalin dari design-and-report/src/design_base.html tanpa perubahan (diverifikasi). Pane Report dibuat dari file hasil (CSV) di
project/results/: setiap angka di teks diformat lewat helper yang mencatatnya, lalu diaudit (token numerik yang tidak berasal
dari CSV, rancangan, atau daftar angka struktural membuat skrip berhenti). Klaim yang dihitung (mis. jumlah catatan) di-assert.

Keluaran: design-and-report/index.html. Jalankan dari mana saja: python design-and-report/src/build_report_v2.py
"""
import html
import re
import sys
from pathlib import Path

import pandas as pd

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2] / "project" / "code"))  # common.py
from common import RES_ANALYSIS, RES_PREP, ROOT

HERE = Path(__file__).resolve().parent            # design-and-report/src
REPO = ROOT.parent
SRC, OUT = HERE / "design_base.html", REPO / "design-and-report" / "index.html"
CSS_V2 = (HERE / "report_v2.css").read_text(encoding="utf-8")

# ------------------------------------------------------------------ pencatat angka
USED: set[str] = set()


def fmt(v, d=0):
    """Format Indonesia (titik ribuan, koma desimal) dan catat hasilnya untuk audit."""
    s = f"{abs(float(v)):,.{d}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    USED.add(s)
    return ("−" if float(v) < 0 and float(s.replace(".", "").replace(",", ".")) != 0 else "") + s


pct = lambda v, d=1: fmt(v, d) + "%"
usd = lambda v, d=0: "US$ " + fmt(v, d)
sgn = lambda v, d=1: ("+" if float(v) > 0 else "") + fmt(v, d)
e = lambda s: html.escape(str(s), quote=False)
rd1 = lambda sub, name: pd.read_csv((RES_PREP if sub == 1 else RES_ANALYSIS) / name)
rd = lambda name: rd1(2, name)

# ------------------------------------------------------------------ data
ov = rd("overall.csv").iloc[0]
kp = rd("kpi_overall.csv").set_index("kpi_id")
con = rd("churn_by_contract.csv").set_index("contract")
ten = rd("churn_by_tenure.csv").set_index("tenure_bucket")
km = rd("retention_curve.csv")
svc = rd("churn_by_service.csv")
svi = rd("churn_by_service_internet.csv")
inet = rd("churn_by_internet.csv").set_index("internet_service")
add = rd("churn_by_addons.csv").set_index("n_addons")
addc = rd("churn_by_addons_contract.csv")
pay = rd("churn_by_payment.csv").set_index("payment_method")
pap = rd("churn_by_paperless.csv").set_index("paperless_billing")
payc = rd("churn_payment_x_contract.csv")
seg = rd("segments.csv")
dem = rd("churn_by_demographics.csv")
senc = rd("churn_senior_x_contract.csv")
par = rd("pareto_lost_mrr.csv")
chg = rd("monthly_charges_churn.csv").set_index("churn")
chc = rd("monthly_charges_churn_contract.csv")
scen = rd("scenarios.csv")
be = rd("breakeven.csv")
sig = rd("significance.csv").set_index("factor")
adj = rd("adjusted_gaps.csv").set_index("perbandingan")
sens = rd("sensitivity.csv").set_index("metric")
hyp = rd("hypotheses.csv")
cc = rd("crosscheck.csv")
prof = rd1(1, "profile_columns.csv").set_index("column")
dq = rd1(1, "data_quality.csv").set_index("check")
clog = rd1(1, "cleaning_log.csv")

# ------------------------------------------------------------------ rancangan (dibaca dari index.html, bukan diketik)
src = SRC.read_text(encoding="utf-8")
a = src.index('<div class="pane" id="report"')
design_pane = src[src.index('<div class="pane" id="design"'):a]
design_text = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style).*?</\1>", "", design_pane, flags=re.S))
DESIGN_TOKENS = set(re.findall(r"\d+(?:[.,]\d+)*", html.unescape(design_text)))
QS = re.findall(r'<div class="q" data-p="([MSN])"><span class="id">(Q\d+)</span><span>(.*?)<span class="pri', design_pane)
assert len(QS) == 14, len(QS)
PRIO = {q: p for p, q, _ in QS}
QTXT = {q: t for _, q, t in QS}
n_utama, n_pend, n_tamb = (sum(1 for p in PRIO.values() if p == k) for k in "MSN")
assert (n_utama, n_pend, n_tamb) == (9, 4, 1), (n_utama, n_pend, n_tamb)
STEPS = [(i, html.unescape(t)) for i, t in re.findall(r'<div class="wb[^"]*"><span class="n">(\d+)</span><b>([^<]+)</b>', design_pane)]
assert [int(i) for i, _ in STEPS] == list(range(1, 13)), STEPS
DOCS = re.findall(r"<tr><td><b>([^<]+)</b></td><td>([^<]+)</td><td>([A-D])</td><td>(Utama|Opsional)</td></tr>", design_pane)
assert len(DOCS) == 17, len(DOCS)
OUTS = [(html.unescape(t), l) for t, l in re.findall(r'<div class="oh"><b>([^<]+)</b><span class="ob[^"]*">([^<]+)</span>', design_pane)]
assert len(OUTS) == 8, OUTS
CRIT = [html.unescape(c) for c in re.findall(r"<li>([^<]+)</li>", design_pane[design_pane.index("Project dianggap berhasil jika"):])[:5]]
assert len(CRIT) == 5, CRIT

# ------------------------------------------------------------------ komponen HTML
pill = lambda t, c="": f'<span class="pill {c}">{e(t)}</span>'.replace('class="pill "', 'class="pill"')
OK, WARN, NO = lambda t: pill(t), lambda t: pill(t, "p"), lambda t: pill(t, "d")


def table(head, rows, cls="rt"):
    h = "".join(f"<th>{c}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table class="{cls}"><tr>{h}</tr>{b}</table></div>'


def kpi(v, l, d, h):
    return f'<div class="card kpi" style="--h:var(--{h}H)"><span class="v">{v}</span><span class="l">{l}</span><span class="d">{d}</span></div>'


def bars(items, title, xmax=None, cls="b1", note="", valfmt=None):
    """items: (label, value, n, kelas_opsional). Batang horizontal SVG; n < 30 tidak digambar."""
    w, lh, lab = 640, 26, 230
    xm = xmax or max(v for _, v, _, *_ in items) * 1.25
    s = f'<svg viewBox="0 0 {w} {lh * len(items) + 8}" role="img" aria-label="{e(title)}" class="ch">'
    for i, it in enumerate(items):
        l, v, n = it[:3]
        c = it[3] if len(it) > 3 else cls
        y = i * lh + 4
        s += f'<text x="{lab - 8}" y="{y + 16}" text-anchor="end">{e(l)}</text>'
        if n < 30:
            s += f'<text x="{lab}" y="{y + 16}" class="mut">n kecil (n={fmt(n)})</text>'
            continue
        bw = max(1, (w - lab - 150) * v / xm)
        s += f'<rect x="{lab}" y="{y + 2}" width="{bw:.1f}" height="18" rx="4" class="{c}"/>'
        s += f'<text x="{lab + bw + 6:.1f}" y="{y + 16}">{(valfmt or pct)(v)} (n={fmt(n)})</text>'
    return f'<div class="figw rc sm"><h4>{e(title)}</h4>{s}</svg>{f"<p class=note>{note}</p>" if note else ""}</div>'


def lines(title):
    W, H, L, B = 640, 300, 44, 34
    x = lambda m: L + (W - L - 10) * m / 72
    y = lambda v: 12 + (H - 12 - B) * (1 - v / 100)
    s = f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}" class="ch">'
    for v in (0, 25, 50, 75, 100):
        s += f'<line class="gl" x1="{L}" x2="{W - 10}" y1="{y(v):.1f}" y2="{y(v):.1f}"/><text x="{L - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v}%</text>'
    for m in (0, 12, 24, 36, 48, 60, 72):
        s += f'<text x="{x(m):.1f}" y="{H - 14}" text-anchor="middle">{m}</text>'
    s += f'<text x="{(W + L) / 2}" y="{H - 1}" text-anchor="middle">Tenure (bulan)</text>'
    cls = {"Month-to-month": "l1", "One year": "l2", "Two year": "l3", "Semua": "l4"}
    for i, (g, c) in enumerate(cls.items()):
        d = km[km.contract == g]
        pts = [(0, 100)] + list(zip(d.month, d.retention_pct))
        s += f'<polyline fill="none" class="{c}" points="{" ".join(f"{x(m):.1f},{y(v):.1f}" for m, v in pts)}"/>'
        s += f'<g transform="translate({L + 10 + i * 140},12)"><line x1="0" x2="18" y1="0" y2="0" class="{c}"/><text x="23" y="4">{g}</text></g>'
    return f'<div class="figw rc sm"><h4>{e(title)}</h4>{s}</svg></div>'


def qa(q, answer, warn=False, status=None):
    st = status or ("Terjawab, catatan" if warn else "Terjawab")
    lab = {"M": "Utama", "S": "Pendukung", "N": "Tambahan"}[PRIO[q]]
    return (f'<div class="qa{" w" if warn else ""}" id="{q.lower()}"><span class="qn">{q}</span><div><div class="qt">{QTXT[q]}</div>'
            f'<div class="qm">{lab} · {pill(st, "p" if warn else "")}</div><p>{answer}</p></div></div>')


# ------------------------------------------------------------------ angka turunan
N = int(ov.n); CH = int(ov.churned)
top = par.iloc[0]
top5_share = par.head(5).share_lost_mrr.sum()
top5_cust = par.head(5).n.sum() / N * 100
reco = par[par.n >= 100].head(5)
mrr_share = ov.lost_mrr / ov.mrr_total * 100
m2m, oy, ty = con.loc["Month-to-month"], con.loc["One year"], con.loc["Two year"]
first12 = ten.loc["0-6 bulan"].share_of_churners + ten.loc["7-12 bulan"].share_of_churners
rr = lambda g, m: km[(km.contract == g) & (km.month <= m)].retention_pct.iloc[-1]
sv = lambda name, st, d=svi: d[(d.service_name == name) & (d.status == st) & (d.internet_service == "Fiber optic")].churn_rate.iloc[0]
svall = lambda name, st: svc[(svc.service_name == name) & (svc.status == st)]
int_only = lambda name, st: (lambda d: 100 * d.churned.sum() / d.n.sum())(svi[(svi.service_name == name) & (svi.status == st)])
int_n = lambda name, st: svi[(svi.service_name == name) & (svi.status == st)].n.sum()
ad = lambda lab: adj.loc[lab]
ADJ = {k: ad(v) for k, v in {
    "ech": "Electronic check vs metode lain", "fib": "Fiber optic vs DSL (pelanggan internet)", "pap": "Paperless billing vs tidak",
    "sec": "Punya Online Security vs tidak (pelanggan internet)", "ts": "Punya Tech Support vs tidak (pelanggan internet)",
    "sen": "Senior vs non-senior", "par": "Punya partner vs tidak"}.items()}
assert (hyp.kesimpulan.str.startswith("Didukung")).all()
ncross = len(cc); npass = int((cc.status == "PASS").sum())
assert ncross == npass
sc20 = scen[scen.cut_pct == 20]
k5 = float(kp.loc["K5", "value"])
assert abs(sc20.assign(v=lambda d: d.saved_revenue_year).v.sum() - k5) <= 60
seg1_20 = sc20.iloc[0]
be1 = be[(be.rank_all == 1) & (be.cut_pct == 20)].iloc[0]
tc_blank = int(prof.loc["TotalCharges", "n_blank"])
assert tc_blank == len(clog) and (clog.tenure == 0).all()
dup = N - int(prof.loc["customerID", "n_unique"])
n_cols = len(prof)
n_nointernet = int(inet.loc["No", "n"])
n_nophone = int(svall("PhoneService", "No").n.iloc[0])
oddrows = int(re.search(r"(\d+) baris di luar", dq.loc[[i for i in dq.index if i.startswith("TotalCharges masuk akal")][0], "detail"]).group(1))
med_ratio = float(re.search(r"rasio median ([\d.]+)", dq.loc[[i for i in dq.index if i.startswith("TotalCharges masuk akal")][0], "detail"]).group(1))
max_rel = sens.loc[["churn_rate", "churn_M2M", "churn_TwoYear", "churn_tenure_0_6"], "diff_pct_tanpa_tenure_0"].astype(float).abs().max()
sens_vals = sens.drop(index="top1_segment")
max_rel2 = max(abs((sens_vals.tanpa_totalcharges_janggal.astype(float) - sens_vals.dasar.astype(float)) / sens_vals.dasar.astype(float) * 100).drop("lost_mrr").max(), max_rel)

# ------------------------------------------------------------------ bagian 1: data
sec1 = f'''<h2 id="rp1">1. Data yang berhasil didapatkan<small>Isi data mentah, tabel di database, dan data hasil analisis</small></h2>
<div class="kpis">{kpi(fmt(N), "pelanggan", "Satu baris = satu pelanggan. customerID unik, " + fmt(dup) + " duplikat.", "navy")}{kpi(fmt(n_cols), "kolom", "Kolom asli dari sumber; tidak ada kolom tanggal.", "amber")}{kpi(fmt(CH), "pelanggan churn", "Churn rate " + pct(ov.churn_rate) + " dari seluruh pelanggan.", "rose")}{kpi(usd(ov.lost_mrr), "lost MRR per bulan", "Tagihan bulanan pelanggan churn, " + pct(mrr_share) + " dari MRR " + usd(ov.mrr_total) + ".", "teal")}{kpi(fmt(len(clog)), "nilai diubah", "Hanya TotalCharges kosong (tenure 0) menjadi NULL; tidak ada baris dibuang.", "plum")}</div>
<h3>1.1 Data mentah (telco_churn.csv)</h3>
<div class="card"><h4>Tabel 1.1. Pemeriksaan kualitas data (Q13)</h4>{table(["Pemeriksaan", "Status", "Hasil"], [
    ["Jumlah baris dan kolom", OK("Sesuai"), f"{fmt(N)} baris, {fmt(n_cols)} kolom"],
    ["customerID unik", OK("Sesuai"), f"{fmt(dup)} duplikat"],
    ["TotalCharges terisi", WARN("Catatan"), f"{fmt(tc_blank)} baris berisi spasi, semuanya tenure 0 (pelanggan baru); diubah menjadi NULL, baris dipertahankan"],
    ["Churn hanya Yes/No; SeniorCitizen hanya 0/1", OK("Sesuai"), "Tidak ada nilai di luar himpunan"],
    ["tenure 0 sampai 72; MonthlyCharges positif", OK("Sesuai"), f"Rentang MonthlyCharges {fmt(prof.loc['MonthlyCharges','min'], 2)} sampai {fmt(prof.loc['MonthlyCharges','max'], 2)}"],
    ["'No internet service' konsisten", OK("Sesuai"), f"{fmt(n_nointernet)} pelanggan tanpa internet, ketidakcocokan 0; dipetakan ke Not available"],
    ["'No phone service' konsisten", OK("Sesuai"), f"{fmt(n_nophone)} pelanggan tanpa telepon, ketidakcocokan 0"],
    ["TotalCharges masuk akal terhadap tenure × MonthlyCharges", WARN("Catatan"), f"Rasio median {fmt(med_ratio, 3)}; {fmt(oddrows)} baris di luar rentang 0,5 sampai 1,5 (tarif bisa berubah); dicatat, tidak dibuang"]])}
<p class="note">Sensitivitas: mengeluarkan baris tenure 0 atau baris TotalCharges janggal mengubah metrik utama paling besar {pct(max_rel2)} secara relatif; segmen teratas tetap sama (<code>sensitivity.csv</code>). Tidak ada imputasi.</p></div>
<h3>1.2 Tabel di database (<code>churn.duckdb</code>)</h3>
<div class="card">{table(["Tabel", "Baris", "Isi"], [
    ["churn_raw", fmt(N), "Salinan CSV apa adanya (semua kolom teks). Tidak pernah diubah."],
    ["customers", fmt(N), "Profil: gender, senior_citizen, partner, dependents."],
    ["accounts", fmt(N), "Kontrak, tenure, metode bayar, tagihan, churn."],
    ["services", fmt(N * 9), "9 layanan per pelanggan (format panjang); No internet/phone service menjadi Not available."],
    ["dim_tenure_bucket", "5", "Lima kelompok tenure (referensi)."],
    ["v_customer (tampilan)", fmt(N), "Gabungan untuk query: kelompok tenure, jenis internet, jumlah layanan tambahan."]])}</div>
<div class="card"><h4>Data hasil analisis (<code>project/results/2-analysis/</code>)</h4>{table(["File", "Isi", "Baris", "Menjawab"], [
    ["<code>kpi_overall.csv</code>", "5 KPI utama (K1 sampai K5)", fmt(len(kp)), "Q1, Q9, Q11"],
    ["<code>churn_by_contract.csv</code>, <code>churn_by_tenure.csv</code>", "Churn per kontrak dan tenure", f"{fmt(len(con))} dan {fmt(len(ten))}", "Q1, Q2"],
    ["<code>retention_curve.csv</code>", "Kurva retensi Kaplan-Meier", fmt(len(km)), "Q3"],
    ["<code>churn_by_service*.csv</code>, <code>churn_by_addons*.csv</code>", "Churn per layanan dan bundling", f"{fmt(len(svc))}, {fmt(len(svi))}, {fmt(len(add))}, {fmt(len(addc))}", "Q4, Q5"],
    ["<code>churn_by_payment.csv</code>, <code>churn_payment_x_*.csv</code>", "Metode bayar, paperless, tabel silang", f"{fmt(len(pay))}, {fmt(len(pap))}, {fmt(len(payc))}", "Q6"],
    ["<code>segments.csv</code>, <code>pareto_lost_mrr.csv</code>", "Segmen kontrak × internet × bayar dan Pareto lost MRR", f"{fmt(len(seg))} dan {fmt(len(par))}", "Q7, Q9"],
    ["<code>churn_by_demographics.csv</code>, <code>monthly_charges_churn*.csv</code>", "Demografi dan tagihan", f"{fmt(len(dem))}, {fmt(len(chg))}, {fmt(len(chc))}", "Q8, Q10"],
    ["<code>scenarios.csv</code>, <code>breakeven.csv</code>", "Skenario revenue terselamatkan dan batas biaya impas", f"{fmt(len(scen))} dan {fmt(len(be))}", "Q11, Q12"],
    ["<code>crosscheck.csv</code>, <code>significance.csv</code>, <code>adjusted_gaps.csv</code>, <code>sensitivity.csv</code>, <code>hypotheses.csv</code>", "Validasi", f"{fmt(len(cc))}, {fmt(len(sig))}, {fmt(len(adj))}, {fmt(len(sens))}, {fmt(len(hyp))}", "Q13, Q14, hipotesis"]])}</div>
<h3>1.3 Angka kunci (KPI)</h3>
<div class="card">{table(["KPI", "Rumus ringkas", "Hasil", "Jumlah data"], [
    ["K1 Churn rate", "pelanggan churn ÷ seluruh pelanggan", pct(kp.loc["K1", "value"], 2), fmt(kp.loc["K1", "n"]) + " pelanggan"],
    ["K2 Retention rate", "100 − churn rate", pct(kp.loc["K2", "value"], 2), fmt(kp.loc["K2", "n"]) + " pelanggan"],
    ["K3 Lost MRR", "jumlah MonthlyCharges pelanggan churn", usd(kp.loc["K3", "value"], 2) + " per bulan", fmt(kp.loc["K3", "n"]) + " pelanggan churn"],
    ["K4 ARPU", "rata-rata MonthlyCharges", usd(kp.loc["K4", "value"], 2) + " per bulan", fmt(kp.loc["K4", "n"]) + " pelanggan"],
    ["K5 Revenue terselamatkan (estimated)", "churn 5 segmen teratas turun 20% relatif", usd(kp.loc["K5", "value"], 2) + " per tahun", fmt(kp.loc["K5", "n"]) + " pelanggan di 5 segmen"]])}</div>'''

# ------------------------------------------------------------------ bagian 2: business question
def addon_pair(name):
    return int_only(name, "Yes"), int_only(name, "No")

sec_sig = f"<p class=note>Ukuran hubungan (Cramer's V): kontrak {fmt(sig.loc['Tipe kontrak','cramers_v'], 2)}; tenure {fmt(sig.loc['Kelompok tenure','cramers_v'], 2)}; jenis internet {fmt(sig.loc['Jenis internet','cramers_v'], 2)}; metode bayar {fmt(sig.loc['Metode bayar','cramers_v'], 2)}; gender {fmt(sig.loc['Gender','cramers_v'], 3)} (p = {fmt(sig.loc['Gender','p_value'], 2)}).</p>"
ci_con = rd("segment_ci.csv").set_index("segment")

q_warn = {"Q3": True, "Q5": True, "Q10": True, "Q11": True, "Q12": True, "Q14": True}
n_warn = sum(q_warn.values())
chip = lambda q: f'<a class="qc{" w" if q_warn.get(q) else ""}" href="#{q.lower()}" title="{e(re.sub("<[^>]+>", "", QTXT[q]))}">{q}</a>'

ABR_C = {"Month-to-month": "M2M", "One year": "1Y", "Two year": "2Y"}
ABR_I = {"Fiber optic": "Fiber", "DSL": "DSL", "No": "Tanpa internet"}
ABR_P = {"Electronic check": "E-check", "Mailed check": "Mailed", "Bank transfer (automatic)": "Bank", "Credit card (automatic)": "Card"}
blocks = []
blocks.append(("2.1 Kontrak dan tenure", "Q1, Q2", [
    bars([(c, con.loc[c, "churn_rate"], con.loc[c, "n"]) for c in ["Month-to-month", "One year", "Two year"]], "Grafik 2.1a. Churn rate per tipe kontrak", 60),
    bars([(t, ten.loc[t, "churn_rate"], ten.loc[t, "n"]) for t in ten.index], "Grafik 2.1b. Churn rate per kelompok tenure", 60),
    qa("Q1", f"Churn rate {pct(ov.churn_rate)} ({fmt(CH)} dari {fmt(N)}). Month-to-month {pct(m2m.churn_rate)} (interval 95%: {pct(ci_con.loc['Kontrak: Month-to-month','ci95_low'])} sampai {pct(ci_con.loc['Kontrak: Month-to-month','ci95_high'])}), One year {pct(oy.churn_rate)}, Two year {pct(ty.churn_rate)}. Kontrak bulanan = {pct(m2m.share_of_customers)} pelanggan tetapi {pct(m2m.share_of_churners)} dari semua churn."),
    qa("Q2", f"Tertinggi di 0 sampai 6 bulan: {pct(ten.loc['0-6 bulan','churn_rate'])}, lalu {pct(ten.loc['7-12 bulan','churn_rate'])}, {pct(ten.loc['13-24 bulan','churn_rate'])}, {pct(ten.loc['25-48 bulan','churn_rate'])}, dan {pct(ten.loc['49-72 bulan','churn_rate'])} pada 49 sampai 72 bulan. Dua kelompok pertama (12 bulan pertama) menyumbang {pct(first12)} dari semua churn."),
    sec_sig]))
blocks.append(("2.2 Kurva retensi", "Q3", [
    lines("Grafik 2.2. Kurva retensi per tipe kontrak (Kaplan-Meier, pendekatan dari tenure)"),
    qa("Q3", f"Retensi bulan ke-12: Month-to-month {pct(rr('Month-to-month', 12))}, One year {pct(rr('One year', 12))}, Two year {pct(rr('Two year', 12))}. Bulan ke-24: {pct(rr('Month-to-month', 24))}, {pct(rr('One year', 24))}, {pct(rr('Two year', 24))}. <b>Catatan:</b> ini pendekatan, bukan kurva kohort: tidak ada tanggal bergabung atau berhenti, kontrak adalah kontrak saat ini, pelanggan kontrak tahunan hampir tidak bisa churn sebelum kontrak habis, dan ujung kurva (di atas sekitar 60 bulan) berbasis sedikit pelanggan.", True)]))
blocks.append(("2.3 Layanan dan bundling", "Q4, Q5", [
    bars([(f"{nm}: ada", addon_pair(nm)[0], int_n(nm, "Yes"), "b1") for nm in ["OnlineSecurity", "TechSupport", "OnlineBackup", "DeviceProtection"]] +
         [(f"{nm}: tidak ada", addon_pair(nm)[1], int_n(nm, "No"), "b2") for nm in ["OnlineSecurity", "TechSupport", "OnlineBackup", "DeviceProtection"]],
         "Grafik 2.3a. Churn rate menurut layanan tambahan (pelanggan internet saja)", 60),
    bars([(f"{i} layanan", add.loc[i, "churn_rate"], add.loc[i, "n"]) for i in add.index], "Grafik 2.3b. Churn rate menurut jumlah layanan tambahan (pelanggan internet)", 60),
    qa("Q4", f"Jenis internet: Fiber optic {pct(inet.loc['Fiber optic','churn_rate'])}, DSL {pct(inet.loc['DSL','churn_rate'])}, tanpa internet {pct(inet.loc['No','churn_rate'])}. Di antara pelanggan internet, dengan Online Security {pct(addon_pair('OnlineSecurity')[0])} vs tanpa {pct(addon_pair('OnlineSecurity')[1])}; dengan Tech Support {pct(addon_pair('TechSupport')[0])} vs tanpa {pct(addon_pair('TechSupport')[1])}. Setelah kontrak dan tenure disamakan, selisihnya menjadi {sgn(ADJ['sec'].selisih_setelah_strata_pts)} dan {sgn(ADJ['ts'].selisih_setelah_strata_pts)} poin (mentah {sgn(ADJ['sec'].selisih_mentah_pts)} dan {sgn(ADJ['ts'].selisih_mentah_pts)})."),
    qa("Q5", f"Pelanggan internet dengan 0 layanan tambahan churn {pct(add.loc[0,'churn_rate'])}, dengan 6 layanan {pct(add.loc[6,'churn_rate'])} (n={fmt(add.loc[6,'n'])}). Polanya turun jelas pada kontrak bulanan ({pct(addc[(addc.contract=='Month-to-month')&(addc.addon_group=='0')].churn_rate.iloc[0])} untuk 0 layanan menjadi {pct(addc[(addc.contract=='Month-to-month')&(addc.addon_group=='5-6')].churn_rate.iloc[0])} untuk 5 sampai 6 layanan), tetapi <b>tidak konsisten pada kontrak tahunan</b> (One year: {pct(addc[(addc.contract=='One year')&(addc.addon_group=='1-2')].churn_rate.iloc[0])} untuk 1 sampai 2 layanan, {pct(addc[(addc.contract=='One year')&(addc.addon_group=='5-6')].churn_rate.iloc[0])} untuk 5 sampai 6 layanan). Bundling belum bisa dibaca sebagai penyebab.", True)]))
blocks.append(("2.4 Metode bayar dan kombinasi segmen", "Q6, Q7", [
    bars([(p, pay.loc[p, "churn_rate"], pay.loc[p, "n"]) for p in pay.index], "Grafik 2.4a. Churn rate per metode bayar", 60),
    table(["Metode bayar", "Month-to-month", "One year", "Two year"], [[p] + [f"{pct(r.churn_rate)} (n={fmt(r.n)})" for c in ["Month-to-month", "One year", "Two year"] for r in [payc[(payc.payment_method == p) & (payc.contract == c)].iloc[0]]] for p in pay.index]),
    qa("Q6", f"Electronic check {pct(pay.loc['Electronic check','churn_rate'])} vs {pct(pay.loc[['Credit card (automatic)','Bank transfer (automatic)','Mailed check'],'churn_rate'].min())} sampai {pct(pay.loc[['Credit card (automatic)','Bank transfer (automatic)','Mailed check'],'churn_rate'].max())} untuk metode lain; paperless billing {pct(pap.loc['Yes','churn_rate'])} vs {pct(pap.loc['No','churn_rate'])}. Di dalam kontrak bulanan saja, Electronic check {pct(payc[(payc.contract=='Month-to-month')&(payc.payment_method=='Electronic check')].churn_rate.iloc[0])} vs {pct(payc[(payc.contract=='Month-to-month')&(payc.payment_method!='Electronic check')].churn_rate.min())} sampai {pct(payc[(payc.contract=='Month-to-month')&(payc.payment_method!='Electronic check')].churn_rate.max())}. Setelah kontrak dan tenure disamakan, selisih Electronic check {sgn(ADJ['ech'].selisih_setelah_strata_pts)} poin (mentah {sgn(ADJ['ech'].selisih_mentah_pts)})."),
    qa("Q7", f"Kombinasi terbesar: <b>{e(top.contract)} · {e(top.internet_service)} · {e(top.payment_method)}</b>, n={fmt(top.n)}, churn {pct(top.churn_rate)} (interval 95%: {pct(ci_con.loc[f'{top.contract} | {top.internet_service} | {top.payment_method}','ci95_low'])} sampai {pct(ci_con.loc[f'{top.contract} | {top.internet_service} | {top.payment_method}','ci95_high'])}). Segmen n < 100 tidak dijadikAN rekomendasi utama.".replace("dijadikAN", "dijadikan"))]))
blocks.append(("2.5 Revenue hilang per segmen", "Q7, Q9", [
    bars([(f"{ABR_C[r.contract]} · {ABR_I[r.internet_service]} · {ABR_P[r.payment_method]}", r.lost_mrr, r.n, "b3") for r in par.head(10).itertuples()],
         "Grafik 2.5. Lost MRR per segmen (US$ per bulan), 10 teratas", None, valfmt=usd,
         note="Label: kontrak (M2M = Month-to-month, 1Y = One year, 2Y = Two year) · internet · metode bayar (Bank = transfer otomatis, Card = kartu kredit otomatis)."),
    table(["#", "Segmen", "n", "Churn", "Lost MRR/bulan", "Porsi", "Kumulatif"], [[fmt(r.rank), f"{e(r.contract)} · {e(r.internet_service)} · {e(r.payment_method)}", fmt(r.n), pct(r.churn_rate), usd(r.lost_mrr), pct(r.share_lost_mrr), pct(r.cum_share_lost_mrr)] for r in par.head(8).itertuples()]),
    qa("Q7", f"Empat segmen berikutnya berukuran {fmt(par.iloc[1:5].n.min())} sampai {fmt(par.iloc[1:5].n.max())} pelanggan dengan churn {pct(par.iloc[1:5].churn_rate.min())} sampai {pct(par.iloc[1:5].churn_rate.max())}."),
    qa("Q9", f"Lost MRR {usd(ov.lost_mrr)} per bulan ({pct(mrr_share)} dari MRR) dari {fmt(CH)} pelanggan. Segmen teratas menyumbang {pct(top.share_lost_mrr)}; lima segmen teratas {pct(top5_share)} dengan hanya {pct(top5_cust)} pelanggan (dari {fmt(len(par))} segmen berchurn).")]))
blocks.append(("2.6 Demografi dan tagihan", "Q8, Q10", [
    bars([(f"{r.factor}: {r.level}", r.churn_rate, r.n) for r in dem.itertuples()], "Grafik 2.6. Churn rate menurut demografi", 60),
    table(["Kelompok", "Pelanggan", "Rata-rata tagihan", "Median tagihan"], [["Churn", fmt(chg.loc["Yes", "n"]), usd(chg.loc["Yes", "mean_charge"], 2), usd(chg.loc["Yes", "median_charge"], 2)], ["Bertahan", fmt(chg.loc["No", "n"]), usd(chg.loc["No", "mean_charge"], 2), usd(chg.loc["No", "median_charge"], 2)]]),
    qa("Q8", f"Gender tidak berpengaruh ({pct(dem[(dem.factor=='gender')&(dem.level=='Female')].churn_rate.iloc[0])} vs {pct(dem[(dem.factor=='gender')&(dem.level=='Male')].churn_rate.iloc[0])}). Senior {pct(dem[dem.level=='Senior'].churn_rate.iloc[0])} vs {pct(dem[dem.level=='Non-senior'].churn_rate.iloc[0])}; setelah kontrak dan tenure disamakan selisihnya {sgn(ADJ['sen'].selisih_setelah_strata_pts)} poin (mentah {sgn(ADJ['sen'].selisih_mentah_pts)}). Selisih partner {sgn(ADJ['par'].selisih_mentah_pts)} poin mentah menjadi {sgn(ADJ['par'].selisih_setelah_strata_pts)} setelah strata, jadi tidak berdiri sendiri."),
    qa("Q10", f"Pelanggan churn membayar rata-rata {usd(chg.loc['Yes','mean_charge'], 2)} per bulan vs {usd(chg.loc['No','mean_charge'], 2)} yang bertahan. <b>Catatan:</b> churn terkonsentrasi pada Fiber optic yang lebih mahal, jadi harga dan jenis layanan bercampur; di dalam tiap tipe kontrak selisihnya tetap ada.", True)]))
blocks.append(("2.7 Dampak program retensi", "Q11, Q12", [
    table(["Skenario (churn turun relatif)", "Segmen 1 saja", "5 segmen teratas"], [[f"{fmt(c)}%" + (" (K5, ditetapkan di muka)" if c == 20 else ""), usd(scen[(scen.rank_all == 1) & (scen.cut_pct == c)].saved_revenue_year.iloc[0]) + " / tahun", usd(scen[scen.cut_pct == c].saved_revenue_year.sum()) + " / tahun"] for c in sorted(scen.cut_pct.unique())]),
    qa("Q11", f"Jika churn turun {fmt(20)}% relatif, revenue terselamatkan sekitar {usd(seg1_20.saved_revenue_year)} per tahun di segmen 1 (dari {pct(seg1_20.churn_rate)} menjadi {pct(seg1_20.churn_rate_new)}) dan {usd(k5)} per tahun di lima segmen teratas. Semua angka <b>estimated</b>: penurunan churn dan ARPU adalah asumsi.", True),
    qa("Q12", f"Skenario {fmt(20)}% di segmen 1: program masih sepadan jika biayanya di bawah sekitar {usd(be1.breakeven_cost_per_customer_year)} per pelanggan segmen per tahun (atau {usd(be1.breakeven_cost_per_saved_customer)} per pelanggan yang berhasil dipertahankan). Biaya program nyata belum diketahui.", True)]))
blocks.append(("2.8 Validitas data dan cek silang", "Q13, Q14", [
    table(["Pemeriksaan", "Selisih maks", "Status"], [[e(r.check), fmt(r.max_abs_diff, 3), OK(r.status)] for r in cc.itertuples()]),
    qa("Q13", f"{fmt(tc_blank)} baris TotalCharges kosong (semuanya tenure 0) diubah menjadi NULL dan dicatat di <code>cleaning_log.csv</code>. Hasil utama berubah paling besar {pct(max_rel2)} secara relatif jika baris bermasalah dikeluarkan (Tabel 1.1)."),
    qa("Q14", f"SQL (DuckDB) dibandingkan dengan hitungan ulang pandas dari CSV mentah: {fmt(npass)} dari {fmt(ncross)} pemeriksaan lolos (hitungan sama persis, pecahan selisih paling besar setengah digit pembulatan). <b>Catatan:</b> rancangan menyebut Excel PivotTable; dipakai pandas, lembar Excel tidak dibuat.", True)]))

sec2_parts = []
for title, qs, items in blocks:
    sec2_parts.append(f'<h3 id="sec{title[:3].replace(".", "")}">{title} <span class="qlist">{qs}</span></h3><div class="card">{"".join(items)}</div>')
chips = "".join(chip(q) for q in sorted(PRIO, key=lambda x: int(x[1:])))
USED.update(re.findall(r"\d+(?:,\d+)*", " ".join(e(b).replace(".", ",") for b in hyp.bukti)))   # angka di kolom bukti berasal dari hypotheses.csv
hyp_t = table(["ID", "Hipotesis", "Bukti", "Hasil"], [[h.id, e(h.hipotesis), e(h.bukti).replace(".", ","), OK("Terbukti") if h.kesimpulan == "Didukung" else WARN("Terbukti, catatan")] for h in hyp.itertuples()])
n_h_note = int((hyp.kesimpulan != "Didukung").sum())
sec2 = f'''<h2 id="rp2">2. Apakah business question terjawab?<small>{fmt(len(PRIO))} pertanyaan pada Design Project, dijawab dengan data</small></h2>
<div class="card"><p><b>Jawaban singkat:</b> seluruh {fmt(len(PRIO))} pertanyaan terjawab dengan angka dari data ({fmt(n_utama)} Utama, {fmt(n_pend)} Pendukung, {fmt(n_tamb)} Tambahan). Tidak ada yang tidak terjawab. {fmt(n_warn)} jawaban diberi catatan (kuning) karena keterbatasan data atau metode. Pembahasan dikelompokkan menurut grafik atau tabel buktinya; pertanyaan yang muncul di dua grafik ditampilkan di keduanya.</p><div class="qchips">{chips}</div></div>
{"".join(sec2_parts)}
<h3>Hipotesis pada Design Project</h3><div class="card">{hyp_t}<p class="note">"Terbukti" berarti pola ada di data ini dan lolos uji kewajaran; bukan bukti sebab-akibat.</p></div>'''

# ------------------------------------------------------------------ bagian 3-6: kesesuaian
sec3 = f'''<h2 id="rp3">3. Apakah dataset sesuai dengan Design Project?<small>Perbandingan rancangan dengan realisasi</small></h2>
<div class="card"><p><b>Jawaban singkat:</b> dataset yang dipakai <b>sama</b> dengan rancangan (Telco Customer Churn, IBM). Ada tiga perubahan kecil: sumber unduhan, pemetaan "No internet service", dan struktur tabel. Dua hal belum dikerjakan: verifikasi lisensi dan sitasi.</p></div>
{table(["Aspek", "Rancangan", "Realisasi", "Verdict"], [
    ["Sumber", "IBM Telco Customer Churn, Kaggle", "File diunduh dari salinan IBM di GitHub; dibandingkan dengan file Kaggle pengguna: isi identik, hanya akhir baris (CRLF vs LF) berbeda (<code>project/data/README.md</code>)", OK("Sesuai")],
    ["Ukuran", "Perkiraan ±7.043 pelanggan, 21 kolom, belum diverifikasi", f"{fmt(N)} pelanggan, {fmt(n_cols)} kolom; customerID unik", OK("Terverifikasi")],
    ["Kolom waktu", "Tidak ada; pola waktu dari tenure", "Sama. Kurva retensi hanya pendekatan dari tenure", OK("Sesuai")],
    ["TotalCharges", "Teks dengan beberapa baris kosong", f"{fmt(tc_blank)} baris kosong (tenure 0) menjadi NULL; baris dipertahankan", OK("Sesuai")],
    ["SeniorCitizen", "Memakai 0/1", "Disimpan sebagai angka 0/1", OK("Sesuai")],
    ["No internet service", "Perlu diputuskan", "Dipetakan ke Not available; layanan dibandingkan di antara pelanggan internet saja", OK("Diputuskan")],
    ["Tabel", "4 tabel: customers, accounts, services, dim_tenure_bucket", "4 tabel yang sama + churn_raw (salinan mentah) + tampilan v_customer", WARN("Ditambah")],
    ["Lisensi dan sitasi", "Dicek sebelum publikasi", "Belum diverifikasi", NO("Belum")]])}'''

sec4 = f'''<h2 id="rp4">4. Apakah tools yang digunakan sesuai?<small>Perbandingan rancangan dengan eksekusi</small></h2>
<div class="card"><p><b>Jawaban singkat:</b> tools inti (Python/pandas, DuckDB + SQL, Markdown) sesuai rancangan. Perubahan: dashboard utama berupa HTML statis (Streamlit tersedia sebagai opsional dan belum dipublikasikan), cek silang memakai pandas (bukan Excel), dan KPI dibuat sebagai tabel (bukan view). Kode dan hasil sudah di GitHub (branch main, lewat pull request).</p></div>
{table(["Tool", "Rancangan", "Realisasi", "Verdict"], [
    ["Python (pandas)", "Memuat CSV, cleaning, memecah tabel, skenario dampak", "Profiling dan audit (<code>01</code>), cek silang (<code>04</code>), validasi (<code>05</code>), pembuat dashboard dan notebook (<code>06</code>, <code>07</code>). Ditambah numpy, scipy, matplotlib", OK("Sesuai")],
    ["DuckDB + SQL", "Database 4 tabel; KPI sebagai view", f"File SQL 01 sampai 06 mengisi tabel dan hasil; {fmt(len(kp))} KPI dan hasil query dibuat sebagai <b>tabel</b> supaya mudah diekspor ke CSV", WARN("Sesuai, catatan")],
    ["Excel", "Opsional: cek silang PivotTable", "Tidak dibuat; diganti cek silang pandas", NO("Tidak dibuat")],
    ["Streamlit + Plotly", "Dashboard di Streamlit Community Cloud", "Aplikasi Streamlit dibuat dan lolos tes headless; <b>dashboard utama berupa HTML statis</b> satu file (bisa dibuka offline dan lewat GitHub Pages). Belum dipublikasikan ke link publik", WARN("Sebagian")],
    ["GitHub", "Menyimpan kode, query, README", "Semua di-commit dan sudah di branch main lewat pull request; struktur folder mengikuti Project 1", OK("Sesuai")],
    ["Markdown", "README", "README, definisi, kamus data, keputusan cleaning", OK("Sesuai")]])}'''

# nama langkah rancangan -> realisasi (file yang benar-benar ada, dicek di bawah)
REAL = {
    1: ("project/docs/definitions.md", "Sesuai", "Ditambah batas sampel (n < 30, n < 100) dan skenario K5 yang ditetapkan di muka"),
    2: ("project/docs/data_dictionary.md", "Sesuai", ""),
    3: ("project/code/1-data-preparation/python/01_profile_audit.py, project/docs/profiling_summary.md", "Sesuai", "Profiling dan audit kualitas dijadikan satu skrip"),
    4: ("project/docs/cleaning_decisions.md, project/results/1-data-preparation/cleaning_log.csv", "Sesuai", f"{fmt(len(clog))} nilai diubah, semuanya tercatat"),
    5: ("project/code/1-data-preparation/python/02_build_tables.py, project/code/1-data-preparation/sql/02_clean.sql", "Sesuai", "Dengan pemeriksaan integritas (jumlah baris, jumlah churn, kunci unik)"),
    6: ("project/code/2-analysis/sql/03_churn_core.sql, project/code/2-analysis/sql/04_segments.sql, project/code/2-analysis/sql/05_revenue.sql, project/code/2-analysis/sql/06_kpi.sql", "Sesuai", "Hasil sebagai tabel, diekspor ke CSV oleh 03_run_queries.py"),
    7: ("project/code/2-analysis/python/04_crosscheck.py", "Berbeda", "Cek silang dengan pandas, bukan Excel"),
    8: ("project/code/2-analysis/python/03_run_queries.py, project/results/3-presentation/analysis.ipynb", "Sesuai", "Q1 sampai Q10"),
    9: ("project/results/2-analysis/scenarios.csv, project/results/2-analysis/breakeven.csv", "Sesuai", "Q11 dan Q12, berlabel estimated"),
    10: ("project/code/2-analysis/python/05_validation.py", "Sesuai", "Chi-square, interval Wilson, standardisasi strata, sensitivitas, hipotesis"),
    11: ("project/code/3-presentation/python/06_build_dashboard.py, project/code/3-presentation/streamlit/app.py", "Sebagian", "Dashboard HTML selesai; Streamlit belum dipublikasikan"),
    12: ("README.md, design-and-report/index.html", "Sesuai", "README dan laporan terisi; hasil sudah di GitHub (branch main)")}
for k, (files, *_r) in REAL.items():
    for f in files.split(", "):
        assert (REPO / f).exists() or f == "design-and-report/index.html", f
vpill = {"Sesuai": OK, "Berbeda": WARN, "Sebagian": WARN}
rows5 = [[fmt(i), e(t), "<br>".join(f"<code>{x}</code>" for x in REAL[int(i)][0].split(", ")), vpill[REAL[int(i)][1]](REAL[int(i)][1]), e(REAL[int(i)][2])] for i, t in STEPS]
RENAME = [("index.html", "design-and-report/index.html (index.html di root hanya pengalihan)"),
          ("scripts/clean_load.py", "project/code/1-data-preparation/python/01_profile_audit.py dan 02_build_tables.py"),
          ("sql/", "project/code/1-data-preparation/sql/ dan project/code/2-analysis/sql/"),
          ("notebooks/analysis.ipynb", "project/results/3-presentation/analysis.ipynb"),
          ("outputs/", "project/results/1-data-preparation/ dan project/results/2-analysis/"),
          ("outputs/crosscheck.xlsx", "project/results/2-analysis/crosscheck.csv (pandas)"),
          ("dashboard/app.py", "project/results/3-presentation/dashboard.html dan project/code/3-presentation/streamlit/app.py"),
          ("churn.duckdb", "project/churn.duckdb"), ("docs/kpi_definitions.md", "project/docs/definitions.md")]
sec5 = f'''<h2 id="rp5">5. Apakah alur pengerjaan sesuai dengan Design Project?<small>{fmt(len(STEPS))} langkah rancangan vs yang dijalankan</small></h2>
<div class="card"><p><b>Jawaban singkat:</b> kedua belas langkah dijalankan dengan urutan tahap A sampai D yang sama. Perubahan bersifat teknis: struktur folder mengikuti Project 1 (kode dan hasil dipisah per tahap), cek silang memakai pandas, dan satu langkah tambahan (validasi, langkah 10, diperluas dengan standardisasi strata).</p></div>
{table(["No", "Langkah rancangan", "Realisasi (file)", "Verdict", "Catatan"], rows5)}
<div class="card"><h4>Perubahan nama file terhadap rancangan</h4>{table(["Rancangan", "Realisasi"], [[f"<code>{a_}</code>", f"<code>{b_}</code>"] for a_, b_ in RENAME])}</div>'''

# ------------------------------------------------------------------ bagian 6: output
OUT_STATUS = {
    "Dashboard interaktif": ("Sebagian", "<code>project/results/3-presentation/dashboard.html</code>: 4 bagian (Ringkasan, Segmen churn, Retensi per tenure, Revenue dan skenario), filter kontrak, internet, metode bayar, tenure, slider skenario. Streamlit siap tetapi belum dipublikasikan; link publik belum ada"),
    "One-sheet infografik": ("Tidak dibuat", "Belum dibuat (PDF/PNG)"),
    "Database & query SQL": ("Tercapai", "<code>project/churn.duckdb</code> (dibuat ulang oleh skrip, tidak di-commit) dan SQL 01 sampai 06"),
    "Skrip cleaning & pemuat data": ("Tercapai", "<code>01_profile_audit.py</code>, <code>02_build_tables.py</code>, <code>cleaning_log.csv</code>"),
    "Notebook analisis": ("Tercapai", "<code>project/results/3-presentation/analysis.ipynb</code>, dieksekusi tanpa error"),
    "Laporan temuan & rekomendasi": ("Tercapai", "Tab Report Project (halaman ini) dan README, dengan angka dari file hasil"),
    "Repositori GitHub": ("Tercapai", "Struktur mengikuti Project 1 (<code>design-and-report/</code>, <code>project/</code>, README) dan sudah di branch main"),
    "Slide presentasi": ("Tidak dibuat", "Belum dibuat (Opsional)")}
assert [t for t, _ in OUTS] == list(OUT_STATUS), [t for t, _ in OUTS]
def outrow(t, lab):
    s_, b_ = OUT_STATUS[t]
    return [f"<b>{e(t)}</b>", lab, {"Tercapai": OK, "Sebagian": WARN}.get(s_, NO)(s_), b_]
rows6 = [outrow(t, l) for t, l in OUTS]
DOCSTAT = {"index.html": ("design-and-report/index.html", "Ada, folder berbeda"), "docs/kpi_definitions.md": ("project/docs/definitions.md", "Ada, nama berbeda"),
           "docs/data_dictionary.md": ("project/docs/data_dictionary.md", "Ada"), "data/README.md": ("project/data/README.md", "Ada"),
           "data/raw/telco_churn.csv": ("project/data/raw/telco_churn.csv", "Ada, tidak di-commit"),
           "scripts/clean_load.py": ("project/code/1-data-preparation/python/02_build_tables.py", "Ada, nama berbeda"),
           "outputs/cleaning_log.csv": ("project/results/1-data-preparation/cleaning_log.csv", "Ada"),
           "churn.duckdb": ("project/churn.duckdb", "Ada, tidak di-commit"), "requirements.txt": ("project/requirements.txt", "Ada"),
           "sql/": ("project/code/2-analysis/sql", "Ada"), "notebooks/analysis.ipynb": ("project/results/3-presentation/analysis.ipynb", "Ada"),
           "outputs/crosscheck.xlsx": (None, "Tidak dibuat (diganti crosscheck.csv)"), "outputs/scenarios.csv": ("project/results/2-analysis/scenarios.csv", "Ada"),
           "dashboard/app.py": ("project/code/3-presentation/streamlit/app.py", "Ada"), "outputs/one_sheet.pdf / .png": (None, "Tidak dibuat"),
           "README.md": ("README.md", "Ada"), "slides/": (None, "Tidak dibuat")}
rowsd = []
for name, isi, tahap, label in DOCS:
    real, st = DOCSTAT[name]
    if real and "tidak di-commit" not in st:
        assert (REPO / real).exists() or real == "design-and-report/index.html", real
    rowsd.append([f"<code>{e(name)}</code>", e(isi), (f"<code>{real}</code>" if real else "-"), (OK if st.startswith("Ada") and "berbeda" not in st else WARN if st.startswith("Ada") else NO)(st), label])
n_missing = sum(1 for r in rowsd if "pill d" in r[3])
n_out_ok = sum(1 for r in rows6 if "pill d" not in r[2] and "pill p" not in r[2])
sec6 = f'''<h2 id="rp6">6. Apakah project output tercapai?<small>Output pada Design Project, bagian 7</small></h2>
<div class="card"><p><b>Jawaban singkat:</b> {fmt(n_out_ok)} dari {fmt(len(rows6))} output tercapai penuh, {fmt(sum(1 for r in rows6 if "pill p" in r[2]))} sebagian (dashboard: HTML selesai, link publik belum), dan {fmt(sum(1 for r in rows6 if "pill d" in r[2]))} tidak dibuat (one-sheet). Dari {fmt(len(DOCS))} dokumen pada rancangan, {fmt(len(DOCS) - n_missing)} ada (beberapa dengan nama berbeda) dan {fmt(n_missing)} tidak dibuat: lembar Excel (diganti CSV pandas), one-sheet, dan slide.</p></div>
{table(["Output", "Label", "Status", "Bukti"], rows6)}
<div class="card"><h4>Daftar dokumen pada rancangan vs repositori</h4>{table(["Dokumen (rancangan)", "Isi", "Realisasi", "Status", "Label"], rowsd)}</div>'''

# ------------------------------------------------------------------ bagian 7: kesimpulan
crit_rows = [
    (CRIT[0], OK("Tercapai"), f"{fmt(n_utama)} dari {fmt(n_utama)} pertanyaan Utama terjawab dengan angka (bagian 2)"),
    (CRIT[1], WARN("Sebagian"), f"Cek silang dengan pandas: {fmt(npass)} dari {fmt(ncross)} lolos; Excel PivotTable tidak dibuat"),
    (CRIT[2], OK("Tercapai"), f"{fmt(N)} pelanggan dan {fmt(CH)} churn cocok dengan data mentah (dijaga oleh pemeriksaan integritas); {fmt(len(clog))} nilai yang diubah tercatat di log"),
    (CRIT[3], NO("Belum teruji"), "Belum diuji dengan pembaca awam"),
    (CRIT[4], WARN("Sebagian"), "Pertanyaan, cleaning, SQL, dan README terpenuhi; dashboard belum di-deploy ke link publik")]
sec7 = f'''<h2 id="rp7">7. Kesimpulan<small>Hasil analisis, Impact, success criteria, rekomendasi, saran perbaikan, dan batasan</small></h2>
<div class="card"><h4>7.1 Hasil analisis: jawaban atas pertanyaan utama</h4><p><i>Segmen pelanggan mana (tipe kontrak, tenure, layanan, metode bayar) yang paling banyak churn, dan berapa revenue bulanan yang hilang dari segmen tersebut?</i></p><ul class="tight">
<li><b>Segmen:</b> <b>{e(top.contract)} · {e(top.internet_service)} · {e(top.payment_method)}</b> ({fmt(top.n)} pelanggan, {pct(top.n / N * 100)} dari seluruh pelanggan) churn {pct(top.churn_rate)} dan menyumbang {pct(top.share_lost_mrr)} dari revenue bulanan yang hilang ({usd(top.lost_mrr)} dari {usd(ov.lost_mrr)}). Lima segmen teratas menyumbang {pct(top5_share)}.</li>
<li><b>Kontrak dan tenure:</b> kontrak bulanan {pct(m2m.churn_rate)} vs {pct(ty.churn_rate)} pada dua tahun; churn tertinggi di 0 sampai 6 bulan ({pct(ten.loc['0-6 bulan','churn_rate'])}); 12 bulan pertama = {pct(first12)} dari semua churn.</li>
<li><b>Layanan dan pembayaran:</b> Fiber optic {pct(inet.loc['Fiber optic','churn_rate'])} vs DSL {pct(inet.loc['DSL','churn_rate'])}; Electronic check {pct(pay.loc['Electronic check','churn_rate'])}; Online Security dan Tech Support berkaitan dengan churn lebih rendah. Setelah kontrak dan tenure disamakan, selisih ini mengecil (Fiber vs DSL {sgn(ADJ['fib'].selisih_setelah_strata_pts)} poin dari {sgn(ADJ['fib'].selisih_mentah_pts)}), tetapi tetap ada.</li>
<li><b>Bukan penyebab:</b> gender tidak berpengaruh, dan selisih partner hilang setelah kontrak dan tenure disamakan.</li></ul></div>
<div class="card"><h4>7.2 Impact <span class="pill p">estimated</span></h4><ul class="tight">
<li><b>Skenario:</b> churn lima segmen teratas turun {fmt(20)}% relatif menyelamatkan sekitar {usd(k5)} per tahun; segmen 1 saja {usd(seg1_20.saved_revenue_year)}. Batas biaya impas segmen 1: sekitar {usd(be1.breakeven_cost_per_customer_year)} per pelanggan segmen per tahun.</li>
<li><b>Nilai portofolio:</b> cleaning terdokumentasi, SQL, cek silang, uji kewajaran (strata, interval kepercayaan), dan dashboard yang bisa dijalankan ulang.</li>
<li><b>Belum terukur:</b> dampak nyata. Tidak ada data penerapan program atau uji A/B.</li></ul></div>
<div class="card"><h4>7.3 Success criteria</h4>{table(["Kriteria (Design Project, bagian 8)", "Status", "Bukti"], [[e(c), s, b] for c, s, b in crit_rows])}</div>
<div class="card"><h4>7.4 Rekomendasi</h4>{table(["#", "Segmen sasaran (n ≥ 100)", "n", "Churn", "Lost MRR/bulan"], [[fmt(i + 1), f"{e(r.contract)} · {e(r.internet_service)} · {e(r.payment_method)}", fmt(r.n), pct(r.churn_rate), usd(r.lost_mrr) + " (" + pct(r.share_lost_mrr) + ")"] for i, r in enumerate(reco.itertuples())])}
<ul class="tight"><li><b>Fokuskan program retensi pada segmen 1</b> dahulu. Usulan tindakan (belum teruji): tawaran pindah ke pembayaran otomatis dan kontrak 12 bulan dengan insentif.</li>
<li><b>Garap 12 bulan pertama</b> pelanggan kontrak bulanan ({pct(first12)} dari semua churn).</li>
<li><b>Dorong Online Security dan Tech Support</b> pada pelanggan Fiber optic ({pct(sv('OnlineSecurity', 'No'))} churn tanpa vs {pct(sv('OnlineSecurity', 'Yes'))} dengan Online Security), tetapi uji dulu karena selisihnya mengecil setelah kontrol.</li>
<li><b>Jangan memakai gender atau status partner</b> sebagai dasar sasaran.</li></ul></div>
<div class="card"><h4>7.5 Saran perbaikan</h4><ol class="tight">
<li>Uji program retensi lewat A/B test di sebagian segmen 1 sebelum diperluas (lihat project A/B Test Analysis).</li>
<li>Bila tersedia data bertanggal, ganti kurva retensi pendekatan dengan analisis kohort sebenarnya.</li>
<li>Tambahkan model dengan beberapa faktor sekaligus (mis. regresi logistik) untuk memisahkan pengaruh kontrak, harga, dan layanan.</li>
<li>Publikasikan dashboard Streamlit (atau halaman HTML) ke link publik, buat one-sheet, dan uji dengan 3 sampai 5 pembaca awam apakah segmen paling berisiko terbaca dalam 1 menit.</li>
<li>Verifikasi lisensi dan sitasi dataset sebelum publikasi.</li></ol></div>
<div class="card"><h4>7.6 Batasan</h4><ul class="tight">
<li><b>Lisensi dan sitasi dataset</b> belum diverifikasi.</li>
<li><b>Success criteria belum tercapai penuh:</b> cek silang Excel (diganti pandas), uji pemahaman 1 menit, dan dashboard ter-deploy.</li>
<li><b>Output yang tidak dibuat:</b> one-sheet infografik, lembar Excel cek silang, slide wawancara, dan link publik dashboard.</li></ul></div>'''

# ------------------------------------------------------------------ rangkai halaman
status = f'''<div class="callout g"><h4>Report Project versi 2: evaluasi hasil terhadap Design Project</h4><p>Halaman ini menjawab 7 pertanyaan evaluasi: data yang didapat, terjawabnya pertanyaan bisnis, kesesuaian dataset, tools, alur, output, dan kesimpulan. Semua angka dihasilkan dari file hasil SQL (DuckDB) pada data {fmt(N)} pelanggan, dicek silang dengan pandas ({fmt(npass)} dari {fmt(ncross)} lolos), dan diaudit otomatis terhadap file CSV. Rancangan lengkap ada di tab <a href="#design">Design Project</a>.</p></div>
<div class="scroll"><table class="evq"><tr><th>No</th><th>Pertanyaan evaluasi</th><th>Verdict</th><th>Ringkasan</th></tr>
<tr><td><span class="en">1</span></td><td><a href="#rp1">Data yang didapat</a></td><td>{OK("Didapat")}</td><td>{fmt(N)} pelanggan, {fmt(n_cols)} kolom; {fmt(len(clog))} nilai diubah; hasil di <code>project/results/</code></td></tr>
<tr><td><span class="en">2</span></td><td><a href="#rp2">Business question terjawab?</a></td><td>{OK(f"{len(PRIO)} dari {len(PRIO)}")}</td><td>Semua terjawab; {fmt(n_warn)} dengan catatan</td></tr>
<tr><td><span class="en">3</span></td><td><a href="#rp3">Dataset sesuai?</a></td><td>{OK("Sesuai")}</td><td>Dataset sama; lisensi belum diverifikasi</td></tr>
<tr><td><span class="en">4</span></td><td><a href="#rp4">Tools sesuai?</a></td><td>{WARN("Sebagian")}</td><td>Inti sesuai; Excel tidak dibuat, Streamlit belum publik</td></tr>
<tr><td><span class="en">5</span></td><td><a href="#rp5">Alur kerja sesuai?</a></td><td>{OK("Sesuai")}</td><td>{fmt(len(STEPS))} langkah dijalankan; perubahan teknis</td></tr>
<tr><td><span class="en">6</span></td><td><a href="#rp6">Project output tercapai?</a></td><td>{WARN("Sebagian")}</td><td>One-sheet dan link publik belum ada</td></tr>
<tr><td><span class="en">7</span></td><td><a href="#rp7">Kesimpulan</a></td><td>{OK("Tersedia")}</td><td>Segmen 1 = {pct(top.share_lost_mrr)} lost MRR; skenario estimated</td></tr></table></div>'''
REPORT = f'<div class="pane" id="report" data-tab="report" hidden>\n{status}\n{sec1}\n{sec2}\n{sec3}\n{sec4}\n{sec5}\n{sec6}\n{sec7}\n</div>\n'

NAV = ('<nav aria-label="Project navigation"><button type="button" class="tab on" data-t="design" aria-expanded="true" aria-controls="design">Design Project</button>'
       '<button type="button" class="tab" data-t="report" aria-expanded="false" aria-controls="report">Report Project</button>')
dn = re.search(r'<div class="links" data-tab="design">.*?</div>', src, re.S).group(0)
rn = ('<div class="links" data-tab="report" hidden><a href="#rp1">Data</a><a href="#rp2">Business Questions</a><a href="#rp3">Dataset</a><a href="#rp4">Tools</a>'
      '<a href="#rp5">Alur Kerja</a><a href="#rp6">Project Output</a><a href="#rp7">Kesimpulan</a></div></nav>')
page = src[:a] + REPORT + src[src.index("</main>", a):]
page = re.sub(r'<nav aria-label="Project navigation">.*?</nav>', lambda m: NAV + dn + rn, page, count=1, flags=re.S)
CH_CSS = """.ch{width:100%;height:auto;display:block}.ch text{fill:var(--ink);font-size:13px}.ch .mut{fill:var(--mut)}.ch .gl{stroke:var(--line);stroke-dasharray:3 4}
.ch .b1{fill:var(--bar)}.ch .b2{fill:var(--amberH)}.ch .b3{fill:var(--roseH)}.ch .l1{stroke:var(--roseH);stroke-width:2.5}.ch .l2{stroke:var(--amberH);stroke-width:2.5}.ch .l3{stroke:var(--tealH);stroke-width:2.5}.ch .l4{stroke:var(--mut);stroke-width:2;stroke-dasharray:5 4}
.figw.rc h4{margin:6px 0}.pane code{overflow-wrap:anywhere}.pane pre code{overflow-wrap:normal}.rt td:first-child{white-space:normal}.evq td:first-child{white-space:nowrap}
"""
page = page.replace("</style>", CSS_V2 + "\n" + CH_CSS + "</style>", 1)
page = re.sub(r"<title>.*?</title>", "<title>Project 2: Customer Churn Telco (v2)</title>", page, count=1)
# pane Design tidak boleh berubah
new_design = page[page.index('<div class="pane" id="design"'):page.index('<div class="pane" id="report"')]
assert new_design == design_pane, "pane Design berubah"

# ------------------------------------------------------------------ audit angka
vis = re.sub(r"<svg.*?</svg>", lambda m: " ".join(re.findall(r">([^<]+)<", m.group(0))), REPORT, flags=re.S)
vis = html.unescape(re.sub(r"<[^>]+>", " ", vis))
NUM = r"(?<![\d.,])"          # awal angka; mencegah memotong bagian dari angka lain
vis = re.sub(rf"\bQ\d+\b|\bK\d\b|\bH\d\b|\bGrafik \d\.\d\w?|\bTabel \d\.\d|{NUM}\d\.\d(?![\d.,])|\bProject (?:1|2)\b|#\d+", " ", vis)
vis = re.sub(rf"{NUM}0[1-9](?=_)|(?<=SQL ){NUM}0[1-9](?= sampai 06)|(?<=sampai )06(?![\d.,])", " ", vis)
tokens = re.findall(r"\d+(?:[.,]\d+)*", vis)
STRUCT = {str(i) for i in range(0, 13)} | {f"0{i}" for i in range(1, 9)} | {"20", "25", "50", "75", "60", "100", "95", "30", "5", "7", "0,5", "1,5", "1", "9", "4", "14", "12", "21", "24", "36", "48", "72", "13", "25", "49", "6", "8", "10", "3", "5"}
bad = sorted({t for t in tokens if t not in USED and t not in DESIGN_TOKENS and t not in STRUCT})
print(f"token numerik di laporan: {len(tokens)} ({len(set(tokens))} unik); dari CSV/helper: {sum(1 for t in set(tokens) if t in USED)}; dari rancangan/struktural: {sum(1 for t in set(tokens) if t not in USED)}")
if bad:
    print("TOKEN TANPA SUMBER:", bad)
    sys.exit(1)
OUT.write_text(page, encoding="utf-8")
print(f"{OUT.name}: {len(page) / 1024:.0f} KB; pertanyaan {len(PRIO)} (catatan {n_warn}); langkah {len(STEPS)}; dokumen {len(DOCS)}")
