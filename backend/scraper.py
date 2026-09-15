import urllib.request
import re
from bs4 import BeautifulSoup
from typing import List, Dict

# Verified institutional & macroeconomic feeds
FEEDS = {
    # --- Pakistan Macroeconomic, Banking & FX Feeds ---
    "Business Recorder": "https://www.brecorder.com/feeds/latest-news",
    "Dawn Business": "https://www.dawn.com/feeds/business/",
    "The News (Business)": "https://www.thenews.com.pk/rss/1/2",
    "Express Tribune (Business)": "https://tribune.com.pk/feed/business",
    "ProPakistani Business": "https://propakistani.pk/category/business/feed/",

    # --- Global Wire (Bloomberg, Reuters & Institutional Coverage) ---
    "Yahoo Finance Wire (Bloomberg/Reuters/WSJ)": "https://finance.yahoo.com/news/rssindex",
    
    # --- Institutional Investment Research & Insights ---
    "Goldman Sachs Insights": "https://www.goldmansachs.com/insights/rss.xml",
    "J.P. Morgan Asset Management": "https://am.jpmorgan.com/us/en/asset-management/adv/insights/rss/"
}

def fetch_wire_stories() -> List[Dict[str, str]]:
    """
    Ingests live financial and macroeconomic stories across national
    and global institutional wires with feed-specific headers.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*'
    }
    stories = []

    for source_name, feed_url in FEEDS.items():
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                content = response.read()

            soup = BeautifulSoup(content, 'xml')
            items = soup.find_all('item')

            for item in items[:15]:  # Capture up to 15 latest items per feed
                title = item.find('title').get_text().strip() if item.find('title') else ""
                desc = item.find('description').get_text().strip() if item.find('description') else ""
                clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
                pub_date = item.find('pubDate').get_text().strip() if item.find('pubDate') else "Recent"

                # Filter out video-only or empty headlines
                if title and len(title) > 10:
                    stories.append({
                        "source": source_name,
                        "headline": title,
                        "summary": clean_desc,
                        "published_date": pub_date
                    })
        except Exception as err:
            # Continue uninterrupted if a single institutional server is down or rate-limiting
            print(f"Warning: Could not fetch feed [{source_name}]: {err}")

    return stories