import re
from bs4 import BeautifulSoup, Tag


NON_ARTICLE_PARENTS = {
    "nav", "header", "footer", "aside", "form", "script", "style", "noscript", "menu"
}

NON_ARTICLE_CLASS_SUBSTRINGS = [
    "nav", "menu", "footer", "header", "sidebar", "breadcrumb", "pagination",
    "cookie", "modal", "popup", "banner", "advert", "search", "widget-social"
]

ARTICLE_SEMANTIC_CLASSES = [
    "article", "news", "press", "release", "card", "story", "entry",
    "post", "teaser", "media", "item", "report", "publication"
]

GENERIC_LAYOUT_CLASSES = {
    "row", "col", "container", "flex", "grid", "d-flex", "d-block", "d-none",
    "w-100", "h-100", "wrapper", "clearfix", "active", "hover", "focus",
    "section", "content", "main", "body"
}


def parse_html(html: str):
    soup = BeautifulSoup(html, "html.parser")

    return {
        "title": soup.title.get_text(strip=True) if soup.title else None,
        "links": [
            {
                "text": link.get_text(" ", strip=True),
                "href": link.get("href"),
            }
            for link in soup.find_all("a", href=True)
        ],
    }


def is_inside_non_article_area(element: Tag) -> bool:
    """Check if the element or its ancestors are located inside a header, navigation, footer, or sidebar."""
    current = element
    while current and isinstance(current, Tag):
        if current.name in NON_ARTICLE_PARENTS:
            return True
        classes = " ".join(current.get("class") or []).lower()
        elem_id = str(current.get("id") or "").lower()
        role = str(current.get("role") or "").lower()

        if role in ("navigation", "banner", "contentinfo", "search"):
            return True

        for sub in ["nav", "menu", "footer", "header", "breadcrumb", "pagination", "cookie", "modal", "onetrust", "ot-", "didomi", "consent"]:
            if sub in classes or sub in elem_id:
                # Avoid false-positive if class is 'news-header' or 'article-header'
                if sub == "header" and any(k in classes or k in elem_id for k in ["article", "news", "press", "post", "card"]):
                    continue
                return True

        current = current.parent
    return False


def build_container_selector(tag_name: str, classes: list[str], parent: Tag | None = None) -> str | None:
    """Build a clean, robust CSS selector for a container group."""
    clean_classes = [
        c for c in classes
        if c.lower() not in GENERIC_LAYOUT_CLASSES
        and not c.startswith("ng-")
        and not c.startswith("v-")
        and not c.startswith("data-")
        and not c.startswith("_")
        and ":" not in c
        and "[" not in c
    ]

    semantic = [c for c in clean_classes if any(k in c.lower() for k in ARTICLE_SEMANTIC_CLASSES)]
    
    if semantic:
        base_sel = f"{tag_name}.{semantic[0]}"
    elif clean_classes:
        base_sel = f"{tag_name}.{clean_classes[0]}"
    elif tag_name == "article":
        base_sel = "article"
    elif "-" in tag_name and any(k in tag_name for k in ["card", "item", "article", "media", "post"]):
        base_sel = tag_name
    elif tag_name == "li" and parent and parent.name in ("ul", "ol"):
        p_classes = [c for c in (parent.get("class") or []) if c.lower() not in GENERIC_LAYOUT_CLASSES]
        if p_classes:
            return f"{parent.name}.{p_classes[0]} > li"
        return "li"
    else:
        # Bare generic div without classes should not become a top container candidate
        return None

    if parent and isinstance(parent, Tag) and parent.name not in ("body", "html", "main"):
        p_classes = [
            c for c in (parent.get("class") or [])
            if c.lower() not in GENERIC_LAYOUT_CLASSES and not c.startswith("_")
        ]
        p_semantic = [c for c in p_classes if any(k in c.lower() for k in ARTICLE_SEMANTIC_CLASSES)]
        if p_semantic:
            return f"{parent.name}.{p_semantic[0]} > {base_sel}"
        elif p_classes and not semantic:
            return f"{parent.name}.{p_classes[0]} > {base_sel}"

    return base_sel


def detect_article_candidates(html: str):
    """
    Intelligently detect, score, and rank repeating article/news containers on the page.
    Filters out navigation, header, footer, and sidebar noise.
    """
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script, style, noscript tags to avoid skewing text analysis
    for s in soup(["script", "style", "noscript", "svg"]):
        s.decompose()

    candidates = []
    seen_signatures = set()

    # Step 1: Scan for repeating sibling container groups in parents
    parents = soup.find_all(lambda t: len(t.find_all(recursive=False)) >= 2)

    for parent in parents:
        if is_inside_non_article_area(parent):
            continue

        children = [c for c in parent.find_all(recursive=False) if isinstance(c, Tag) and c.name not in ("script", "style")]
        if len(children) < 2:
            continue

        # Group siblings by tag + primary class
        groups: dict[tuple, list[Tag]] = {}
        for child in children:
            c_classes = tuple(sorted(child.get("class") or []))
            key = (child.name, c_classes)
            groups.setdefault(key, []).append(child)

        for (tag_name, class_tuple), items in groups.items():
            count = len(items)
            if count < 2 or count > 200:
                continue

            classes_list = list(class_tuple)
            selector = build_container_selector(tag_name, classes_list, parent)
            if not selector:
                continue

            sig = (tag_name, class_tuple, parent.name)
            if sig in seen_signatures:
                continue
            seen_signatures.add(sig)

            # Score this candidate group
            score = 0
            
            # Repetition score
            if 3 <= count <= 50:
                score += 20
            elif count == 2 or 51 <= count <= 100:
                score += 10
            else:
                score -= 10

            # Content analysis across items
            headings_count = 0
            links_count = 0
            dates_count = 0
            images_count = 0
            total_text_len = 0
            sample_title = None
            sample_link = None
            sample_date = None

            for it in items[:10]:
                text = it.get_text(" ", strip=True)
                total_text_len += len(text)

                heading = it.find(["h1", "h2", "h3", "h4", "h5", "h6"])
                if heading:
                    headings_count += 1
                    if not sample_title:
                        sample_title = heading.get_text(" ", strip=True)

                a_tag = it if it.name == "a" and it.get("href") else it.find("a", href=True)
                if a_tag and a_tag.get("href"):
                    href = a_tag.get("href", "").strip()
                    if not href.startswith("javascript:") and not href.startswith("#") and len(href) > 1:
                        links_count += 1
                        if not sample_link:
                            sample_link = href
                        if not sample_title and a_tag.get_text(strip=True):
                            sample_title = a_tag.get_text(" ", strip=True)

                time_tag = it.find(["time", lambda t: t.has_attr("datetime") or t.has_attr("data-date")])
                if time_tag:
                    dates_count += 1
                    if not sample_date:
                        sample_date = time_tag.get("datetime") or time_tag.get_text(strip=True)
                elif re.search(r"\b(202[0-9]|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b", text, re.I):
                    dates_count += 1

                if it.find("img"):
                    images_count += 1

            sample_size = min(len(items), 10)
            avg_text_len = total_text_len / sample_size if sample_size else 0

            # Score attributes
            if headings_count >= max(1, sample_size // 2):
                score += 35
            elif headings_count > 0:
                score += 15

            if links_count >= max(1, sample_size // 2):
                score += 30
            elif links_count > 0:
                score += 15

            if dates_count >= max(1, sample_size // 3):
                score += 20
            elif dates_count > 0:
                score += 10

            if images_count > 0:
                score += 10

            # Semantic classes score
            all_classes_str = " ".join(classes_list).lower()
            if any(k in all_classes_str for k in ARTICLE_SEMANTIC_CLASSES) or tag_name == "article":
                score += 30

            # Text length scoring & penalties
            if 40 <= avg_text_len <= 3000:
                score += 25
            elif avg_text_len < 25:
                score -= 45  # Penalty: likely menu or navigation items
            elif avg_text_len < 40:
                score -= 15

            # Penalize if mostly links and very short text
            if links_count >= sample_size and avg_text_len < 35:
                score -= 30

            sample_item = items[0]
            first_text = sample_item.get_text(" ", strip=True)[:300]

            candidates.append({
                "tag": tag_name,
                "class": classes_list,
                "id": sample_item.get("id"),
                "selector": selector,
                "match_count": count,
                "score": score,
                "sample_title": sample_title,
                "sample_link": sample_link,
                "sample_date": sample_date,
                "text": first_text,
            })

    # Sort candidates by score descending
    candidates.sort(key=lambda c: c["score"], reverse=True)

    # Deduplicate candidate list while preserving top-scoring entries
    filtered_candidates = []
    seen_selectors = set()
    for cand in candidates:
        if cand["score"] <= 0:
            continue
        if cand["selector"] not in seen_selectors:
            seen_selectors.add(cand["selector"])
            filtered_candidates.append(cand)
            if len(filtered_candidates) >= 20:
                break

    return filtered_candidates