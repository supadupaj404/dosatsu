# Dōsatsu Automated Weekly Updates

## Overview

Dōsatsu now has **zero-maintenance weekly automation** that keeps your Billboard data fresh automatically.

### What Gets Updated Automatically

Every **Tuesday at 1:00 PM EST**:
- ✅ Downloads latest Billboard Hot 100 chart data
- ✅ Updates all datasets (billboard_all_time.json, billboard_25years.json)
- ✅ Checks for new artists to classify
- ✅ Generates weekly insights
- ✅ Logs all activity to auto_update.log

**You don't have to do anything!** The system runs in the background.

---

## Quick Start

### Install the Automation (One-Time Setup)

```bash
cd ~/CodeProjects/Active/dosatsu
./setup_automation.sh
```

That's it! You'll see:
```
✅ Automation setup complete!

Next Tuesday at 1 PM:
Your Billboard data will update automatically!
```

---

## How It Works

### The Components

1. **auto_weekly_update.py** - Main automation script
   - Downloads latest Billboard data
   - Updates all datasets
   - Checks for new artists
   - Logs everything

2. **com.dosatsu.weeklyupdate.plist** - macOS scheduling configuration
   - Runs every Tuesday at 1:00 PM
   - Uses macOS `launchd` (more reliable than cron)

3. **setup_automation.sh** - One-time installation script
   - Installs the automation job
   - Creates log files
   - Loads the schedule

### The Schedule

- **When:** Every Tuesday at 1:00 PM EST
- **Why Tuesday:** Billboard releases new Hot 100 charts on Tuesday mornings
- **Duration:** ~5-10 seconds per update
- **Silent:** Runs in the background, no interruptions

---

## Monitoring & Management

### Check if automation is running:
```bash
launchctl list | grep dosatsu
```

You should see:
```
-    0    com.dosatsu.weeklyupdate
```

### View recent updates:
```bash
tail -50 ~/CodeProjects/Active/dosatsu/auto_update.log
```

### Check last update metadata:
```bash
cat ~/CodeProjects/Active/dosatsu/last_update.json
```

Example output:
```json
{
  "last_update": "2025-12-28T17:40:54.323067",
  "last_update_readable": "December 28, 2025 at 05:40 PM",
  "update_status": "success"
}
```

### Manually trigger an update (don't wait for Tuesday):
```bash
cd ~/CodeProjects/Active/dosatsu
python3 auto_weekly_update.py
```

---

## Managing the Automation

### Disable automation (pause weekly updates):
```bash
launchctl unload ~/Library/LaunchAgents/com.dosatsu.weeklyupdate.plist
```

### Re-enable automation:
```bash
launchctl load ~/Library/LaunchAgents/com.dosatsu.weeklyupdate.plist
```

### Uninstall completely:
```bash
launchctl unload ~/Library/LaunchAgents/com.dosatsu.weeklyupdate.plist
rm ~/Library/LaunchAgents/com.dosatsu.weeklyupdate.plist
```

### Change the schedule:

Edit the plist file:
```bash
nano ~/Library/LaunchAgents/com.dosatsu.weeklyupdate.plist
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.dosatsu.weeklyupdate.plist
launchctl load ~/Library/LaunchAgents/com.dosatsu.weeklyupdate.plist
```

---

## What Happens During Each Update

### Step 1: Download Latest Billboard Data
```
📥 Downloading latest Billboard Hot 100 data...
✓ Downloaded 3517 weeks of data
✓ Updated 25-year dataset: 1304 weeks
📊 Latest chart week: 2025-12-27
```

### Step 2: Check for New Artists
```
🎵 Checking for new artists to classify...
✓ Loaded 9449 cached artist genres
📝 Found 1722 new artists to classify
💡 You may want to run: python3 classify_remaining_artists.py
```

### Step 3: Generate Weekly Insights
```
💡 Generating weekly insights...
✓ Latest week: 2025-12-27
✓ Songs in top 40: 40

🔝 Top 5 songs this week:
  #1: All I Want For Christmas Is You - Mariah Carey
  #2: Jingle Bell Rock - Bobby Helms
  #3: Rockin' Around The Christmas Tree - Brenda Lee
```

### Step 4: Update Metadata
```
✓ Updated metadata: December 28, 2025 at 05:40 PM

✅ UPDATE COMPLETE in 5.0 seconds
```

---

## New Artist Classification

When new artists appear on the charts, you'll see this in the logs:
```
⚠️  NOTE: 1722 new artists need genre classification
Run: python3 classify_remaining_artists.py
```

### To classify new artists (uses Spotify API):
```bash
cd ~/CodeProjects/Active/dosatsu
python3 classify_remaining_artists.py
```

This is **optional** but improves genre insights.

---

## Files Created by Automation

| File | Purpose |
|------|---------|
| `auto_update.log` | All update activity logs |
| `auto_update_stdout.log` | Standard output from automation |
| `auto_update_stderr.log` | Error logs (if any) |
| `last_update.json` | Metadata about last successful update |
| `billboard_all_time.json` | Complete Billboard history (updated) |
| `billboard_25years.json` | 25-year dataset for analysis (updated) |
| `temp_all_charts.json` | Temporary download file |

---

## Troubleshooting

### Automation not running?

1. **Check if it's loaded:**
   ```bash
   launchctl list | grep dosatsu
   ```

2. **Check error logs:**
   ```bash
   tail -50 ~/CodeProjects/Active/dosatsu/auto_update_stderr.log
   ```

3. **Reload the job:**
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.dosatsu.weeklyupdate.plist
   launchctl load ~/Library/LaunchAgents/com.dosatsu.weeklyupdate.plist
   ```

### Updates are failing?

1. **Check internet connection**
2. **View detailed logs:**
   ```bash
   tail -100 ~/CodeProjects/Active/dosatsu/auto_update.log
   ```
3. **Run manually to see errors:**
   ```bash
   python3 ~/CodeProjects/Active/dosatsu/auto_weekly_update.py
   ```

### Want to test before Tuesday?

Run the script manually anytime:
```bash
cd ~/CodeProjects/Active/dosatsu
python3 auto_weekly_update.py
```

---

## FAQ

**Q: Will this run if my Mac is asleep?**
A: No. `launchd` will run the job the next time your Mac is awake.

**Q: Will I get notifications?**
A: No, it runs silently. Check `last_update.json` or logs to verify.

**Q: Does this use a lot of data?**
A: No. ~5-10 MB per week for Billboard data.

**Q: Can I change the time it runs?**
A: Yes! Edit the plist file (see "Change the schedule" above).

**Q: What if I don't want it anymore?**
A: Run the uninstall command (see "Uninstall completely" above).

**Q: Will this affect my Streamlit dashboard?**
A: The data updates in the background. If your dashboard is running, refresh the browser to see new data.

---

## Your Dashboard is Now Self-Maintaining! 🎉

- **No manual downloads needed**
- **Always shows current Billboard Hot 100 data**
- **Runs silently every Tuesday**
- **Zero maintenance required**

Just launch your Streamlit dashboard anytime and you'll have fresh data:
```bash
cd ~/CodeProjects/Active/dosatsu
streamlit run streamlit_app.py
```

---

## Summary

**Installed:** Weekly automated Billboard data updates
**Schedule:** Every Tuesday at 1:00 PM EST
**Runtime:** ~5-10 seconds
**Maintenance:** Zero

**Your Dōsatsu insights are now always up to date!** 💡
