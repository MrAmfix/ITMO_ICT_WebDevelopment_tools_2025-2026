# Task 2 — parallel web page parsing using asyncio + aiohttp
# Uses aiohttp + BeautifulSoup + SQLAlchemy async + asyncpg.

import asyncio
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).parent.parent))
from database import async_session_maker, init_db
from models import ParsedPage

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
CONCURRENCY = 5


async def fetch_title(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch a page and extract its <title>."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            return soup.title.string.strip() if soup.title and soup.title.string else "No title"
    except Exception as e:
        return f"ERROR: {e}"


async def parse_and_save(session: aiohttp.ClientSession, sem: asyncio.Semaphore, url: str) -> dict:
    """Fetch title and save to DB."""
    async with sem:
        title = await fetch_title(session, url)

    async with async_session_maker() as db:
        page = ParsedPage(url=url, title=title, parsed_at=datetime.now(timezone.utc))
        db.add(page)
        await db.commit()
        await db.refresh(page)
        return {"id": page.id, "url": url, "title": title}


async def main():
    await init_db()
    sem = asyncio.Semaphore(CONCURRENCY)

    print(f"Parsing {len(URLS)} URLs with asyncio (concurrency={CONCURRENCY})...")

    start_time = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, sem, url) for url in URLS]
        results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start_time

    print(f"\n=== Async (aiohttp) parser ===")
    print(f"URLs parsed: {len(results)}")
    print(f"Time: {elapsed:.4f} s")
    for r in results:
        title_short = r["title"][:80] + "..." if len(r["title"]) > 80 else r["title"]
        print(f"  [{r['id']}] {r['url']} → {title_short}")


if __name__ == "__main__":
    asyncio.run(main())
