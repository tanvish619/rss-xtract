from datetime import datetime, timezone
from email.utils import format_datetime
from xml.etree.ElementTree import Element, SubElement, indent, tostring


def format_pub_date(value):
    if value is None:
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return format_datetime(value)


def build_rss(
    feed_title: str,
    feed_description: str,
    feed_url: str,
    articles: list[dict],
) -> str:

    rss = Element(
        "rss",
        {
            "version": "2.0",
            "xmlns:media": "http://search.yahoo.com/mrss/",
        },
    )

    channel = SubElement(rss, "channel")

    title = SubElement(channel, "title")
    title.text = feed_title

    link = SubElement(channel, "link")
    link.text = feed_url

    description = SubElement(channel, "description")
    description.text = feed_description or feed_title

    last_build = SubElement(channel, "lastBuildDate")
    last_build.text = format_datetime(
        datetime.now(timezone.utc)
    )

    for article in articles:
        item = SubElement(channel, "item")

        title_element = SubElement(item, "title")
        title_element.text = article.get("title") or "Untitled"

        link_element = SubElement(item, "link")
        link_element.text = article.get("link") or ""

        guid = SubElement(item, "guid")
        guid.set("isPermaLink", "false")
        guid.text = article.get("guid") or ""

        description_element = SubElement(
            item,
            "description",
        )
        description_element.text = (
            article.get("description") or ""
        )

        author = article.get("author")

        if author:
            author_element = SubElement(
                item,
                "author",
            )
            author_element.text = author

        category = article.get("category")

        if category:
            category_element = SubElement(
                item,
                "category",
            )
            category_element.text = category

        published_at = article.get("published_at")

        if published_at:
            pub_date = SubElement(
                item,
                "pubDate",
            )
            pub_date.text = format_pub_date(
                published_at
            )

        image_url = article.get("image_url")

        if image_url:
            enclosure = SubElement(
                item,
                "enclosure",
            )
            enclosure.set("url", image_url)
            enclosure.set("type", "image/jpeg")

    # Pretty-print the tree in-place with 4-space indentation
    # (xml.etree.ElementTree.indent is available from Python 3.9+)
    indent(rss, space="    ")

    xml_body = tostring(
        rss,
        encoding="unicode",
        xml_declaration=False,
    )

    # Prepend a clean XML declaration with double-quoted attributes
    return '<?xml version="1.0" encoding="utf-8"?>\n' + xml_body
