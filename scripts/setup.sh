#!/bin/bash
# Dōsatsu First-Time Setup Script
# Sets up everything needed to run Dōsatsu

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=================================================="
echo "  Dōsatsu Setup"
echo "  洞察 - \"Insight\""
echo "=================================================="
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $python_version"

# Check if Python 3.8+
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
    echo "   ❌ Error: Python 3.8 or higher is required"
    echo "   Please install Python 3.8+ and try again"
    exit 1
fi
echo "   ✓ Python version is compatible"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip3 install -q -r "$PROJECT_ROOT/requirements.txt"
    echo "   ✓ Dependencies installed"
else
    echo "   ⚠️  requirements.txt not found, skipping"
fi
echo ""

# Create data directories
echo "📁 Creating data directories..."
mkdir -p "$PROJECT_ROOT/data/billboard"
mkdir -p "$PROJECT_ROOT/data/cache"
mkdir -p "$PROJECT_ROOT/data/logs"
echo "   ✓ Data directories created"
echo ""

# Download Billboard data
echo "📥 Downloading Billboard Hot 100 data..."
echo "   This may take 10-15 seconds..."
cd "$PROJECT_ROOT"
python3 src/billboard_downloader.py > /dev/null 2>&1 || {
    echo "   Using alternative download method..."
    python3 -c "
from src.billboard_downloader import BillboardDataDownloader
downloader = BillboardDataDownloader()
data = downloader.download_all_charts('data/billboard/billboard_all_time.json')
recent = downloader.download_recent_charts(years=25, save_path='data/billboard/billboard_25years.json')
print(f'Downloaded {len(data)} weeks of chart data')
"
}
echo "   ✓ Billboard data downloaded"
echo ""

# Check file sizes
echo "📊 Verifying data..."
if [ -f "$PROJECT_ROOT/data/billboard/billboard_all_time.json" ]; then
    size=$(du -h "$PROJECT_ROOT/data/billboard/billboard_all_time.json" | awk '{print $1}')
    echo "   ✓ billboard_all_time.json ($size)"
fi
if [ -f "$PROJECT_ROOT/data/billboard/billboard_25years.json" ]; then
    size=$(du -h "$PROJECT_ROOT/data/billboard/billboard_25years.json" | awk '{print $1}')
    echo "   ✓ billboard_25years.json ($size)"
fi
echo ""

# Create .streamlit directory if it doesn't exist
echo "⚙️  Configuring Streamlit..."
mkdir -p "$PROJECT_ROOT/dashboard/.streamlit"
cat > "$PROJECT_ROOT/dashboard/.streamlit/config.toml" << 'EOF'
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"

[server]
headless = true
enableCORS = false
EOF
echo "   ✓ Streamlit configured"
echo ""

# Summary
echo "=================================================="
echo "  ✅ Setup Complete!"
echo "=================================================="
echo ""
echo "🚀 To launch the dashboard:"
echo ""
echo "   streamlit run dashboard/streamlit_app.py"
echo ""
echo "   Your browser will open to http://localhost:8501"
echo ""
echo "=================================================="
echo "  Optional Next Steps:"
echo "=================================================="
echo ""
echo "📅 Enable weekly automation (updates data every Tuesday):"
echo "   ./automation/setup_automation.sh"
echo ""
echo "🎵 Add Spotify integration (better genre classification):"
echo "   See docs/SPOTIFY_INTEGRATION_GUIDE.md"
echo ""
echo "📖 Read the documentation:"
echo "   docs/QUICKSTART.md"
echo ""
echo "=================================================="
echo ""
