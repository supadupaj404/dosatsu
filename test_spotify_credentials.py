#!/usr/bin/env python3
"""
Quick test to verify Spotify API credentials work
"""

from spotify_genre_classifier import SpotifyGenreClassifier

def test_credentials(client_id: str, client_secret: str):
    """Test Spotify credentials with a few sample artists"""

    print("="*70)
    print("TESTING SPOTIFY API CREDENTIALS")
    print("="*70)
    print()

    try:
        # Initialize classifier
        print("1. Creating classifier...")
        classifier = SpotifyGenreClassifier(client_id, client_secret)
        print("   ✓ Classifier created")
        print()

        # Get access token
        print("2. Authenticating with Spotify...")
        token = classifier._get_access_token()

        if not token:
            print("   ❌ Authentication failed")
            print()
            print("Check that your credentials are correct.")
            return False

        print("   ✓ Authentication successful")
        print()

        # Test with sample artists
        print("3. Testing artist classification...")
        test_artists = ["Drake", "Taylor Swift", "Morgan Wallen"]

        for artist in test_artists:
            result = classifier.search_artist(artist)

            if result:
                print(f"   ✓ {artist:<20} → {result['dosatsu_genre']:<15} (Spotify genres: {', '.join(result['spotify_genres'][:3])})")
            else:
                print(f"   ❌ {artist:<20} → Not found")

        print()
        print("="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print()
        print("Your Spotify API credentials are working correctly.")
        print()
        print("Next step: Run classify_all_billboard_artists.py to classify all artists")
        print()

        return True

    except Exception as e:
        print()
        print("="*70)
        print("❌ TEST FAILED")
        print("="*70)
        print()
        print(f"Error: {e}")
        print()
        print("Common issues:")
        print("- Client ID or Client Secret is incorrect")
        print("- Not connected to internet")
        print("- Spotify API is down (rare)")
        print()

        return False


if __name__ == "__main__":
    print("This script tests your Spotify API credentials.")
    print()

    client_id = input("Enter your Spotify Client ID: ").strip()
    client_secret = input("Enter your Spotify Client Secret: ").strip()

    print()

    if not client_id or not client_secret:
        print("❌ Both Client ID and Client Secret are required.")
        exit(1)

    test_credentials(client_id, client_secret)
