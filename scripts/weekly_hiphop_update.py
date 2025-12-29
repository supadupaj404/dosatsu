#!/usr/bin/env python3
"""
Weekly Hip-Hop Update Generator
Run this every Monday to get fresh insights for social media
"""

import json
from datetime import datetime, timedelta
from hiphop_trend_analyzer import HipHopTrendAnalyzer, HIPHOP_ARTISTS

def get_latest_week_insight():
    """Generate insight for the most recent week"""

    # Load data
    try:
        with open('billboard_5years.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Run billboard_downloader.py first to get fresh data")
        return

    # Initialize analyzer
    analyzer = HipHopTrendAnalyzer(data, HIPHOP_ARTISTS)

    # Get latest week
    latest_date = max(data.keys())
    latest_chart = data[latest_date]

    # Analyze top 40
    top_40 = [s for s in latest_chart if s.get('position', 999) <= 40]

    hiphop_in_top40 = []
    for song in top_40:
        artist = song.get('artist')
        if analyzer._is_hiphop(artist):
            hiphop_in_top40.append(song)

    count = len(hiphop_in_top40)
    percentage = (count / len(top_40) * 100) if top_40 else 0

    # Get recent average for comparison
    recent_weeks = sorted(data.keys())[-4:]  # Last 4 weeks
    recent_counts = []
    for date in recent_weeks:
        chart = data[date]
        top = [s for s in chart if s.get('position', 999) <= 40]
        hh_count = sum(1 for s in top if analyzer._is_hiphop(s.get('artist')))
        recent_counts.append(hh_count)

    four_week_avg = sum(recent_counts) / len(recent_counts)

    # Generate insight
    print("=" * 70)
    print("WEEKLY HIP-HOP UPDATE")
    print("=" * 70)
    print()
    print(f"Week of: {format_date(latest_date)}")
    print(f"Hip-Hop in Top 40: {count} songs ({percentage:.1f}%)")
    print(f"4-Week Average: {four_week_avg:.1f} songs")
    print()

    # Determine trend
    if count == 0:
        status = "🚨 DROUGHT WEEK"
        tweet = generate_drought_tweet(latest_date)
    elif count < four_week_avg - 2:
        status = "📉 Declining"
        tweet = generate_decline_tweet(latest_date, count, percentage)
    elif count > four_week_avg + 2:
        status = "📈 Recovering"
        tweet = generate_recovery_tweet(latest_date, count, percentage)
    else:
        status = "➡️ Stable"
        tweet = generate_stable_tweet(latest_date, count, percentage)

    print(f"Status: {status}")
    print()

    if hiphop_in_top40:
        print("Hip-Hop Songs in Top 40:")
        print("-" * 70)
        for song in sorted(hiphop_in_top40, key=lambda x: x['position']):
            print(f"  #{song['position']:2d} - {song['song']} - {song['artist']}")
    else:
        print("No hip-hop songs in top 40 this week.")

    print()
    print("=" * 70)
    print("TWEET-READY CONTENT")
    print("=" * 70)
    print()
    print(tweet)
    print()
    print("=" * 70)

    # Save weekly log
    log_entry = {
        'date': latest_date,
        'count': count,
        'percentage': round(percentage, 2),
        'status': status,
        'songs': [{'position': s['position'], 'song': s['song'], 'artist': s['artist']}
                  for s in hiphop_in_top40],
        'tweet': tweet
    }

    # Append to log file
    try:
        with open('weekly_hiphop_log.json', 'r') as f:
            log = json.load(f)
    except FileNotFoundError:
        log = []

    # Check if this week already logged
    if not any(entry['date'] == latest_date for entry in log):
        log.append(log_entry)

        with open('weekly_hiphop_log.json', 'w') as f:
            json.dump(log, f, indent=2)

        print(f"✓ Logged to weekly_hiphop_log.json")

    return log_entry


def format_date(date_str):
    """Format date as 'October 30, 2024'"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%B %d, %Y")


def generate_drought_tweet(date):
    """Generate tweet for drought week"""
    return f"""🚨 DROUGHT ALERT

Zero hip-hop tracks in Billboard Hot 100 top 40 this week.

Week of {format_date(date)}

Hip-hop's chart decline continues.

#HipHop #Billboard #MusicIndustry"""


def generate_decline_tweet(date, count, percentage):
    """Generate tweet for declining week"""
    return f"""📉 Hip-hop representation dropping

Only {count} tracks in Billboard top 40 ({percentage:.1f}%)

Week of {format_date(date)}

Below recent average. Trend continues.

#HipHop #Billboard #ChartData"""


def generate_recovery_tweet(date, count, percentage):
    """Generate tweet for recovery week"""
    return f"""📈 Hip-hop showing signs of recovery

{count} tracks in Billboard top 40 ({percentage:.1f}%)

Week of {format_date(date)}

Above recent average. Bounce back?

#HipHop #Billboard #MusicTrends"""


def generate_stable_tweet(date, count, percentage):
    """Generate tweet for stable week"""
    return f"""➡️ Hip-hop holding steady

{count} tracks in Billboard top 40 ({percentage:.1f}%)

Week of {format_date(date)}

Consistent with recent weeks.

#HipHop #Billboard #ChartData"""


def compare_to_last_year():
    """Compare current week to same week last year"""
    try:
        with open('billboard_5years.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return

    analyzer = HipHopTrendAnalyzer(data, HIPHOP_ARTISTS)

    latest_date = max(data.keys())
    latest_obj = datetime.strptime(latest_date, "%Y-%m-%d")

    # Find closest date one year ago
    year_ago = latest_obj - timedelta(days=365)
    year_ago_str = year_ago.strftime("%Y-%m-%d")

    # Find closest available date
    closest_date = min(data.keys(), key=lambda d: abs((datetime.strptime(d, "%Y-%m-%d") - year_ago).days))

    # Compare
    current_chart = data[latest_date]
    past_chart = data[closest_date]

    current_count = sum(1 for s in current_chart
                       if s.get('position', 999) <= 40
                       and analyzer._is_hiphop(s.get('artist')))

    past_count = sum(1 for s in past_chart
                    if s.get('position', 999) <= 40
                    and analyzer._is_hiphop(s.get('artist')))

    change = current_count - past_count

    print()
    print("=" * 70)
    print("YEAR-OVER-YEAR COMPARISON")
    print("=" * 70)
    print(f"This week ({format_date(latest_date)}): {current_count} hip-hop songs")
    print(f"Same week last year ({format_date(closest_date)}): {past_count} hip-hop songs")
    print(f"Change: {'+' if change >= 0 else ''}{change} songs")
    print()


if __name__ == "__main__":
    print("🎵 Fetching latest Billboard Hot 100 data...")
    print()

    # Note: In production, you'd re-download the latest week
    # For now, using existing data

    get_latest_week_insight()
    compare_to_last_year()

    print()
    print("💡 TIP: Run this script every Monday for fresh weekly insights!")
    print("   To get the absolute latest data, run billboard_downloader.py first.")
