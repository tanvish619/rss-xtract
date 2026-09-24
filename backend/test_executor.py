from app.database import SessionLocal
from app.services.scraper_executor import execute_scraper


FEED_VERSION_ID = "afd05993-d31e-41ab-af93-d7b381eeedef"


db = SessionLocal()

try:
    articles = execute_scraper(
        db=db,
        feed_version_id=FEED_VERSION_ID
    )

    print(f"Articles returned: {len(articles)}")

    for article in articles[:3]:
        print(article)

finally:
    db.close()