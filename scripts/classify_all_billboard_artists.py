#!/usr/bin/env python3
"""
Classify All Billboard Artists Using Spotify API
One-time script to build comprehensive genre database
"""

import json
from collections import Counter
from src.spotify_genre_classifier import SpotifyGenreClassifier

def get_all_unique_artists(start_year="2000", end_year="2025"):
    """Extract all unique artists from Billboard data"""

    # Load Billboard data
    with open('billboard_25years.json', 'r') as f:
        data = json.load(f)

    # Track all unique artists
    all_artists = set()

    for date, chart in data.items():
        if start_year <= date[:4] <= end_year:
            for song in chart:
                artist = song.get('artist')
                if artist:
                    all_artists.add(artist)

    return sorted(list(all_artists))


def classify_all_artists(client_id: str, client_secret: str):
    """Classify all unique Billboard artists"""

    print("="*70)
    print("DŌSATSU: CLASSIFY ALL BILLBOARD ARTISTS")
    print("="*70)
    print()

    # Get all unique artists
    print("Step 1: Extracting unique artists from Billboard data...")
    artists = get_all_unique_artists()
    print(f"✓ Found {len(artists)} unique artists (2000-2025)")
    print()

    # Initialize classifier
    print("Step 2: Initializing Spotify classifier...")
    classifier = SpotifyGenreClassifier(client_id, client_secret)
    print("✓ Connected to Spotify API")
    print()

    # Classify all artists
    print("Step 3: Classifying artists...")
    print("(This will take ~10-30 minutes for all artists)")
    print()

    results = classifier.classify_artists(artists, save_interval=50)

    print()
    print("="*70)
    print("✅ CLASSIFICATION COMPLETE!")
    print("="*70)
    print()

    # Analyze genre distribution
    print("GENRE DISTRIBUTION:")
    print("-"*70)

    genre_counts = Counter()
    for artist, data in classifier.cache.items():
        genre = data.get('dosatsu_genre', 'Unknown')
        genre_counts[genre] += 1

    for genre, count in genre_counts.most_common():
        percentage = (count / len(classifier.cache) * 100)
        print(f"{genre:<20} {count:>6} artists ({percentage:>5.1f}%)")

    print()
    print("="*70)
    print("COVERAGE ANALYSIS:")
    print("="*70)

    coverage = ((results['total'] - results['not_found']) / results['total'] * 100)
    print(f"Total unique artists: {results['total']:,}")
    print(f"Successfully classified: {results['total'] - results['not_found']:,}")
    print(f"Not found on Spotify: {results['not_found']:,}")
    print(f"Coverage: {coverage:.1f}%")
    print()

    print("✓ Genre cache saved to: spotify_genre_cache.json")
    print()
    print("You can now use this cache with all Dōsatsu analysis scripts!")
    print()

    return classifier


if __name__ == "__main__":
    print("="*70)
    print("SPOTIFY API CREDENTIALS REQUIRED")
    print("="*70)
    print()
    print("Please provide your Spotify API credentials.")
    print()
    print("If you don't have them yet:")
    print("1. Go to https://developer.spotify.com/dashboard")
    print("2. Create an app")
    print("3. Copy your Client ID and Client Secret")
    print()

    # Get credentials from user
    client_id = input("Enter your Spotify Client ID: ").strip()
    client_secret = input("Enter your Spotify Client Secret: ").strip()

    if not client_id or not client_secret:
        print()
        print("❌ Credentials required. Exiting.")
        exit(1)

    print()
    print("Testing credentials...")

    # Test authentication
    try:
        test_classifier = SpotifyGenreClassifier(client_id, client_secret)
        token = test_classifier._get_access_token()

        if token:
            print("✓ Credentials valid!")
            print()

            # Ask to proceed
            proceed = input("Classify all Billboard artists? (yes/no): ").strip().lower()

            if proceed == 'yes':
                print()
                classify_all_artists(client_id, client_secret)
            else:
                print("Cancelled.")
        else:
            print("❌ Could not authenticate. Check your credentials.")

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure:")
        print("- Client ID and Client Secret are correct")
        print("- You're connected to the internet")
        print("- Your Spotify app is set up correctly")
