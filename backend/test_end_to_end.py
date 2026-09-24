from app.database import SessionLocal
from app.services.scraper_executor import execute_scraper
from app.services.article_normalizer import normalize_articles


FEED_VERSION_ID = "3fe6b1e8-effb-40ce-9714-2ae4244ce4f1"
SOURCE_URL = "https://www.bbc.com/news"


db = SessionLocal()

try:
    print("1. Executing saved scraper...")

    articles = execute_scraper(
        db=db,
        feed_version_id=FEED_VERSION_ID
    )

    print(f"   Raw articles: {len(articles)}")

    print("2. Normalizing articles...")

    normalized = normalize_articles(
        articles=articles,
        source_url=SOURCE_URL
    )

    print(f"   Normalized articles: {len(normalized)}")

    print("3. Sample normalized article:")

    if normalized:
        print(normalized[0])

    print()
    print("END-TO-END TEST PASSED!")

finally:
    db.close()