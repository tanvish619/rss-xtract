from urllib.parse import urljoin
from datetime import datetime, timezone
import hashlib
import re
from dateutil import parser as date_parser


def parse_flexible_date(date_str: str | None) -> datetime | None:
    if not date_str or not isinstance(date_str, str):
        return None

    cleaned = date_str.strip()
    if not cleaned:
        return None

    # Try ISO format directly
    try:
        dt = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass

    # Try dateutil parser with fuzzy matching
    try:
        dt = date_parser.parse(cleaned, fuzzy=True)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass

    return None


def clean_text(text: str | None) -> str | None:
    if not text or not isinstance(text, str):
        return None
    # Normalize multiple whitespace and newlines to single spaces
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned if cleaned else None


def is_valid_article_url(url: str | None) -> bool:
    if not url or not isinstance(url, str):
        return False
    u = url.strip().lower()
    if u.startswith("javascript:") or u.startswith("#") or u.startswith("mailto:") or u.startswith("tel:"):
        return False
    return u.startswith("http://") or u.startswith("https://")


def normalize_article(article: dict, source_url: str) -> dict:
    title = clean_text(article.get("title"))
    link = article.get("link")
    description = clean_text(article.get("description"))
    image = article.get("image")
    author = clean_text(article.get("author"))
    category = clean_text(article.get("category"))
    date_val = article.get("date")

    # Convert relative URLs into absolute URLs
    if link and isinstance(link, str):
        link = urljoin(source_url, link.strip())
        # Strip fragment-only suffix like #section
        if "#" in link:
            base_part, fragment = link.split("#", 1)
            # If the base URL is non-empty, keep base URL
            if base_part and base_part != source_url.rstrip("/") + "/":
                link = base_part

    if image and isinstance(image, str):
        image = urljoin(source_url, image.strip())

    if not is_valid_article_url(link):
        link = None

    # Sanitize title: if title is too long (> 350 chars), take the first sentence or chunk
    if title and len(title) > 350:
        sentences = re.split(r"(?<=[.!?])\s+", title)
        title = sentences[0] if sentences and len(sentences[0]) > 10 else title[:300] + "..."

    # Generate a stable GUID from the article link or title
    if link:
        guid = hashlib.sha256(link.encode("utf-8")).hexdigest()
    else:
        guid = hashlib.sha256((title or "").encode("utf-8")).hexdigest()

    published_at = parse_flexible_date(date_val)

    return {
        "guid": guid,
        "title": title,
        "link": link,
        "description": description,
        "content": None,
        "image_url": image,
        "author": author,
        "category": category,
        "published_at": published_at,
    }


def normalize_articles(articles: list[dict], source_url: str) -> list[dict]:
    normalized = []
    seen_links = set()

    for article in articles:
        normalized_article = normalize_article(article, source_url)

        # Must have title and valid link
        if not normalized_article["title"] or not normalized_article["link"]:
            continue

        # Prevent duplicate entries within the same scraper run
        link_key = normalized_article["link"]
        if link_key in seen_links:
            continue
        seen_links.add(link_key)

        normalized.append(normalized_article)

    return normalized