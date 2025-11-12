# Billboard Insights Quick Start Guide
### Find shareable music industry insights for Twitter & LinkedIn

---

## 🎯 Your Use Case
Find data-driven insights like:
> "For the first time in 35 years, there wasn't a hip-hop track in the top 40 of the Billboard Hot 100 (Week of October 30th)"

These scripts help you find those moments automatically.

---

## 📥 Step 1: Download Billboard Data (One Time Setup)

```bash
cd ~/CodeProjects/Experiments/api-tests/
python3 billboard_downloader.py
```

**What this does:**
- Downloads 10 years of Billboard Hot 100 charts
- Saves to `billboard_recent.json`
- Takes ~30 seconds

---

## 🔍 Step 2: Generate General Insights

### Option A: Auto-Generate Top Insights
```bash
python3 billboard_insights_generator.py
```

**Finds automatically:**
- ✅ Biggest chart jumps ("Song jumped 40 spots this week")
- ✅ Artist dominance ("Drake has 7 songs in top 40")
- ✅ High debuts ("Song debuts at #3")
- ✅ Longest chart runs ("Old Town Road: 19 weeks at #1")
- ✅ Year-over-year comparisons

**Output:** `billboard_insights.json` - Top 10 shareable insights

---

## 🎵 Step 3: Track Genre Droughts (Like Your Hip-Hop Example)

### Track Hip-Hop Representation
```bash
python3 genre_tracker.py
```

**What this finds:**
- 🚨 Weeks with ZERO hip-hop in top 40
- 📊 "First time in X years" calculations
- 📈 Genre trends over time
- 🔥 Peak weeks for any genre

### How It Works

The script uses a **genre mapping file** that classifies artists by genre:

```json
{
  "Drake": "Hip-Hop",
  "Taylor Swift": "Pop",
  "Morgan Wallen": "Country"
}
```

**Starter mapping:** `genre_mapping_sample.json` (auto-generated)

---

## 🎨 Customizing Genre Tracking

### Step 1: Edit the Genre Mapping
```bash
# Open the generated mapping file
nano genre_mapping_sample.json

# Or use any text editor
code genre_mapping_sample.json
```

### Step 2: Add More Artists
```json
{
  "Drake": "Hip-Hop",
  "Kendrick Lamar": "Hip-Hop",
  "Taylor Swift": "Pop",
  "Morgan Wallen": "Country",
  "Bad Bunny": "Latin",
  "ADD YOUR ARTISTS HERE": "GENRE"
}
```

### Step 3: Run Analysis
```python
from genre_tracker import GenreTracker
import json

# Load data
with open('billboard_recent.json') as f:
    data = json.load(f)

# Load your custom mapping
with open('genre_mapping_sample.json') as f:
    genres = json.load(f)

# Track Hip-Hop
tracker = GenreTracker(data, genres)

# Find droughts
droughts = tracker.find_genre_droughts("Hip-Hop", top_n=40)

for drought in droughts:
    print(drought['tweet'])  # Ready for Twitter!
```

---

## 📱 Social Media Ready Formats

### For Twitter
Every insight includes a `tweet` field formatted for 280 chars:

```python
insight = {
    'tweet': "For the first time in 35 years, no Hip-Hop in top 40.\n\n"
             "Week of October 30, 2024\n\n"
             "#MusicIndustry #Billboard #HipHop"
}
```

### For LinkedIn
Use the report generator:

```python
tracker = GenreTracker(data, genres)
report = tracker.generate_genre_report("Hip-Hop", top_n=40)
print(report)  # Full analysis ready to post
```

---

## 🔥 Examples of Insights You Can Find

### 1. Genre Droughts
```python
droughts = tracker.find_genre_droughts("Hip-Hop", top_n=40)
# "First time in 35 years: No Hip-Hop in top 40"
```

### 2. Artist Dominance
```python
from billboard_insights_generator import BillboardInsightsGenerator
gen = BillboardInsightsGenerator(data)
dominance = gen.find_artist_dominance_weeks(min_songs=5)
# "Drake has 8 songs in top 40 this week"
```

### 3. Biggest Chart Jumps
```python
velocity = gen.analyze_chart_velocity()
# "Song jumped 47 positions (72 → 25)"
```

### 4. High Debuts
```python
debuts = gen.find_new_entry_debuts(position_threshold=10)
# "Song debuts at #4 - highest debut this month"
```

### 5. Longevity Records
```python
runs = gen.find_longest_chart_runs(top_n=10)
# "Anti by Rihanna: 450+ weeks on chart"
```

### 6. Year-Over-Year Changes
```python
yoy = gen.compare_year_over_year()
# "2024 had 30% more #1 songs than 2023"
```

---

## 🚀 Automated Weekly Workflow

Create a weekly routine to find fresh insights:

```bash
#!/bin/bash
# weekly_insights.sh

echo "Downloading latest Billboard data..."
python3 billboard_downloader.py

echo "Generating insights..."
python3 billboard_insights_generator.py

echo "Checking genre trends..."
python3 genre_tracker.py

echo "✓ Done! Check billboard_insights.json for new content"
```

Run every Monday:
```bash
chmod +x weekly_insights.sh
./weekly_insights.sh
```

---

## 💡 Pro Tips for Social Media Engagement

### What Gets Engagement:
✅ **Historic firsts** - "First time in X years"
✅ **Surprising trends** - "Country now dominates more than Pop"
✅ **Big jumps** - "Biggest chart jump in 5 years"
✅ **Records broken** - "Longest chart run ever"
✅ **Unexpected winners** - "Independent artist beats major labels"

### Content Templates:

**Twitter Thread Starter:**
```
🚨 CHART ALERT

[Your insight here]

Here's what this means for the industry 🧵
```

**LinkedIn Post:**
```
📊 Music Industry Data Point:

[Your insight]

What does this tell us?

[Your analysis of 2-3 paragraphs]

What trends are you seeing in the charts?

#MusicIndustry #DataAnalytics #Billboard
```

---

## 🎯 Next Level: Combine with MusicBrainz

Enrich your insights with metadata:

```bash
python3 billboard_musicbrainz_enricher.py
```

**Adds:**
- Genre tags from MusicBrainz
- ISRC codes
- Release dates
- Label information

This makes genre tracking more accurate!

---

## 📊 Sample Output

```
🚨 TOP INSIGHTS FOR SOCIAL MEDIA

1. [Chart Velocity]
   'Paint The Town Red' by Doja Cat jumped 42 spots (67 → 25)

2. [Artist Dominance]
   Taylor Swift has 9 songs in top 40 (Week of 2023-10-28)

3. [Hot Debut]
   'Water' by Tyla debuts at #10

4. [Chart Longevity]
   'Anti' by Rihanna: 450 weeks on chart, 1 weeks at #1

5. [Genre Drought]
   🚨 FIRST TIME IN 35 YEARS: No Hip-Hop tracks in top 40
```

---

## 🛠️ Files You Need

| File | Purpose |
|------|---------|
| `billboard_downloader.py` | Downloads chart data |
| `billboard_insights_generator.py` | Finds general insights |
| `genre_tracker.py` | Tracks genre droughts & trends |
| `genre_mapping_sample.json` | Artist → Genre classifications |
| `billboard_musicbrainz_enricher.py` | Adds metadata (optional) |

---

## 🆘 Troubleshooting

### "Billboard data not found"
```bash
python3 billboard_downloader.py
```

### "No droughts detected"
Check your genre mapping - you may need to add more artists:
```bash
nano genre_mapping_sample.json
```

### Want more historical data?
Edit `billboard_downloader.py` line with `years=10` to `years=20`

---

## 📈 Advanced: Build Your Own Insights

```python
from genre_tracker import GenreTracker
import json

# Load data
with open('billboard_recent.json') as f:
    data = json.load(f)

with open('genre_mapping_sample.json') as f:
    genres = json.load(f)

# Initialize
tracker = GenreTracker(data, genres)

# Custom analysis
weekly = tracker.analyze_genre_presence_by_week("Hip-Hop", top_n=40)

# Find your own patterns
for date, info in weekly.items():
    if info['count'] == 1:  # Only 1 hip-hop song
        print(f"Barely hanging on: {date} had just 1 hip-hop song in top 40")
```

---

## 🎤 Share Your Insights!

Tag me when you post your data insights:
- Twitter: @YourHandle
- LinkedIn: Jeremy Stevenson

Let's bring data-driven storytelling to music!

---

**Questions?** Check the code comments or reach out!

**Last Updated:** January 2025
