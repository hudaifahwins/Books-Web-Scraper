# 🕸️ BookScraper Pro: Enterprise Data Pipeline

> A full-stack, cloud-native application that scrapes, stores, and visualizes 1,000+ book records with a premium, interactive dashboard.

**[🚀 View Live Demo](https://hudaifahwins.github.io/Books-Web-Scraper/)** | **[📚 API Documentation](https://books-web-scraper.onrender.com/docs)**

![BookScraper Pro Dashboard](https://img.shields.io/badge/Status-Live-success) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![Docker](https://img.shields.io/badge/Docker-Ready-blue) ![License](https://img.shields.io/badge/License-MIT-purple)

## 🏗️ Architecture Overview

BookScraper Pro is not just a script; it is a fully decoupled, 3-tier cloud application deployed across multiple free-tier providers.

1. **Frontend (GitHub Pages):** A highly custom, dark-mode UI built with Tailwind CSS and Chart.js. Features a floating navigation bar, real-time search, and dynamic data visualizations.
2. **Backend API (Render):** A Dockerized Python `FastAPI` microservice. Handles all business logic, database connections, and serves the REST API.
3. **Database (Neon):** A serverless PostgreSQL database hosting the scraped book records. 
4. **Scraper (Python):** An automated data pipeline using `BeautifulSoup` and `Pandas` to extract, clean, and push data to the database.

```text
[ Web Scraper ] ---> [ Neon PostgreSQL DB ]
                             |
                             v
[ GitHub Pages Frontend ] <---> [ Render FastAPI Backend ]
