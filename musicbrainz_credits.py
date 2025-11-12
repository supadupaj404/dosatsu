#!/usr/bin/env python3
"""
MusicBrainz Credits Fetcher for Dōsatsu
Fetches songwriter, composer, lyricist, and producer credits
"""

import json
import requests
import time
from typing import Dict, Optional, List

class MusicBrainzCredits:
    """Fetch music credits using MusicBrainz API"""

    def __init__(self, cache_file: str = 'musicbrainz_credits_cache.json'):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.base_url = "https://musicbrainz.org/ws/2/"
        self.user_agent = "Dosatsu/1.0 (jeremy@whetstone.com)"
        self.rate_limit = 1.0  # 1 request per second

    def _load_cache(self) -> Dict:
        """Load cached credits data"""
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

    def _get_cache_key(self, song_title: str, artist_name: str) -> str:
        """Generate cache key for song + artist combo"""
        return f"{song_title}|||{artist_name}".lower()

    def search_recording(self, song_title: str, artist_name: str) -> Optional[str]:
        """
        Search for a recording and return its MBID
        Returns the best matching recording ID
        """
        params = {
            'query': f'recording:"{song_title}" AND artist:"{artist_name}"',
            'limit': 1,
            'fmt': 'json'
        }

        data = self._make_request('recording', params)

        if data and 'recordings' in data and len(data['recordings']) > 0:
            return data['recordings'][0]['id']

        return None

    def get_recording_credits(self, recording_id: str) -> Optional[Dict]:
        """Get credits for a recording including work relationships"""
        params = {
            'inc': 'artist-credits+work-rels+artist-rels',
            'fmt': 'json'
        }

        recording_data = self._make_request(f'recording/{recording_id}', params)

        if not recording_data:
            return None

        credits = {
            'title': recording_data.get('title'),
            'length_ms': recording_data.get('length'),
            'composers': [],
            'lyricists': [],
            'producers': [],
            'samples': [],
            'work_id': None,
            'work_title': None
        }

        # Parse recording-level relationships
        if 'relations' in recording_data:
            for rel in recording_data['relations']:
                rel_type = rel.get('type')

                # Producers
                if rel_type == 'producer' and 'artist' in rel:
                    producer_name = rel['artist'].get('name')
                    if producer_name and producer_name not in credits['producers']:
                        credits['producers'].append(producer_name)

                # Samples
                if rel_type == 'samples material' and 'recording' in rel:
                    sampled_title = rel['recording'].get('title')
                    if sampled_title:
                        credits['samples'].append(sampled_title)

                # Work relationship (leads to composers/lyricists)
                if rel_type == 'performance' and 'work' in rel:
                    work = rel['work']
                    credits['work_id'] = work.get('id')
                    credits['work_title'] = work.get('title')

        return credits

    def get_work_credits(self, work_id: str) -> Dict[str, List[str]]:
        """Get composer and lyricist credits from a work"""
        params = {
            'inc': 'artist-rels+aliases',
            'fmt': 'json'
        }

        work_data = self._make_request(f'work/{work_id}', params)

        credits = {
            'composers': [],
            'lyricists': []
        }

        if not work_data or 'relations' not in work_data:
            return credits

        for rel in work_data['relations']:
            rel_type = rel.get('type')

            if 'artist' in rel:
                artist_name = rel['artist'].get('name')

                if rel_type == 'composer' and artist_name:
                    if artist_name not in credits['composers']:
                        credits['composers'].append(artist_name)

                elif rel_type == 'lyricist' and artist_name:
                    if artist_name not in credits['lyricists']:
                        credits['lyricists'].append(artist_name)

                # Sometimes "writer" encompasses both
                elif rel_type == 'writer' and artist_name:
                    if artist_name not in credits['composers']:
                        credits['composers'].append(artist_name)
                    if artist_name not in credits['lyricists']:
                        credits['lyricists'].append(artist_name)

        return credits

    def get_credits(self, song_title: str, artist_name: str) -> Optional[Dict]:
        """
        Get complete credits for a song
        Returns dict with all available credit information
        """
        cache_key = self._get_cache_key(song_title, artist_name)

        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Search for recording
        recording_id = self.search_recording(song_title, artist_name)

        if not recording_id:
            self.cache[cache_key] = None
            self._save_cache()
            return None

        # Get recording credits
        credits = self.get_recording_credits(recording_id)

        if not credits:
            self.cache[cache_key] = None
            self._save_cache()
            return None

        # If we have a work ID, get composer/lyricist info
        if credits['work_id']:
            work_credits = self.get_work_credits(credits['work_id'])
            credits['composers'] = work_credits['composers']
            credits['lyricists'] = work_credits['lyricists']

        # Add metadata
        credits['song'] = song_title
        credits['artist'] = artist_name
        credits['recording_id'] = recording_id
        credits['source'] = 'musicbrainz'

        # Cache result
        self.cache[cache_key] = credits
        self._save_cache()

        return credits

    def get_credits_batch(self, songs: List[Dict[str, str]], save_interval: int = 50) -> Dict:
        """
        Fetch credits for multiple songs
        songs: List of dicts with 'song' and 'artist' keys
        Returns dict with results and statistics
        """
        results = {
            'total': len(songs),
            'found': 0,
            'not_found': 0,
            'credits': []
        }

        for i, song_data in enumerate(songs, 1):
            song_title = song_data.get('song')
            artist_name = song_data.get('artist')

            if not song_title or not artist_name:
                results['not_found'] += 1
                continue

            credits = self.get_credits(song_title, artist_name)

            if credits:
                results['found'] += 1
                results['credits'].append(credits)
            else:
                results['not_found'] += 1

            # Progress update
            if i % 10 == 0:
                print(f"Progress: {i}/{len(songs)} ({i/len(songs)*100:.1f}%) - "
                      f"Found: {results['found']}, Not found: {results['not_found']}")

            # Save cache periodically
            if i % save_interval == 0:
                self._save_cache()
                print(f"✓ Cache saved ({len(self.cache)} songs)")

        return results

    def format_credits(self, credits: Dict) -> str:
        """Format credits data as readable string"""
        if not credits:
            return "Credits not found"

        lines = []
        lines.append(f"🎵 {credits['song']} - {credits['artist']}")
        lines.append("")

        if credits.get('composers'):
            lines.append("✍️ Composers/Writers:")
            for composer in credits['composers']:
                lines.append(f"  • {composer}")
            lines.append("")

        if credits.get('lyricists'):
            lines.append("📝 Lyricists:")
            for lyricist in credits['lyricists']:
                lines.append(f"  • {lyricist}")
            lines.append("")

        if credits.get('producers'):
            lines.append("🎛️ Producers:")
            for producer in credits['producers']:
                lines.append(f"  • {producer}")
            lines.append("")

        if credits.get('samples'):
            lines.append("🎼 Samples:")
            for sample in credits['samples']:
                lines.append(f"  • {sample}")
            lines.append("")

        return "\n".join(lines)
