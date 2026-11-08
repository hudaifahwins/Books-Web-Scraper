"""
Production-ready web scraper for books.toscrape.com.

This script fetches the first page of the books catalogue, extracts each
book's title and price, and saves the data to a CSV file.

Usage:
    python scraper.py
"""

import re
from typing import Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Constants
TARGET_URL = "http://books.toscrape.com"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/119.0.0.0 Safari/537.36"
)
CSV_FILENAME = "books.csv"


def fetch_page(url: str) -> str:
    """
    Fetch the HTML content of a given URL.

    Args:
        url: The URL to fetch.

    Returns:
        The HTML content as a string.

    Raises:
        requests.RequestException: If the network request fails.
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


def save_to_csv(data: List[Dict[str, object]], filename: str = CSV_FILENAME) -> None:
    """
    Save extracted data to a CSV file using pandas.

    Args:
        data: List of dictionaries with keys 'title' and 'price'.
        filename: Output CSV filename.

    Returns:
        None
    """
    if not data:
        raise ValueError("No data to save.")

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)


def main() -> None:
    """Main execution function."""
    try:
        print(f"Fetching {TARGET_URL} ...")
        html = fetch_page(TARGET_URL)

        print("Parsing book data ...")
        books = parse_books(html)

        if not books:
            raise ValueError("No books found on the page.")

        print(f"Saving {len(books)} books to {CSV_FILENAME} ...")
        save_to_csv(books)

        print(f"Success: Scraped {len(books)} books and saved to {CSV_FILENAME}")

    except requests.RequestException as exc:
        print(f"Network error: {exc}")
    except (ValueError, AttributeError) as exc:
        print(f"Parsing error: {exc}")
    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")


if __name__ == "__main__":
    main()
