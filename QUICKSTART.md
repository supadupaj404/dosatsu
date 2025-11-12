# Dōsatsu Dashboard - Quick Start

## Launch the Dashboard (2 steps)

### Step 1: Open Terminal
Open your Terminal app (Command + Space, type "Terminal")

### Step 2: Run these commands
Copy and paste this entire block:

```bash
cd ~/CodeProjects/Experiments/api-tests
streamlit run streamlit_app.py
```

**When you see "Email:" just press Enter** (leave it blank)

### Step 3: Open in Browser
After you press Enter, you'll see:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Your browser should open automatically to `http://localhost:8501`

If it doesn't, manually open your browser and go to:
```
http://localhost:8501
```

## What You'll See

The Dōsatsu dashboard with 5 pages:
- **Home**: Overview stats (67 years of Billboard data)
- **Current Charts**: Latest Hot 100 with genre breakdown
- **Year Comparison**: Compare any two years
- **Decade Analysis**: 67-year genre evolution
- **Artist Search**: Search 11,147 artists

## To Stop the Server

Press `Ctrl + C` in the Terminal window

---

## Troubleshooting

### "Port 8501 is already in use"
```bash
lsof -ti:8501 | xargs kill -9
```
Then try running streamlit again.

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Still not working?
Try a different port:
```bash
streamlit run streamlit_app.py --server.port 8502
```
Then go to `http://localhost:8502`

---

## Next Steps: Deploy for Beta Testing

Once you've tested it locally, see `DEPLOYMENT_GUIDE.md` for instructions on:
1. Pushing to GitHub
2. Deploying to Streamlit Cloud (free)
3. Getting a public URL to share with your beta testers

**You're 3 commands away from having a public URL!**
