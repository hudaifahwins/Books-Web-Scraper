import requests
import plotly.express as px
import pandas as pd
import streamlit as st

API_URL = "http://api:8000/books"

st.set_page_config(page_title="Book Dashboard", page_icon="📚", layout="wide")

st.title("📚 Book Prices Dashboard")
st.markdown("Data fetched from the Book API service.")

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

st.subheader("📋 Book Data Table")
st.dataframe(df, use_container_width=True)

st.subheader("📊 Book Prices Bar Chart")
fig = px.bar(
    df,
    x="title",
    y="price",
    title="Book Prices",
    labels={"title": "Book Title", "price": "Price (£)"},
    color="price",
    color_continuous_scale="Viridis",
)
fig.update_layout(
    xaxis_tickangle=-45,
    height=600,
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)
