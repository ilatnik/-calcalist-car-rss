import urllib.request
import xml.etree.ElementTree as ET
from email.utils import formatdate
from html import escape

GOOGLE_NEWS_URL = (
    "https://news.google.com/rss/search"
    "?q=site%3Acalcalist.co.il%2Flocal_news%2Fcar"
    "&hl=he&gl=IL&ceid=IL%3Ahe"
)

def fetch(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()

def main():
    data = fetch(GOOGLE_NEWS_URL)
    root = ET.fromstring(data)

    items = []

    for item in root.findall("./channel/item"):
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        description = item.findtext("description", "")
        pub_date = item.findtext("pubDate", "")
        guid = item.findtext("guid", link)

        if "calcalist.co.il" not in (link or ""):
            continue

        items.append(f"""
        <item>
          <title>{escape(title)}</title>
          <link>{escape(link)}</link>
          <guid isPermaLink="false">{escape(guid)}</guid>
          <pubDate>{escape(pub_date)}</pubDate>
          <description>{escape(description)}</description>
        </item>
        """)

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>כלכליסט - חדשות רכב</title>
    <link>https://www.calcalist.co.il/local_news/car</link>
    <description>חדשות רכב מכלכליסט</description>
    <language>he</language>
    <lastBuildDate>{formatdate(usegmt=True)}</lastBuildDate>
    {''.join(items)}
  </channel>
</rss>
"""

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(rss)

if __name__ == "__main__":
    main()