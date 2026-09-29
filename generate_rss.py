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

def clean_text(value):
    if not value:
        return ""
    return "".join(
        c for c in value
        if c in "\t\n\r" or ord(c) >= 32
    )

def main():
    data = fetch(GOOGLE_NEWS_URL)
    root = ET.fromstring(data)

    rss_items = []

    for item in root.findall("./channel/item"):
        title = clean_text(item.findtext("title", ""))
        link = clean_text(item.findtext("link", ""))
        description = clean_text(item.findtext("description", ""))
        pub_date = clean_text(item.findtext("pubDate", ""))
        guid = clean_text(item.findtext("guid", link))

        if "calcalist.co.il" not in link:
            continue

        rss_items.append(
            "    <item>\n"
            f"      <title>{escape(title)}</title>\n"
            f"      <link>{escape(link)}</link>\n"
            f"      <guid isPermaLink=\"false\">{escape(guid)}</guid>\n"
            f"      <pubDate>{escape(pub_date)}</pubDate>\n"
            f"      <description>{escape(description)}</description>\n"
            "    </item>"
        )

    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        '  <channel>\n'
        '    <title>כלכליסט - חדשות רכב</title>\n'
        '    <link>https://www.calcalist.co.il/local_news/car</link>\n'
        '    <description>חדשות רכב מכלכליסט</description>\n'
        '    <language>he</language>\n'
        f'    <lastBuildDate>{formatdate(usegmt=True)}</lastBuildDate>\n'
        + "\n".join(rss_items) +
        '\n  </channel>\n'
        '</rss>\n'
    )
    
    with open("feed.rss", "w", encoding="utf-8", newline="\n") as f:
        f.write(rss)

if __name__ == "__main__":
    main()
