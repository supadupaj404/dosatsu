#!/usr/bin/env python3
"""
2024 vs 2025 Year-Over-Year Analysis
Generates interesting, shareable insights comparing the two years
"""

import json
from collections import Counter, defaultdict
from datetime import datetime
from src.spotify_genre_classifier import SpotifyGenreClassifier

class YearOverYearAnalyzer:
    """Compare 2024 vs 2025 for interesting insights"""

    def __init__(self, data_file='billboard_67years.json'):
        # Load data
        with open(data_file, 'r') as f:
            self.data = json.load(f)

        # Load genre classifier
        self.classifier = SpotifyGenreClassifier('dummy', 'dummy')

        # Filter by year
        self.data_2024 = {date: chart for date, chart in self.data.items() if date.startswith('2024')}
        self.data_2025 = {date: chart for date, chart in self.data.items() if date.startswith('2025')}

        print(f"Loaded {len(self.data_2024)} weeks from 2024")
        print(f"Loaded {len(self.data_2025)} weeks from 2025")
        print()

    def get_genre_stats(self, year_data, top_n=40):
        """Calculate genre statistics for a year"""
        genre_weekly = defaultdict(list)
        drought_weeks = defaultdict(int)
        peak_weeks = defaultdict(int)

        for date in sorted(year_data.keys()):
            chart = year_data[date]
            top_songs = [s for s in chart if s.get('position', 999) <= top_n]

            genre_count = Counter()
            for song in top_songs:
                artist = song.get('artist', '')
                genre = self.classifier.get_genre(artist)
                if genre != 'Unknown':
                    genre_count[genre] += 1

            # Track weekly percentages
            total = len(top_songs)
            for genre in ['Hip-Hop', 'Pop', 'Country', 'R&B', 'Rock', 'Alternative', 'Latin']:
                count = genre_count.get(genre, 0)
                pct = (count / total * 100) if total > 0 else 0
                genre_weekly[genre].append(pct)

                # Track drought weeks (0% representation)
                if count == 0:
                    drought_weeks[genre] += 1

                # Track peak weeks (25%+ representation)
                if pct >= 25:
                    peak_weeks[genre] += 1

        # Calculate averages
        averages = {}
        for genre, percentages in genre_weekly.items():
            averages[genre] = sum(percentages) / len(percentages) if percentages else 0

        return {
            'averages': averages,
            'drought_weeks': drought_weeks,
            'peak_weeks': peak_weeks,
            'weekly_data': genre_weekly
        }

    def compare_genres(self):
        """Compare genre performance 2024 vs 2025"""
        print("="*70)
        print("GENRE COMPARISON: 2024 vs 2025")
        print("="*70)
        print()

        stats_2024 = self.get_genre_stats(self.data_2024)
        stats_2025 = self.get_genre_stats(self.data_2025)

        # Print comparison table
        print(f"{'Genre':<15} {'2024 Avg':<12} {'2025 Avg':<12} {'Change':<12} {'Status'}")
        print("-"*70)

        changes = []
        for genre in ['Country', 'Pop', 'Latin', 'Hip-Hop', 'R&B', 'Alternative', 'Rock']:
            avg_2024 = stats_2024['averages'].get(genre, 0)
            avg_2025 = stats_2025['averages'].get(genre, 0)
            change = avg_2025 - avg_2024
            change_pct = (change / avg_2024 * 100) if avg_2024 > 0 else 0

            # Status indicator
            if change > 0:
                status = f"📈 +{change_pct:.1f}%"
            elif change < 0:
                status = f"📉 {change_pct:.1f}%"
            else:
                status = "➡️  0%"

            print(f"{genre:<15} {avg_2024:>10.1f}% {avg_2025:>10.1f}% {change:>+10.1f}pp {status}")
            changes.append((genre, change, change_pct))

        print()

        # Biggest winner and loser
        changes.sort(key=lambda x: x[1], reverse=True)
        print("🏆 BIGGEST WINNER:", changes[0][0], f"(+{changes[0][1]:.1f}pp, +{changes[0][2]:.1f}%)")
        print("📉 BIGGEST LOSER:", changes[-1][0], f"({changes[-1][1]:.1f}pp, {changes[-1][2]:.1f}%)")
        print()

        return stats_2024, stats_2025

    def drought_week_analysis(self, stats_2024, stats_2025):
        """Analyze drought weeks (weeks with zero representation)"""
        print("="*70)
        print("DROUGHT WEEK ANALYSIS (Weeks With 0% Representation)")
        print("="*70)
        print()

        print(f"{'Genre':<15} {'2024 Droughts':<15} {'2025 Droughts':<15} {'Change'}")
        print("-"*70)

        for genre in ['Hip-Hop', 'Pop', 'Country', 'Latin', 'R&B', 'Alternative', 'Rock']:
            drought_2024 = stats_2024['drought_weeks'].get(genre, 0)
            drought_2025 = stats_2025['drought_weeks'].get(genre, 0)
            change = drought_2025 - drought_2024

            change_str = f"+{change}" if change > 0 else str(change)
            if change > 0:
                indicator = "⚠️"
            elif change < 0:
                indicator = "✅"
            else:
                indicator = "➡️"

            print(f"{genre:<15} {drought_2024:>13} {drought_2025:>13}    {change_str:>5} {indicator}")

        print()

    def peak_week_analysis(self, stats_2024, stats_2025):
        """Analyze peak weeks (weeks with 25%+ representation)"""
        print("="*70)
        print("PEAK WEEK ANALYSIS (Weeks With 25%+ Representation)")
        print("="*70)
        print()

        print(f"{'Genre':<15} {'2024 Peaks':<15} {'2025 Peaks':<15} {'Change'}")
        print("-"*70)

        for genre in ['Country', 'Pop', 'Latin', 'Hip-Hop', 'R&B', 'Alternative', 'Rock']:
            peak_2024 = stats_2024['peak_weeks'].get(genre, 0)
            peak_2025 = stats_2025['peak_weeks'].get(genre, 0)
            change = peak_2025 - peak_2024

            change_str = f"+{change}" if change > 0 else str(change)
            if change > 0:
                indicator = "🔥"
            elif change < 0:
                indicator = "❄️"
            else:
                indicator = "➡️"

            print(f"{genre:<15} {peak_2024:>13} {peak_2025:>13}    {change_str:>5} {indicator}")

        print()

    def artist_turnover(self):
        """Calculate artist turnover between years"""
        print("="*70)
        print("ARTIST TURNOVER ANALYSIS")
        print("="*70)
        print()

        # Get unique artists per year
        artists_2024 = set()
        artists_2025 = set()

        for chart in self.data_2024.values():
            for song in chart:
                if song.get('position', 999) <= 40:
                    artists_2024.add(song.get('artist', ''))

        for chart in self.data_2025.values():
            for song in chart:
                if song.get('position', 999) <= 40:
                    artists_2025.add(song.get('artist', ''))

        # Calculate overlap
        both_years = artists_2024 & artists_2025
        only_2024 = artists_2024 - artists_2025
        only_2025 = artists_2025 - artists_2024

        print(f"Total artists in 2024: {len(artists_2024)}")
        print(f"Total artists in 2025: {len(artists_2025)}")
        print(f"Artists in both years: {len(both_years)} ({len(both_years)/len(artists_2024)*100:.1f}% retention)")
        print(f"New artists in 2025: {len(only_2025)}")
        print(f"Artists who left: {len(only_2024)}")
        print()

        turnover_rate = len(only_2025) / len(artists_2025) * 100
        print(f"Turnover rate: {turnover_rate:.1f}% (new artists as % of total)")
        print()

    def collaboration_analysis(self):
        """Analyze collaboration trends"""
        print("="*70)
        print("COLLABORATION ANALYSIS")
        print("="*70)
        print()

        # Count collaborations (songs with "Featuring", "&", "X", etc.)
        collab_indicators = ['Featuring', 'featuring', 'Feat.', 'feat.', 'With', 'with', '&', ' X ', ' x ']

        def count_collabs(year_data):
            total = 0
            collabs = 0
            for chart in year_data.values():
                for song in chart:
                    if song.get('position', 999) <= 40:
                        total += 1
                        artist = song.get('artist', '')
                        if any(indicator in artist for indicator in collab_indicators):
                            collabs += 1
            return collabs, total

        collabs_2024, total_2024 = count_collabs(self.data_2024)
        collabs_2025, total_2025 = count_collabs(self.data_2025)

        pct_2024 = collabs_2024 / total_2024 * 100
        pct_2025 = collabs_2025 / total_2025 * 100

        print(f"2024: {collabs_2024}/{total_2024} songs were collaborations ({pct_2024:.1f}%)")
        print(f"2025: {collabs_2025}/{total_2025} songs were collaborations ({pct_2025:.1f}%)")
        print(f"Change: {pct_2025 - pct_2024:+.1f}pp")
        print()

    def generate_shareable_insights(self, stats_2024, stats_2025):
        """Generate tweet-ready insights"""
        print("="*70)
        print("SHAREABLE INSIGHTS (Tweet-Ready)")
        print("="*70)
        print()

        # Find most dramatic changes
        changes = []
        for genre in ['Hip-Hop', 'Pop', 'Country', 'Latin', 'R&B', 'Alternative', 'Rock']:
            avg_2024 = stats_2024['averages'].get(genre, 0)
            avg_2025 = stats_2025['averages'].get(genre, 0)
            change = avg_2025 - avg_2024
            change_pct = (change / avg_2024 * 100) if avg_2024 > 0 else 0
            changes.append((genre, avg_2024, avg_2025, change, change_pct))

        changes.sort(key=lambda x: abs(x[3]), reverse=True)

        print("INSIGHT #1: Biggest Shift")
        print("-"*70)
        top_change = changes[0]
        if top_change[3] > 0:
            print(f"📈 {top_change[0]} surged in 2025:")
            print(f"   2024: {top_change[1]:.1f}% → 2025: {top_change[2]:.1f}%")
            print(f"   That's a {top_change[3]:+.1f}pp gain ({top_change[4]:+.1f}% increase)")
        else:
            print(f"📉 {top_change[0]} collapsed in 2025:")
            print(f"   2024: {top_change[1]:.1f}% → 2025: {top_change[2]:.1f}%")
            print(f"   That's a {top_change[3]:.1f}pp drop ({top_change[4]:.1f}% decline)")
        print()

        print("INSIGHT #2: Drought Weeks")
        print("-"*70)
        for genre in ['Hip-Hop', 'Pop', 'Country']:
            drought_2024 = stats_2024['drought_weeks'].get(genre, 0)
            drought_2025 = stats_2025['drought_weeks'].get(genre, 0)
            if drought_2025 > drought_2024 and drought_2025 > 0:
                print(f"⚠️  {genre} had {drought_2025} drought weeks in 2025 (vs {drought_2024} in 2024)")
                print(f"   {genre} was completely absent from the Top 40 for {drought_2025} weeks")
        print()

        print("INSIGHT #3: Peak Dominance")
        print("-"*70)
        for genre in ['Country', 'Pop', 'Latin']:
            peak_2024 = stats_2024['peak_weeks'].get(genre, 0)
            peak_2025 = stats_2025['peak_weeks'].get(genre, 0)
            if peak_2025 > peak_2024:
                print(f"🔥 {genre} dominated (25%+ of charts) for {peak_2025} weeks in 2025")
                print(f"   Up from {peak_2024} weeks in 2024")
        print()

def main():
    analyzer = YearOverYearAnalyzer()

    # Run all analyses
    stats_2024, stats_2025 = analyzer.compare_genres()
    analyzer.drought_week_analysis(stats_2024, stats_2025)
    analyzer.peak_week_analysis(stats_2024, stats_2025)
    analyzer.artist_turnover()
    analyzer.collaboration_analysis()
    analyzer.generate_shareable_insights(stats_2024, stats_2025)

if __name__ == "__main__":
    main()
