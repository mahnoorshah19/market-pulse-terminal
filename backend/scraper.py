import urllib.request
import re
from bs4 import BeautifulSoup
from typing import List, Dict

# Verified institutional & macroeconomic feeds
# backend/scraper.py
FEEDS = {
    # --- Pakistan Macroeconomic, Banking & FX Feeds ---
    "Business Recorder": "https://www.brecorder.com/feeds/latest-news",
    "Dawn Business": "https://www.dawn.com/feeds/business/",
    "The News (Business)": "https://www.thenews.com.pk/rss/1/2",
    "Express Tribune (Business)": "https://tribune.com.pk/feed/business",
    "ProPakistani Business": "https://propakistani.pk/category/business/feed/",

    # --- Global Wires (Bloomberg, Reuters & Macro Markets) ---
    "Yahoo Finance Wire": "https://finance.yahoo.com/news/rssindex",
    "CNBC Central Banks & Economy": "https://search.cnbc.com/rs/search/combinedList/view.xml?partnerId=wrss01&id=20910258",
    "MarketWatch Macro": "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines"
}

def fetch_wire_stories() -> List[Dict[str, str]]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    stories = []

    for source_name, feed_url in FEEDS.items():
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()

            soup = BeautifulSoup(content, 'xml')
            items = soup.find_all('item')

            for item in items[:15]:
                title = item.find('title').get_text().strip() if item.find('title') else ""
                desc = item.find('description').get_text().strip() if item.find('description') else ""
                clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
                pub_date = item.find('pubDate').get_text().strip() if item.find('pubDate') else "Recent"

                if title and len(title) > 10:
                    stories.append({
                        "source": source_name,
                        "headline": title,
                        "summary": clean_desc,
                        "published_date": pub_date
                    })
        except Exception as err:
            print(f"Warning: Could not fetch feed [{source_name}]: {err}")

    return stories