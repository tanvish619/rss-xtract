from app.database import SessionLocal
from app.services.scraper_executor import execute_scraper
from app.services.article_normalizer import normalize_articles


FEED_VERSION_ID = "3fe6b1e8-effb-40ce-9714-2ae4244ce4f1"
SOURCE_URL = "https://www.bbc.com/news"


db = SessionLocal()

try:
    articles = execute_scraper(
        db=db,
        feed_version_id=FEED_VERSION_ID
    )

    normalized = normalize_articles(
        articles=articles,
        source_url=SOURCE_URL
    )

    print(f"Normalized articles: {len(normalized)}")

    for article in normalized[:3]:
        print(article)

finally:
    db.close()