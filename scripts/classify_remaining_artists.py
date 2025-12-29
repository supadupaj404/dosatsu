#!/usr/bin/env python3
"""
Classify remaining unclassified artists using hybrid approach
Spotify first, MusicBrainz fallback
"""

import json
from hybrid_classifier import HybridClassifier
from collections import Counter

def main():
    print("="*70)
    print("CLASSIFYING REMAINING ARTISTS (HYBRID APPROACH)")
    print("="*70)
    print()

    # Load 67-year dataset
    print("Step 1: Loading Billboard data...")
    with open('billboard_67years.json', 'r') as f:
        data = json.load(f)

    # Get all unique artists
    all_artists = set()
    for date, chart in data.items():
        for song in chart:
            artist = song.get('artist')
            if artist:
                all_artists.add(artist)

    print(f"✓ Found {len(all_artists):,} total unique artists")
    print()

    # Load Spotify cache
    print("Step 2: Loading existing Spotify cache...")
    try:
        with open('spotify_genre_cache.json', 'r') as f:
            spotify_cache = json.load(f)
        print(f"✓ Loaded {len(spotify_cache):,} artists from Spotify cache")
    except FileNotFoundError:
        spotify_cache = {}
        print("✗ No Spotify cache found")

    print()

    # Find unclassified artists
    unclassified = sorted([a for a in all_artists if a not in spotify_cache])
    print(f"Unclassified artists: {len(unclassified):,}")
    print()

    if len(unclassified) == 0:
        print("All artists already classified!")
        return

    # Initialize hybrid classifier
    print("Step 3: Initializing hybrid classifier...")
    client_id = '62eb62fd0fac433196d32f4aa51f0b6f'
    client_secret = 'c9b37aa1dfb440efbaf0005bc9cfadb3'

    hybrid = HybridClassifier(client_id, client_secret)
    print("✓ Hybrid classifier ready")
    print()

    # Classify unclassified artists
    print(f"Step 4: Classifying {len(unclassified):,} artists...")
    print("Strategy: Try Spotify first, fall back to MusicBrainz")
    print(f"Estimated time: ~{len(unclassified) // 60} minutes")
    print()

    results = hybrid.classify_artists(unclassified, save_interval=50)

    # Print results
    print()
    print("="*70)
    print("CLASSIFICATION COMPLETE")
    print("="*70)
    print()

    print(f"Total processed: {results['total']:,}")
    print(f"Successfully classified: {results['found']:,}")
    print(f"  - via Spotify: {results['spotify']:,}")
    print(f"  - via MusicBrainz: {results['musicbrainz']:,}")
    print(f"Not found: {results['not_found']:,}")
    print()

    success_rate = (results['found'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    print()

    # Calculate new overall coverage
    total_classified = len(spotify_cache) + results['found']
    total_artists = len(all_artists)
    new_coverage = (total_classified / total_artists * 100)

    print("="*70)
    print("OVERALL COVERAGE IMPROVEMENT")
    print("="*70)
    print(f"Before: {len(spotify_cache):,} / {total_artists:,} ({len(spotify_cache)/total_artists*100:.1f}%)")
    print(f"After:  {total_classified:,} / {total_artists:,} ({new_coverage:.1f}%)")
    print(f"Improvement: +{results['found']:,} artists (+{new_coverage - len(spotify_cache)/total_artists*100:.1f}pp)")
    print()

    # Show genre distribution from MusicBrainz finds
    if results['musicbrainz'] > 0:
        print("="*70)
        print("MUSICBRAINZ CONTRIBUTIONS BY GENRE")
        print("="*70)

        mb_genres = Counter()
        for artist_data in results['artists']:
            if artist_data.get('source') == 'musicbrainz':
                genre = artist_data.get('dosatsu_genre', 'Unknown')
                mb_genres[genre] += 1

        for genre, count in mb_genres.most_common():
            print(f"{genre:<20} {count:>4} artists")
        print()

    print(f"✓ Results saved to: hybrid_genre_cache.json")
    print()

if __name__ == "__main__":
    main()
