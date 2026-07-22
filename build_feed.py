#!/usr/bin/env python3
"""Build feed.xml (RSS 2.0) from markdown posts in posts/.

Post format: posts/YYYY-MM-DD-slug.md with front matter:
---
title: Post Title
description: One-sentence meta description.
---
(markdown body)
"""
import os, re, sys, html
from datetime import datetime, timezone
from email.utils import format_datetime

try:
    import markdown
except ImportError:
    sys.exit("pip install markdown --break-system-packages")

SITE_TITLE = "Flathead Valley Real Estate Insights | Ryan Berner"
SITE_LINK = os.environ.get("FEED_SITE_LINK", "https://thealpinerealtor-ui.github.io/lofty-blog-feed")  # set to GitHub Pages URL
SITE_DESC = ("Market updates, buyer and seller guides, and straight answers for "
             "Kalispell and Whitefish real estate — including divorce and estate home sales. "
             "By Ryan Berner, West and Company | Brokered by eXp Realty.")
MAX_ITEMS = 20

def parse_post(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError(f"missing front matter: {path}")
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
    body_html = markdown.markdown(m.group(2), extensions=["extra"])
    fname = os.path.basename(path)
    date_str = fname[:10]
    slug = fname[11:-3]
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=6, minute=30, tzinfo=timezone.utc)
    return {"title": meta["title"], "desc": meta.get("description", ""),
            "html": body_html, "dt": dt, "slug": slug}

def build():
    posts = sorted(
        (parse_post(os.path.join("posts", f)) for f in os.listdir("posts") if f.endswith(".md")),
        key=lambda p: p["dt"], reverse=True)[:MAX_ITEMS]
    now = format_datetime(datetime.now(timezone.utc))
    items = []
    for p in posts:
        link = f"{SITE_LINK}/posts/{p['slug']}"
        items.append(f"""  <item>
    <title>{html.escape(p['title'])}</title>
    <link>{html.escape(link)}</link>
    <guid isPermaLink="false">{html.escape(p['slug'])}</guid>
    <pubDate>{format_datetime(p['dt'])}</pubDate>
    <description>{html.escape(p['desc'])}</description>
    <content:encoded><![CDATA[{p['html']}]]></content:encoded>
  </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{html.escape(SITE_TITLE)}</title>
  <link>{html.escape(SITE_LINK)}</link>
  <atom:link href="{html.escape(SITE_LINK)}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>{html.escape(SITE_DESC)}</description>
  <language>en-us</language>
  <lastBuildDate>{now}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>
"""
    open("feed.xml", "w", encoding="utf-8").write(feed)
    print(f"feed.xml written with {len(posts)} items")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    build()
