# YouTube API Setup for Dōsatsu

## Quick Setup (5 minutes)

### Step 1: Get YouTube API Key

1. Go to **Google Cloud Console**: https://console.cloud.google.com/

2. **Create a project** (or select existing)
   - Click "Select a project" → "New Project"
   - Name it: `Dosatsu YouTube Integration`
   - Click "Create"

3. **Enable YouTube Data API v3**
   - Go to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click on it → Click "Enable"

4. **Create API Key**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the API key (looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXX`)

5. **Restrict the API Key** (Optional but recommended)
   - Click on your API key
   - Under "API restrictions":
     - Select "Restrict key"
     - Choose "YouTube Data API v3"
   - Click "Save"

### Step 2: Test the API Key

```bash
cd ~/CodeProjects/Experiments/api-tests
python3 fetch_youtube_top40.py
```

When prompted, paste your API key.

### Step 3: Monitor Quota Usage

Check your quota at: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas

---

## What You Get (FREE)

- **10,000 units/day** (resets midnight PT)
- Search for videos: 100 units each
- Get video stats: 1 unit each
- **~99 new songs per day**

---

## Expected Output

The script will:
1. Load your Billboard data
2. Get the most recent Top 40
3. Search YouTube for each song
4. Fetch view counts, likes, comments
5. Save results to `youtube_top40_results.json`
6. Save video IDs to `youtube_cache.json` (for future cheap updates)

---

## Quota Optimization

**First run:** Uses ~4,040 units (40 songs × 101 units)
**Future runs:** Uses ~40 units (just update stats)

You can run this **weekly** with minimal quota usage!

---

## Ready to Run!

```bash
python3 fetch_youtube_top40.py
```

Just paste your API key when prompted!
