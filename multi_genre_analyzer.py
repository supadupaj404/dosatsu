#!/usr/bin/env python3
"""
Dōsatsu: Multi-Genre Analyzer
Track ANY genre trend on Billboard charts
"""

import json
from datetime import datetime
from collections import defaultdict
import statistics

class MultiGenreAnalyzer:
    """Analyze multiple genres simultaneously"""

    def __init__(self, billboard_data, genre_mapping):
        self.data = billboard_data
        self.dates = sorted(billboard_data.keys())
        self.genre_mapping = genre_mapping

    def analyze_all_genres(self, top_n=40):
        """Analyze representation for all genres"""

        # Track each genre week by week
        genre_weekly = defaultdict(lambda: defaultdict(lambda: {
            'count': 0,
            'songs': []
        }))

        for date in self.dates:
            chart = self.data[date]
            top_songs = [s for s in chart if s.get('position', 999) <= top_n]

            for song in top_songs:
                artist = song.get('artist')
                genre = self.genre_mapping.get(artist, 'Unknown')

                if genre != 'Unknown':
                    genre_weekly[genre][date]['count'] += 1
                    genre_weekly[genre][date]['songs'].append({
                        'position': song.get('position'),
                        'song': song.get('song'),
                        'artist': artist
                    })

        return genre_weekly

    def calculate_genre_stats(self, genre_weekly, years=5):
        """Calculate statistics for each genre"""

        stats = {}

        for genre, weekly_data in genre_weekly.items():
            # Get counts for all weeks
            counts = [data['count'] for data in weekly_data.values()]
            percentages = [(count / 40 * 100) for count in counts]

            # Group by year
            yearly_avg = defaultdict(list)
            for date, data in weekly_data.items():
                year = date[:4]
                yearly_avg[year].append(data['count'])

            # Calculate year averages
            year_avgs = {
                year: sum(counts) / len(counts) if counts else 0
                for year, counts in yearly_avg.items()
            }

            # Recent years only
            recent_years = sorted(year_avgs.keys())[-years:]

            if len(recent_years) >= 2:
                first_year_avg = year_avgs[recent_years[0]]
                last_year_avg = year_avgs[recent_years[-1]]
                trend_change = last_year_avg - first_year_avg

                if trend_change > 1:
                    trend = "📈 Rising"
                elif trend_change < -1:
                    trend = "📉 Declining"
                else:
                    trend = "➡️ Stable"
            else:
                trend = "➡️ Stable"
                trend_change = 0

            stats[genre] = {
                'avg_count': statistics.mean(counts) if counts else 0,
                'avg_percentage': statistics.mean(percentages) if percentages else 0,
                'max_count': max(counts) if counts else 0,
                'total_weeks': len(weekly_data),
                'trend': trend,
                'trend_change': round(trend_change, 2),
                'recent_avg': year_avgs.get(recent_years[-1], 0) if recent_years else 0,
                'yearly_breakdown': year_avgs
            }

        return stats

    def get_market_share(self, genre_stats):
        """Calculate current market share by genre"""

        total_representation = sum(
            s['recent_avg'] for s in genre_stats.values()
        )

        market_share = {}
        for genre, stats in genre_stats.items():
            if total_representation > 0:
                share = (stats['recent_avg'] / total_representation) * 100
            else:
                share = 0

            market_share[genre] = {
                'share_percent': round(share, 1),
                'avg_songs': round(stats['recent_avg'], 1),
                'trend': stats['trend']
            }

        return market_share

    def generate_competitive_report(self, top_n=40):
        """Generate multi-genre competitive landscape"""

        print("Analyzing all genres across Billboard Hot 100...")
        print()

        # Analyze
        genre_weekly = self.analyze_all_genres(top_n)
        genre_stats = self.calculate_genre_stats(genre_weekly, years=5)
        market_share = self.get_market_share(genre_stats)

        # Sort by current market share
        sorted_genres = sorted(
            market_share.items(),
            key=lambda x: x[1]['share_percent'],
            reverse=True
        )

        print("="*70)
        print("DŌSATSU: MULTI-GENRE COMPETITIVE ANALYSIS")
        print("="*70)
        print()

        print("CURRENT MARKET SHARE (Top 40):")
        print("-"*70)
        for genre, data in sorted_genres:
            if data['share_percent'] > 0:
                print(f"{data['trend']} {genre:20s} {data['share_percent']:5.1f}% "
                      f"({data['avg_songs']:.1f} songs/week)")

        print()
        print("="*70)
        print("OPPORTUNITIES & THREATS")
        print("="*70)
        print()

        # Rising genres (opportunities)
        rising = [(g, d) for g, d in sorted_genres
                  if d['trend'] == "📈 Rising" and d['share_percent'] > 5]

        if rising:
            print("🚀 RISING GENRES (Invest Here):")
            for genre, data in rising:
                print(f"  • {genre}: {data['share_percent']}% market share (+growing)")

        print()

        # Declining genres (threats)
        declining = [(g, d) for g, d in sorted_genres
                     if d['trend'] == "📉 Declining" and d['share_percent'] > 5]

        if declining:
            print("⚠️  DECLINING GENRES (Caution):")
            for genre, data in declining:
                print(f"  • {genre}: {data['share_percent']}% market share (declining)")

        print()
        print("="*70)

        return {
            'market_share': market_share,
            'genre_stats': genre_stats,
            'rising': [g for g, _ in rising],
            'declining': [g for g, _ in declining]
        }


# Expanded genre mapping (all major genres)
MULTI_GENRE_MAPPING = {
    # Hip-Hop/Rap
    "Drake": "Hip-Hop",
    "21 Savage": "Hip-Hop",
    "Travis Scott": "Hip-Hop",
    "Lil Baby": "Hip-Hop",
    "Future": "Hip-Hop",
    "Gunna": "Hip-Hop",
    "Kendrick Lamar": "Hip-Hop",
    "J. Cole": "Hip-Hop",
    "Megan Thee Stallion": "Hip-Hop",
    "Cardi B": "Hip-Hop",
    "Nicki Minaj": "Hip-Hop",

    # Country
    "Morgan Wallen": "Country",
    "Luke Combs": "Country",
    "Zach Bryan": "Country",
    "Jelly Roll": "Country",
    "Kane Brown": "Country",
    "Chris Stapleton": "Country",
    "Thomas Rhett": "Country",
    "Bailey Zimmerman": "Country",
    "Cody Johnson": "Country",
    "Lainey Wilson": "Country",
    "Megan Moroney": "Country",

    # Pop
    "Taylor Swift": "Pop",
    "Ariana Grande": "Pop",
    "Olivia Rodrigo": "Pop",
    "Billie Eilish": "Pop",
    "Dua Lipa": "Pop",
    "Harry Styles": "Pop",
    "Miley Cyrus": "Pop",
    "Sabrina Carpenter": "Pop",
    "Tate McRae": "Pop",
    "Selena Gomez": "Pop",
    "Doja Cat": "Pop",
    "Rihanna": "Pop",
    "Katy Perry": "Pop",
    "Lady Gaga": "Pop",

    # R&B
    "SZA": "R&B",
    "The Weeknd": "R&B",
    "Beyoncé": "R&B",
    "Usher": "R&B",
    "Chris Brown": "R&B",
    "Summer Walker": "R&B",
    "Brent Faiyaz": "R&B",
    "Victoria Monét": "R&B",

    # Rock/Alternative
    "Imagine Dragons": "Rock",
    "OneRepublic": "Rock",
    "Hozier": "Alternative",
    "Noah Kahan": "Alternative",
    "The Lumineers": "Alternative",
    "AJR": "Alternative",

    # Latin
    "Bad Bunny": "Latin",
    "Peso Pluma": "Latin",
    "Karol G": "Latin",
    "Feid": "Latin",
    "Rauw Alejandro": "Latin",
}


def demo():
    """Run multi-genre analysis"""

    # Load data
    try:
        with open('billboard_25years.json', 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded 25 years of Billboard data")
        print()
    except FileNotFoundError:
        print("❌ Run billboard_downloader.py first")
        return

    # Initialize
    analyzer = MultiGenreAnalyzer(data, MULTI_GENRE_MAPPING)

    # Generate report
    report = analyzer.generate_competitive_report()

    # Save
    with open('dosatsu_genre_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("✓ Full report saved to: dosatsu_genre_report.json")
    print()
    print("="*70)
    print("💡 This analysis works for ANY genre you track!")
    print("   Just add artists to the genre mapping.")
    print("="*70)


if __name__ == "__main__":
    demo()
