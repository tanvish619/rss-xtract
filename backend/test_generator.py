from app.database import SessionLocal
from app.services.scraper_generator import generate_scraper


FEED_VERSION_ID = "3fe6b1e8-effb-40ce-9714-2ae4244ce4f1"


db = SessionLocal()

try:
    result = generate_scraper(
        db=db,
        feed_version_id=FEED_VERSION_ID
    )

    print("Scraper generated successfully!")
    print(f"Version: {result['version']}")
    print(f"Scraper: {result['scraper_path']}")
    print(f"Config: {result['config_path']}")

finally:
    db.close()