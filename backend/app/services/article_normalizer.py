from urllib.parse import urljoin
from datetime import datetime
import hashlib


def normalize_article(article: dict, source_url: str):
    title = article.get("title")
    link = article.get("link")
    description = article.get("description")
    image = article.get("image")
    author = article.get("author")
    category = article.get("category")
    date = article.get("date")

    # Convert relative URLs into absolute URLs
    if link:
        link = urljoin(source_url, link)

    if image:
        image = urljoin(source_url, image)

    # Generate a stable GUID from the article link
    if link:
        guid = hashlib.sha256(
            link.encode("utf-8")
        ).hexdigest()
    else:
        guid = hashlib.sha256(
            (title or "").encode("utf-8")
        ).hexdigest()

    # Date parsing will be expanded later
    published_at = None

    if date:
        try:
            published_at = datetime.fromisoformat(date)
        except ValueError:
            published_at = None

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


def normalize_articles(
    articles: list[dict],
    source_url: str
):
    normalized = []

    for article in articles:
        normalized_article = normalize_article(
            article,
            source_url
        )

        if not normalized_article["title"] or not normalized_article["link"]:
            continue

        normalized.append(normalized_article)

    return normalized