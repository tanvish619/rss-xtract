import sys
import time
from pathlib import Path
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.fetcher import fetch_page
from app.parser import detect_article_candidates
from app.services.article_normalizer import normalize_articles


SITES = [
    (1, "BNP Paribas", "France", "https://invest.bnpparibas/en/search/reports/documents/press-release"),
    (2, "HSBC Holdings", "UK", "https://www.hsbc.com/news-and-views/news"),
    (3, "Crédit Agricole Group", "France", "https://www.credit-agricole.com/en/all-press-releases"),
    (4, "Banco Santander", "Spain", "https://www.santander.com/en/press-room/press-releases"),
    (5, "Barclays", "UK", "https://home.barclays/news/press-releases/"),
    (6, "Groupe BPCE", "France", "https://www.groupebpce.com/en/all-the-latest-news/"),
    (7, "Société Générale", "France", "https://www.societegenerale.com/fr/communiques-de-presse"),
    (8, "Deutsche Bank", "Germany", "https://www.db.com/media/news?language_id=1"),
    (9, "UBS Group", "Switzerland", "https://www.ubs.com/global/en/media.html"),
    (10, "Crédit Mutuel Group", "France", "https://www.creditmutuel.com/fr/communiques-de-presse.html"),
    (11, "Lloyds Banking Group", "UK", "https://www.lloydsbankinggroup.com/media/press-releases.html"),
    (12, "NatWest Group", "UK", "https://www.natwestgroup.com/news-and-insights/latest-stories/financial-reporting.html"),
    (13, "ING Group", "Netherlands", "https://ing.com/newsroom/news"),
    (14, "UniCredit", "Italy", "https://www.unicreditgroup.eu/en/press-media/press-releases.html"),
    (15, "BBVA", "Spain", "https://accionistaseinversores.bbva.com/noticias/"),
    (16, "Commerzbank", "Germany", "https://www.commerzbank.de/group/newsroom/press-releases/"),
    (17, "Sberbank", "Russia", "https://www.sberbank.ru/en/press_center"),
    (18, "Intesa Sanpaolo", "Italy", "https://group.intesasanpaolo.com/en/newsroom/press-releases"),
    (19, "La Banque Postale", "France", "https://www.labanquepostale.com/newsroom-publications.typo-pressrelease.html"),
    (20, "CaixaBank", "Spain", "https://www.caixabank.com/en/headlines/news.html"),
    (21, "DZ Bank", "Germany", "https://www.dzbank.com/content/dzbank/en/home/we-are-dz-bank/press.html"),
    (22, "Nordea Bank", "Finland", "https://www.nordea.com/en/news-insights/press-room/press-releases"),
    (23, "Rabobank", "Netherlands", "https://www.rabobank.com/about-us/press/press-releases"),
    (24, "Banca Monte dei Paschi di Siena", "Italy", "https://www.gruppomps.it/en/media-and-news/press-releases/index.html"),
    (25, "First Abu Dhabi Bank (FAB)", "UAE", "https://www.bankfab.com/en-ae/about-fab/group/in-the-media"),
    (26, "Qatar National Bank (QNB)", "Qatar", "https://www.qnb.com/sites/qnb/qnbglobal/page/en/ennewsandinsight.html"),
    (27, "Emirates NBD", "UAE", "https://www.emiratesnbd.com/en/media-center"),
    (28, "Saudi National Bank (SNB)", "Saudi Arabia", "https://www.alahli.com/en/pages/about-us/newsroom"),
    (29, "Al Rajhi Bank", "Saudi Arabia", "https://www.alrajhibank.com.sa/en/About-alrajhi-bank/Media-Center?category=all&year;=all&page;=1"),
    (30, "Abu Dhabi Commercial Bank (ADCB)", "UAE", "https://www.adcb.com/en/about-us/media-centre/news/"),
    (31, "Ziraat Bank", "Türkiye", "https://www.ziraatbank.com.tr/tr/bankamiz/basin-odasi/basin-bultenleri"),
    (32, "Bank Leumi", "Israel", "https://www.leumi.co.il/en/node/2438"),
    (33, "Bank Hapoalim", "Israel", "https://www.bhiusa.com/news"),
    (34, "HSBC Holdings", "UK", "https://www.hsbc.com/news-and-views/news/media-releases"),
    (35, "Crédit Agricole Group", "France", "https://presse.credit-agricole.com/en/"),
    (36, "Barclays", "UK", "https://home.barclays/news/"),
    (37, "Groupe BPCE", "France", "https://newsroom-en.groupebpce.fr/news/"),
    (38, "Société Générale", "France", "https://www.societegenerale.com/en/press-release"),
    (39, "Deutsche Bank", "Germany", "https://www.db.com/newsroom/press-releases"),
    (40, "Crédit Mutuel Group", "France", "https://www.creditmutuel.com/en/press.html"),
    (41, "NatWest Group", "UK", "https://www.natwestgroup.com/news-and-insights/news-room/press-releases.html"),
    (42, "ING Group", "Netherlands", "https://ing.com/news/press-releases"),
    (43, "BBVA", "Spain", "https://www.bbva.com/en/specials/press-releases/"),
    (44, "Sberbank", "Russia", "https://www.sberbank.com/news-and-media/press-releases"),
    (45, "La Banque Postale", "France", "https://www.labanquepostale.com/en/newsroom-publications.html"),
    (46, "CaixaBank", "Spain", "https://www.caixabank.com/en/headlines/press-releases.html"),
    (47, "Banca Monte dei Paschi di Siena", "Italy", "https://www.gruppomps.it/en/media-and-news/press-releases.html"),
    (48, "First Abu Dhabi Bank (FAB)", "UAE", "https://www.bankfab.com/en-ae/about-fab/media-centre"),
    (49, "Qatar National Bank (QNB)", "Qatar", "https://www.qnb.com/sites/qnb/qnbglobal/en/enpressrelease"),
    (50, "Saudi National Bank (SNB)", "Saudi Arabia", "https://www.alahli.com/en-us/about-us/news-and-media"),
    (51, "Al Rajhi Bank", "Saudi Arabia", "https://www.alrajhibank.com/en/About-alrajhi-bank/Media-Center"),
    (52, "Ziraat Bank", "Türkiye", "https://www.ziraatbank.com.tr/en"),
    (53, "Bank Leumi", "Israel", "https://www.leumi.co.il/en/Press-Release"),
    (54, "Bank Hapoalim", "Israel", "https://www.bankhapoalim.com/en/investor-relations/financial-information/press-releases"),
    (55, "BNP Paribas", "France", "https://group.bnpparibas/en/all-news"),
    (56, "Banco Santander", "Spain", "https://www.santander.com/en/press-room"),
    (57, "Groupe BPCE", "France", "https://newsroom-en.groupebpce.fr/"),
    (58, "Société Générale", "France", "https://www.societegenerale.com/en/news"),
    (59, "Deutsche Bank", "Germany", "https://www.db.com/newsroom"),
    (60, "Crédit Mutuel Group", "France", "https://www.creditmutuel.com/en/news.html"),
    (61, "Lloyds Banking Group", "UK", "https://www.lloydsbankinggroup.com/media.html"),
    (62, "NatWest Group", "UK", "https://www.natwestgroup.com/news-and-insights/news-room.html"),
    (63, "UniCredit", "Italy", "https://www.unicreditgroup.eu/en/press-media/news.html"),
    (64, "BBVA", "Spain", "https://www.bbva.com/en/news/"),
    (65, "Commerzbank", "Germany", "https://www.commerzbank.de/group/newsroom/"),
    (66, "Sberbank", "Russia", "https://www.sberbank.com/news-and-media"),
    (67, "Intesa Sanpaolo", "Italy", "https://group.intesasanpaolo.com/en/newsroom"),
    (68, "DZ Bank", "Germany", "https://www.dzbank.com/content/dzbank/en/home/we-are-dz-bank/investor-relations/news.html"),
    (69, "Nordea Bank", "Finland", "https://www.nordea.com/en/news-insights"),
    (70, "Rabobank", "Netherlands", "https://www.rabobank.com/about-us/press"),
    (71, "Banca Monte dei Paschi di Siena", "Italy", "https://www.gruppomps.it/en/media-and-news.html"),
    (72, "Qatar National Bank (QNB)", "Qatar", "https://www.qnb.com/sites/qnb/qnbglobal/en/ennews"),
    (73, "Ziraat Bank", "Türkiye", "https://www.ziraatbank.com.tr/en/about-us/news"),
    (74, "Bank Leumi", "Israel", "https://www.leumi.co.il/en/Investor-Relations"),
    (75, "Bank Hapoalim", "Israel", "https://www.bankhapoalim.com/en/about-us/news"),
]


def is_valid_href(href):
    if not href or not isinstance(href, str):
        return False
    h = href.strip().lower()
    if h.startswith("javascript:") or h.startswith("#") or h.startswith("mailto:") or h.startswith("tel:"):
        return False
    return len(h) > 0


def find_valid_link(it):
    if it.name == "a" and is_valid_href(it.get("href")):
        return it.get("href")
    if is_valid_href(it.get("data-href") or it.get("data-url") or it.get("data-link")):
        return it.get("data-href") or it.get("data-url") or it.get("data-link")
    for a in it.find_all("a", href=True):
        if is_valid_href(a.get("href")):
            return a.get("href")
    parent_a = it.find_parent("a", href=True)
    if parent_a and is_valid_href(parent_a.get("href")):
        return parent_a.get("href")
    return None


def test_site(site_info):
    sid, name, country, url = site_info
    print(f"[{sid}/75] Testing {name} ({country}): {url} ...", end=" ", flush=True)

    try:
        html = fetch_page(url, rendering_mode="request")
        if len(html) < 200:
            print(f"FAIL (empty html)")
            return {"id": sid, "name": name, "status": "FAIL", "articles": 0, "error": "Empty HTML"}

        candidates = detect_article_candidates(html)
        if not candidates:
            # Try JS mode
            html = fetch_page(url, rendering_mode="js")
            candidates = detect_article_candidates(html)

        if not candidates:
            print(f"FAIL (no article candidates)")
            return {"id": sid, "name": name, "status": "FAIL", "articles": 0, "error": "No candidates"}

        best_cand = candidates[0]
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(best_cand["selector"])

        if not items:
            print(f"FAIL (selector returned 0 items: {best_cand['selector']})")
            return {"id": sid, "name": name, "status": "FAIL", "articles": 0, "error": "Selector returned 0"}

        raw_articles = []
        for it in items:
            heading = it.find(["h1", "h2", "h3", "h4", "h5", "h6"])
            href = find_valid_link(it)
            t_text = heading.get_text(" ", strip=True) if heading else it.get_text(" ", strip=True)[:150]
            
            raw_articles.append({
                "title": t_text,
                "link": href,
                "date": None,
                "description": None,
                "image": None,
            })

        normalized = normalize_articles(raw_articles, url)
        norm_count = len(normalized)

        if norm_count >= 2:
            print(f"PASS ({norm_count} articles, selector={best_cand['selector']})")
            return {"id": sid, "name": name, "status": "PASS", "articles": norm_count, "selector": best_cand["selector"]}
        elif norm_count == 1:
            print(f"PARTIAL (1 article, selector={best_cand['selector']})")
            return {"id": sid, "name": name, "status": "PARTIAL", "articles": 1, "selector": best_cand["selector"]}
        else:
            print(f"FAIL (0 normalized articles from {len(items)} raw)")
            return {"id": sid, "name": name, "status": "FAIL", "articles": 0, "error": "0 normalized"}

    except Exception as exc:
        print(f"FAIL ({exc})")
        return {"id": sid, "name": name, "status": "FAIL", "articles": 0, "error": str(exc)}


if __name__ == "__main__":
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end_idx = int(sys.argv[2]) if len(sys.argv) > 2 else len(SITES)

    selected = [s for s in SITES if start_idx <= s[0] <= end_idx]
    results = []
    
    for s in selected:
        res = test_site(s)
        results.append(res)
        time.sleep(0.5)

    passes = sum(1 for r in results if r["status"] == "PASS")
    partials = sum(1 for r in results if r["status"] == "PARTIAL")
    fails = sum(1 for r in results if r["status"] == "FAIL")
    working = passes + partials
    total = len(results)

    print("\n" + "="*50)
    print(f"Batch {start_idx}-{end_idx} Results:")
    print(f"PASS: {passes}, PARTIAL: {partials}, FAIL: {fails}")
    print(f"Working: {working}/{total} ({working/total*100:.1f}%)")
    print("="*50)
