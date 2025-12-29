#!/usr/bin/env python3
"""
MusicBrainz Genre Classifier for Dōsatsu
Fallback classifier for artists not found on Spotify
"""

import json
import requests
import time
from typing import Dict, Optional, List

class MusicBrainzClassifier:
    """Classify artists using MusicBrainz API"""

    def __init__(self, cache_file: str = 'musicbrainz_cache.json'):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.base_url = "https://musicbrainz.org/ws/2/"
        self.user_agent = "Dosatsu/1.0 (jeremy@whetstone.com)"
        self.rate_limit = 1.0  # 1 request per second

    def _load_cache(self) -> Dict:
        """Load cached MusicBrainz data"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with rate limiting"""
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json'
        }

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            time.sleep(self.rate_limit)  # Respect rate limit
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"MusicBrainz API error: {e}")
            time.sleep(self.rate_limit)
            return None

    def _map_tags_to_genre(self, tags: List[str]) -> str:
        """Map MusicBrainz tags to Dōsatsu genres"""
        # Convert all tags to lowercase for matching
        tags_lower = [tag.lower() for tag in tags]

        # Genre mapping (order matters - check most specific first)
        genre_mappings = {
            'Hip-Hop': [
                'hip hop', 'hip-hop', 'rap', 'trap', 'gangsta rap',
                'underground hip hop', 'conscious hip hop', 'east coast hip hop',
                'west coast hip hop', 'southern hip hop', 'hardcore hip hop'
            ],
            'R&B': [
                'r&b', 'rnb', 'rhythm and blues', 'soul', 'neo soul',
                'contemporary r&b', 'quiet storm', 'motown', 'funk',
                'disco', 'doo wop', 'northern soul'
            ],
            'Rock': [
                'rock', 'hard rock', 'classic rock', 'rock and roll',
                'blues rock', 'psychedelic rock', 'progressive rock',
                'glam rock', 'soft rock', 'arena rock', 'garage rock',
                'folk rock', 'southern rock'
            ],
            'Alternative': [
                'alternative rock', 'alternative', 'indie', 'indie rock',
                'grunge', 'punk', 'punk rock', 'emo', 'post-punk',
                'new wave', 'shoegaze', 'noise rock', 'art rock',
                'experimental', 'industrial', 'gothic rock'
            ],
            'Country': [
                'country', 'country rock', 'country pop', 'alt-country',
                'bluegrass', 'honky tonk', 'outlaw country',
                'contemporary country', 'nashville sound', 'americana'
            ],
            'Pop': [
                'pop', 'pop rock', 'synth-pop', 'electropop', 'dance-pop',
                'teen pop', 'bubblegum pop', 'power pop', 'sophisti-pop',
                'adult contemporary', 'easy listening', 'soft pop'
            ],
            'Latin': [
                'latin', 'reggaeton', 'salsa', 'bachata', 'merengue',
                'latin pop', 'spanish', 'mexican', 'cumbia', 'banda',
                'regional mexican', 'tejano', 'latin rock', 'bossa nova'
            ]
        }

        # Count matches for each genre
        genre_scores = {}
        for genre, keywords in genre_mappings.items():
            score = 0
            for tag in tags_lower:
                for keyword in keywords:
                    if keyword in tag:
                        # Weight earlier tags more heavily
                        position_weight = 1.0 - (tags_lower.index(tag) * 0.05)
                        score += max(position_weight, 0.5)
            if score > 0:
                genre_scores[genre] = score

        # Return genre with highest score
        if genre_scores:
            return max(genre_scores.items(), key=lambda x: x[1])[0]

        return 'Unknown'

    def search_artist(self, artist_name: str) -> Optional[str]:
        """
        Search for artist and return MBID (MusicBrainz ID)
        Returns the best matching artist ID
        """
        params = {
            'query': f'artist:"{artist_name}"',
            'limit': 1,
            'fmt': 'json'
        }

        data = self._make_request('artist', params)

        if data and 'artists' in data and len(data['artists']) > 0:
            return data['artists'][0]['id']

        return None

    def get_artist_tags(self, mbid: str) -> List[str]:
        """Get tags/genres for an artist by MBID"""
        params = {
            'inc': 'tags+ratings',
            'fmt': 'json'
        }

        data = self._make_request(f'artist/{mbid}', params)

        if data and 'tags' in data:
            # Return tags sorted by vote count (most popular first)
            tags = sorted(data['tags'], key=lambda x: x.get('count', 0), reverse=True)
            return [tag['name'] for tag in tags[:20]]  # Top 20 tags

        return []

    def classify_artist(self, artist_name: str) -> Optional[Dict]:
        """
        Classify a single artist
        Returns dict with genre info or None if not found
        """
        # Check cache first
        if artist_name in self.cache:
            return self.cache[artist_name]

        # Search for artist
        mbid = self.search_artist(artist_name)

        if not mbid:
            self.cache[artist_name] = None
            self._save_cache()
            return None

        # Get tags
        tags = self.get_artist_tags(mbid)

        if not tags:
            self.cache[artist_name] = None
            self._save_cache()
            return None

        # Map to genre
        genre = self._map_tags_to_genre(tags)

        result = {
            'name': artist_name,
            'mbid': mbid,
            'tags': tags[:10],  # Store top 10 tags
            'dosatsu_genre': genre,
            'source': 'musicbrainz'
        }

        self.cache[artist_name] = result
        self._save_cache()

        return result

    def classify_artists(self, artists: List[str], save_interval: int = 50) -> Dict:
        """
        Classify multiple artists
        Returns dict with results and statistics
        """
        results = {
            'total': len(artists),
            'found': 0,
            'not_found': 0,
            'artists': []
        }

        for i, artist in enumerate(artists, 1):
            result = self.classify_artist(artist)

            if result:
                results['found'] += 1
                results['artists'].append(result)
            else:
                results['not_found'] += 1

            # Progress update
            if i % 10 == 0:
                print(f"Progress: {i}/{len(artists)} ({i/len(artists)*100:.1f}%) - "
                      f"Found: {results['found']}, Not found: {results['not_found']}")

            # Save cache periodically
            if i % save_interval == 0:
                self._save_cache()
                print(f"✓ Cache saved ({len(self.cache)} artists)")

        return results

    def get_genre(self, artist_name: str) -> str:
        """Quick lookup for genre (for compatibility with Spotify classifier)"""
        if artist_name in self.cache:
            data = self.cache[artist_name]
            if data:
                return data.get('dosatsu_genre', 'Unknown')
        return 'Unknown'
