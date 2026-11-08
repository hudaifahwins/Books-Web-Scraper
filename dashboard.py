import requests
import plotly.express as px
import pandas as pd
import streamlit as st

API_URL = "http://api:8000/books"

st.set_page_config(page_title="BookScraper Pro", layout="wide")

# ------------------------------------------------------------------
# Custom CSS: Inter font, hide Streamlit chrome, premium card styling
# ------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
        color: #ffffff;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .premium-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 24px;
        backdrop-filter: blur(10px);
    }

    .card-label {
        font-size: 14px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    .card-value {
        font-size: 36px;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.2;
    }

    .card-subtitle {
        font-size: 13px;
        color: rgba(255, 255, 255, 0.5);
        margin-top: 8px;
    }

    .header-title {
        font-size: 42px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    }

    .header-subtitle {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.6);
        font-weight: 300;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown('<div class="header-title">📚 BookScraper Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Enterprise Data Pipeline & Analytics</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def fetch_books():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Failed to fetch data from API: {exc}")
        return []

books = fetch_books()

if not books:
    st.warning("No book data available. Please check that the scraper has populated the database.")
    st.stop()

df = pd.DataFrame(books)

# ------------------------------------------------------------------
# KPI Cards (custom HTML instead of st.metric)
# ------------------------------------------------------------------
total_books = len(df)
avg_price = df["price"].mean()
max_price = df["price"].max()
most_expensive = df.loc[df["price"].idxmax(), "title"]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="premium-card">
        <div class="card-label">Total Books</div>
        <div class="card-value">{total_books}</div>
        <div class="card-subtitle">Scraped titles</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="premium-card">
        <div class="card-label">Average Price</div>
        <div class="card-value">£{avg_price:.2f}</div>
        <div class="card-subtitle">Across all titles</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="premium-card">
        <div class="card-label">Most Expensive</div>
        <div class="card-value">£{max_price:.2f}</div>
        <div class="card-subtitle">{most_expensive[:50]}{'...' if len(most_expensive) > 50 else ''}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Sidebar Filter
# ------------------------------------------------------------------
st.sidebar.title("🔍 Filters")
search_query = st.sidebar.text_input("Search by book title:", "")

if search_query:
    filtered_df = df[df["title"].str.contains(search_query, case=False, na=False)]
else:
    filtered_df = df

# ------------------------------------------------------------------
# Horizontal Bar Chart (Top 10 most expensive books)
# ------------------------------------------------------------------
st.subheader("🏆 Top 10 Most Expensive Books")
top_10 = filtered_df.nlargest(10, "price")

fig = px.bar(
    top_10,
    x="price",
    y="title",
    orientation="h",
    title="Top 10 Book Prices",
    labels={"title": "", "price": "Price (£)"},
    color="price",
    color_continuous_scale=["#4a00e0", "#00e5ff"],
)

fig.update_layout(
    height=700,
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=14, color="#ffffff"),
    margin=dict(l=20, r=20, t=60, b=20),
)

fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(color="rgba(255,255,255,0.7)"))
fig.update_yaxes(showgrid=False, zeroline=False, tickfont=dict(color="#ffffff", size=13))

fig.update_traces(marker_line_width=0)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# Data Table with CSV Download
# ------------------------------------------------------------------
st.subheader("📋 Book Data Table")
st.dataframe(filtered_df, use_container_width=True)

csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="books.csv",
    mime="text/csv",
)
