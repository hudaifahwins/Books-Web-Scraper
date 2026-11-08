"""
Production-ready web scraper for books.toscrape.com.

This script fetches all pages of the books catalogue, extracts each
book's title and price, and saves the data to CSV, JSON, and SQLite.
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


def main() -> None:
    """Main execution function."""
    all_books = []
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

        if not all_books:
            raise ValueError("No books found.")

        logger.info("Saving %d books ...", len(all_books))
        save_to_csv(all_books)
        logger.info(
            "Success: Scraped %d books and saved to CSV, JSON, and SQLite.",
            len(all_books),
        )

    except requests.RequestException as exc:
        logger.error("Network error after retries: %s", exc)
    except (ValueError, AttributeError) as exc:
        logger.error("Parsing error: %s", exc)
    except Exception as exc:
        logger.error("An unexpected error occurred: %s", exc)


if __name__ == "__main__":
    main()
