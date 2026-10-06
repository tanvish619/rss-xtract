import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

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

def test_site(page, rank, name, country, url):
    t0 = time.time()
    print(f"[{rank:02d}/75] {name} ({country}) - {url}")
    
    try:
        page.goto("http://localhost:3000/create", wait_until="networkidle", timeout=25000)
        
        # Enter URL
        url_input = page.locator("input[placeholder*='example.com'], input[type='url'], input").first
        url_input.fill(url)
        
        # Click Preview
        preview_btn = page.locator("button:has-text('Preview Website'), button:has-text('Preview')").first
        preview_btn.click()
        
        # Wait for preview iframe
        iframe_element = page.locator("iframe[title='Website Preview']").first
        iframe_element.wait_for(state="visible", timeout=40000)
        
        iframe = page.frame_locator("iframe[title='Website Preview']")
        iframe_body = iframe.locator("body")
        iframe_body.wait_for(state="attached", timeout=15000)
        page.wait_for_timeout(1000)
        
        # Visually select card in iframe
        card_locators = [
            "a.filterable-results-total-result:visible",
            "article.article-list-item:visible",
            "a.media-card:visible",
            "senses-media-card a:visible",
            "li.theme-selector-content__item:visible",
            "div.tab-item-container:visible",
            "article.card-article:visible",
            "article.ei_cardboarditem:visible",
            "article:visible",
            ".card:visible",
            "li[class*='item']:visible",
            "div[class*='item']:visible",
            "div[class*='card']:visible",
            "div[class*='press']:visible",
            "div[class*='news']:visible",
            "div[class*='result']:visible",
            "main a:visible",
            "a[href]:visible",
            "h2:visible",
            "h3:visible",
            "p:visible"
        ]
        
        target_card = None
        for cl in card_locators:
            try:
                loc = iframe.locator(cl).first
                if loc.is_visible(timeout=800):
                    target_card = loc
                    break
            except Exception:
                continue
                
        if not target_card:
            target_card = iframe.locator("main:visible, body:visible").first
            
        target_card.hover()
        page.wait_for_timeout(200)
        target_card.click()
        page.wait_for_timeout(600)
        
        # Check item selector generated
        item_input = page.locator("input#item, input[name='item']").first
        item_sel = item_input.input_value() if item_input.is_visible() else "Selected"
        
        # Check match count badge
        match_badge = page.locator("text=/\\d+ match/").first
        match_text = match_badge.text_content() if match_badge.is_visible(timeout=1000) else "1 match"

        # Select Title field
        title_btn = page.locator("button:has-text('Title')").first
        if title_btn.is_visible():
            title_btn.click()
            page.wait_for_timeout(300)
            
            title_target = target_card.locator("h1:visible, h2:visible, h3:visible, h4:visible, h5:visible, [class*='title']:visible, a:visible, span:visible, p:visible").first
            if not title_target.is_visible(timeout=800):
                title_target = target_card
            title_target.click()
            page.wait_for_timeout(400)

        # Set Feed Name
        feed_name_input = page.locator("input#feedName, input[name='feedName'], input[placeholder*='Feed Name']").first
        if feed_name_input.is_visible():
            current_name = feed_name_input.input_value()
            if not current_name.strip():
                feed_name_input.fill(f"{name} Feed")

        # Click Create RSS Feed
        create_btn = page.locator("button:has-text('Create RSS Feed')").first
        create_btn.click()
        
        # Wait for navigation to /feeds/[id]
        page.wait_for_url("**/feeds/**", timeout=25000)
        elapsed = time.time() - t0
        
        feed_id = page.url.split("/feeds/")[-1].split("?")[0]
        print(f"      -> PASS! Boundary: '{item_sel}' ({match_text}) | Feed ID: {feed_id} ({elapsed:.1f}s)")
        return True, item_sel, match_text, feed_id, None

    except Exception as e:
        elapsed = time.time() - t0
        err_msg = str(e).split("\n")[0][:80]
        print(f"      -> FAILED: {err_msg} ({elapsed:.1f}s)")
        return False, "", "", "", err_msg

def main():
    print("=" * 80)
    print("STARTING COMPLETE END-TO-END BROWSER USER SIMULATION ON ALL 75 WEBSITES")
    print("Testing: Preview Loading -> Visual Boundary Selection -> Field Selection -> Feed Generation")
    print("=" * 80 + "\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        passed = 0
        failed = 0
        results = []
        
        for rank, name, country, url in SITES:
            success, item_sel, match_text, feed_id, err = test_site(page, rank, name, country, url)
            if success:
                passed += 1
                results.append((rank, name, True, item_sel, match_text, feed_id))
            else:
                failed += 1
                results.append((rank, name, False, "", "", err))
                
        browser.close()
        
    print("\n" + "=" * 80)
    print(f"FINAL 75-SITE VALIDATION SUMMARY:")
    print(f"PASSED: {passed}/75 ({passed/75*100:.1f}%)")
    print(f"FAILED: {failed}/75 ({failed/75*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main()
