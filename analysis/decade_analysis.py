#!/usr/bin/env python3
"""
Decade-by-Decade Genre Analysis (1960s - 2020s)
Reveals how genres have risen, dominated, and declined over 67 years
"""

import json
from collections import Counter, defaultdict
from src.spotify_genre_classifier import SpotifyGenreClassifier

class DecadeAnalyzer:
    """Analyze genre trends by decade"""

    def __init__(self, data_file='billboard_67years.json'):
        # Load data
        with open(data_file, 'r') as f:
            self.data = json.load(f)

        # Load genre classifier
        self.classifier = SpotifyGenreClassifier('dummy', 'dummy')

        # Organize by decade
        self.decades = {
            '1960s': {},
            '1970s': {},
            '1980s': {},
            '1990s': {},
            '2000s': {},
            '2010s': {},
            '2020s': {}
        }

        for date, chart in self.data.items():
            year = int(date.split('-')[0])
            if 1960 <= year < 1970:
                self.decades['1960s'][date] = chart
            elif 1970 <= year < 1980:
                self.decades['1970s'][date] = chart
            elif 1980 <= year < 1990:
                self.decades['1980s'][date] = chart
            elif 1990 <= year < 2000:
                self.decades['1990s'][date] = chart
            elif 2000 <= year < 2010:
                self.decades['2000s'][date] = chart
            elif 2010 <= year < 2020:
                self.decades['2010s'][date] = chart
            elif 2020 <= year < 2030:
                self.decades['2020s'][date] = chart

        print("Decade Coverage:")
        for decade, data in self.decades.items():
            print(f"  {decade}: {len(data)} weeks")
        print()

    def get_decade_genre_stats(self, decade_data):
        """Calculate average genre percentages for a decade"""
        genre_weekly = defaultdict(list)

        for date in sorted(decade_data.keys()):
            chart = decade_data[date]
            top_40 = [s for s in chart if s.get('position', 999) <= 40]

            genre_count = Counter()
            for song in top_40:
                artist = song.get('artist', '')
                genre = self.classifier.get_genre(artist)
                if genre != 'Unknown':
                    genre_count[genre] += 1

            # Calculate percentages
            total = len(top_40)
            for genre in ['Hip-Hop', 'Pop', 'Country', 'R&B', 'Rock', 'Alternative', 'Latin']:
                count = genre_count.get(genre, 0)
                pct = (count / total * 100) if total > 0 else 0
                genre_weekly[genre].append(pct)

        # Calculate averages
        averages = {}
        for genre, percentages in genre_weekly.items():
            averages[genre] = sum(percentages) / len(percentages) if percentages else 0

        return averages

    def print_decade_comparison(self):
        """Print decade-by-decade genre comparison"""
        print("="*70)
        print("GENRE EVOLUTION: 1960s - 2020s")
        print("="*70)
        print()

        # Calculate stats for each decade
        decade_stats = {}
        for decade, data in self.decades.items():
            if len(data) > 0:
                decade_stats[decade] = self.get_decade_genre_stats(data)

        # Print header
        decades_list = ['1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s']
        available_decades = [d for d in decades_list if d in decade_stats]

        header = f"{'Genre':<15}"
        for decade in available_decades:
            header += f" {decade:>8}"
        print(header)
        print("-"*70)

        # Print each genre
        for genre in ['Rock', 'Pop', 'R&B', 'Country', 'Hip-Hop', 'Alternative', 'Latin']:
            row = f"{genre:<15}"
            for decade in available_decades:
                pct = decade_stats[decade].get(genre, 0)
                row += f" {pct:>7.1f}%"
            print(row)

        print()

    def find_biggest_shifts(self):
        """Find the biggest decade-to-decade changes"""
        print("="*70)
        print("BIGGEST DECADE-TO-DECADE SHIFTS")
        print("="*70)
        print()

        decade_stats = {}
        for decade, data in self.decades.items():
            if len(data) > 0:
                decade_stats[decade] = self.get_decade_genre_stats(data)

        decades_list = ['1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s']
        available_decades = [d for d in decades_list if d in decade_stats]

        biggest_shifts = []

        for i in range(len(available_decades) - 1):
            current_decade = available_decades[i]
            next_decade = available_decades[i + 1]

            for genre in ['Rock', 'Pop', 'R&B', 'Country', 'Hip-Hop', 'Alternative', 'Latin']:
                current_pct = decade_stats[current_decade].get(genre, 0)
                next_pct = decade_stats[next_decade].get(genre, 0)
                change = next_pct - current_pct

                if abs(change) > 5:  # Only show shifts > 5pp
                    biggest_shifts.append({
                        'genre': genre,
                        'from_decade': current_decade,
                        'to_decade': next_decade,
                        'from_pct': current_pct,
                        'to_pct': next_pct,
                        'change': change
                    })

        # Sort by absolute change
        biggest_shifts.sort(key=lambda x: abs(x['change']), reverse=True)

        # Print top 15
        for i, shift in enumerate(biggest_shifts[:15], 1):
            direction = "📈" if shift['change'] > 0 else "📉"
            print(f"{i:2d}. {direction} {shift['genre']} ({shift['from_decade']} → {shift['to_decade']})")
            print(f"     {shift['from_pct']:.1f}% → {shift['to_pct']:.1f}% ({shift['change']:+.1f}pp)")
            print()

    def genre_dominance_eras(self):
        """Identify which genres dominated which decades"""
        print("="*70)
        print("GENRE DOMINANCE BY DECADE")
        print("="*70)
        print()

        decade_stats = {}
        for decade, data in self.decades.items():
            if len(data) > 0:
                decade_stats[decade] = self.get_decade_genre_stats(data)

        decades_list = ['1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s']
        available_decades = [d for d in decades_list if d in decade_stats]

        for decade in available_decades:
            stats = decade_stats[decade]
            # Sort genres by percentage
            sorted_genres = sorted(stats.items(), key=lambda x: x[1], reverse=True)

            print(f"{decade}:")
            print(f"  1st: {sorted_genres[0][0]} ({sorted_genres[0][1]:.1f}%)")
            print(f"  2nd: {sorted_genres[1][0]} ({sorted_genres[1][1]:.1f}%)")
            print(f"  3rd: {sorted_genres[2][0]} ({sorted_genres[2][1]:.1f}%)")
            print()

def main():
    analyzer = DecadeAnalyzer()

    analyzer.print_decade_comparison()
    analyzer.find_biggest_shifts()
    analyzer.genre_dominance_eras()

if __name__ == "__main__":
    main()
