#!/usr/bin/env python3
"""
10-Year Fall-Off Analysis with Comprehensive Mapping
"""

import json
from collections import defaultdict
from scripts.comprehensive_genre_mapping import COMPREHENSIVE_GENRE_MAPPING

class ComprehensiveGenreAnalyzer:
    """Analyzer using comprehensive mapping"""

    def __init__(self, billboard_data, genre_mapping):
        self.data = billboard_data
        self.dates = sorted(billboard_data.keys())
        self.genre_mapping = genre_mapping

    def analyze_all_genres(self, top_n=40):
        """Analyze representation for all genres"""
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
                    # Handle multi-genre (use primary)
                    if "/" in genre:
                        genre = genre.split("/")[0]

                    genre_weekly[genre][date]['count'] += 1
                    genre_weekly[genre][date]['songs'].append({
                        'position': song.get('position'),
                        'song': song.get('song'),
                        'artist': artist
                    })

        return genre_weekly


def find_biggest_10year_falloff():
    """Find which genre had the biggest 10-year decline"""

    # Load data
    with open('billboard_25years.json') as f:
        data = json.load(f)

    print("="*70)
    print("DŌSATSU: 10-YEAR GENRE FALL-OFF (COMPREHENSIVE ANALYSIS)")
    print("="*70)
    print()
    print(f"Using comprehensive mapping: {len(COMPREHENSIVE_GENRE_MAPPING)} artists")
    print()

    # Analyze all genres
    analyzer = ComprehensiveGenreAnalyzer(data, COMPREHENSIVE_GENRE_MAPPING)
    genre_weekly = analyzer.analyze_all_genres(top_n=40)

    # Calculate yearly averages for each genre
    genre_yearly_avg = defaultdict(lambda: defaultdict(list))

    for genre, weekly_data in genre_weekly.items():
        for date, data in weekly_data.items():
            year = date[:4]
            percentage = (data['count'] / 40 * 100) if data['count'] > 0 else 0
            genre_yearly_avg[genre][year].append(percentage)

    # Calculate average percentage per year
    genre_year_avg_pct = {}
    for genre, yearly_data in genre_yearly_avg.items():
        genre_year_avg_pct[genre] = {
            year: sum(percentages) / len(percentages) if percentages else 0
            for year, percentages in yearly_data.items()
        }

    # Find all possible 10-year periods
    all_years = sorted(set(year for genre_data in genre_year_avg_pct.values() for year in genre_data.keys()))

    # Calculate 10-year changes for each genre
    falloffs = []

    for genre, yearly_avgs in genre_year_avg_pct.items():
        for start_year in all_years:
            end_year = str(int(start_year) + 10)

            if start_year in yearly_avgs and end_year in yearly_avgs:
                start_pct = yearly_avgs[start_year]
                end_pct = yearly_avgs[end_year]
                change = end_pct - start_pct
                change_pct = (change / start_pct * 100) if start_pct > 0 else 0

                falloffs.append({
                    'genre': genre,
                    'start_year': start_year,
                    'end_year': end_year,
                    'start_pct': start_pct,
                    'end_pct': end_pct,
                    'absolute_change': change,
                    'percent_change': change_pct
                })

    # Sort by absolute decline (most negative)
    falloffs.sort(key=lambda x: x['absolute_change'])

    print("TOP 10 BIGGEST GENRE FALL-OFFS (10-Year Periods):")
    print("-"*70)
    print(f"{'Rank':<5} {'Genre':<15} {'Period':<15} {'Change':<25} {'%Δ':<10}")
    print("-"*70)

    for i, falloff in enumerate(falloffs[:10], 1):
        period = f"{falloff['start_year']}-{falloff['end_year']}"
        change_str = f"{falloff['start_pct']:.1f}% → {falloff['end_pct']:.1f}%"
        pct_change = f"{falloff['percent_change']:.0f}%"

        print(f"{i:<5} {falloff['genre']:<15} {period:<15} {change_str:<25} {pct_change:<10}")

    print()
    print("="*70)

    # The biggest fall-off
    biggest = falloffs[0]

    print("🏆 BIGGEST 10-YEAR FALL-OFF:")
    print("="*70)
    print(f"Genre: {biggest['genre']}")
    print(f"Period: {biggest['start_year']} to {biggest['end_year']}")
    print(f"Starting: {biggest['start_pct']:.1f}% of top 40")
    print(f"Ending: {biggest['end_pct']:.1f}% of top 40")
    print(f"Decline: {abs(biggest['absolute_change']):.1f} percentage points")
    print(f"Percent change: {abs(biggest['percent_change']):.0f}%")
    print()

    # Also show biggest rises
    print("="*70)
    print("FOR CONTEXT: BIGGEST 10-YEAR RISES")
    print("="*70)
    print()

    rises = sorted(falloffs, key=lambda x: x['absolute_change'], reverse=True)[:10]

    for i, rise in enumerate(rises, 1):
        print(f"{i}. {rise['genre']}: {rise['start_year']}-{rise['end_year']} "
              f"({rise['start_pct']:.1f}% → {rise['end_pct']:.1f}%, +{rise['absolute_change']:.1f}pp)")

    print()

    # Detailed year-by-year for biggest fall-off
    print("="*70)
    print(f"YEAR-BY-YEAR BREAKDOWN: {biggest['genre']}")
    print(f"({biggest['start_year']}-{biggest['end_year']})")
    print("="*70)
    print()

    start = int(biggest['start_year'])
    end = int(biggest['end_year'])

    for year in range(start, end + 1):
        year_str = str(year)
        if year_str in genre_year_avg_pct[biggest['genre']]:
            pct = genre_year_avg_pct[biggest['genre']][year_str]
            print(f"{year}: {pct:>6.1f}%")

    print()

    # Generate insight
    print("="*70)
    print("SOCIAL MEDIA INSIGHT:")
    print("="*70)
    print()

    tweet = f"""🚨 Biggest 10-year genre fall-off in Billboard history:

{biggest['genre']}: {biggest['start_year']}-{biggest['end_year']}
{biggest['start_pct']:.1f}% → {biggest['end_pct']:.1f}% ({abs(biggest['absolute_change']):.1f}pp drop)

{abs(biggest['percent_change']):.0f}% decline over a decade.

Genre cycles are brutal.

#Dōsatsu #MusicIndustry #{biggest['genre'].replace(' ', '')}"""

    print(tweet)
    print()

    return biggest, falloffs

if __name__ == "__main__":
    biggest, all_falloffs = find_biggest_10year_falloff()
