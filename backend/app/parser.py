from bs4 import BeautifulSoup


def parse_html(html: str):
    soup = BeautifulSoup(html, "lxml")

    return {
        "title": soup.title.get_text(strip=True) if soup.title else None,
        "links": [
            {
                "text": link.get_text(" ", strip=True),
                "href": link.get("href")
            }
            for link in soup.find_all("a", href=True)
        ]
    }


def detect_article_candidates(html: str):
    soup = BeautifulSoup(html, "lxml")

    candidates = []

    # Look for semantic article elements
    for article in soup.find_all("article"):
        candidates.append({
            "tag": "article",
            "class": article.get("class"),
            "id": article.get("id"),
            "text": article.get_text(" ", strip=True)[:300]
        })

    # Look for common article-related class names
    common_classes = [
        "article",
        "post",
        "story",
        "news-item",
        "article-item"
    ]

    for class_name in common_classes:
        for element in soup.find_all(
            class_=lambda value: value and class_name in value
        ):
            candidates.append({
                "tag": element.name,
                "class": element.get("class"),
                "id": element.get("id"),
                "text": element.get_text(" ", strip=True)[:300]
            })

    return candidates