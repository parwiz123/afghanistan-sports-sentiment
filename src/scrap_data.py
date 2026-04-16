from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import requests

# =========================
# CONFIG
# =========================
BASE_URL = "https://www.ariananews.af/category/sport/page/{}/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# STEP 1: FILTER FUNCTION
# =========================
def is_afghanistan_national_sport(text):
    t = text.lower()

    # -------------------
    # 1. allowed sports
    # -------------------
    allowed_sports = [
        "cricket", "football", "soccer", "futsal",
        "t20", "odi", "test"
    ]

    # -------------------
    # 2. MUST be Afghanistan related
    # -------------------
    country_keywords = [
        "afghanistan", "afghan", "afg",
        "afghanistan national", "afghan national team"
    ]

    # -------------------
    # 3. MUST indicate international / national team context
    # -------------------
    national_context = [
        "national team",
        "u17", "u-17",
        "u19", "u-19",
        "u23", "u-23",
        "under-17", "under-19", "under-23",
        "world cup",
        "asian cup",
        "qualifier",
        "international",
        "vs "
    ]

    # -------------------
    # 4. REMOVE LOCAL / BAD SPORTS
    # -------------------
    bad_noise = [
        "ipl", "indian premier league",
        "bpl", "psl",
        "domestic", "league",
        "snooker", "billiards",
        "buzkashi",
        "ski", "skiing",
        "winter sports",
        "kabaddi"
    ]

    # -------------------
    # 5. FILTER OUT NOISE FIRST
    # -------------------
    if any(b in t for b in bad_noise):
        return False

    # -------------------
    # 6. MUST have sport
    # -------------------
    if not any(s in t for s in allowed_sports):
        return False

    # -------------------
    # 7. MUST have Afghanistan
    # -------------------
    if not any(c in t for c in country_keywords):
        return False

    # -------------------
    # 8. MUST be national/international context
    # -------------------
    if not any(n in t for n in national_context):
        return False

    return True
# =========================
# STEP 2: SPORT CLASSIFIER
# =========================
def classify_sport(text):
    t = text.lower()

    if "cricket" in t or "t20" in t or "odi" in t or "test" in t:
        return "cricket"

    if "football" in t or "soccer" in t:
        return "football"

    if "futsal" in t:
        return "futsal"

    return "unknown"

# =========================
# STEP 3: SCRAPE LINKS
# =========================
def get_links():
    links = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for i in range(1, 10):  # increase later to 81
            page = browser.new_page()
            url = BASE_URL.format(i)

            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)

            anchors = page.query_selector_all("a")

            for a in anchors:
                href = a.get_attribute("href")

                if not href:
                    continue

                if href.startswith("/"):
                    href = "https://www.ariananews.af" + href

                if (
                    "ariananews.af" in href and
                    "/category/" not in href and
                    "/page/" not in href and
                    len(href.split("-")) > 3
                ):
                    links.add(href)

            print(f"Page {i} → {len(links)} links")

            page.close()

        browser.close()

    return list(links)


# =========================
# STEP 4: EXTRACT ARTICLE TEXT
# =========================
def extract_article(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")

        # TITLE
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # ✅ MAIN FIX: ONLY THIS DIV
        content_div = soup.find("div", id="mvp-content-main")

        if not content_div:
            return title, ""

        paragraphs = content_div.find_all("p")

        text = " ".join([
            p.get_text(strip=True)
            for p in paragraphs
            if p.get_text(strip=True) != ""
        ])

        return title, text

    except Exception as e:
        print("Error:", url, e)
        return None, None

# =========================
# STEP 5: MAIN PIPELINE
# =========================
def main():

    print("🔵 Scraping links...")
    links = get_links()

    print(f"\nTotal links found: {len(links)}")

    dataset = []

    print("\n🔵 Extracting articles...")

    for i, url in enumerate(links):
        title, text = extract_article(url)

        if not title or not text:
            continue

        combined_text = title + " " + text

        # FILTER ONLY AFGHAN NATIONAL SPORTS
        if not is_afghanistan_national_sport(combined_text):
            continue

        dataset.append({
            "url": url,
            "title": title,
            "text": text,
            "sport": classify_sport(combined_text)
        })

        print(f"{i+1}/{len(links)} processed → kept {len(dataset)}")

        time.sleep(1)

    # =========================
    # SAVE DATASET
    # =========================
    df = pd.DataFrame(dataset)
    df.to_csv("afghanistan_sports_dataset2.csv", index=False)

    print("\n🏁 DONE!")
    print("Final dataset size:", len(dataset))
    print("Saved → afghanistan_sports_dataset.csv")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()