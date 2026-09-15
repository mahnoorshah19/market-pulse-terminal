import urllib.request
import re
from bs4 import BeautifulSoup
from typing import List, Dict

FEEDS = [
    "https://propakistani.pk/category/business/feed/",
    "https://www.brecorder.com/feeds/latest-news"
]

def fetch_wire_stories() -> List[Dict[str, str]]:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    stories = []

    for feed_url in FEEDS:
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()

            soup = BeautifulSoup(content, 'xml')
            for item in soup.find_all('item'):
                title = item.find('title').get_text().strip() if item.find('title') else ""
                desc = item.find('description').get_text().strip() if item.find('description') else ""
                clean_desc = re.sub(r'<[^>]+>', '', desc)
                pub_date = item.find('pubDate').get_text().strip() if item.find('pubDate') else "Recent"

                if title:
                    stories.append({
                        "headline": title,
                        "summary": clean_desc,
                        "published_date": pub_date
                    })
        except Exception as err:
            print(f"Failed to fetch {feed_url}: {err}")

    return stories