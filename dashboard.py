import requests
import plotly.express as px
import pandas as pd
import streamlit as st

API_URL = "http://api:8000/books"

st.set_page_config(page_title="BookScraper Pro", layout="wide")

# ------------------------------------------------------------------
# Massive CSS Override
# ------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background-color: #09090b;
    }

    [data-testid="stHeader"],
    footer,
    #MainMenu {
        visibility: hidden;
    }

    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Ensure sidebar is visible and styled to match theme */
    [data-testid="stSidebar"] {
        background: #18181b;
        border-right: 1px solid #27272a;
    }

    /* Dataframe: remove border, transparent background, no shadow */
    [data-testid="stDataFrame"] {
        border: none !important;
        background: rgba(0, 0, 0, 0) !important;
        box-shadow: none !important;
    }

    /* Custom header */
    .custom-header {
        margin-bottom: 40px;
    }

    .custom-header h1 {
        font-weight: 600;
        font-size: 32px;
        letter-spacing: -1px;
        color: #ffffff;
        margin-bottom: 4px;
    }

    .custom-header p {
        font-size: 16px;
        color: #a1a1aa;
        margin: 0;
    }

    /* KPI cards */
    .kpi-container {
        display: flex;
        gap: 16px;
        margin-bottom: 32px;
    }

    .kpi-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 24px;
        flex: 1;
    }

    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        color: #a1a1aa;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 36px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Custom Header (raw HTML)
# ------------------------------------------------------------------
st.markdown("""
<div class="custom-header">
    <h1>BookScraper Pro</h1>
    <p>Enterprise Data Pipeline and Analytics</p>
</div>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def fetch_books():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []

books = fetch_books()

if not books:
    st.warning("No book data available. Please check the API connection.")
    st.stop()

df = pd.DataFrame(books)

# ------------------------------------------------------------------
# Sidebar Search Filter
# ------------------------------------------------------------------
st.sidebar.title("🔍 Filters")
search_query = st.sidebar.text_input("Search by book title:", "")

if search_query:
    filtered_df = df[df["title"].str.contains(search_query, case=False, na=False)]
else:
    filtered_df = df

# ------------------------------------------------------------------
# KPI Cards (flexbox HTML, no st.metric)
# ------------------------------------------------------------------
total_books = len(filtered_df)
avg_price = filtered_df["price"].mean()
max_price = filtered_df["price"].max()

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-label">Total Books</div>
        <div class="kpi-value">{total_books:,}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Average Price</div>
        <div class="kpi-value">£{avg_price:.2f}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Most Expensive</div>
        <div class="kpi-value">£{max_price:.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Plotly Horizontal Bar Chart (Top 10 most expensive books)
# ------------------------------------------------------------------
st.subheader("Top 10 Most Expensive Books")
top_10 = filtered_df.nlargest(10, "price")

fig = px.bar(
    top_10,
    x="price",
    y="title",
    orientation="h",
    labels={"price": "Price (£)", "title": ""},
)

fig.update_traces(marker_color="#6366f1")

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=20, b=0),
    height=400,
    showlegend=False,
    bargap=0.4,
    font=dict(color="#ffffff"),
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=False,
        tickfont=dict(size=14, color="#a1a1aa"),
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=False,
        tickfont=dict(size=14, color="#a1a1aa"),
    ),
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# Data Table
# ------------------------------------------------------------------
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
