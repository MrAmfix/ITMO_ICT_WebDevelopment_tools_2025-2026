"""Celery configuration and tasks for async URL parsing."""

import os
from datetime import datetime, timezone

from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL_SYNC = os.getenv(
    "DATABASE_URL_SYNC",
    "postgresql://postgres:postgres@localhost:5432/finance_db",
)

celery_app = Celery(
    "parser_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

sync_engine = create_engine(DATABASE_URL_SYNC)
SyncSession = sessionmaker(sync_engine, class_=Session, expire_on_commit=False)


def _save_parsed_page(url: str, title: str) -> dict:
    """Save a parsed page title to the database (sync)."""
    from app.models.models import ParsedPage

    with SyncSession() as session:
        page = ParsedPage(url=url, title=title, parsed_at=datetime.now(timezone.utc))
        session.add(page)
        session.commit()
        session.refresh(page)
        return {"id": page.id, "url": page.url, "title": page.title}


@celery_app.task(bind=True, name="parse_url")
def parse_url_task(self, url: str) -> dict:
    """Celery task: fetch a URL, extract its <title>, and save to DB."""
    import requests
    from bs4 import BeautifulSoup

    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
    except Exception as e:
        title = f"ERROR: {e}"

    result = _save_parsed_page(url, title)
    return result
