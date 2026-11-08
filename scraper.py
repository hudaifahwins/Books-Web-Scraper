"""
Production-ready web scraper for books.toscrape.com.

This script fetches all pages of the books catalogue, extracts each
book's title and price, and saves the data to CSV, JSON, SQLite,
and PostgreSQL.

If a local books.csv already exists, it will load that data instead
of re-scraping the website.
"""

import logging
import os
import re
import sqlite3
import time
from typing import Dict, List
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from tqdm import tqdm

from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
load_dotenv()

# Constants
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/119.0.0.0 Safari/537.36"
)
CSV_FILENAME = "books.csv"
JSON_FILENAME = "books.json"
SQLITE_DB_FILENAME = "books.db"
TABLE_NAME = "books"
TOTAL_PAGES = 50

# Environment-driven configuration
TARGET_URL = os.getenv("TARGET_URL", "http://books.toscrape.com")
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1"))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://admin:secret@db:5432/books_db",
)

# SQLAlchemy setup for PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Float)


# Logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("scraper.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


@retry(
    retry=retry_if_exception_type(requests.RequestException),
    wait=wait_exponential(multiplier=2, min=2, max=8),
    stop=stop_after_attempt(5),
    reraise=True,
)
def fetch_page(url: str) -> str:
    """
    Fetch the HTML content of a given URL with exponential backoff retry.

    Args:
        url: The URL to fetch.

    Returns:
        The HTML content as a string.

    Raises:
        requests.RequestException: If the network request fails after retries.
    """
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def parse_books(html: str) -> List[Dict[str, object]]:
    """
    Parse HTML to extract book titles and prices.

    Args:
        html: The HTML content of the page.

    Returns:
        A list of dictionaries containing 'title' and 'price' keys.
        The price is a float (e.g., 51.77).

    Raises:
        ValueError: If the page structure is not as expected.
    """
    soup = BeautifulSoup(html, "html.parser")
    books = []

    # Each book is inside an <article class="product_pod">
    for article in soup.select("article.product_pod"):
        title_tag = article.select_one("h3 a")
        if title_tag is None:
            logger.warning("Book article missing title link; skipping.")
            continue

        title = title_tag.get("title") or title_tag.get_text(strip=True)

        price_tag = article.select_one("div.product_price p.price_color")
        if price_tag is None:
            raise ValueError(f"Price not found for book: {title}")

        price_text = price_tag.get_text(strip=True)
        # Clean the price: remove currency symbol and convert to float
        price_match = re.search(r"£([0-9]+\.[0-9]{2})", price_text)
        if not price_match:
            raise ValueError(f"Invalid price format: {price_text}")

        price = float(price_match.group(1))
        books.append({"title": title, "price": price})

    return books


def get_next_page_url(html: str, current_url: str) -> str | None:
    """
    Find the URL of the next page from the 'next' button.

    Args:
        html: The HTML content of the current page.
        current_url: The URL of the current page (used for resolution).

    Returns:
        The absolute URL of the next page, or None if there is no next page.
    """
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")
    if next_link is None:
        return None
    return urljoin(current_url, next_link["href"])


def load_from_csv(filename: str = CSV_FILENAME) -> List[Dict[str, object]]:
    """
    Load book data from a local CSV file.

    Args:
        filename: Path to the CSV file.

    Returns:
        List of dicts with 'title' and 'price' keys.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"CSV file not found: {filename}")

    df = pd.read_csv(filename)
    # Normalise column names (in case of whitespace)
    df.columns = [col.strip() for col in df.columns]

    if "title" not in df.columns or "price" not in df.columns:
        raise ValueError("CSV must contain 'title' and 'price' columns")

    # Convert price to float and drop invalid rows
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["title", "price"])

    books = df[["title", "price"]].to_dict(orient="records")
    logger.info("Loaded %d books from %s", len(books), filename)
    return books


def save_to_csv(data: List[Dict[str, object]], filename: str = CSV_FILENAME) -> None:
    """
    Save extracted data to CSV, JSON, and SQLite using pandas.

    Args:
        data: List of dictionaries with keys 'title' and 'price'.
        filename: Output CSV filename (default: books.csv).

    Returns:
        None
    """
    if not data:
        raise ValueError("No data to save.")

    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(filename, index=False)
    logger.info("Saved %d books to %s", len(data), filename)

    # Save to JSON
    try:
        df.to_json(JSON_FILENAME, orient="records")
        logger.info("Saved %d books to %s", len(data), JSON_FILENAME)
    except Exception as exc:
        logger.error("Failed to save JSON: %s", exc)

    # Save to SQLite
    try:
        conn = sqlite3.connect(SQLITE_DB_FILENAME)
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        conn.close()
        logger.info("Saved %d books to SQLite database %s", len(data), SQLITE_DB_FILENAME)
    except Exception as exc:
        logger.error("Failed to save SQLite: %s", exc)


def save_to_postgres(data: List[Dict[str, object]]) -> None:
    """
    Save extracted data to the PostgreSQL database via SQLAlchemy.

    Args:
        data: List of dictionaries with keys 'title' and 'price'.

    Returns:
        None
    """
    if not data:
        raise ValueError("No data to save to PostgreSQL.")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Clear existing rows to avoid duplicates
        db.query(Book).delete()
        db.commit()

        # Insert new books
        for item in data:
            book = Book(title=item["title"], price=item["price"])
            db.add(book)

        db.commit()
        logger.info("Saved %d books to PostgreSQL", len(data))
    except Exception as exc:
        db.rollback()
        logger.error("Failed to save to PostgreSQL: %s", exc)
        raise
    finally:
        db.close()


def main() -> None:
    """Main execution function."""
    all_books = []

    # First check if a local CSV with book data already exists.
    if os.path.exists(CSV_FILENAME):
        logger.info("Found existing %s. Loading data from file.", CSV_FILENAME)
        try:
            all_books = load_from_csv(CSV_FILENAME)
        except (ValueError, FileNotFoundError) as exc:
            logger.error("Failed to load CSV: %s", exc)
            all_books = []
    else:
        logger.info("No local CSV found. Scraping website.")
        url = TARGET_URL

        try:
            # Use tqdm to display a progress bar for the known total number of pages.
            with tqdm(total=TOTAL_PAGES, desc="Scraping pages", unit="page") as pbar:
                while url and pbar.n < TOTAL_PAGES:
                    logger.info("Fetching %s ...", url)
                    html = fetch_page(url)

                    logger.info("Parsing book data ...")
                    books = parse_books(html)
                    all_books.extend(books)

                    next_url = get_next_page_url(html, url)
                    if next_url is None:
                        logger.info("No next page found; stopping.")
                        break

                    # Respect the server: wait before the next request.
                    logger.debug("Waiting %.2f seconds before next request.", REQUEST_DELAY)
                    time.sleep(REQUEST_DELAY)
                    url = next_url
                    pbar.update(1)

        except requests.RequestException as exc:
            logger.error("Network error after retries: %s", exc)
        except (ValueError, AttributeError) as exc:
            logger.error("Parsing error: %s", exc)
        except Exception as exc:
            logger.error("An unexpected error occurred: %s", exc)

    if not all_books:
        logger.error("No books data available for insertion.")
        return

    logger.info("Saving %d books ...", len(all_books))
    # Always write the local files to keep them up-to-date
    save_to_csv(all_books)
    # Save to PostgreSQL (this is what the API and dashboard read)
    save_to_postgres(all_books)
    logger.info(
        "Success: %d books saved to CSV, JSON, SQLite, and PostgreSQL.",
        len(all_books),
    )


if __name__ == "__main__":
    main()
