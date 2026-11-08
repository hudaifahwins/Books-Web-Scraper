import requests
import plotly.express as px
import pandas as pd
import streamlit as st

API_URL = "http://api:8000/books"

st.set_page_config(page_title="BookScraper Pro", layout="wide")

# Inject custom CSS to hide Streamlit default chrome for a SaaS-like look
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📚 BookScraper Pro")
st.markdown("Enterprise-grade book price analytics dashboard.")

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

# --- KPI Metrics ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Books", len(df))

with col2:
    avg_price = df["price"].mean()
    st.metric("Average Price", f"£{avg_price:.2f}")

with col3:
    max_price = df["price"].max()
    most_expensive = df.loc[df["price"].idxmax(), "title"]
    st.metric("Most Expensive Book", f"£{max_price:.2f}", delta=most_expensive)

st.divider()

# --- Sidebar Filter ---
st.sidebar.title("🔍 Filters")
search_query = st.sidebar.text_input("Search by book title:", "")

if search_query:
    filtered_df = df[df["title"].str.contains(search_query, case=False, na=False)]
else:
    filtered_df = df

# --- Bar Chart (Top 10 most expensive books) ---
st.subheader("🏆 Top 10 Most Expensive Books")
top_10 = filtered_df.nlargest(10, "price")

fig = px.bar(
    top_10,
    x="title",
    y="price",
    title="Top 10 Book Prices",
    labels={"title": "Book Title", "price": "Price (£)"},
    color="price",
    color_continuous_scale="Plasma",
)
fig.update_layout(
    xaxis_tickangle=-45,
    height=600,
    showlegend=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Arial, sans-serif", size=14, color="#333333"),
)
st.plotly_chart(fig, use_container_width=True)

# --- Data Table ---
st.subheader("📋 Book Data Table")
st.dataframe(filtered_df, use_container_width=True)
