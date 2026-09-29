import requests
from bs4 import BeautifulSoup
from xml.sax.saxutils import escape
from datetime import datetime, timezone
from urllib.parse import urljoin

SOURCE_URL = "https://www.calcalist.co.il/local_news/car"

# שירות proxy לקריאת האתר
PROXY_URL = "https://api.allorigins.win/raw?url="

url = PROXY_URL + SOURCE_URL

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    url,
    headers=headers,
    timeout=60
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

articles = []
seen = set()

for a in soup.find_all("a", href=True):

    title = a.get_text(" ", strip=True)
    href = a["href"]

    if not title:
        continue

    if len(title) < 10:
        continue

    link = urljoin(SOURCE_URL, href)

    if "calcalist.co.il" not in link:
        continue

    if link in seen:
        continue

    # רק כתבות ממדור הרכב
    if "/local_news/car" not in link and "/category/3783" not in link:
        continue

    seen.add(link)

    articles.append({
        "title": title,
        "link": link
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

<description>חדשות הרכב של כלכליסט</description>

<language>he</language>

<lastBuildDate>{now.strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>

{''.join(items)}

</channel>
</rss>
"""


with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(rss)

print("RSS created:", len(articles), "articles")