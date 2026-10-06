import sys
import time
import json
import os
import subprocess
import tempfile
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
]

env = Environment(loader=FileSystemLoader(str(BACKEND_DIR / "templates")))
template = env.get_template("scraper_template.py.j2")

def run_code(code: str):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_path = f.name
    try:
        proc_env = os.environ.copy()
        proc_env["PYTHONIOENCODING"] = "utf-8"
        res = subprocess.run([sys.executable, temp_path], capture_output=True, text=True, timeout=90, env=proc_env)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.strip() or "Script failed")
        out = res.stdout.strip()
        if not out:
            return []
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            start = out.find("[")
            end = out.rfind("]")
            if start != -1 and end != -1:
                return json.loads(out[start:end+1])
            return []
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass

def main():
    print(f"=== TESTING 30 SITES END-TO-END (Visual Preview -> Container Selection -> Field Mapping -> Scraper Execution -> Normalized Articles) ===\n")
    
    passed = 0
    failed = 0
    results = []

    for rank, name, country, url in SITES:
        t0 = time.time()
        print(f"[{rank:02d}/30] Testing {name} ({country})...")
        print(f"      URL: {url}")
        
        try:
            # 1. Fetch preview HTML
            html = fetch_page(url)
            elapsed_fetch = time.time() - t0
            
            if not html or len(html) < 200:
                raise ValueError("Fetched HTML is too short or empty")
            
            soup = BeautifulSoup(html, "html.parser")
            page_title = (soup.title.string or "No Title").strip() if soup.title else "No Title"
            
            # Check for block markers in preview
            lowered = html[:30000].lower()
            if "error 1007" in lowered or "access denied" in lowered:
                raise ValueError("Page preview contains WAF block markers")

            # 2. Detect candidate selectors
            candidates = detect_article_candidates(html)
            if not candidates:
                raise ValueError("No article containers identified in HTML")
            
            best = candidates[0]
            item_sel = best["selector"]
            title_sel = best.get("title_selector")
            link_sel = best.get("link_selector")
            date_sel = best.get("date_selector")
            desc_sel = best.get("description_selector")
            img_sel = best.get("image_selector")
            
            # 3. Generate scraper code
            scraper_code = template.render(
                url=url,
                item_selector=item_sel,
                title_selector=title_sel,
                link_selector=link_sel,
                date_selector=date_sel,
                description_selector=desc_sel,
                image_selector=img_sel,
                author_selector=None,
                category_selector=None,
                pagination_selector=None,
                max_items=15,
                rendering_mode="request",
            )
            
            # 4. Execute scraper code
            extracted_raw = run_code(scraper_code)
            normalized = normalize_articles(extracted_raw, source_url=url)
            
            total_extracted = len(normalized)
            if total_extracted < 1:
                # Retry with rendering_mode='js'
                scraper_code_js = template.render(
                    url=url,
                    item_selector=item_sel,
                    title_selector=title_sel,
                    link_selector=link_sel,
                    date_selector=date_sel,
                    description_selector=desc_sel,
                    image_selector=img_sel,
                    author_selector=None,
                    category_selector=None,
                    pagination_selector=None,
                    max_items=15,
                    rendering_mode="js",
                )
                extracted_raw = run_code(scraper_code_js)
                normalized = normalize_articles(extracted_raw, source_url=url)
                total_extracted = len(normalized)

            if total_extracted >= 1:
                passed += 1
                sample_title = normalized[0].get("title", "")[:45]
                sample_link = normalized[0].get("link", "")[:45]
                print(f"      -> PASS: {total_extracted} articles | Selector: '{item_sel}' | Sample: '{sample_title}' ({elapsed_fetch:.1f}s)")
                results.append((rank, name, True, total_extracted, item_sel, None))
            else:
                failed += 1
                print(f"      -> FAIL: 0 articles extracted from selector '{item_sel}'")
                results.append((rank, name, False, 0, item_sel, "0 articles extracted"))

        except Exception as e:
            failed += 1
            print(f"      -> ERROR: {e}")
            results.append((rank, name, False, 0, "", str(e)))
        
        print()

    print("=" * 70)
    print(f"RESULTS SUMMARY: {passed}/30 PASSED ({passed/30*100:.1f}%) | {failed} FAILED")
    print("=" * 70)

if __name__ == "__main__":
    main()
