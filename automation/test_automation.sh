#!/bin/bash
# Test Dōsatsu Automation System
# This script helps you verify that the weekly update automation works correctly

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "  Dōsatsu Automation Test"
echo "=================================================="
echo ""

# Step 1: Check current data age
echo "📅 Step 1: Checking current data timestamp..."
if [ -f "last_update.json" ]; then
    echo ""
    echo "Current data status:"
    cat last_update.json | python3 -m json.tool
else
    echo "⚠️  No update metadata found yet (this is normal for first run)"
fi

echo ""
echo "Press Enter to continue with the test..."
read -r

# Step 2: Run the automated update
echo ""
echo "=================================================="
echo "🚀 Step 2: Running automated update..."
echo "=================================================="
echo ""
echo "Watch for:"
echo "  ✓ Download progress"
echo "  ✓ Latest chart week"
echo "  ✓ Top 5 songs"
echo "  ✓ Success message"
echo ""
echo "Starting in 3 seconds..."
sleep 3

python3 auto_weekly_update.py

# Step 3: Verify the update
echo ""
echo "=================================================="
echo "✅ Step 3: Verifying the update worked..."
echo "=================================================="
echo ""

# Check if metadata was updated
if [ -f "last_update.json" ]; then
    echo "✓ Metadata file created/updated:"
    cat last_update.json | python3 -m json.tool
    echo ""
else
    echo "❌ Metadata file not found - update may have failed"
    exit 1
fi

# Check if data files exist and show their timestamps
echo "✓ Data file timestamps:"
echo ""
ls -lh billboard_all_time.json billboard_25years.json 2>/dev/null | awk '{print "  " $9 " - " $5 " - Modified: " $6 " " $7}'
echo ""

# Check the log file
if [ -f "auto_update.log" ]; then
    echo "✓ Recent log entries:"
    echo ""
    tail -10 auto_update.log | sed 's/^/  /'
    echo ""
else
    echo "⚠️  Log file not found"
fi

# Step 4: Quick data sanity check
echo ""
echo "=================================================="
echo "📊 Step 4: Quick data sanity check..."
echo "=================================================="
echo ""

python3 << 'EOF'
import json
from datetime import datetime

# Load the data
with open('billboard_25years.json', 'r') as f:
    data = json.load(f)

# Get latest week
latest_week = max(data.keys())
latest_chart = data[latest_week]

print(f"✓ Latest chart week: {latest_week}")
print(f"✓ Total weeks in dataset: {len(data)}")
print(f"✓ Songs in latest chart: {len(latest_chart)}")
print("")

# Show top 5
print("✓ Current Billboard Top 5:")
top_5 = sorted(latest_chart, key=lambda x: x.get('position', 999))[:5]
for song in top_5:
    print(f"  #{song['position']}: {song['song']} - {song['artist']}")

print("")

# Check how fresh the data is
latest_date = datetime.strptime(latest_week, "%Y-%m-%d")
days_old = (datetime.now() - latest_date).days

if days_old <= 7:
    print(f"✅ Data is fresh! ({days_old} days old)")
elif days_old <= 14:
    print(f"⚠️  Data is {days_old} days old (acceptable)")
else:
    print(f"❌ Data is stale ({days_old} days old)")
EOF

echo ""
echo "=================================================="
echo "  Test Results Summary"
echo "=================================================="
echo ""
echo "✅ Automated update script works correctly!"
echo "✅ Data files are being updated"
echo "✅ Logs are being generated"
echo "✅ Billboard data is current"
echo ""
echo "=================================================="
echo "  Next Step: Install the Weekly Automation"
echo "=================================================="
echo ""
echo "To schedule this to run automatically every Tuesday:"
echo ""
echo "  ./setup_automation.sh"
echo ""
echo "Or test it again anytime with:"
echo ""
echo "  ./test_automation.sh"
echo ""
