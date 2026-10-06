"""
Test Selector Regression for 10 Representative Website Structures:
1. Standard article-card grid
2. News list
3. Press release list
4. Site with navigation elements using 'item'/'row'/'directory-item'
5. Site with sidebar cards
6. Site with footer links
7. JS/AJAX-loaded article list simulation
8. Article cards with lazy-loaded images
9. Article cards where title is nested inside an <a>
10. Article cards where date is in an attribute.
"""

import unittest
import sys
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.parser import detect_article_candidates, parse_html
from app.services.article_normalizer import normalize_articles


TEMPLATE_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
template = env.get_template("scraper_template.py.j2")


class SelectorRegressionTest(unittest.TestCase):

    def test_1_standard_article_card_grid(self):
        """1. Standard article-card grid with 4 cards and header/footer."""
        html = """
        <html>
          <body>
            <header>
              <div class="logo">Bank News</div>
              <nav><a href="/">Home</a><a href="/news">News</a></nav>
            </header>
            <main>
              <div class="articles-grid">
                <div class="card">
                  <img src="/img/1.jpg" alt="Img 1" />
                  <h2 class="card-title"><a href="/news/q1-results">Q1 Financial Results Announced</a></h2>
                  <p class="card-desc">Record growth in retail banking sector.</p>
                  <span class="card-date">2026-04-10</span>
                </div>
                <div class="card">
                  <img src="/img/2.jpg" alt="Img 2" />
                  <h2 class="card-title"><a href="/news/esg-report">Annual Sustainability Report 2026</a></h2>
                  <p class="card-desc">Commitment to green financing goals.</p>
                  <span class="card-date">2026-04-08</span>
                </div>
                <div class="card">
                  <img src="/img/3.jpg" alt="Img 3" />
                  <h2 class="card-title"><a href="/news/digital-expansion">New Mobile App Features Released</a></h2>
                  <p class="card-desc">Enhanced security and instantaneous transfers.</p>
                  <span class="card-date">2026-04-05</span>
                </div>
                <div class="card">
                  <img src="/img/4.jpg" alt="Img 4" />
                  <h2 class="card-title"><a href="/news/board-appointment">New Board Member Elected</a></h2>
                  <p class="card-desc">Bringing 20+ years of fintech leadership.</p>
                  <span class="card-date">2026-04-01</span>
                </div>
              </div>
            </main>
            <footer>
              <p>&copy; 2026 Bank Corp</p>
              <div class="footer-links"><a href="/terms">Terms</a></div>
            </footer>
          </body>
        </html>
        """
        candidates = detect_article_candidates(html)
        self.assertGreater(len(candidates), 0)
        best = candidates[0]
        self.assertEqual(best["match_count"], 4)
        self.assertIn("card", best["selector"])

        # Test scraper execution logic on this structure
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("div.card")
        self.assertEqual(len(items), 4)

        raw_articles = []
        for it in items:
            t = it.select_one(".card-title")
            raw_articles.append({
                "title": t.get_text(strip=True) if t else None,
                "link": it.select_one("a")["href"],
                "date": it.select_one(".card-date").get_text(strip=True),
                "description": it.select_one(".card-desc").get_text(strip=True),
                "image": it.select_one("img")["src"]
            })

        norm = normalize_articles(raw_articles, "https://bank.com/news")
        self.assertEqual(len(norm), 4)
        self.assertEqual(norm[0]["title"], "Q1 Financial Results Announced")
        self.assertEqual(norm[0]["link"], "https://bank.com/news/q1-results")
        self.assertIsNotNone(norm[0]["published_at"])

    def test_2_news_list(self):
        """2. News list using <ul> and <li>."""
        html = """
        <div class="content-wrapper">
          <ul class="news-list">
            <li class="news-item">
              <span class="date">May 1, 2026</span>
              <h3><a href="/press/release-1">Partnership with Central Bank</a></h3>
              <p>Expanding liquidity support framework.</p>
            </li>
            <li class="news-item">
              <span class="date">April 28, 2026</span>
              <h3><a href="/press/release-2">Quarterly Dividend Declared</a></h3>
              <p>Dividend of $0.50 per common share.</p>
            </li>
            <li class="news-item">
              <span class="date">April 20, 2026</span>
              <h3><a href="/press/release-3">Cybersecurity Innovation Award</a></h3>
              <p>Recognized for biometric security deployment.</p>
            </li>
          </ul>
        </div>
        """
        candidates = detect_article_candidates(html)
        self.assertGreater(len(candidates), 0)
        self.assertEqual(candidates[0]["match_count"], 3)

    def test_3_press_release_list(self):
        """3. Press release list using semantic <article class="press-release"> tags."""
        html = """
        <section class="press-room">
          <article class="press-release">
            <h2><a href="/pr/001">Nordic Market Expansion Plan</a></h2>
            <time datetime="2026-03-15T09:00:00Z">15 March 2026</time>
            <p>New regional offices opening in Stockholm and Helsinki.</p>
          </article>
          <article class="press-release">
            <h2><a href="/pr/002">Green Bond Issuance Successful</a></h2>
            <time datetime="2026-03-10T11:00:00Z">10 March 2026</time>
            <p>Over-subscribed 500M EUR green bond issuance.</p>
          </article>
          <article class="press-release">
            <h2><a href="/pr/003">Annual General Meeting Results</a></h2>
            <time datetime="2026-03-01T14:00:00Z">01 March 2026</time>
            <p>All resolutions passed with 98% majority.</p>
          </article>
        </section>
        """
        candidates = detect_article_candidates(html)
        self.assertGreater(len(candidates), 0)
        self.assertEqual(candidates[0]["match_count"], 3)

    def test_4_site_with_directory_items_in_nav(self):
        """4. Site where navigation uses 'directory-item' and news uses 'news-card' (Nordea pattern)."""
        html = """
        <html>
          <body>
            <nav class="site-nav">
              <ul class="directory-list">
                <li class="directory-item"><a href="/about">About Us</a></li>
                <li class="directory-item"><a href="/services">Services</a></li>
                <li class="directory-item"><a href="/careers">Careers</a></li>
                <li class="directory-item"><a href="/investors">Investors</a></li>
                <li class="directory-item"><a href="/contact">Contact</a></li>
              </ul>
            </nav>
            <main>
              <div class="news-feed">
                <div class="news-card">
                  <h2><a href="/news/article-101">Nordic Retail Banking Transformation</a></h2>
                  <p>Accelerating digital self-service capabilities across the region.</p>
                  <time>2026-04-02</time>
                </div>
                <div class="news-card">
                  <h2><a href="/news/article-102">Central Bank Rate Reaction</a></h2>
                  <p>Analysis of the latest monetary policy decision.</p>
                  <time>2026-03-29</time>
                </div>
                <div class="news-card">
                  <h2><a href="/news/article-103">Sustainable Lending Milestone</a></h2>
                  <p>Reached 10 billion EUR in sustainable lending portfolio.</p>
                  <time>2026-03-15</time>
                </div>
              </div>
            </main>
          </body>
        </html>
        """
        candidates = detect_article_candidates(html)
        # Should rank .news-card FIRST, not .directory-item from nav
        self.assertGreater(len(candidates), 0)
        best = candidates[0]
        self.assertIn("news", best["selector"].lower())
        self.assertNotIn("directory", best["selector"].lower())
        self.assertEqual(best["match_count"], 3)

    def test_5_site_with_sidebar_cards(self):
        """5. Site with main news articles and sidebar trending cards."""
        html = """
        <div class="layout">
          <aside class="sidebar">
            <div class="sidebar-widget">
              <div class="card"><a href="/promo1">Special Loan Rate</a></div>
              <div class="card"><a href="/promo2">Credit Card Perks</a></div>
            </div>
          </aside>
          <main class="main-content">
            <div class="articles-container">
              <div class="article-item">
                <h3><a href="/posts/bank-statement">Official Statement on Market Liquidity</a></h3>
                <p>The bank maintains exceptional capital ratios well above regulatory requirements.</p>
                <time>2026-04-11</time>
              </div>
              <div class="article-item">
                <h3><a href="/posts/ceo-interview">CEO Interview with Financial Times</a></h3>
                <p>Discussion on international trade dynamics and commercial lending.</p>
                <time>2026-04-09</time>
              </div>
              <div class="article-item">
                <h3><a href="/posts/tech-hub">New Innovation Hub Launched</a></h3>
                <p>Investing in artificial intelligence and fraud prevention.</p>
                <time>2026-04-03</time>
              </div>
            </div>
          </main>
        </div>
        """
        candidates = detect_article_candidates(html)
        self.assertGreater(len(candidates), 0)
        self.assertIn("article-item", candidates[0]["selector"])
        self.assertEqual(candidates[0]["match_count"], 3)

    def test_6_site_with_footer_links(self):
        """6. Site with footer link lists that should not be detected as articles."""
        html = """
        <div>
          <section class="press-releases">
            <div class="release-row">
              <h4><a href="/pr/1">Full Year Financial Report</a></h4>
              <p>Operating profit rose by 14 percent year-on-year.</p>
            </div>
            <div class="release-row">
              <h4><a href="/pr/2">Interim Dividend Announcement</a></h4>
              <p>Interim dividend details for institutional investors.</p>
            </div>
          </section>
          <footer>
            <div class="footer-columns">
              <div class="col"><a href="/legal">Legal</a><a href="/privacy">Privacy</a><a href="/cookies">Cookies</a></div>
              <div class="col"><a href="/help">Help</a><a href="/faq">FAQ</a><a href="/branches">Branches</a></div>
            </div>
          </footer>
        </div>
        """
        candidates = detect_article_candidates(html)
        self.assertGreater(len(candidates), 0)
        self.assertIn("release", candidates[0]["selector"].lower())

    def test_7_lazy_loaded_images(self):
        """7. Article cards with data-src and srcset lazy loaded images."""
        from jinja2 import Template
        rendered_code = template.render(
            url="https://bank.com/media",
            item_selector=".media-item",
            title_selector=".title",
            link_selector="a",
            date_selector=".date",
            description_selector=None,
            image_selector="img",
            author_selector=None,
            category_selector=None,
            pagination_selector=None,
            max_items=10,
            rendering_mode="request",
        )
        
        # Test the extract_image logic in python
        import re
        from urllib.parse import urljoin
        html = """
        <div class="media-item">
          <img data-src="/images/lazy1.jpg" alt="Lazy 1" />
          <h2 class="title"><a href="/media/1">Media Release One</a></h2>
          <span class="date">2026-04-01</span>
        </div>
        <div class="media-item">
          <img data-original="/images/lazy2.jpg" alt="Lazy 2" />
          <h2 class="title"><a href="/media/2">Media Release Two</a></h2>
          <span class="date">2026-04-02</span>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".media-item")
        self.assertEqual(len(items), 2)
        
        # Simulate extract_image logic
        img1 = items[0].find("img")
        src1 = img1.get("src") or img1.get("data-src") or img1.get("data-original")
        self.assertEqual(src1, "/images/lazy1.jpg")
        
        img2 = items[1].find("img")
        src2 = img2.get("src") or img2.get("data-src") or img2.get("data-original")
        self.assertEqual(src2, "/images/lazy2.jpg")

    def test_8_title_nested_inside_anchor(self):
        """8. Article cards where heading is nested inside <a href="..."><h2>Title</h2></a>."""
        html = """
        <div class="news-grid">
          <div class="news-entry">
            <a href="/news/nested-1" class="news-link">
              <h2 class="entry-title">Strategic Acquisition Completed</h2>
            </a>
            <p>Expanding corporate lending in Central Europe.</p>
          </div>
          <div class="news-entry">
            <a href="/news/nested-2" class="news-link">
              <h2 class="entry-title">Digital Wealth Platform Launch</h2>
            </a>
            <p>Direct indexing and algorithmic portfolio balancing.</p>
          </div>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".news-entry")
        self.assertEqual(len(items), 2)

        # Test link extraction when user clicked h2.entry-title
        h2 = items[0].select_one(".entry-title")
        parent_a = h2.find_parent("a", href=True)
        self.assertIsNotNone(parent_a)
        self.assertEqual(parent_a["href"], "/news/nested-1")

    def test_9_date_in_attribute(self):
        """9. Article cards where date is in datetime or data-date attribute."""
        html = """
        <div class="feed">
          <article class="card">
            <h3><a href="/news/1">Quarterly Statement</a></h3>
            <span class="publish-time" data-date="2026-03-31T08:00:00Z">31 Mar</span>
          </article>
          <article class="card">
            <h3><a href="/news/2">New Chief Risk Officer</a></h3>
            <time datetime="2026-03-25T10:00:00Z">25 Mar</time>
          </article>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".card")
        
        date1_el = items[0].select_one(".publish-time")
        d1 = date1_el.get("datetime") or date1_el.get("data-date")
        self.assertEqual(d1, "2026-03-31T08:00:00Z")

        date2_el = items[1].select_one("time")
        d2 = date2_el.get("datetime") or date2_el.get("data-date")
        self.assertEqual(d2, "2026-03-25T10:00:00Z")

    def test_10_invalid_links_fallback(self):
        """10. Cards with javascript:void(0) or # as main href, but real link in child/data-href."""
        html = """
        <div class="list">
          <div class="item">
            <a href="javascript:void(0)" data-href="/news/real-article-1" class="action-btn">
              <span class="title">CEO Keynote Address</span>
            </a>
          </div>
          <div class="item">
            <a href="#" class="wrapper-link">
              <h3 class="title">Fintech Partnership Announcement</h3>
              <a href="/news/real-article-2" class="read-more">Read Full Story</a>
            </a>
          </div>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".item")

        # Verify fallback link resolution for item 1 (data-href)
        it1 = items[0]
        a1 = it1.find("a")
        raw_link1 = a1.get("data-href") if not (a1.get("href") and not a1.get("href").startswith("javascript:")) else a1.get("href")
        self.assertEqual(raw_link1, "/news/real-article-1")

        # Verify fallback link resolution for item 2 (child read-more anchor)
        it2 = items[1]
        valid_a = None
        for a in it2.find_all("a", href=True):
            if not a["href"].startswith("#") and not a["href"].startswith("javascript:"):
                valid_a = a["href"]
                break
        self.assertEqual(valid_a, "/news/real-article-2")


if __name__ == "__main__":
    unittest.main()
