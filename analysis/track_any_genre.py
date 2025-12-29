#!/usr/bin/env python3
"""
Dōsatsu: Track ANY Genre on Demand
Simple interface to analyze any genre trend
"""

import json
from analysis.multi_genre_analyzer import MultiGenreAnalyzer, MULTI_GENRE_MAPPING

def track_genre(genre_name, years=5):
    """
    Track a specific genre over time

    Usage:
        track_genre("Country", years=5)
        track_genre("Latin", years=10)
        track_genre("Rock", years=25)
    """

    # Load data
    with open('billboard_25years.json') as f:
        data = json.load(f)

    # Initialize analyzer
    analyzer = MultiGenreAnalyzer(data, MULTI_GENRE_MAPPING)

    # Analyze all genres
    genre_weekly = analyzer.analyze_all_genres(top_n=40)
    genre_stats = analyzer.calculate_genre_stats(genre_weekly, years=years)

    # Get specific genre
    if genre_name not in genre_stats:
        print(f"❌ Genre '{genre_name}' not found.")
        print(f"Available genres: {', '.join(genre_stats.keys())}")
        return

    stats = genre_stats[genre_name]

    # Display results
    print("="*70)
    print(f"DŌSATSU: {genre_name.upper()} ANALYSIS")
    print("="*70)
    print()

    print(f"Time Period: Last {years} years")
    print(f"Current Status: {stats['trend']}")
    print()

    print("METRICS:")
    print("-"*70)
    print(f"Average Representation: {stats['avg_percentage']:.1f}% of top 40")
    print(f"Current Average: {stats['recent_avg']:.1f} songs per week")
    print(f"Peak Count: {stats['max_count']} songs in one week")
    print(f"Trend Change: {'+' if stats['trend_change'] > 0 else ''}{stats['trend_change']:.2f} songs/week")
    print()

    print("YEAR-BY-YEAR:")
    print("-"*70)
    for year in sorted(stats['yearly_breakdown'].keys())[-years:]:
        avg = stats['yearly_breakdown'][year]
        print(f"{year}: {avg:.2f} songs/week avg")

    print()

    # Generate insight
    if stats['trend'] == "📈 Rising":
        action = "✅ INVEST - This genre is growing"
    elif stats['trend'] == "📉 Declining":
        action = "⚠️  CAUTION - This genre is declining"
    else:
        action = "➡️  STABLE - This genre is holding steady"

    print("="*70)
    print(f"RECOMMENDATION: {action}")
    print("="*70)
    print()

    # Social media ready
    tweet = generate_tweet(genre_name, stats, years)
    print("TWEET-READY INSIGHT:")
    print("-"*70)
    print(tweet)
    print()

    return stats


def generate_tweet(genre, stats, years):
    """Generate social media post for genre"""

    yearly = stats['yearly_breakdown']
    sorted_years = sorted(yearly.keys())

    if len(sorted_years) >= 2:
        first_year = sorted_years[-years] if len(sorted_years) >= years else sorted_years[0]
        last_year = sorted_years[-1]

        first_avg = yearly[first_year]
        last_avg = yearly[last_year]

        change = last_avg - first_avg
        change_pct = (change / first_avg * 100) if first_avg > 0 else 0

        if stats['trend'] == "📈 Rising":
            emoji = "🚀"
            verb = "surging"
        elif stats['trend'] == "📉 Declining":
            emoji = "📉"
            verb = "declining"
        else:
            emoji = "➡️"
            verb = "stable"

        tweet = f"""{emoji} {genre} is {verb} on the Billboard Hot 100

{first_year}: {first_avg:.1f} songs/week
{last_year}: {last_avg:.1f} songs/week

{'+' if change > 0 else ''}{change_pct:.0f}% change in {years} years

#Dōsatsu #MusicIndustry #{genre.replace(' ', '')}"""

        return tweet

    return f"{genre} averaging {stats['recent_avg']:.1f} songs/week in top 40"


def compare_genres(genre1, genre2, years=5):
    """Compare two genres head-to-head"""

    # Load data
    with open('billboard_25years.json') as f:
        data = json.load(f)

    analyzer = MultiGenreAnalyzer(data, MULTI_GENRE_MAPPING)
    genre_weekly = analyzer.analyze_all_genres(top_n=40)
    genre_stats = analyzer.calculate_genre_stats(genre_weekly, years=years)

    if genre1 not in genre_stats or genre2 not in genre_stats:
        print("One or both genres not found")
        return

    stats1 = genre_stats[genre1]
    stats2 = genre_stats[genre2]

    print("="*70)
    print(f"DŌSATSU: {genre1.upper()} vs {genre2.upper()}")
    print("="*70)
    print()

    print(f"{'METRIC':<30} {genre1:<15} {genre2:<15}")
    print("-"*70)
    print(f"{'Current Avg (songs/week)':<30} {stats1['recent_avg']:<15.1f} {stats2['recent_avg']:<15.1f}")
    print(f"{'Trend':<30} {stats1['trend']:<15} {stats2['trend']:<15}")
    print(f"{'5-Year Change':<30} {stats1['trend_change']:<15.2f} {stats2['trend_change']:<15.2f}")
    print(f"{'Peak Count':<30} {stats1['max_count']:<15} {stats2['max_count']:<15}")
    print()

    # Determine winner
    if stats1['recent_avg'] > stats2['recent_avg']:
        winner = genre1
        loser = genre2
        diff = stats1['recent_avg'] - stats2['recent_avg']
    else:
        winner = genre2
        loser = genre1
        diff = stats2['recent_avg'] - stats1['recent_avg']

    print("="*70)
    print(f"WINNER: {winner} leads by {diff:.1f} songs/week")
    print("="*70)


def show_all_genres():
    """Quick snapshot of all genres"""

    with open('billboard_25years.json') as f:
        data = json.load(f)

    analyzer = MultiGenreAnalyzer(data, MULTI_GENRE_MAPPING)
    genre_weekly = analyzer.analyze_all_genres(top_n=40)
    genre_stats = analyzer.calculate_genre_stats(genre_weekly, years=5)
    market_share = analyzer.get_market_share(genre_stats)

    sorted_genres = sorted(
        market_share.items(),
        key=lambda x: x[1]['share_percent'],
        reverse=True
    )

    print("="*70)
    print("DŌSATSU: ALL GENRES AT A GLANCE")
    print("="*70)
    print()
    print(f"{'Genre':<20} {'Market Share':<15} {'Trend':<15}")
    print("-"*70)

    for genre, data in sorted_genres:
        if data['share_percent'] > 0:
            print(f"{genre:<20} {data['share_percent']:>5.1f}% {data['avg_songs']:>6.1f}/wk    {data['trend']:<15}")

    print()


# Interactive demo
if __name__ == "__main__":
    print("DŌSATSU: Track Any Genre")
    print()

    # Show all genres first
    show_all_genres()

    print()
    print("="*70)
    print("DETAILED ANALYSIS: COUNTRY")
    print("="*70)
    print()

    # Track specific genre
    track_genre("Country", years=5)

    print()
    print("="*70)
    print("COMPARISON: COUNTRY vs HIP-HOP")
    print("="*70)
    print()

    # Compare genres
    compare_genres("Country", "Hip-Hop", years=5)

    print()
    print("="*70)
    print("💡 TIP: You can track ANY genre!")
    print()
    print("Examples:")
    print("  track_genre('Latin', years=10)")
    print("  track_genre('Alternative', years=5)")
    print("  compare_genres('Pop', 'R&B')")
    print("="*70)
