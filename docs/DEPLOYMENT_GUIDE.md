# Dōsatsu Beta Deployment Guide

## Quick Start - Test Locally

1. **Open Terminal and navigate to the project:**
   ```bash
   cd ~/CodeProjects/Experiments/api-tests
   ```

2. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **The app will automatically open in your browser at:**
   ```
   http://localhost:8501
   ```

4. **Test all 5 pages:**
   - Home (Overview)
   - Current Charts
   - Year Comparison
   - Decade Analysis
   - Artist Search

5. **Stop the app when done:**
   - Press `Ctrl+C` in the terminal

---

## Deploy to Streamlit Cloud (For Beta Testing)

### Step 1: Prepare GitHub Repository

1. **Initialize Git (if not already done):**
   ```bash
   cd ~/CodeProjects/Experiments/api-tests
   git init
   git add .
   git commit -m "Initial Dōsatsu dashboard

   - Streamlit dashboard with 5 analysis pages
   - 67 years of Billboard Hot 100 data (1958-2025)
   - Genre classification via Spotify + MusicBrainz
   - 99.5% artist coverage (11,091 artists)

   Generated with Claude Code

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

2. **Create GitHub repository:**
   ```bash
   gh repo create dosatsu-dashboard --public --source=. --remote=origin --push
   ```

   Or manually:
   - Go to https://github.com/new
   - Repository name: `dosatsu-dashboard`
   - Make it **Public** (required for free Streamlit Cloud)
   - Don't initialize with README (you already have files)
   - Click "Create repository"

3. **Push your code:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/dosatsu-dashboard.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit https://streamlit.io/cloud
   - Click "Sign up" or "Sign in" (use your GitHub account)

2. **Deploy the app:**
   - Click "New app"
   - Repository: Select `dosatsu-dashboard`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Wait for deployment (2-3 minutes)**
   - Streamlit will install dependencies from `requirements.txt`
   - You'll see build logs in real-time
   - Once complete, you'll get a public URL

4. **Your app will be live at:**
   ```
   https://YOUR_APP_NAME.streamlit.app
   ```

### Step 3: Share with Beta Testers

1. **Send them the URL** - that's it! No login required for viewers

2. **Gather feedback via:**
   - Google Form
   - Discord/Slack channel
   - Email
   - Notion database

3. **Example message to beta testers:**
   ```
   Hey! I've built Dōsatsu - a music industry intelligence platform
   analyzing 67 years of Billboard Hot 100 data.

   Check it out: https://your-app.streamlit.app

   Would love your feedback on:
   - What insights are most valuable?
   - What's missing?
   - Any bugs or issues?
   - Additional features you'd want?

   Thanks!
   ```

---

## Files Overview

```
api-tests/
├── streamlit_app.py          # Main dashboard (5 pages)
├── requirements.txt           # Python dependencies
├── .streamlit/config.toml     # Streamlit configuration
├── .gitignore                 # Git ignore rules
│
├── billboard_67years.json     # 67 years of chart data (1958-2025)
├── hybrid_genre_cache.json    # Artist genre classifications
│
├── spotify_genre_classifier.py    # Spotify API integration
├── musicbrainz_classifier.py      # MusicBrainz API integration
├── hybrid_classifier.py           # Combined classifier
│
└── DEPLOYMENT_GUIDE.md        # This file
```

---

## Dashboard Features

### Page 1: Home
- Overview statistics
- 67 years, 3,510 weeks, 11,091 artists
- Dataset coverage: 99.5%

### Page 2: Current Charts
- Latest Billboard Hot 100
- Genre breakdown pie chart
- Top 10 songs with genres

### Page 3: Year Comparison
- Compare any two years (2000-2025)
- Genre distribution changes
- Biggest gainers/decliners

### Page 4: Decade Analysis
- 67-year genre evolution (1960s-2020s)
- Interactive line chart
- Key insights (Rock's decline, Country's rise)

### Page 5: Artist Search
- Search 11,091 artists
- See their genre classification
- View chart appearance history

---

## Updating the Dashboard

When you want to update the live dashboard:

```bash
cd ~/CodeProjects/Experiments/api-tests

# Make your changes to streamlit_app.py

# Commit and push
git add .
git commit -m "Update: [describe your changes]"
git push

# Streamlit Cloud will auto-deploy in ~30 seconds
```

---

## Troubleshooting

### Local Testing Issues

**Problem:** Import errors
```bash
pip install -r requirements.txt
```

**Problem:** File not found errors
- Make sure you're in `/Users/jeremystevenson/CodeProjects/Experiments/api-tests`
- Verify data files exist: `ls *.json`

**Problem:** Port already in use
```bash
# Use a different port
streamlit run streamlit_app.py --server.port 8502
```

### Deployment Issues

**Problem:** Build fails on Streamlit Cloud
- Check `requirements.txt` has all dependencies
- Verify all imports in `streamlit_app.py` are correct
- Check build logs for specific errors

**Problem:** App loads but shows errors
- Make sure all data files (`*.json`) are committed to Git
- Verify file paths are correct (no hardcoded absolute paths)

**Problem:** Slow loading
- Streamlit Cloud free tier has limited resources
- Consider reducing data size or adding more caching

---

## Next Steps

1. **Test locally first** - make sure everything works
2. **Deploy to Streamlit Cloud** - get a public URL
3. **Gather feedback** - share with 5-10 beta testers
4. **Iterate** - add requested features
5. **Scale** - consider paid Streamlit plan if traffic grows

---

## Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Cloud Docs:** https://docs.streamlit.io/streamlit-community-cloud
- **Plotly Charts:** https://plotly.com/python/
- **Billboard API:** https://github.com/guoguo12/billboard-charts

---

## Contact

For issues or questions about Dōsatsu, reach out to Jeremy at Whetstone.

**Generated with Claude Code**
