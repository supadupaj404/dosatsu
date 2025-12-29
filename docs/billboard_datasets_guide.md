# Billboard Chart Data Sources (2015-2025)

## Overview
Comprehensive guide to free, publicly available Billboard chart datasets covering the last 10 years.

---

## Best Options for 10-Year Historical Data

### 1. **mhollingshead/billboard-hot-100** (RECOMMENDED)
- **Platform:** GitHub
- **URL:** https://github.com/mhollingshead/billboard-hot-100
- **Format:** JSON
- **Coverage:** ALL Billboard Hot 100 charts in history
- **Update Frequency:** Updated daily (automated)
- **Access:** Direct JSON download

**Quick Access:**
```bash
# Download all charts (large file)
curl https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/all.json > billboard_all_charts.json

# Or clone the repo
git clone https://github.com/mhollingshead/billboard-hot-100.git
```

**Data Structure:**
- Weekly charts from 1958 to present
- Song rankings, artist info, chart movement
- Perfect for time-series analysis

---

### 2. **Billboard Hot 100 (1958-2024) - Kaggle**
- **Platform:** Kaggle
- **URL:** https://www.kaggle.com/datasets/elizabethearhart/billboard-hot-1001958-2024
- **Format:** CSV
- **Coverage:** 1958 - June 2024
- **Access:** Requires Kaggle account (free)

**Features:**
- Clean CSV format for easy analysis
- Complete historical coverage
- Good for data science projects

---

### 3. **Billboard Hot-100 [2000-2023] with Spotify Features**
- **Platform:** Kaggle
- **URL:** https://www.kaggle.com/datasets/suparnabiswas/billboard-hot-1002000-2023-data-with-features
- **Format:** CSV with enriched data
- **Coverage:** 2000-2023
- **Unique Feature:** Includes Spotify audio features (danceability, energy, tempo, etc.)

**Why This Is Powerful:**
- Combines Billboard chart position with Spotify metrics
- Perfect for analyzing what makes a hit song
- Includes lyrics data
- Great for machine learning models

---

### 4. **utdata/rwd-billboard-data** (CSV Format)
- **Platform:** GitHub
- **URL:** https://github.com/utdata/rwd-billboard-data
- **Format:** CSV
- **Coverage:**
  - Hot 100: 1958 to present
  - Billboard 200: 1967 to present
- **Files:**
  - `data-out/hot-100-current.csv`
  - `data-out/billboard-200-current.csv`

**Access:**
```bash
# Clone the repository
git clone https://github.com/utdata/rwd-billboard-data.git
```

---

### 5. **Billboard Hot 100 & More - Kaggle**
- **Platform:** Kaggle
- **URL:** https://www.kaggle.com/datasets/ludmin/billboard
- **Format:** CSV
- **Coverage:** Full history to present
- **Last Updated:** 2 weeks ago (actively maintained)

---

## Python API for Live Scraping

### **billboard-charts** (Python Package)
- **Platform:** GitHub/PyPI
- **URL:** https://github.com/guoguo12/billboard-charts
- **Install:** `pip install billboard.py`

**Example Usage:**
```python
import billboard

# Get current Hot 100
chart = billboard.ChartData('hot-100')

# Get specific date
chart = billboard.ChartData('hot-100', date='2020-01-04')

# Iterate through songs
for song in chart:
    print(f"{song.rank}. {song.title} by {song.artist}")
```

**Note:** Rate limits apply; best for current data or small historical queries.

---

## Commercial APIs (Paid Options)

### **Billboard Charts API - Zyla API Hub**
- **URL:** https://zylalabs.com/api-marketplace/music/billboard+charts+api/1335
- **Format:** JSON via REST API
- **Coverage:** Current and historical
- **Pricing:** Subscription-based
- **Use Case:** Production applications requiring real-time data

---

## Recommended Approach for Your Use Case

### For Historical Analysis (2015-2025):
1. **Download mhollingshead/billboard-hot-100** JSON file
   - Most comprehensive
   - Updated daily
   - Free and reliable

2. **Supplement with Spotify Features Dataset** (Kaggle)
   - Adds audio analysis dimensions
   - Great for understanding hit patterns
   - Useful for A&R and talent evaluation

### For Live/Current Data:
1. Use **billboard.py** Python package
2. Respect rate limits (1 request per second)
3. Cache results locally

---

## Quick Start Script

```python
import requests
import json

# Download all Billboard Hot 100 data
url = "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/all.json"
response = requests.get(url)
all_charts = response.json()

# Filter for 2015-2025
recent_charts = {
    date: chart
    for date, chart in all_charts.items()
    if date >= "2015-01-01"
}

# Save locally
with open('billboard_2015_2025.json', 'w') as f:
    json.dump(recent_charts, f, indent=2)

print(f"Downloaded {len(recent_charts)} weeks of Billboard Hot 100 data")
```

---

## Data Enrichment Strategy

Combine Billboard chart data with:
1. **Spotify API** - Popularity metrics, audio features
2. **MusicBrainz** - Songwriter credits, ISRC codes
3. **Genius API** - Lyrics analysis
4. **Last.fm** - User listening patterns

This creates a comprehensive music intelligence dataset for Whetstone's talent evaluation and A&R work.

---

## Next Steps

1. Download the mhollingshead dataset (all.json)
2. Create a local database or data pipeline
3. Enrich with Spotify/MusicBrainz metadata
4. Build analytics dashboards for talent trends

---

**Last Updated:** January 2025
