import requests
from bs4 import BeautifulSoup
from xml.sax.saxutils import escape
from datetime import datetime, timezone

URL = "https://www.calcalist.co.il/local_news/car"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; CalcalistRSS/1.0)"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

articles = []
seen = set()

# Find links to Calcalist articles
for a in soup.find_all("a", href=True):

    href = a["href"]

    if not href.startswith("https://www.calcalist.co.il/"):
        continue

    if "/local_news/" not in href:
        continue

    title = a.get_text(" ", strip=True)

    if not title:
        continue

    if len(title) < 10:
        continue

    if href in seen:
        continue

    seen.add(href)

    articles.append({
        "title": title,
        "link": href
    })

    if len(articles) >= 50:
        break


now = datetime.now(timezone.utc)

items = []

for article in articles:

    title = escape(article["title"])
    link = escape(article["link"])

    items.append(f"""
    <item>
        <title>{title}</title>
        <link>{link}</link>
        <guid isPermaLink="true">{link}</guid>
        <pubDate>{now.strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>
    </item>
    """)

rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>

<title>כלכליסט – רכב</title>

<link>https://www.calcalist.co.il/local_news/car</link>

<description>כל הכתבות החדשות ממדור הרכב של כלכליסט</description>

<language>he</language>

<lastBuildDate>{now.strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>

{''.join(items)}

</channel>
</rss>
"""

with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(rss)

print(f"Created RSS feed with {len(articles)} articles")