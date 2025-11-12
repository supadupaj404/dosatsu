#!/bin/bash
# Dōsatsu Dashboard Launcher

cd ~/CodeProjects/Experiments/api-tests

echo "========================================"
echo "Launching Dōsatsu Dashboard"
echo "========================================"
echo ""

# Kill any existing Streamlit processes
echo "Cleaning up any existing Streamlit processes..."
pkill -9 streamlit 2>/dev/null
lsof -ti:8501 | xargs kill -9 2>/dev/null
sleep 1

echo "Starting Streamlit..."
echo ""
echo "Dashboard will open automatically in your browser"
echo "URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit with headless config to skip email prompt
STREAMLIT_SERVER_HEADLESS=true streamlit run streamlit_app.py
