#!/usr/bin/env python3
"""
YouTube Data API Integration for Dōsatsu
Fetches video stats (views, likes) for Billboard songs
"""

import json
import requests
import time
from typing import Dict, Optional, List

class YouTubeDataFetcher:
    """Fetch and cache YouTube video data for songs"""

    def __init__(self, api_key: str, cache_file: str = 'youtube_cache.json'):
        self.api_key = api_key
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.quota_used = 0

    def _load_cache(self) -> Dict:
        """Load cached YouTube data"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def _make_request(self, url: str, params: Dict) -> Optional[Dict]:
        """Make API request with error handling"""
        params['key'] = self.api_key

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making YouTube API request: {e}")
            return None

    def search_video(self, artist: str, song: str) -> Optional[str]:
        """
        Search for a music video and return video ID
        Cost: 100 units
        """
        query = f"{artist} {song} official music video"

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'videoCategoryId': '10',  # Music category
            'maxResults': 1
        }

        data = self._make_request(url, params)
        self.quota_used += 100  # Search costs 100 units

        if data and 'items' in data and len(data['items']) > 0:
            return data['items'][0]['id']['videoId']

        return None

    def get_video_stats(self, video_id: str) -> Optional[Dict]:
        """
        Get statistics for a video
        Cost: 1 unit
        """
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'statistics,snippet',
            'id': video_id
        }

        data = self._make_request(url, params)
        self.quota_used += 1  # Video stats costs 1 unit

        if data and 'items' in data and len(data['items']) > 0:
            item = data['items'][0]
            stats = item.get('statistics', {})
            snippet = item.get('snippet', {})

            return {
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'title': snippet.get('title', ''),
                'channel': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'comment_count': int(stats.get('commentCount', 0)),
                'last_updated': time.strftime('%Y-%m-%d')
            }

        return None

    def get_song_data(self, artist: str, song: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get YouTube data for a song (search + stats)
        Uses cache if available
        Cost: 101 units (first time), 0 units (cached), 1 unit (refresh only)
        """
        cache_key = f"{artist} - {song}"

        # Check cache
        if cache_key in self.cache and not force_refresh:
            print(f"✓ Cache hit: {cache_key}")
            return self.cache[cache_key]

        # Search for video
        print(f"Searching YouTube: {cache_key}")
        video_id = self.search_video(artist, song)

        if not video_id:
            print(f"✗ Video not found: {cache_key}")
            self.cache[cache_key] = None
            self._save_cache()
            return None

        # Get video stats
        stats = self.get_video_stats(video_id)

        if stats:
            self.cache[cache_key] = stats
            self._save_cache()
            print(f"✓ Added to cache: {cache_key} ({stats['view_count']:,} views)")
            return stats

        return None

    def refresh_stats(self, artist: str, song: str) -> Optional[Dict]:
        """
        Refresh stats for an already-cached song
        Cost: 1 unit (only gets stats, no search needed)
        """
        cache_key = f"{artist} - {song}"

        if cache_key not in self.cache or self.cache[cache_key] is None:
            print(f"Not in cache, need full search: {cache_key}")
            return self.get_song_data(artist, song)

        video_id = self.cache[cache_key]['video_id']

        print(f"Refreshing stats: {cache_key}")
        stats = self.get_video_stats(video_id)

        if stats:
            self.cache[cache_key] = stats
            self._save_cache()
            print(f"✓ Updated: {cache_key} ({stats['view_count']:,} views)")
            return stats

        return None

    def batch_get_songs(self, songs: List[tuple], max_quota: int = 10000) -> Dict:
        """
        Process multiple songs with quota limit
        songs: List of (artist, song) tuples
        Returns: Dict with results and quota usage
        """
        results = {
            'processed': 0,
            'found': 0,
            'not_found': 0,
            'cached': 0,
            'quota_used': 0,
            'songs': []
        }

        for artist, song in songs:
            # Check if we'd exceed quota
            cache_key = f"{artist} - {song}"
            estimated_cost = 0 if cache_key in self.cache else 101

            if self.quota_used + estimated_cost > max_quota:
                print(f"\n⚠️  Quota limit reached ({self.quota_used}/{max_quota} units)")
                print(f"Processed {results['processed']} of {len(songs)} songs")
                break

            # Process song
            data = self.get_song_data(artist, song)

            results['processed'] += 1
            if data:
                results['found'] += 1
                results['songs'].append({
                    'artist': artist,
                    'song': song,
                    'youtube_data': data
                })
            else:
                results['not_found'] += 1

        results['quota_used'] = self.quota_used
        results['cached'] = results['processed'] - results['found'] - results['not_found']

        return results

    def get_quota_status(self) -> Dict:
        """Get current quota usage"""
        return {
            'quota_used': self.quota_used,
            'quota_remaining': 10000 - self.quota_used,
            'percentage_used': (self.quota_used / 10000) * 100
        }
