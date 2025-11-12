import feedparser
from datetime import datetime, timedelta

search_terms = [
    "generative audio", "audio generation", "music generation", 
    "text-to-audio", "audio transformer", "speech synthesis", 
    "neural vocoder"
]

feeds = {
    "cs.SD (Sound)": "http://export.arxiv.org/rss/cs.SD",
    "eess.AS (Audio/Speech)": "http://export.arxiv.org/rss/eess.AS",
    "cs.CL (CompLang)": "http://export.arxiv.org/rss/cs.CL",
    "cs.LG (ML)": "http://export.arxiv.org/rss/cs.LG"
}

def matches_search(text, keywords):
    text = text.lower()
    return any(term in text for term in keywords)

cutoff = datetime.now() - timedelta(days=60)
results = []

for name, url in feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries:
        published = datetime(*entry.published_parsed[:6])
        if published > cutoff and matches_search(entry.title + entry.summary, search_terms):
            results.append({
                "Title": entry.title,
                "Published": published.strftime("%Y-%m-%d"),
                "Link": entry.link,
                "Category": name
            })

for paper in sorted(results, key=lambda x: x["Published"], reverse=True):
    print(f"[{paper['Published']}] ({paper['Category']}) {paper['Title']}\n{paper['Link']}\n")
