# 🕸️ BookScraper Pro

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)

**Enterprise‑grade web scraper for extracting book data from [books.toscrape.com](http://books.toscrape.com) with robust retry logic, structured logging, and multi‑format output.**

---

## Overview

BookScraper Pro is a production‑ready Python scraper that extracts book titles and prices from the demo bookstore. It includes exponential backoff retries, structured logging, and exports results to CSV, JSON, and SQLite — all containerized with Docker for easy deployment.

---

## Features

- 🔄 **Tenacity Retry** – Automatic retry with exponential backoff (2s, 4s, 8s) on 429/500 network errors.
- 🧾 **Structured Logging** – Logs to console and `scraper.log` with timestamps and levels.
- 📊 **Multi‑Format Output** – Saves data to `books.csv`, `books.json`, and `books.db` (SQLite).
- 🐳 **Dockerized** – Simple one‑command containerization with `docker-compose`.
- 🔧 **Configurable** – Target URL and request delay configurable via `.env`.

---

## Architecture

