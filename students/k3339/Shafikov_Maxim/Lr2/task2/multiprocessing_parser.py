# Task 2 — parallel web page parsing using multiprocessing
# Uses requests + BeautifulSoup + multiprocessing.Pool + psycopg2.

import sys
import time
from datetime import datetime, timezone
from multiprocessing import Pool
from pathlib import Path

import psycopg2
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATABASE_URL

SYNC_DSN = DATABASE_URL.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql")

URLS = [
    "https://www.python.org",
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://fastapi.tiangolo.com",
    "https://www.sqlalchemy.org",
    "https://www.djangoproject.com",
    "https://github.com",
    "https://en.wikipedia.org/wiki/Web_scraping",
    "https://httpbin.org",
    "https://pypi.org",
    "https://docs.python.org/3/",
]
NUM_WORKERS = 5


def init_table():
    """Ensure the parsed_page table exists."""
    conn = psycopg2.connect(SYNC_DSN)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parsed_page (
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL,
            title VARCHAR(500) NOT NULL,
            parsed_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def parse_and_save(url: str) -> dict:
    """Fetch a page, extract its title, save to DB."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
    except Exception as e:
        title = f"ERROR: {e}"

    conn = psycopg2.connect(SYNC_DSN)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO parsed_page (url, title, parsed_at) VALUES (%s, %s, %s) RETURNING id",
        (url, title, datetime.now(timezone.utc)),
    )
    row_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {"id": row_id, "url": url, "title": title}


def main():
    init_table()
    print(f"Parsing {len(URLS)} URLs with {NUM_WORKERS} processes...")

    start_time = time.perf_counter()

    with Pool(processes=NUM_WORKERS) as pool:
        results = pool.map(parse_and_save, URLS)

    elapsed = time.perf_counter() - start_time

    print(f"\n=== Multiprocessing parser ===")
    print(f"URLs parsed: {len(results)}")
    print(f"Time: {elapsed:.4f} s")
    for r in results:
        title_short = r["title"][:80] + "..." if len(r["title"]) > 80 else r["title"]
        print(f"  [{r['id']}] {r['url']} → {title_short}")


if __name__ == "__main__":
    main()
