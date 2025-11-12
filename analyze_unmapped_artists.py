#!/usr/bin/env python3
"""
Find unmapped artists from 2000-2015 to build comprehensive genre mapping
"""

import json
from collections import Counter
from multi_genre_analyzer import MULTI_GENRE_MAPPING

def find_unmapped_artists(start_year="2000", end_year="2015"):
    """Find most common unmapped artists in a time period"""

    # Load data
    with open('billboard_25years.json') as f:
        data = json.load(f)

    # Track artist appearances
    artist_counts = Counter()
    unmapped_artists = Counter()
    total_songs = 0
    mapped_songs = 0

    for date, chart in data.items():
        # Filter by date range
        if start_year <= date[:4] <= end_year:
            # Look at top 40 only
            top_40 = [s for s in chart if s.get('position', 999) <= 40]

            for song in top_40:
                artist = song.get('artist')
                if artist:
                    total_songs += 1
                    artist_counts[artist] += 1

                    if artist not in MULTI_GENRE_MAPPING:
                        unmapped_artists[artist] += 1
                    else:
                        mapped_songs += 1

    # Calculate coverage
    coverage = (mapped_songs / total_songs * 100) if total_songs > 0 else 0

    print("="*70)
    print(f"UNMAPPED ARTISTS ANALYSIS ({start_year}-{end_year})")
    print("="*70)
    print()
    print(f"Total songs in top 40: {total_songs:,}")
    print(f"Mapped songs: {mapped_songs:,} ({coverage:.1f}%)")
    print(f"Unmapped songs: {total_songs - mapped_songs:,} ({100-coverage:.1f}%)")
    print()

    print("="*70)
    print(f"TOP 100 UNMAPPED ARTISTS ({start_year}-{end_year})")
    print("="*70)
    print()
    print(f"{'Rank':<5} {'Artist':<45} {'Appearances':<12}")
    print("-"*70)

    # Show top 100 unmapped artists
    for i, (artist, count) in enumerate(unmapped_artists.most_common(100), 1):
        print(f"{i:<5} {artist:<45} {count:<12}")

    print()

    # Save to file for manual classification
    output = {
        'period': f"{start_year}-{end_year}",
        'total_songs': total_songs,
        'mapped_songs': mapped_songs,
        'coverage_percent': coverage,
        'unmapped_artists': [
            {'rank': i, 'artist': artist, 'appearances': count}
            for i, (artist, count) in enumerate(unmapped_artists.most_common(100), 1)
        ]
    }

    with open(f'unmapped_artists_{start_year}_{end_year}.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✓ Saved to: unmapped_artists_{start_year}_{end_year}.json")
    print()

    return unmapped_artists

if __name__ == "__main__":
    # Analyze 2000-2015 period
    find_unmapped_artists("2000", "2015")
