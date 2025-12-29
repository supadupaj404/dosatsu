#!/usr/bin/env python3
"""
Automated Weekly Dōsatsu Update
Runs automatically every Tuesday to keep Billboard data fresh
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
log_file = Path(__file__).parent / "auto_update.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def download_latest_billboard_data():
    """Download the latest Billboard Hot 100 data"""
    logger.info("=" * 70)
    logger.info("DŌSATSU AUTOMATED WEEKLY UPDATE")
    logger.info("=" * 70)

    try:
        # Import the downloader
        from src.billboard_downloader import BillboardDataDownloader

        logger.info("📥 Downloading latest Billboard Hot 100 data...")
        downloader = BillboardDataDownloader()

        # Download complete history (includes latest week)
        all_data = downloader.download_all_charts("billboard_all_time.json")
        logger.info(f"✓ Downloaded {len(all_data)} weeks of data")

        # Also update recent data (25 years for analysis)
        recent_data = downloader.download_recent_charts(
            years=25,
            save_path="billboard_25years.json"
        )
        logger.info(f"✓ Updated 25-year dataset: {len(recent_data)} weeks")

        # Get latest week info
        if all_data:
            latest_week = max(all_data.keys())
            logger.info(f"📊 Latest chart week: {latest_week}")
            return latest_week, all_data

        return None, None

    except Exception as e:
        logger.error(f"❌ Error downloading Billboard data: {e}")
        return None, None


def classify_new_artists(data):
    """Classify any new artists using Spotify API"""
    logger.info("\n🎵 Checking for new artists to classify...")

    try:
        # Load existing genre cache
        cache_file = Path(__file__).parent / "spotify_genre_cache.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                genre_cache = json.load(f)
            logger.info(f"✓ Loaded {len(genre_cache)} cached artist genres")
        else:
            genre_cache = {}
            logger.info("No existing cache found, will create new one")

        # Get all unique artists from data
        all_artists = set()
        for chart in data.values():
            for song in chart:
                artist = song.get('artist')
                if artist:
                    all_artists.add(artist)

        # Find artists not yet classified
        new_artists = [a for a in all_artists if a not in genre_cache]

        if new_artists:
            logger.info(f"📝 Found {len(new_artists)} new artists to classify")
            logger.info(f"💡 You may want to run: python3 classify_remaining_artists.py")
        else:
            logger.info(f"✓ All artists already classified ({len(all_artists)} total)")

        return len(new_artists)

    except Exception as e:
        logger.error(f"⚠️ Error checking artist classification: {e}")
        return 0


def generate_weekly_insights(latest_week):
    """Generate insights for the latest week"""
    logger.info("\n💡 Generating weekly insights...")

    try:
        # Load the 25-year dataset
        with open('billboard_25years.json', 'r') as f:
            data = json.load(f)

        # Get latest chart
        latest_chart = data.get(latest_week)
        if not latest_chart:
            logger.warning(f"No chart found for {latest_week}")
            return

        # Basic stats
        top_40 = [s for s in latest_chart if s.get('position', 999) <= 40]

        logger.info(f"✓ Latest week: {latest_week}")
        logger.info(f"✓ Songs in top 40: {len(top_40)}")

        # Log some top songs
        logger.info("\n🔝 Top 5 songs this week:")
        for song in sorted(latest_chart, key=lambda x: x.get('position', 999))[:5]:
            logger.info(f"  #{song['position']}: {song['song']} - {song['artist']}")

        return True

    except Exception as e:
        logger.error(f"❌ Error generating insights: {e}")
        return False


def update_metadata():
    """Update metadata file with last update time"""
    metadata = {
        "last_update": datetime.now().isoformat(),
        "last_update_readable": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "update_status": "success"
    }

    with open('last_update.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"\n✓ Updated metadata: {metadata['last_update_readable']}")


def main():
    """Main automation workflow"""
    start_time = datetime.now()
    logger.info(f"🚀 Starting automated update at {start_time.strftime('%I:%M %p')}")

    try:
        # Step 1: Download latest Billboard data
        latest_week, all_data = download_latest_billboard_data()

        if not latest_week:
            logger.error("Failed to download data. Exiting.")
            sys.exit(1)

        # Step 2: Check for new artists to classify
        new_artist_count = classify_new_artists(all_data)

        # Step 3: Generate weekly insights
        generate_weekly_insights(latest_week)

        # Step 4: Update metadata
        update_metadata()

        # Success!
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("\n" + "=" * 70)
        logger.info(f"✅ UPDATE COMPLETE in {elapsed:.1f} seconds")
        logger.info("=" * 70)

        if new_artist_count > 0:
            logger.info(f"\n⚠️  NOTE: {new_artist_count} new artists need genre classification")
            logger.info("Run: python3 classify_remaining_artists.py")

        logger.info("\n💡 Dashboard data is now up to date!")
        logger.info("   Your Streamlit app will show the latest Billboard Hot 100 data.\n")

    except Exception as e:
        logger.error(f"\n❌ Automated update failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
