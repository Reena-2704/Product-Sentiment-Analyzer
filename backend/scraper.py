from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from urllib.parse import urlparse


REVIEW_SELECTORS = [
    '[data-hook="review-body"]',
    '[data-testid*="review-body"]',
    '[data-testid*="review-text"]',
    '[class*="review-text"]',
    '[class*="review-content"]',
    '[class*="review-body"]',
    '[class*="review"] p',
    '.review',
]

PRODUCT_SELECTORS = [
    'meta[property="og:title"]',
    '[data-testid*="product-title"]',
    '[data-testid*="product-name"]',
    '[class*="product-title"]',
    '[class*="product-name"]',
    'h1',
    'title',
]


def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,1600")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=options)


def first_text(soup, selectors):
    for selector in selectors:
        node = soup.select_one(selector)
        if not node:
            continue
        if node.name == "meta":
            value = node.get("content", "")
        else:
            value = node.get_text(" ", strip=True)
        if value:
            return value
    return "Unknown Product"


def collect_review_nodes(soup):
    seen = set()
    found = []

    for selector in REVIEW_SELECTORS:
        for node in soup.select(selector):
            text = node.get_text(" ", strip=True)
            if not text or len(text) < 10:
                continue
            key = " ".join(text.split()).lower()
            if key not in seen:
                seen.add(key)
                found.append(node)

    return found[:100]


def scrape_reviews(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Please enter a valid http:// or https:// product link.")

    driver = create_driver()
    try:
        driver.get(url)
        time.sleep(3)

        # Give dynamically loaded review sections a chance to appear.
        for _ in range(4):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        product = first_text(soup, PRODUCT_SELECTORS)
        review_nodes = collect_review_nodes(soup)

        reviews = []
        seen = set()

        for node in review_nodes:
            text = " ".join(node.get_text(" ", strip=True).split())
            if not text:
                continue

            key = text.lower()
            if key in seen:
                continue
            seen.add(key)

            rating = ""
            parent = node
            for _ in range(4):
                parent = parent.parent
                if not parent:
                    break
                rating_node = parent.select_one(
                    '[class*="rating"], [aria-label*="star"], [data-hook*="rating"]'
                )
                if rating_node:
                    rating = rating_node.get("aria-label") or rating_node.get_text(" ", strip=True)
                    break

            reviews.append({
                "product": product,
                "review": text,
                "rating": rating
            })

        if not reviews:
            raise ValueError(
                "No reviews were found on this page. The site may use different HTML, "
                "require login, load reviews after interaction, or block automated access."
            )

        return reviews

    finally:
        driver.quit()
