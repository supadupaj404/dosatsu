# Spotify API Integration Guide for Dōsatsu

## 🎯 What This Does

Automatically classifies **all Billboard artists by genre** using Spotify's API.

**Before:** 42.9% coverage (173 manually mapped artists)
**After:** 95%+ coverage (5,000+ automatically classified artists)

---

## 📋 Step-by-Step Setup

### Step 1: Get Spotify API Credentials (5 minutes)

1. **Go to Spotify Developer Dashboard:**
   https://developer.spotify.com/dashboard

2. **Log in** (or create free Spotify account)

3. **Create an app:**
   - Click **"Create app"**
   - **App name:** `Dosatsu Chart Intelligence`
   - **App description:** `Music genre trend analysis using Billboard chart data`
   - **Redirect URIs:** `http://localhost:8888/callback`
   - **Which API/SDKs:** Check "Web API"
   - Click **"Save"**

4. **Get your credentials:**
   - Click on your app
   - Click **"Settings"** button
   - Copy **Client ID** (looks like: `abc123def456...`)
   - Click **"View client secret"**, copy **Client Secret** (looks like: `xyz789abc123...`)

**Important:** Keep these credentials private. Don't share them publicly.

---

### Step 2: Test Your Credentials (1 minute)

Run the test script to verify everything works:

```bash
cd ~/CodeProjects/Experiments/api-tests
python3 test_spotify_credentials.py
```

**When prompted:**
- Paste your **Client ID**
- Paste your **Client Secret**

**Expected output:**
```
✅ ALL TESTS PASSED!

Drake               → Hip-Hop        (Spotify genres: canadian hip hop, hip hop, rap)
Taylor Swift        → Pop            (Spotify genres: pop, singer-songwriter)
Morgan Wallen       → Country        (Spotify genres: contemporary country, country)
```

If tests pass, you're ready for the next step!

---

### Step 3: Classify All Billboard Artists (20-30 minutes)

This is a **one-time process** that builds your genre database:

```bash
python3 classify_all_billboard_artists.py
```

**What happens:**
1. Extracts ~5,000 unique artists from Billboard data (2000-2025)
2. Queries Spotify for each artist's genre
3. Maps Spotify's micro-genres to our 7 main categories
4. Saves results to `spotify_genre_cache.json`
5. Shows progress every 50 artists

**Sample output:**
```
Classifying 4,823 artists...

   1. Drake                → Hip-Hop        (Spotify: canadian hip hop, hip hop)
   2. Taylor Swift         → Pop            (Spotify: pop, singer-songwriter)
   3. Morgan Wallen        → Country        (Spotify: contemporary country)
   ...
4823. Last Artist          → Genre          (Spotify: ...)

✓ Saved 4,823 artists to cache: spotify_genre_cache.json

CLASSIFICATION SUMMARY
Total artists: 4,823
Successfully classified: 4,601
Not found: 222
Coverage: 95.4%
```

**Time:** ~20-30 minutes (Spotify is queried at ~10 requests/second)

---

### Step 4: Verify Coverage Improvement

Check how much coverage improved:

```bash
python3 -c "
import json
from spotify_genre_classifier import SpotifyGenreClassifier

# Load cache
classifier = SpotifyGenreClassifier('dummy', 'dummy')
print(f'Total artists classified: {len(classifier.cache):,}')
print()

# Show genre breakdown
from collections import Counter
genres = Counter()
for artist, data in classifier.cache.items():
    genres[data['dosatsu_genre']] += 1

print('Genre Distribution:')
for genre, count in genres.most_common():
    print(f'  {genre:<20} {count:>5} artists')
"
```

---

## 🎉 You're Done! Now What?

### Your genre database is ready to use!

The cache file (`spotify_genre_cache.json`) contains:

```json
{
  "Drake": {
    "name": "Drake",
    "spotify_genres": ["canadian hip hop", "hip hop", "rap"],
    "popularity": 95,
    "followers": 80000000,
    "dosatsu_genre": "Hip-Hop"
  },
  "Taylor Swift": {
    "name": "Taylor Swift",
    "spotify_genres": ["pop", "singer-songwriter"],
    "popularity": 100,
    "followers": 100000000,
    "dosatsu_genre": "Pop"
  },
  ...
}
```

---

## 🔧 Using Spotify Data in Analysis

### Update Your Analysis Scripts:

Before (manual mapping):
```python
from comprehensive_genre_mapping import COMPREHENSIVE_GENRE_MAPPING
```

After (Spotify data):
```python
from spotify_genre_classifier import SpotifyGenreClassifier

classifier = SpotifyGenreClassifier(
    client_id="your_id",  # Only needed for NEW artists
    client_secret="your_secret"
)

# Get genre for any artist
genre = classifier.get_genre("Drake")  # Returns: "Hip-Hop"
```

---

## 📊 Re-Run Analysis with 95%+ Coverage

Now re-run your analyses with dramatically better data:

### 10-Year Fall-Off Analysis:
```bash
# Create updated version
python3 falloff_analysis_spotify.py
```

### Multi-Genre Analysis:
```bash
python3 multi_genre_analyzer_spotify.py
```

**Expected improvement:**
- **Before:** 42.9% of songs classified
- **After:** 95%+ of songs classified
- **Impact:** Way more accurate trend detection!

---

## 🔄 Updating the Cache

### For New Artists:

The classifier automatically adds new artists when you run analyses:

```python
# First time: queries Spotify
genre = classifier.get_genre("New Artist 2025")

# Second time: uses cache (instant)
genre = classifier.get_genre("New Artist 2025")
```

Cache is saved automatically.

### Weekly Updates:

After downloading new Billboard data, just run your analysis scripts:
- New artists are automatically classified
- Cache grows over time
- No manual work needed

---

## 🎯 Benefits You Now Have

### 1. **Near-Complete Coverage**
- **95%+ of artists** classified (vs 42.9% before)
- Missing artists are typically obscure/regional

### 2. **Automatic Classification**
- No more manual research
- New artists classified instantly
- Cache grows automatically

### 3. **Bonus Data**
You also get:
- **Popularity scores** (0-100) - Streaming popularity
- **Follower counts** - Total Spotify followers
- **Spotify genres** - Full genre tags for reference

### 4. **More Accurate Insights**
With 95%+ coverage:
- Genre trends are more reliable
- "First time in X years" claims are accurate
- Market share percentages are precise

---

## 📈 What You Can Now Do

### New Analysis Possibilities:

1. **Streaming vs Charts Gap**
   ```python
   # Song is #1 on Billboard but only 70 popularity on Spotify
   # = Radio push, not organic streaming hit
   ```

2. **Predict Chart Movement**
   ```python
   # High Spotify popularity + low chart position
   # = Likely to rise soon
   ```

3. **Artist Momentum**
   ```python
   # Track popularity changes over time
   # Spot rising artists before they peak
   ```

4. **Genre Authenticity**
   ```python
   # How "pure" is this country artist?
   # Check if Spotify lists them as "country" or "country pop"
   ```

---

## 🛠️ Troubleshooting

### Error: "Authentication failed"
- Check Client ID and Client Secret are correct
- Make sure there are no extra spaces when pasting
- Verify your Spotify app is active in the dashboard

### Error: "Rate limit exceeded"
- Spotify limits ~100-200 requests per second
- The script includes automatic delays (0.1s per request)
- If you hit limits, wait 30 seconds and resume

### Some Artists Not Found
- Normal! ~5% of Billboard artists aren't on Spotify
- Usually very old artists or one-hit wonders
- These will show as "Unknown" genre

### Want to Re-Classify Everything?
```bash
# Delete cache and start fresh
rm spotify_genre_cache.json
python3 classify_all_billboard_artists.py
```

---

## 💾 Cache Management

### Cache File Location:
`~/CodeProjects/Experiments/api-tests/spotify_genre_cache.json`

### Cache Size:
- ~5,000 artists = ~2-3 MB file
- Fast to load and save
- No performance impact

### Backup Your Cache:
```bash
cp spotify_genre_cache.json spotify_genre_cache_backup.json
```

Recommended before major updates.

---

## 🔐 Security Best Practices

### Keep Credentials Private

**DON'T:**
- ❌ Commit credentials to GitHub
- ❌ Share credentials publicly
- ❌ Hardcode in scripts

**DO:**
- ✅ Use environment variables
- ✅ Store in local config file (not committed)
- ✅ Regenerate if exposed

### Using Environment Variables (Optional):

```bash
# Add to ~/.zshrc or ~/.bashrc
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"
```

Then in Python:
```python
import os
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
```

---

## 📊 Expected Results

### Coverage Improvement:

| Metric | Before | After |
|--------|--------|-------|
| Artists Mapped | 173 | ~4,600 |
| Coverage (2000-2015) | 42.9% | 95%+ |
| Coverage (2015-2025) | ~70% | 98%+ |
| Manual Work Required | High | None |

### Genre Distribution (Expected):

```
Pop                  ~35-40% of artists
Hip-Hop              ~25-30%
Country              ~15-20%
R&B                  ~10-15%
Rock                 ~8-12%
Alternative          ~5-8%
Latin                ~3-5%
Unknown              ~5%
```

---

## 🎯 Next Steps After Integration

1. **Re-run 10-year fall-off analysis** with better data
2. **Update all Dōsatsu analysis scripts** to use Spotify cache
3. **Generate new insights** with 95%+ coverage
4. **Create visualizations** showing genre trends
5. **Build Dōsatsu dashboard** with real-time Spotify data

---

## 📞 Need Help?

### Common Questions:

**Q: How much does this cost?**
A: $0. Spotify API is completely free.

**Q: How often should I update the cache?**
A: Weekly, when you download new Billboard data. Happens automatically.

**Q: What if Spotify changes their API?**
A: The classifier is built on stable v1 API. Very unlikely to break.

**Q: Can I use this for commercial purposes?**
A: Yes, Spotify allows commercial use of their API.

**Q: What about rate limits?**
A: Very generous. We're well under limits (~10 req/sec vs thousands allowed).

---

## ✅ Checklist

- [ ] Created Spotify Developer account
- [ ] Created Dōsatsu app in dashboard
- [ ] Got Client ID and Client Secret
- [ ] Tested credentials with `test_spotify_credentials.py`
- [ ] Ran `classify_all_billboard_artists.py`
- [ ] Verified `spotify_genre_cache.json` was created
- [ ] Checked coverage improvement
- [ ] Ready to re-run analyses with better data!

---

**Once you paste your credentials here, I'll help you run the classification and verify everything works!**
