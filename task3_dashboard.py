
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------------
# PAGE CONFIGURATION
# ---------------------------------
st.set_page_config(
    page_title="CodeAlpha | Books Analytics",
    page_icon="📚",
    layout="wide"
)

# ---------------------------------
# CUSTOM STYLING
# ---------------------------------
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    font-family: Arial, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# LOAD DATA
# ---------------------------------
@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "books_dataset.csv"
    data = pd.read_csv(file_path)
    data["Price_GBP"] = pd.to_numeric(
        data["Price_GBP"], errors="coerce"
    )
    data["Rating"] = pd.to_numeric(
        data["Rating"], errors="coerce"
    )
    return data.dropna(subset=["Price_GBP", "Rating"])

df = load_data()

# ---------------------------------
# HEADER
# ---------------------------------
st.title("📚 Books Analytics Dashboard")
st.caption("CodeAlpha Internship | Data Analytics Project")
st.markdown(
    "Explore book prices, ratings, and patterns "
    "through interactive visualizations."
)

# ---------------------------------
# SIDEBAR FILTERS
# ---------------------------------
st.sidebar.header("🔎 Dashboard Filters")

min_price = float(df["Price_GBP"].min())
max_price = float(df["Price_GBP"].max())

price_range = st.sidebar.slider(
    "Select Price Range (£)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

selected_ratings = st.sidebar.multiselect(
    "Select Book Ratings",
    options=sorted(df["Rating"].unique()),
    default=sorted(df["Rating"].unique())
)

filtered_df = df[
    (df["Price_GBP"] >= price_range[0]) &
    (df["Price_GBP"] <= price_range[1]) &
    (df["Rating"].isin(selected_ratings))
]

# ---------------------------------
# KPI METRICS
# ---------------------------------
total_books = len(filtered_df)
avg_price = filtered_df["Price_GBP"].mean()
avg_rating = filtered_df["Rating"].mean()
five_star = (filtered_df["Rating"] == 5).sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("📚 Total Books", f"{total_books:,}")
col2.metric(
    "💷 Average Price",
    f"£{avg_price:.2f}" if total_books else "N/A"
)
col3.metric(
    "⭐ Average Rating",
    f"{avg_rating:.2f}" if total_books else "N/A"
)
col4.metric("🌟 Five-Star Books", f"{five_star:,}")

st.divider()

if filtered_df.empty:
    st.warning("No books match the selected filters.")
    st.stop()

# ---------------------------------
# VISUALIZATIONS
# ---------------------------------
left, right = st.columns(2)

with left:
    fig_price = px.histogram(
        filtered_df,
        x="Price_GBP",
        nbins=25,
        title="Book Price Distribution",
        labels={"Price_GBP": "Price (£)"},
        color_discrete_sequence=["#7C6BC4"]
    )
    st.plotly_chart(fig_price, use_container_width=True)

with right:
    rating_counts = (
        filtered_df["Rating"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    rating_counts.columns = ["Rating", "Count"]

    fig_rating = px.bar(
        rating_counts,
        x="Rating",
        y="Count",
        title="Book Rating Distribution",
        color="Rating",
        color_continuous_scale="Purples"
    )
    st.plotly_chart(fig_rating, use_container_width=True)

left2, right2 = st.columns(2)

with left2:
    fig_box = px.box(
        filtered_df,
        x="Rating",
        y="Price_GBP",
        color="Rating",
        title="Price Variation by Rating",
        labels={"Price_GBP": "Price (£)"}
    )
    st.plotly_chart(fig_box, use_container_width=True)

with right2:
    avg_by_rating = (
        filtered_df.groupby("Rating", as_index=False)
        ["Price_GBP"].mean()
    )

    fig_avg = px.bar(
        avg_by_rating,
        x="Rating",
        y="Price_GBP",
        title="Average Price by Rating",
        labels={"Price_GBP": "Average Price (£)"},
        color="Rating",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_avg, use_container_width=True)

# ---------------------------------
# DATA TABLE
# ---------------------------------
st.subheader("📋 Explore the Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv_data,
    file_name="filtered_books.csv",
    mime="text/csv"
)

# ---------------------------------
# FOOTER
# ---------------------------------
st.divider()
st.caption(
    "Data Source: Books to Scrape | "
    "Developed for CodeAlpha Data Analytics Internship"
)
