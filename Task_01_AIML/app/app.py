import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Laptop Market Analytics", page_icon="💻", layout="wide")

# ------------------------------------------------------------------ theme
NAVY, BLUE, TEAL, SLATE = "#0f2a43", "#2e75b6", "#1b7f79", "#64748b"
SEQ = ["#0b3c5d", "#1b7f79", "#2e9e8f", "#52b69a", "#76c893", "#99d98c", "#b5e48c"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stMetric {{ font-family: 'Inter', sans-serif; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.stApp {{ background: #f4f7fb; }}
.block-container {{ padding: 1.4rem 2.2rem 3rem 2.2rem; max-width: 1500px; }}

/* sidebar */
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {NAVY} 0%, #123a5c 100%); border-right: none; }}
section[data-testid="stSidebar"] * {{ color: #e6eef7 !important; }}
section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div {{ color: #fff !important; }}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.18); border-radius: 8px; }}
section[data-testid="stSidebar"] [data-baseweb="tag"] {{ background: {BLUE} !important; border-radius: 6px; }}
section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.15); }}
.sb-brand {{ font-size: 1.15rem; font-weight: 700; letter-spacing: .2px; margin-bottom: 2px; }}
.sb-sub {{ font-size: .78rem; opacity: .7; margin-bottom: 14px; }}
.sb-label {{ font-size: .7rem; text-transform: uppercase; letter-spacing: 1.2px; opacity: .6; margin: 6px 0 2px; }}

/* hero */
.hero {{ background: linear-gradient(120deg, {NAVY} 0%, {BLUE} 100%); border-radius: 16px; padding: 26px 32px; color: #fff; margin-bottom: 18px; box-shadow: 0 6px 20px rgba(15,42,67,.18); }}
.hero h1 {{ margin: 0; font-size: 1.8rem; font-weight: 700; color: #fff; }}
.hero p {{ margin: 6px 0 0; font-size: .95rem; opacity: .85; }}

/* KPI cards */
.kpi {{ background: #fff; border-radius: 14px; padding: 16px 18px; border: 1px solid #e3eaf2; border-top: 4px solid {BLUE}; box-shadow: 0 2px 8px rgba(15,42,67,.05); }}
.kpi .v {{ font-size: 1.65rem; font-weight: 700; color: {NAVY}; line-height: 1.15; }}
.kpi .l {{ font-size: .74rem; text-transform: uppercase; letter-spacing: 1px; color: {SLATE}; margin-top: 4px; }}

/* section + chart cards */
.sec {{ display: flex; align-items: center; gap: 10px; margin: 30px 0 10px; }}
.sec .bar {{ width: 5px; height: 24px; border-radius: 3px; background: {BLUE}; }}
.sec h2 {{ margin: 0; font-size: 1.15rem; font-weight: 700; color: {NAVY}; }}
.sec span {{ font-size: .82rem; color: {SLATE}; margin-left: 4px; }}
div[data-testid="stPlotlyChart"] {{ background: #fff; border: 1px solid #e3eaf2; border-radius: 14px; padding: 8px 10px; box-shadow: 0 2px 8px rgba(15,42,67,.05); }}
div[data-testid="stDataFrame"] {{ border: 1px solid #e3eaf2; border-radius: 12px; overflow: hidden; }}
.insight {{ background: #fff; border: 1px solid #e3eaf2; border-left: 4px solid {TEAL}; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; font-size: .92rem; color: #243b53; }}
.foot {{ text-align: center; color: {SLATE}; font-size: .8rem; margin-top: 34px; }}
</style>
""", unsafe_allow_html=True)


def style(fig, title, height=380, legend=False):
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=15, color=NAVY), x=0.01),
        height=height, margin=dict(l=20, r=20, t=55, b=30),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", size=12, color="#334155"),
        showlegend=legend, legend=dict(orientation="h", y=-0.2),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(gridcolor="#eef2f7", zeroline=False, linecolor="#cbd5e1")
    fig.update_yaxes(gridcolor="#eef2f7", zeroline=False, linecolor="#cbd5e1")
    return fig


def section(title, sub=""):
    st.markdown(f'<div class="sec"><div class="bar"></div><h2>{title}</h2><span>{sub}</span></div>', unsafe_allow_html=True)


@st.cache_data
def load():
    return pd.read_csv("dataset/laptop_data_cleaned.csv")


df = load()

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown('<div class="sb-brand">💻 Laptop Analytics</div><div class="sb-sub">Price &amp; specification explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-label">Filters</div>', unsafe_allow_html=True)
    brands = st.multiselect("Brand", sorted(df["brand"].unique()), default=sorted(df["brand"].unique()))
    types = st.multiselect("Laptop type", sorted(df["laptop_type"].unique()), default=sorted(df["laptop_type"].unique()))
    rams = st.multiselect("RAM (GB)", sorted(df["ram_gb"].unique()), default=sorted(df["ram_gb"].unique()))
    lo, hi = int(df["price"].min()), int(df["price"].max())
    price = st.slider("Price range", lo, hi, (lo, hi))
    st.markdown("---")
    st.caption(f"Dataset: {len(df):,} cleaned laptop listings · {df.shape[1]} columns")

f = df[df["brand"].isin(brands) & df["laptop_type"].isin(types) & df["ram_gb"].isin(rams) & df["price"].between(*price)]

# ------------------------------------------------------------------ header + KPIs
st.markdown('<div class="hero"><h1>Laptop Price &amp; Specification Dashboard</h1>'
            '<p>Interactive view of 10 analyses covering price, brands, types, specifications and correlations. '
            'Use the sidebar filters to update every chart.</p></div>', unsafe_allow_html=True)

if f.empty:
    st.warning("No laptops match the current filters. Please widen your selection in the sidebar.")
    st.stop()

kpis = [
    ("Laptops", f"{len(f):,}"),
    ("Average Price", f"{f['price'].mean():,.0f}"),
    ("Median Price", f"{f['price'].median():,.0f}"),
    ("Average RAM", f"{f['ram_gb'].mean():.1f} GB"),
    ("Average Weight", f"{f['weight_kg'].mean():.2f} kg"),
    ("Brands", f"{f['brand'].nunique()}"),
]
for col, (label, val) in zip(st.columns(len(kpis)), kpis):
    col.markdown(f'<div class="kpi"><div class="v">{val}</div><div class="l">{label}</div></div>', unsafe_allow_html=True)

# ------------------------------------------------------------------ 1. price & market
section("Price & Market Overview", "Charts 1–3")
c1, c2 = st.columns(2)

fig = px.histogram(f, x="price", nbins=40, color_discrete_sequence=[TEAL])
fig.add_vline(x=f["price"].mean(), line_dash="dash", line_color="crimson", annotation_text=f"Mean {f['price'].mean():,.0f}", annotation_position="top right")
fig.add_vline(x=f["price"].median(), line_dash="dash", line_color="#d4a017", annotation_text=f"Median {f['price'].median():,.0f}", annotation_position="top left")
fig.update_layout(xaxis_title="Price", yaxis_title="Number of laptops")
c1.plotly_chart(style(fig, "1 · Distribution of Laptop Prices", 420), use_container_width=True)

bs = f.groupby("brand")["price"].agg(["mean", "count"]).reset_index()
bs = bs[bs["count"] >= 5].sort_values("mean", ascending=False)
fig = px.bar(bs, x="brand", y="mean", text=bs["mean"].round(0).map("{:,.0f}".format), color="mean",
             color_continuous_scale=SEQ[::-1], hover_data={"count": True})
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(coloraxis_showscale=False, xaxis_title="Brand", yaxis_title="Average price")
c2.plotly_chart(style(fig, "2 · Average Price by Brand (brands with 5+ laptops)", 420), use_container_width=True)

c3, c4 = st.columns(2)
share = f["laptop_type"].value_counts().reset_index()
share.columns = ["laptop_type", "count"]
fig = px.pie(share, names="laptop_type", values="count", hole=0.5, color_discrete_sequence=px.colors.sequential.Viridis_r)
fig.update_traces(textposition="inside", textinfo="percent", marker=dict(line=dict(color="white", width=2)))
c3.plotly_chart(style(fig, "3 · Share of Laptops by Type", 400, legend=True), use_container_width=True)

so = f["storage_type"].value_counts().reset_index()
so.columns = ["storage_type", "count"]
fig = px.bar(so, x="storage_type", y="count", text="count", color="count", color_continuous_scale=SEQ[::-1])
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(coloraxis_showscale=False, xaxis_title="Storage type", yaxis_title="Number of laptops")
c4.plotly_chart(style(fig, "4 · Number of Laptops by Storage Type", 400), use_container_width=True)

# ------------------------------------------------------------------ 2. price drivers
section("Price Drivers", "Charts 5–7")
c5, c6 = st.columns(2)

rng = np.random.default_rng(7)
pj = f.assign(ram_jitter=f["ram_gb"] * np.exp(rng.normal(0, 0.03, len(f))))
fig = px.scatter(pj, x="ram_jitter", y="price", color="laptop_type", opacity=0.65, log_x=True,
                 color_discrete_sequence=px.colors.sequential.Viridis_r, hover_data={"ram_jitter": False, "ram_gb": True, "brand": True})
fig.update_xaxes(tickvals=[2, 4, 8, 16, 32, 64], ticktext=[2, 4, 8, 16, 32, 64], title="RAM (GB, log scale, jittered)")
fig.update_yaxes(title="Price")
r = f["ram_gb"].corr(f["price"])
c5.plotly_chart(style(fig, f"5 · RAM vs. Price (r = {r:.2f})", 420, legend=True), use_container_width=True)

br = f.groupby("ram_gb")["price"].mean().reset_index()
fig = px.line(br, x=br["ram_gb"].astype(str), y="price", markers=True, text=br["price"].round(0).map("{:,.0f}".format))
fig.update_traces(line=dict(color=TEAL, width=3), marker=dict(size=9), textposition="top center")
fig.update_layout(xaxis_title="RAM (GB)", yaxis_title="Average price")
c6.plotly_chart(style(fig, "6 · Average Price by RAM Size", 420), use_container_width=True)

order = f.groupby("laptop_type")["price"].mean().sort_values(ascending=False).index.tolist()
fig = px.box(f, x="laptop_type", y="price", color="laptop_type", category_orders={"laptop_type": order},
             color_discrete_sequence=px.colors.sequential.Viridis_r)
fig.update_layout(xaxis_title="Laptop type", yaxis_title="Price")
st.plotly_chart(style(fig, "7 · Price Distribution by Laptop Type", 420), use_container_width=True)

# ------------------------------------------------------------------ 3. specs & relationships
section("Specifications & Relationships", "Charts 8–10")
cols = ["price", "ram_gb", "total_storage_gb", "cpu_ghz", "ppi", "screen_inches", "weight_kg", "touchscreen", "ips_panel"]
corr = f[cols].corr().round(2)
corr = corr.where(~np.triu(np.ones(corr.shape, dtype=bool), k=1))
fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
fig.update_layout(coloraxis_colorbar=dict(thickness=12, len=0.8))
c8, c9 = st.columns([1, 1])
c8.plotly_chart(style(fig, "8 · Correlation Heatmap", 520), use_container_width=True)

fams = f["cpu_family"].value_counts()
main = fams[fams >= 10].index
fo = f[f["cpu_family"].isin(main)].groupby("cpu_family")["price"].median().sort_values().index.tolist()
fig = px.violin(f[f["cpu_family"].isin(main)], x="cpu_family", y="price", color="cpu_family", box=True,
                category_orders={"cpu_family": fo}, color_discrete_sequence=SEQ)
fig.update_traces(meanline_visible=True)
fig.update_layout(xaxis_title="CPU family", yaxis_title="Price")
c9.plotly_chart(style(fig, "9 · Price by CPU Family (families with 10+ laptops)", 520), use_container_width=True)

pcols = ["price", "ram_gb", "weight_kg", "ppi", "cpu_ghz"]
ps = f[pcols + ["laptop_type"]].sample(min(900, len(f)), random_state=7)
fig = px.scatter_matrix(ps, dimensions=pcols, color="laptop_type", opacity=0.55,
                        color_discrete_sequence=px.colors.sequential.Viridis_r)
fig.update_traces(diagonal_visible=False, marker=dict(size=4))
st.plotly_chart(style(fig, "10 · Pair Plot of Key Specifications by Laptop Type (sample of up to 900)", 720, legend=True), use_container_width=True)

# ------------------------------------------------------------------ summary + insights
section("Summary Statistics", "Filtered data")
desc = f[["price", "ram_gb", "total_storage_gb", "cpu_ghz", "ppi", "screen_inches", "weight_kg"]].describe().T.round(2)
st.dataframe(desc, use_container_width=True)

section("Key Insights")
for text in [
    "<b>RAM</b> is the strongest driver of price (r ≈ +0.74); screen size has almost no effect.",
    "<b>Core i7</b>, <b>Nvidia graphics</b> and <b>SSD storage</b> mark the more expensive laptops.",
    "<b>Workstations</b> and <b>gaming</b> laptops are the priciest types; netbooks and notebooks the cheapest.",
    "<b>Dell, Lenovo and HP</b> make up about two-thirds of all laptops.",
]:
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)

st.markdown('<div class="foot">Devixo Solutions · AI/ML Internship · Task 01 – Laptop Price &amp; Specification Analysis</div>', unsafe_allow_html=True)
