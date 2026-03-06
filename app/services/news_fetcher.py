"""
Fetches brand-related news articles from:
  - Google News RSS (brand-specific query)
  - Highsnobiety RSS
  - Hypebeast RSS
"""

import feedparser
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus


# Fashion RSS feeds to scan for brand name mentions
RSS_SOURCES = {
    "Highsnobiety": "https://www.highsnobiety.com/feed/",
    "Hypebeast":    "https://hypebeast.com/feed",
}


def _parse_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str).replace(tzinfo=None)
    except Exception:
        return None


def _clean_html(text: str) -> str:
    """Strip HTML tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def _extract_image(entry) -> str | None:
    """Pull thumbnail/media image from an RSS entry."""
    # media:thumbnail
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")
    # media:content
    if hasattr(entry, "media_content") and entry.media_content:
        for m in entry.media_content:
            if m.get("url") and m.get("medium") in (None, "image"):
                return m["url"]
    # enclosures
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if "image" in enc.get("type", ""):
                return enc.get("href") or enc.get("url")
    # <img> inside summary
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.get("summary", ""))
    if match:
        return match.group(1)
    return None


def fetch_google_news(brand_name: str, category: str | None = None) -> list[dict]:
    """Fetch up to 10 recent articles from Google News RSS for a brand."""
    # Add fashion context to disambiguate common words (e.g. "Supreme" → Supreme Court)
    context = "fashion"
    if category == "streetwear":
        context = "streetwear fashion"
    elif category == "luxury":
        context = "luxury fashion"
    query = quote_plus(f'"{brand_name}" {context}')
    url = (
        f"https://news.google.com/rss/search"
        f"?q={query}&hl=en&gl=US&ceid=US:en"
    )
    try:
        feed = feedparser.parse(url)
    except Exception:
        return []

    articles = []
    for entry in feed.entries[:10]:
        # Google News embeds the real source name in <source>
        source = "Google News"
        if hasattr(entry, "source") and entry.source:
            source = entry.source.get("title", "Google News")

        articles.append({
            "title":        entry.get("title", ""),
            "url":          entry.get("link", ""),
            "source":       source,
            "published_at": _parse_date(entry.get("published")),
            "image_url":    None,   # Google News RSS does not include images
            "summary":      _clean_html(entry.get("summary", ""))[:400],
        })
    return articles


def fetch_rss_sources(brand_name: str, category: str | None = None) -> list[dict]:
    """Scan Highsnobiety and Hypebeast RSS feeds for articles mentioning the brand."""
    name_lower = brand_name.lower()
    articles = []

    for source_name, rss_url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(rss_url)
        except Exception:
            continue

        for entry in feed.entries:
            title   = entry.get("title", "")
            summary = entry.get("summary", "")
            if name_lower not in title.lower() and name_lower not in summary.lower():
                continue

            articles.append({
                "title":        title,
                "url":          entry.get("link", ""),
                "source":       source_name,
                "published_at": _parse_date(entry.get("published")),
                "image_url":    _extract_image(entry),
                "summary":      _clean_html(summary)[:400],
            })

    return articles


def fetch_all(brand_name: str, category: str | None = None) -> list[dict]:
    """Combine Google News + fashion RSS, deduplicate by URL."""
    all_articles = fetch_google_news(brand_name, category) + fetch_rss_sources(brand_name, category)

    seen_urls: set[str] = set()
    unique = []
    for a in all_articles:
        url = a.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(a)

    # Sort newest first (None dates go to the end)
    unique.sort(key=lambda a: a["published_at"] or datetime.min, reverse=True)
    return unique
