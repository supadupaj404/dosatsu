#!/usr/bin/env python3
"""
Test MusicBrainz Integration
Tests both standalone MusicBrainz and hybrid classifier
"""

import json
import os
import sys
from musicbrainz_classifier import MusicBrainzClassifier
from hybrid_classifier import HybridClassifier

def test_musicbrainz_only():
    """Test MusicBrainz classifier on classic artists"""
    print("="*70)
    print("TESTING MUSICBRAINZ CLASSIFIER")
    print("="*70)
    print()

    # Classic artists from 1960s-1980s (likely not on Spotify)
    test_artists = [
        "The Supremes",
        "The Beatles",
        "Elvis Presley",
        "Aretha Franklin",
        "James Brown",
        "The Rolling Stones",
        "Led Zeppelin",
        "Queen",
        "Michael Jackson",
        "Prince"
    ]

    mb = MusicBrainzClassifier()

    print(f"Testing {len(test_artists)} classic artists...")
    print()

    for artist in test_artists:
        print(f"Artist: {artist}")
        result = mb.classify_artist(artist)

        if result:
            print(f"  ✓ Found!")
            print(f"    Genre: {result.get('dosatsu_genre', 'Unknown')}")
            print(f"    Tags: {', '.join(result.get('tags', [])[:5])}")
            print(f"    MBID: {result.get('mbid', 'N/A')}")
        else:
            print(f"  ✗ Not found")

        print()

def test_hybrid_classifier():
    """Test hybrid classifier (Spotify + MusicBrainz)"""
    print("="*70)
    print("TESTING HYBRID CLASSIFIER")
    print("="*70)
    print()

    # Mix of modern (Spotify) and classic (MusicBrainz) artists
    test_artists = [
        "Drake",  # Modern - should use Spotify
        "Taylor Swift",  # Modern - should use Spotify
        "The Temptations",  # Classic - might fall back to MusicBrainz
        "Chuck Berry",  # Classic - likely MusicBrainz only
        "Bad Bunny",  # Modern - should use Spotify
        "The Four Tops",  # Classic - might fall back to MusicBrainz
    ]

    # Load Spotify credentials from environment variables
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("❌ ERROR: Spotify credentials not found!")
        print("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables")
        print("Get credentials at: https://developer.spotify.com/dashboard")
        sys.exit(1)

    hybrid = HybridClassifier(client_id, client_secret)

    print(f"Testing {len(test_artists)} artists (mix of modern & classic)...")
    print()

    for artist in test_artists:
        print(f"Artist: {artist}")
        result = hybrid.classify_artist(artist)

        if result:
            print(f"  ✓ Found!")
            print(f"    Genre: {result.get('dosatsu_genre', 'Unknown')}")
            print(f"    Source: {result.get('source', 'N/A')}")
            print(f"    Confidence: {result.get('confidence', 'N/A')}")

            if result.get('source') == 'spotify':
                print(f"    Spotify genres: {', '.join(result.get('spotify_genres', [])[:3])}")
            elif result.get('source') == 'musicbrainz':
                print(f"    MB tags: {', '.join(result.get('mb_tags', [])[:3])}")
        else:
            print(f"  ✗ Not found in either source")

        print()

    # Show coverage stats
    print("="*70)
    print("HYBRID CLASSIFIER STATS")
    print("="*70)
    stats = hybrid.get_coverage_stats()
    print(f"Total cached: {stats['total']}")
    print(f"Classified: {stats['classified']}")
    print(f"  - via Spotify: {stats['spotify']}")
    print(f"  - via MusicBrainz: {stats['musicbrainz']}")
    print(f"Not found: {stats['not_found']}")
    print()

def find_unclassified_artists():
    """Find artists from 67-year dataset that aren't in Spotify cache"""
    print("="*70)
    print("FINDING UNCLASSIFIED ARTISTS")
    print("="*70)
    print()

    # Load 67-year dataset
    with open('billboard_67years.json', 'r') as f:
        data = json.load(f)

    # Get all artists
    all_artists = set()
    for date, chart in data.items():
        for song in chart:
            artist = song.get('artist')
            if artist:
                all_artists.add(artist)

    # Load Spotify cache
    try:
        with open('spotify_genre_cache.json', 'r') as f:
            spotify_cache = json.load(f)
    except FileNotFoundError:
        spotify_cache = {}

    # Find unclassified
    unclassified = [a for a in all_artists if a not in spotify_cache]

    print(f"Total artists: {len(all_artists):,}")
    print(f"In Spotify cache: {len(spotify_cache):,}")
    print(f"Unclassified: {len(unclassified):,}")
    print()

    if unclassified:
        print("Sample of unclassified artists (first 20):")
        for i, artist in enumerate(sorted(unclassified)[:20], 1):
            print(f"  {i:2d}. {artist}")
        print()

    return sorted(unclassified)

def main():
    print("\nDŌSATSU - MUSICBRAINZ INTEGRATION TEST\n")

    # Test 1: MusicBrainz only
    test_musicbrainz_only()

    # Test 2: Hybrid classifier
    test_hybrid_classifier()

    # Test 3: Find unclassified artists
    unclassified = find_unclassified_artists()

    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Verify genres look accurate")
    print("2. Run hybrid classifier on unclassified artists")
    print(f"3. Classify remaining {len(unclassified):,} artists to reach ~95%+ coverage")
    print()

if __name__ == "__main__":
    main()
