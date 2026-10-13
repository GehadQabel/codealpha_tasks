import html
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="BookScope | Analytics Studio", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

NAVY = "#080E1E"
PANEL = "#111B32"
CYAN = "#4DD9F7"
PURPLE = "#A78BFA"
GOLD = "#FFC66D"
TEXT = "#EAF1FF"
MUTED = "#9EAECD"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], [data-testid="stApp"] {font-family:'DM Sans',sans-serif;}
[data-testid="stApp"] {background:radial-gradient(ellipse at 85% 0%, #20224a 0%, #0b1226 40%, #080e1e 80%);color:#EAF1FF;}
[data-testid="stSidebar"] {background:#0D162B;border-right:1px solid #293552;}
[data-testid="stSidebar"] * {color:#EAF1FF;}
.block-container {padding-top:2rem;padding-bottom:3rem;max-width:1480px;}
h1,h2,h3 {letter-spacing:-.025em;}
.hero {padding:30px 34px;border:1px solid #334267;border-radius:22px;background:linear-gradient(115deg,#19284a 0%,#20204b 56%,#12324c 100%);margin-bottom:24px;box-shadow:0 12px 40px #03071155;}
.eyebrow {font-size:.75rem;font-weight:800;letter-spacing:.18em;color:#69E1F8;text-transform:uppercase;}
.hero h1 {font-size:clamp(2rem,3.5vw,3.3rem);line-height:1.15;color:white;margin:9px 0 10px;}
.hero p {font-size:1rem;color:#BDCAE6;max-width:720px;margin:0;}
.kpi {background:linear-gradient(155deg,#162541,#10192F);border:1px solid #2C3C5C;border-radius:17px;padding:20px 20px 16px;min-height:132px;box-shadow:0 7px 20px #00000025;}
.kpi-label {font-size:.75rem;font-weight:800;color:#9FB0D2;letter-spacing:.09em;text-transform:uppercase;}
.kpi-value {font-size:clamp(1.5rem,2.7vw,2.35rem);font-weight:800;color:#F8FAFF;margin-top:9px;}
.kpi-note {font-size:.77rem;color:#8FA6C9;margin-top:4px;}
.kpi-line {height:3px;border-radius:4px;margin-top:15px;}
.section-title {font-size:1.2rem;font-weight:800;color:#F1F5FF;margin:20px 0 4px;}
.section-sub {font-size:.84rem;color:#9BAED1;margin-bottom:14px;}
.insight {background:#121F39;border:1px solid #2D4162;border-radius:14px;padding:17px 18px;height:100%;color:#C8D5F0;}
.insight strong {color:#F0F6FF;}
.small-note {font-size:.8rem;color:#9DAECC;}
[data-testid="stPlotlyChart"] {border:1px solid #2B3A59;border-radius:17px;background:#10192E;padding:8px;}
[data-testid="stMetric"] {background:#121D35;border:1px solid #2B3A59;border-radius:14px;padding:14px;}
div[data-testid="stDownloadButton"] button {background:linear-gradient(90deg,#7C65EF,#477FDE);color:white;border:0;border-radius:10px;font-weight:700;}
hr {border-color:#293750;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file = Path(__file__).resolve().parent / "books_dataset.csv"
    if not file.exists():
        st.error("books_dataset.csv was not found. Please keep it beside task3_dashboard.py in your GitHub repository.")
        st.stop()
    df = pd.read_csv(file)
    required = {"Title", "Price_GBP", "Rating", "Availability", "Product_URL"}
    missing = required - set(df.columns)
    if missing:
        st.error(f"Missing dataset columns: {', '.join(sorted(missing))}")
        st.stop()
    df["Price_GBP"] = pd.to_numeric(df["Price_GBP"].astype(str).str.replace("£", "", regex=False).str.replace(",", "", regex=False), errors="coerce")
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    df["Rating"] = pd.to_numeric(df["Rating"].astype(str).str.strip().str.lower().replace(words), errors="coerce")
    df = df.dropna(subset=["Price_GBP", "Rating"]).copy()
    df["Rating"] = df["Rating"].astype(int)
    return df


def plot_style(fig, height=340):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color=TEXT, size=12),
        height=height, margin=dict(l=24, r=24, t=65, b=35),
        title_font=dict(size=17, color=TEXT),
        xaxis=dict(gridcolor="#26344D", zerolinecolor="#26344D"),
        yaxis=dict(gridcolor="#26344D", zerolinecolor="#26344D"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def kpi(label, value, note, color):
    st.markdown(f'<div class="kpi"><div class="kpi-label">{html.escape(label)}</div><div class="kpi-value">{html.escape(str(value))}</div><div class="kpi-note">{html.escape(note)}</div><div class="kpi-line" style="background:{color}"></div></div>', unsafe_allow_html=True)


df = load_data()

with st.sidebar:
    st.markdown("### 📚 BOOKSCOPE")
    st.caption("ANALYTICS STUDIO · CODEALPHA")
    st.divider()
    st.markdown("#### 🎛️ Explore your data")
    min_price = float(df["Price_GBP"].min())
    max_price = float(df["Price_GBP"].max())
    selected_prices = st.slider("Price range (£)", min_value=min_price, max_value=max_price, value=(min_price, max_price), step=0.5)
    rating_options = sorted(df["Rating"].unique().tolist())
    selected_ratings = st.multiselect("Book ratings", options=rating_options, default=rating_options, format_func=lambda x: f"{'★' * x} ({x})")
    search_term = st.text_input("Search book titles", placeholder="Type a title...")
    st.divider()
    st.caption("💡 Filters update every chart, KPI and the downloadable dataset.")

filtered = df.loc[
    df["Price_GBP"].between(*selected_prices)
    & df["Rating"].isin(selected_ratings)
    & df["Title"].astype(str).str.contains(search_term, case=False, regex=False, na=False)
].copy()

st.markdown('''<div class="hero"><div class="eyebrow">✦ CodeAlpha · Data Analytics Internship</div><h1>BookScope <span style="color:#69E1F8">Analytics</span> Studio</h1><p>Explore 1,000 books through interactive visual stories. Discover pricing patterns, reader ratings, and insights in one place.</p></div>''', unsafe_allow_html=True)

if filtered.empty:
    st.warning("No books match these filters. Try widening the price range or selecting more ratings.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
with k1: kpi("Books in view", f"{len(filtered):,}", f"{len(filtered) / len(df):.0%} of full collection", CYAN)
with k2: kpi("Average price", f"£{filtered['Price_GBP'].mean():.2f}", "GBP per book", PURPLE)
with k3: kpi("Average rating", f"{filtered['Rating'].mean():.2f} / 5", "Reader star rating", GOLD)
with k4: kpi("Five-star books", f"{(filtered['Rating'] == 5).sum():,}", "Highest-rated titles", "#65E5B5")

st.markdown('<div class="section-title">📊 Visual exploration</div><div class="section-sub">Interactive charts respond to your sidebar selections.</div>', unsafe_allow_html=True)

left, right = st.columns(2, gap="large")
with left:
    fig = px.histogram(filtered, x="Price_GBP", nbins=25, title="Price distribution", labels={"Price_GBP": "Price (£)", "count": "Books"}, color_discrete_sequence=[CYAN])
    fig.update_traces(marker_line_color="#0A1933", marker_line_width=0.7, hovertemplate="Price: £%{x:.2f}<br>Books: %{y}<extra></extra>")
    fig.update_yaxes(title="Number of books")
    st.plotly_chart(plot_style(fig), use_container_width=True)
with right:
    rating_counts = filtered["Rating"].value_counts().reindex(range(1, 6), fill_value=0).rename_axis("Rating").reset_index(name="Books")
    fig = px.bar(rating_counts, x="Rating", y="Books", title="Ratings at a glance", text="Books", color="Rating", color_continuous_scale=["#4D83D9", PURPLE, "#E8A9FF"])
    fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(textposition="outside", cliponaxis=False, hovertemplate="%{x} stars: %{y} books<extra></extra>")
    fig.update_xaxes(tickmode="array", tickvals=[1, 2, 3, 4, 5], title="Star rating")
    st.plotly_chart(plot_style(fig), use_container_width=True)

left, right = st.columns(2, gap="large")
with left:
    fig = px.box(filtered, x="Rating", y="Price_GBP", points="outliers", title="Price spread by star rating", color_discrete_sequence=[PURPLE], labels={"Rating": "Star rating", "Price_GBP": "Price (£)"})
    fig.update_xaxes(tickmode="array", tickvals=[1, 2, 3, 4, 5])
    st.plotly_chart(plot_style(fig), use_container_width=True)
with right:
    fig = px.scatter(filtered, x="Price_GBP", y="Rating", title="Do expensive books get better ratings?", opacity=0.6, color="Rating", color_continuous_scale=["#4D83D9", CYAN, PURPLE], hover_data=["Title"], labels={"Price_GBP": "Price (£)", "Rating": "Star rating"})
    fig.update_layout(coloraxis_showscale=False)
    fig.update_yaxes(tickmode="array", tickvals=[1, 2, 3, 4, 5])
    st.plotly_chart(plot_style(fig), use_container_width=True)

st.markdown('<div class="section-title">✨ Key insights</div><div class="section-sub">A few useful takeaways from the currently filtered books.</div>', unsafe_allow_html=True)
correlation = filtered["Price_GBP"].corr(filtered["Rating"]) if filtered["Price_GBP"].nunique() > 1 and filtered["Rating"].nunique() > 1 else float("nan")
insight1, insight2, insight3 = st.columns(3, gap="medium")
with insight1:
    st.markdown(f'<div class="insight"><strong>💷 Typical book price</strong><p>The median price is <b>£{filtered["Price_GBP"].median():.2f}</b>, compared with a mean of £{filtered["Price_GBP"].mean():.2f}.</p></div>', unsafe_allow_html=True)
with insight2:
    popular_rating = int(filtered["Rating"].mode().iloc[0])
    st.markdown(f'<div class="insight"><strong>⭐ Most common rating</strong><p><b>{popular_rating} stars</b> appears most often in the selected collection.</p></div>', unsafe_allow_html=True)
with insight3:
    corr_text = f"{correlation:+.3f}" if pd.notna(correlation) else "N/A"
    corr_note = "Correlation is descriptive, not evidence of causation." if pd.notna(correlation) else "More variation is needed to calculate correlation."
    st.markdown(f'<div class="insight"><strong>🔎 Price × rating</strong><p>Pearson correlation: <b>{corr_text}</b>.<br>{corr_note}</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">📚 Explore the dataset</div><div class="section-sub">Search, inspect and export the books matching your filters.</div>', unsafe_allow_html=True)
st.dataframe(filtered[["Title", "Price_GBP", "Rating", "Availability", "Product_URL"]], use_container_width=True, hide_index=True, column_config={"Price_GBP": st.column_config.NumberColumn("Price (£)", format="£%.2f"), "Product_URL": st.column_config.LinkColumn("Product link")})
st.download_button("⬇ Download filtered dataset (CSV)", data=filtered.to_csv(index=False).encode("utf-8"), file_name="bookscope_filtered_books.csv", mime="text/csv", use_container_width=True)
st.markdown('<p class="small-note">Source: books.toscrape.com · A demo website for scraping practice. Ratings and prices are illustrative, not real-world customer research.</p>', unsafe_allow_html=True)
st.caption("Built with Python · Streamlit · Plotly | CodeAlpha Data Analytics Internship")
