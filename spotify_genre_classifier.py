#!/usr/bin/env python3
"""
Spotify Genre Classifier for Dōsatsu
Automatically classify artists using Spotify Web API
"""

import requests
import json
import base64
import time
from typing import Optional, Dict, List

class SpotifyGenreClassifier:
    """Classify artist genres using Spotify API"""

    def __init__(self, client_id: str, client_secret: str, cache_file: str = "spotify_genre_cache.json"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.cache_file = cache_file
        self.access_token = None
        self.token_expires = 0
        self.cache = self._load_cache()

        # Map Spotify's 5000+ genres to our 7 main categories
        self.genre_mapping = {
            # Hip-Hop/Rap
            "hip hop": "Hip-Hop",
            "rap": "Hip-Hop",
            "trap": "Hip-Hop",
            "southern hip hop": "Hip-Hop",
            "gangster rap": "Hip-Hop",
            "conscious hip hop": "Hip-Hop",
            "east coast hip hop": "Hip-Hop",
            "west coast rap": "Hip-Hop",
            "drill": "Hip-Hop",
            "uk hip hop": "Hip-Hop",
            "canadian hip hop": "Hip-Hop",
            "melodic rap": "Hip-Hop",
            "plugg": "Hip-Hop",
            "atlanta hip hop": "Hip-Hop",
            "chicago rap": "Hip-Hop",
            "detroit hip hop": "Hip-Hop",
            "memphis hip hop": "Hip-Hop",

            # Pop
            "pop": "Pop",
            "dance pop": "Pop",
            "electropop": "Pop",
            "synth pop": "Pop",
            "pop rap": "Pop",
            "viral pop": "Pop",
            "art pop": "Pop",
            "indie pop": "Pop",
            "bedroom pop": "Pop",
            "uk pop": "Pop",
            "boy band": "Pop",
            "candy pop": "Pop",
            "europop": "Pop",
            "k-pop": "Pop",

            # Country
            "country": "Country",
            "contemporary country": "Country",
            "country road": "Country",
            "country pop": "Country",
            "country rap": "Country",
            "modern country rock": "Country",
            "country rock": "Country",
            "alternative country": "Country",
            "outlaw country": "Country",
            "bro-country": "Country",
            "nashville sound": "Country",

            # R&B
            "r&b": "R&B",
            "r n b": "R&B",
            "urban contemporary": "R&B",
            "contemporary r&b": "R&B",
            "neo soul": "R&B",
            "alternative r&b": "R&B",
            "new jack swing": "R&B",
            "quiet storm": "R&B",
            "soul": "R&B",

            # Rock
            "rock": "Rock",
            "hard rock": "Rock",
            "classic rock": "Rock",
            "soft rock": "Rock",
            "garage rock": "Rock",
            "punk": "Rock",
            "post-punk": "Rock",
            "grunge": "Rock",
            "emo": "Rock",
            "screamo": "Rock",
            "metalcore": "Rock",
            "metal": "Rock",

            # Alternative
            "alternative": "Alternative",
            "indie": "Alternative",
            "indie rock": "Alternative",
            "alternative rock": "Alternative",
            "modern rock": "Alternative",
            "stomp and holler": "Alternative",
            "folk": "Alternative",
            "indie folk": "Alternative",
            "singer-songwriter": "Alternative",

            # Latin
            "reggaeton": "Latin",
            "latin": "Latin",
            "latin pop": "Latin",
            "urbano latino": "Latin",
            "latin hip hop": "Latin",
            "latin trap": "Latin",
            "bachata": "Latin",
            "salsa": "Latin",
            "regional mexican": "Latin",
            "banda": "Latin",
            "corrido": "Latin",
            "mariachi": "Latin",
        }

    def _load_cache(self) -> Dict:
        """Load previously classified artists from cache"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
        print(f"✓ Saved {len(self.cache)} artists to cache: {self.cache_file}")

    def _get_access_token(self):
        """Get Spotify API access token"""
        # Check if current token is still valid
        if self.access_token and time.time() < self.token_expires:
            return self.access_token

        # Get new token
        auth_url = "https://accounts.spotify.com/api/token"

        # Encode credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {credentials_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials"
        }

        try:
            response = requests.post(auth_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data['access_token']
            # Set expiration (usually 3600 seconds, we'll refresh 5 min early)
            self.token_expires = time.time() + token_data.get('expires_in', 3600) - 300

            return self.access_token

        except requests.RequestException as e:
            print(f"Error getting Spotify access token: {e}")
            return None

    def search_artist(self, artist_name: str) -> Optional[Dict]:
        """Search for artist on Spotify"""
        # Check cache first
        if artist_name in self.cache:
            return self.cache[artist_name]

        # Get access token
        token = self._get_access_token()
        if not token:
            return None

        # Search Spotify
        search_url = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        params = {
            "q": artist_name,
            "type": "artist",
            "limit": 1
        }

        try:
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            if data['artists']['items']:
                artist = data['artists']['items'][0]

                result = {
                    'name': artist['name'],
                    'spotify_genres': artist.get('genres', []),
                    'popularity': artist.get('popularity', 0),
                    'followers': artist.get('followers', {}).get('total', 0),
                    'spotify_id': artist['id']
                }

                # Map to our genre categories
                result['dosatsu_genre'] = self._map_to_dosatsu_genre(result['spotify_genres'])

                # Cache the result
                self.cache[artist_name] = result

                return result

            return None

        except requests.RequestException as e:
            print(f"Error searching for {artist_name}: {e}")
            return None

    def _map_to_dosatsu_genre(self, spotify_genres: List[str]) -> str:
        """Map Spotify's genres to our main categories"""
        if not spotify_genres:
            return "Unknown"

        # Count matches for each category
        category_scores = {}

        for genre in spotify_genres:
            genre_lower = genre.lower()

            # Check each mapping
            for spotify_term, dosatsu_category in self.genre_mapping.items():
                if spotify_term in genre_lower:
                    category_scores[dosatsu_category] = category_scores.get(dosatsu_category, 0) + 1

        # Return category with most matches
        if category_scores:
            return max(category_scores, key=category_scores.get)

        # Fallback: try to guess from first genre
        first_genre = spotify_genres[0].lower()
        if "pop" in first_genre:
            return "Pop"
        elif "hip" in first_genre or "rap" in first_genre:
            return "Hip-Hop"
        elif "country" in first_genre:
            return "Country"
        elif "r&b" in first_genre or "soul" in first_genre:
            return "R&B"
        elif "rock" in first_genre or "alternative" in first_genre:
            return "Rock"
        elif "latin" in first_genre or "reggaeton" in first_genre:
            return "Latin"

        return "Unknown"

    def classify_artists(self, artist_list: List[str], save_interval: int = 50):
        """Classify multiple artists with rate limiting"""
        print(f"Classifying {len(artist_list)} artists...")
        print()

        classified = 0
        from_cache = 0
        not_found = 0

        for i, artist_name in enumerate(artist_list, 1):
            # Check cache first
            if artist_name in self.cache:
                from_cache += 1
                if i % 100 == 0:
                    print(f"Progress: {i}/{len(artist_list)} ({from_cache} from cache)")
                continue

            # Query Spotify
            result = self.search_artist(artist_name)

            if result:
                classified += 1
                print(f"{i:4d}. {artist_name:<40} → {result['dosatsu_genre']:<15} (Spotify: {', '.join(result['spotify_genres'][:2])})")
            else:
                not_found += 1
                print(f"{i:4d}. {artist_name:<40} → NOT FOUND")

            # Save cache periodically
            if i % save_interval == 0:
                self._save_cache()

            # Rate limiting: ~1 request per 0.1 seconds = safe
            time.sleep(0.1)

        # Final save
        self._save_cache()

        print()
        print("="*70)
        print("CLASSIFICATION SUMMARY")
        print("="*70)
        print(f"Total artists: {len(artist_list)}")
        print(f"From cache: {from_cache}")
        print(f"Newly classified: {classified}")
        print(f"Not found: {not_found}")
        print(f"Total in cache: {len(self.cache)}")
        print()

        return {
            'total': len(artist_list),
            'classified': classified,
            'from_cache': from_cache,
            'not_found': not_found
        }

    def get_genre(self, artist_name: str) -> str:
        """Get genre for an artist (main interface)"""
        # Check cache
        if artist_name in self.cache:
            return self.cache[artist_name]['dosatsu_genre']

        # Search Spotify
        result = self.search_artist(artist_name)

        if result:
            return result['dosatsu_genre']

        return "Unknown"


def demo():
    """Demo the classifier (requires API credentials)"""
    print("="*70)
    print("SPOTIFY GENRE CLASSIFIER DEMO")
    print("="*70)
    print()
    print("To use this tool, you need Spotify API credentials.")
    print()
    print("Get them here: https://developer.spotify.com/dashboard")
    print()
    print("Once you have them, use like this:")
    print()
    print("Example:")
    print("  classifier = SpotifyGenreClassifier(")
    print("      client_id='YOUR_CLIENT_ID',")
    print("      client_secret='YOUR_CLIENT_SECRET'")
    print("  )")
    print()
    print("  genre = classifier.get_genre('Drake')")
    print("  # Returns: 'Hip-Hop'")
    print()


if __name__ == "__main__":
    demo()
