"""Parser endpoints: sync (direct) and async (via Celery queue)."""

import asyncio
import time
from datetime import datetime, timezone

import aiohttp
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from ...core.database import async_session_maker
from ...models.models import ParsedPage

router = APIRouter(prefix="/parse", tags=["parser"])

URLS_DEFAULT = [
    "https://www.python.org",
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://fastapi.tiangolo.com",
    "https://www.sqlalchemy.org",
    "https://github.com",
]


async def _fetch_title(url: str) -> str:
    """Fetch a page and extract its <title>."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"User-Agent": "Mozilla/5.0"},
            ) as resp:
                resp.raise_for_status()
                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                return (
                    soup.title.string.strip()
                    if soup.title and soup.title.string
                    else "No title"
                )
    except Exception as e:
        return f"ERROR: {e}"


# ═══════════════════════════════════════════════
# Subtask 2: Direct synchronous parse via HTTP
# ═══════════════════════════════════════════════

@router.post("/direct")
async def parse_direct(url: str = Query(..., description="URL to parse")):
    """Parse a single URL directly, save to DB, return result (subtask 2)."""
    title = await _fetch_title(url)

    async with async_session_maker() as session:
        page = ParsedPage(url=url, title=title, parsed_at=datetime.now(timezone.utc))
        session.add(page)
        await session.commit()
        await session.refresh(page)
        return {"id": page.id, "url": page.url, "title": page.title}


@router.get("/history")
async def parse_history(limit: int = Query(20, ge=1, le=100)):
    """Get the most recent parsed pages."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(ParsedPage).order_by(ParsedPage.parsed_at.desc()).limit(limit)
        )
        pages = result.scalars().all()
        return [
            {
                "id": p.id,
                "url": p.url,
                "title": p.title,
                "parsed_at": p.parsed_at.isoformat(),
            }
            for p in pages
        ]


# ═══════════════════════════════════════════════
# Subtask 3: Async parse via Celery + Redis queue
# ═══════════════════════════════════════════════

@router.post("/async")
async def parse_async(url: str = Query(..., description="URL to parse")):
    """Enqueue a URL for background parsing via Celery + Redis (subtask 3)."""
    try:
        from ...tasks.celery_tasks import parse_url_task

        task = parse_url_task.delay(url)
        return {
            "message": "Task queued",
            "task_id": task.id,
            "status": "PENDING",
        }
    except ImportError:
        raise HTTPException(status_code=500, detail="Celery is not configured on this server")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {e}")


@router.get("/async/status/{task_id}")
async def parse_async_status(task_id: str):
    """Check the status of a Celery task by its ID."""
    try:
        from celery.result import AsyncResult

        from ...tasks.celery_tasks import celery_app
    except ImportError:
        raise HTTPException(status_code=500, detail="Celery is not configured on this server")

    result = AsyncResult(task_id, app=celery_app)
    response = {"task_id": task_id, "status": result.state}
    if result.state == "SUCCESS":
        response["result"] = result.result
    elif result.state == "FAILURE":
        response["error"] = str(result.info)
    return response


# ═══════════════════════════════════════════════
# Bonus: Batch parsing endpoint (demo)
# ═══════════════════════════════════════════════

@router.post("/batch")
async def parse_batch(urls: list[str] = None):
    """Parse multiple URLs in batch using aiohttp (demo)."""
    if urls is None:
        urls = URLS_DEFAULT

    sem = asyncio.Semaphore(5)

    async def _parse_one(url: str):
        async with sem:
            return await _fetch_title(url)

    start = time.perf_counter()
    titles = await asyncio.gather(*(_parse_one(u) for u in urls))
    elapsed = time.perf_counter() - start

    results = []
    async with async_session_maker() as session:
        for url, title in zip(urls, titles):
            page = ParsedPage(url=url, title=title, parsed_at=datetime.now(timezone.utc))
            session.add(page)
            results.append({"url": url, "title": title})
        await session.commit()

    return {"parsed": len(results), "time_seconds": round(elapsed, 4), "results": results}
