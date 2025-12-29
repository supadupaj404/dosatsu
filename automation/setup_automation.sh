#!/bin/bash
# Dōsatsu Automation Setup Script
# Sets up weekly automated Billboard data updates

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_FILE="$SCRIPT_DIR/com.dosatsu.weeklyupdate.plist"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
INSTALLED_PLIST="$LAUNCHD_DIR/com.dosatsu.weeklyupdate.plist"

echo "=================================================="
echo "  Dōsatsu Weekly Automation Setup"
echo "=================================================="
echo ""

# Create LaunchAgents directory if it doesn't exist
if [ ! -d "$LAUNCHD_DIR" ]; then
    echo "📁 Creating LaunchAgents directory..."
    mkdir -p "$LAUNCHD_DIR"
fi

# Unload existing job if present
if [ -f "$INSTALLED_PLIST" ]; then
    echo "🔄 Unloading existing automation job..."
    launchctl unload "$INSTALLED_PLIST" 2>/dev/null || true
    rm "$INSTALLED_PLIST"
fi

# Copy plist to LaunchAgents
echo "📋 Installing automation job..."
cp "$PLIST_FILE" "$INSTALLED_PLIST"

# Load the job
echo "🚀 Loading automation job..."
launchctl load "$INSTALLED_PLIST"

echo ""
echo "✅ Automation setup complete!"
echo ""
echo "=================================================="
echo "  What This Does:"
echo "=================================================="
echo ""
echo "✓ Downloads latest Billboard Hot 100 data"
echo "✓ Runs every Tuesday at 1:00 PM EST"
echo "✓ Keeps your dashboard data fresh automatically"
echo "✓ Logs all updates to auto_update.log"
echo ""
echo "=================================================="
echo "  Useful Commands:"
echo "=================================================="
echo ""
echo "View automation status:"
echo "  launchctl list | grep dosatsu"
echo ""
echo "View recent logs:"
echo "  tail -50 $SCRIPT_DIR/auto_update.log"
echo ""
echo "Test it manually (run update now):"
echo "  python3 $SCRIPT_DIR/auto_weekly_update.py"
echo ""
echo "Disable automation:"
echo "  launchctl unload $INSTALLED_PLIST"
echo ""
echo "Re-enable automation:"
echo "  launchctl load $INSTALLED_PLIST"
echo ""
echo "=================================================="
echo "  Next Tuesday at 1 PM:"
echo "=================================================="
echo ""
echo "Your Billboard data will update automatically!"
echo "No action needed from you. 🎉"
echo ""
