"""Dashboard Streamlit (opsional). Versi utama adalah results/3-presentation/dashboard.html.

Menjalankan:  cd project  &&  streamlit run code/3-presentation/streamlit/app.py
Membaca hanya agregat di results/2-analysis/ (cube.csv, retention_curve.csv, pareto_lost_mrr.csv, scenarios.csv).
Jalankan code/2-analysis/python/03_run_queries.py dulu jika file itu belum ada.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RES = Path(__file__).resolve().parents[3] / "results" / "2-analysis"
MIN_N, MIN_N_RECO = 30, 100

st.set_page_config(page_title="Churn Telco", layout="wide")


@st.cache_data
def load():
    return (pd.read_csv(RES / "cube.csv"), pd.read_csv(RES / "retention_curve.csv"),
            pd.read_csv(RES / "pareto_lost_mrr.csv"), pd.read_csv(RES / "scenarios.csv"))


cube, km, pareto, scen = load()


def agg(df, by=None):
    g = df.groupby(by) if by else [(None, df)]
    rows = []
    for k, d in g:
        n, ch = d["n"].sum(), d["churned"].sum()
        rows.append({"grup": k, "n": n, "churned": ch, "churn_rate": 100 * ch / n if n else float("nan"),
                     "arpu": d["sum_monthly"].sum() / n if n else float("nan"), "lost_mrr": d["lost_mrr"].sum()})
    return pd.DataFrame(rows)


st.title("Dashboard Churn Pelanggan Telco")
st.caption("Dataset sampel IBM Telco (7.043 pelanggan). Satu potret waktu; pola adalah asosiasi, bukan sebab-akibat. Angka dampak berlabel estimated.")

dims = {"contract": "Tipe kontrak", "internet_service": "Jenis internet", "payment_method": "Metode bayar", "tenure_bucket": "Kelompok tenure"}
flt = {}
cols = st.columns(4)
for c, (k, t) in zip(cols, dims.items()):
    flt[k] = c.multiselect(t, sorted(cube[k].unique()), default=[])


def apply(df, skip=None):
    for k, v in flt.items():
        if v and k != skip:
            df = df[df[k].isin(v)]
    return df


tab1, tab2, tab3, tab4 = st.tabs(["Ringkasan", "Segmen churn", "Retensi per tenure", "Revenue & skenario"])
total = agg(cube).iloc[0]
cur = agg(apply(cube)).iloc[0]

with tab1:
    k = st.columns(5)
    small = cur.n < MIN_N
    k[0].metric("Churn rate", "n kecil" if small else f"{cur.churn_rate:.1f}%", f"{int(cur.churned)} dari {int(cur.n)}", delta_color="off")
    k[1].metric("Retention rate", "n kecil" if small else f"{100 - cur.churn_rate:.1f}%")
    k[2].metric("Lost MRR", f"US$ {cur.lost_mrr:,.0f}", f"{100 * cur.lost_mrr / total.lost_mrr:.1f}% dari total", delta_color="off")
    k[3].metric("ARPU", f"US$ {cur.arpu:.2f}" if cur.n else "-")
    k[4].metric("Pelanggan", f"{int(cur.n):,}")
    top = pareto.iloc[0]
    st.info(f"Segmen **{top.contract} · {top.internet_service} · {top.payment_method}** hanya {100 * top.n / total.n:.1f}% pelanggan "
            f"tetapi {top.share_lost_mrr:.1f}% lost MRR (churn {top.churn_rate:.1f}%, n={int(top.n):,}). "
            f"Lima segmen teratas: {pareto.iloc[4].cum_share_lost_mrr:.1f}%.")

with tab2:
    c1, c2 = st.columns(2)
    for i, (k, t) in enumerate(dims.items()):
        a = agg(apply(cube, skip=k), k).rename(columns={"grup": t})
        a["catatan"] = a["n"].map(lambda n: "n < 30" if n < MIN_N else "")
        fig = px.bar(a, x="churn_rate", y=t, orientation="h", text=a["churn_rate"].round(1).astype(str) + "% (n=" + a["n"].astype(int).astype(str) + ")",
                     labels={"churn_rate": "Churn rate (%)"}, title=t)
        (c1 if i % 2 == 0 else c2).plotly_chart(fig, width="stretch")
    seg = agg(apply(cube), ["contract", "internet_service", "payment_method"]).sort_values("lost_mrr", ascending=False)
    seg[["contract", "internet_service", "payment_method"]] = pd.DataFrame(seg["grup"].tolist(), index=seg.index)
    seg["catatan"] = seg["n"].map(lambda n: "n < 100" if n < MIN_N_RECO else "")
    st.dataframe(seg[["contract", "internet_service", "payment_method", "n", "churn_rate", "arpu", "lost_mrr", "catatan"]].head(15).round(2), hide_index=True)

with tab3:
    fig = px.line(km, x="month", y="retention_pct", color="contract", labels={"month": "Tenure (bulan)", "retention_pct": "Retensi (%)"},
                  title="Kurva retensi Kaplan-Meier (pendekatan dari tenure)")
    st.plotly_chart(fig, width="stretch")
    st.caption("Bukan kurva kohort sebenarnya; ujung kurva berbasis sedikit pelanggan.")

with tab4:
    top10 = pareto.head(10).copy()
    top10["segmen"] = top10.contract + " · " + top10.internet_service + " · " + top10.payment_method
    st.plotly_chart(px.bar(top10, x="lost_mrr", y="segmen", orientation="h", labels={"lost_mrr": "Lost MRR (US$/bulan)"}, title="10 segmen dengan lost MRR terbesar"), width="stretch")
    segs = scen.drop_duplicates("rank_all")
    label = segs.contract + " · " + segs.internet_service + " · " + segs.payment_method + " (n=" + segs.n.astype(str) + ")"
    i = st.selectbox("Segmen", range(len(segs)), format_func=lambda j: label.iloc[j])
    cut = st.slider("Penurunan churn relatif (%)", 0, 50, 20) / 100
    s = segs.iloc[i]
    new = s.churn_rate * (1 - cut)
    saved = (s.churn_rate - new) / 100 * s.n
    rev = saved * s.arpu * 12
    r = st.columns(4)
    r[0].metric("Churn sekarang → sesudah", f"{s.churn_rate:.1f}% → {new:.1f}%")
    r[1].metric("Pelanggan tertahan", f"{saved:,.0f}")
    r[2].metric("Revenue terselamatkan/tahun (estimated)", f"US$ {rev:,.0f}")
    r[3].metric("Batas biaya impas/pelanggan/tahun", f"US$ {rev / s.n:,.0f}")
    st.caption("Revenue terselamatkan per tahun = (churn lama − churn baru) × pelanggan segmen × ARPU × 12. Efek program belum teruji.")
