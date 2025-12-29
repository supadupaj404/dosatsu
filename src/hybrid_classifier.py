#!/usr/bin/env python3
"""
Hybrid Genre Classifier for Dōsatsu
Tries Spotify first (fast, accurate), falls back to MusicBrainz (comprehensive)
"""

import json
from typing import Dict, Optional, List
from spotify_genre_classifier import SpotifyGenreClassifier
from musicbrainz_classifier import MusicBrainzClassifier

class HybridClassifier:
    """
    Combine Spotify and MusicBrainz for maximum coverage

    Strategy:
    1. Check unified cache first
    2. Try Spotify (fast, modern artists, accurate genres)
    3. Fall back to MusicBrainz (older artists, community tags)
    4. Cache all results in unified format
    """

    def __init__(self, spotify_client_id: str, spotify_client_secret: str,
                 cache_file: str = 'hybrid_genre_cache.json'):
        self.cache_file = cache_file
        self.cache = self._load_cache()

        # Initialize both classifiers
        self.spotify = SpotifyGenreClassifier(spotify_client_id, spotify_client_secret)
        self.musicbrainz = MusicBrainzClassifier()

    def _load_cache(self) -> Dict:
        """Load unified cache"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_cache(self):
        """Save unified cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def classify_artist(self, artist_name: str) -> Optional[Dict]:
        """
        Classify artist using both sources
        Returns unified dict with genre info
        """
        # Check unified cache first
        if artist_name in self.cache:
            return self.cache[artist_name]

        # Try Spotify first (preferred)
        # Check if already in Spotify cache
        if artist_name in self.spotify.cache:
            spotify_data = self.spotify.cache[artist_name]
            result = {
                'name': artist_name,
                'dosatsu_genre': spotify_data.get('dosatsu_genre', 'Unknown'),
                'source': 'spotify',
                'spotify_genres': spotify_data.get('genres', []),
                'popularity': spotify_data.get('popularity', 0),
                'confidence': 'high'  # Spotify genres are curated
            }
            self.cache[artist_name] = result
            self._save_cache()
            return result

        # Search Spotify if not in cache
        spotify_result = self.spotify.search_artist(artist_name)

        if spotify_result:
            # Format Spotify result
            result = {
                'name': artist_name,
                'dosatsu_genre': spotify_result.get('dosatsu_genre', 'Unknown'),
                'source': 'spotify',
                'spotify_genres': spotify_result.get('genres', []),
                'popularity': spotify_result.get('popularity', 0),
                'confidence': 'high'
            }
            self.cache[artist_name] = result
            self._save_cache()
            return result

        # Fall back to MusicBrainz
        print(f"  → Spotify not found, trying MusicBrainz...")
        mb_result = self.musicbrainz.classify_artist(artist_name)

        if mb_result:
            # Format MusicBrainz result
            result = {
                'name': artist_name,
                'dosatsu_genre': mb_result.get('dosatsu_genre', 'Unknown'),
                'source': 'musicbrainz',
                'mb_tags': mb_result.get('tags', []),
                'mbid': mb_result.get('mbid', ''),
                'confidence': 'medium'  # Community tags are less precise
            }
            self.cache[artist_name] = result
            self._save_cache()
            return result

        # Not found in either source
        self.cache[artist_name] = None
        self._save_cache()
        return None

    def classify_artists(self, artists: List[str], save_interval: int = 50) -> Dict:
        """
        Classify multiple artists using hybrid approach
        Returns detailed statistics
        """
        results = {
            'total': len(artists),
            'found': 0,
            'not_found': 0,
            'spotify': 0,
            'musicbrainz': 0,
            'artists': []
        }

        for i, artist in enumerate(artists, 1):
            result = self.classify_artist(artist)

            if result:
                results['found'] += 1
                results['artists'].append(result)

                # Track source
                source = result.get('source', 'unknown')
                if source == 'spotify':
                    results['spotify'] += 1
                elif source == 'musicbrainz':
                    results['musicbrainz'] += 1
            else:
                results['not_found'] += 1

            # Progress update
            if i % 10 == 0:
                print(f"Progress: {i}/{len(artists)} ({i/len(artists)*100:.1f}%) - "
                      f"Found: {results['found']} (Spotify: {results['spotify']}, "
                      f"MusicBrainz: {results['musicbrainz']}) | "
                      f"Not found: {results['not_found']}")

            # Save cache periodically
            if i % save_interval == 0:
                self._save_cache()
                print(f"✓ Cache saved ({len(self.cache)} artists)")

        return results

    def get_genre(self, artist_name: str) -> str:
        """Quick genre lookup (for compatibility with existing code)"""
        if artist_name in self.cache:
            data = self.cache[artist_name]
            if data:
                return data.get('dosatsu_genre', 'Unknown')
        return 'Unknown'

    def get_coverage_stats(self) -> Dict:
        """Analyze cache coverage and sources"""
        stats = {
            'total': len(self.cache),
            'classified': 0,
            'spotify': 0,
            'musicbrainz': 0,
            'not_found': 0,
            'genres': {}
        }

        for artist, data in self.cache.items():
            if data is None:
                stats['not_found'] += 1
            else:
                stats['classified'] += 1

                source = data.get('source', 'unknown')
                if source == 'spotify':
                    stats['spotify'] += 1
                elif source == 'musicbrainz':
                    stats['musicbrainz'] += 1

                genre = data.get('dosatsu_genre', 'Unknown')
                stats['genres'][genre] = stats['genres'].get(genre, 0) + 1

        return stats

    def import_existing_caches(self):
        """
        Import data from existing Spotify and MusicBrainz caches
        Useful for migrating to hybrid system
        """
        imported = 0

        # Import Spotify cache
        if hasattr(self.spotify, 'cache'):
            for artist, data in self.spotify.cache.items():
                if artist not in self.cache and data:
                    self.cache[artist] = {
                        'name': artist,
                        'dosatsu_genre': data.get('dosatsu_genre', 'Unknown'),
                        'source': 'spotify',
                        'spotify_genres': data.get('genres', []),
                        'popularity': data.get('popularity', 0),
                        'confidence': 'high'
                    }
                    imported += 1

        # Import MusicBrainz cache
        if hasattr(self.musicbrainz, 'cache'):
            for artist, data in self.musicbrainz.cache.items():
                if artist not in self.cache and data:
                    self.cache[artist] = {
                        'name': artist,
                        'dosatsu_genre': data.get('dosatsu_genre', 'Unknown'),
                        'source': 'musicbrainz',
                        'mb_tags': data.get('tags', []),
                        'mbid': data.get('mbid', ''),
                        'confidence': 'medium'
                    }
                    imported += 1

        if imported > 0:
            self._save_cache()
            print(f"✓ Imported {imported} artists from existing caches")

        return imported
