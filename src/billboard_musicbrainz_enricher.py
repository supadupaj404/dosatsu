#!/usr/bin/env python3
"""
Billboard + MusicBrainz Data Enricher
Combines Billboard chart data with MusicBrainz metadata for comprehensive analysis
"""

import requests
import json
import time
from typing import Dict, List, Optional
from datetime import datetime

class MusicBrainzEnricher:
    """Enrich Billboard data with MusicBrainz metadata"""

    def __init__(self, app_name: str = "BillboardEnricher", version: str = "1.0", contact: str = "jeremy@whetstone.com"):
        self.base_url = "https://musicbrainz.org/ws/2"
        self.headers = {
            'User-Agent': f'{app_name}/{version} ({contact})'
        }
        self.rate_limit_delay = 1.1  # MusicBrainz requires 1 request per second

    def search_recording(self, song_title: str, artist_name: str) -> Optional[Dict]:
        """Search for a recording (song) in MusicBrainz"""
        url = f"{self.base_url}/recording"
        params = {
            'query': f'recording:"{song_title}" AND artist:"{artist_name}"',
            'fmt': 'json',
            'limit': 5
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get('recordings'):
                return data['recordings'][0]  # Return best match
            return None

        except requests.RequestException as e:
            print(f"Error searching MusicBrainz: {e}")
            return None

        finally:
            time.sleep(self.rate_limit_delay)  # Respect rate limits

    def get_recording_details(self, mbid: str) -> Optional[Dict]:
        """Get detailed metadata for a recording"""
        url = f"{self.base_url}/recording/{mbid}"
        params = {
            'fmt': 'json',
            'inc': 'artist-credits+releases+isrcs+work-rels+artist-rels+tags+ratings'
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Error getting recording details: {e}")
            return None

        finally:
            time.sleep(self.rate_limit_delay)

    def get_artist_details(self, artist_name: str) -> Optional[Dict]:
        """Get artist metadata from MusicBrainz"""
        url = f"{self.base_url}/artist"
        params = {
            'query': f'artist:"{artist_name}"',
            'fmt': 'json',
            'limit': 1
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get('artists'):
                artist = data['artists'][0]

                # Get full details
                artist_id = artist['id']
                detail_url = f"{self.base_url}/artist/{artist_id}"
                detail_params = {
                    'fmt': 'json',
                    'inc': 'tags+ratings+genres'
                }

                time.sleep(self.rate_limit_delay)
                detail_response = requests.get(detail_url, headers=self.headers, params=detail_params)
                detail_response.raise_for_status()
                return detail_response.json()

            return None

        except requests.RequestException as e:
            print(f"Error getting artist details: {e}")
            return None

        finally:
            time.sleep(self.rate_limit_delay)

    def enrich_billboard_song(self, billboard_entry: Dict) -> Dict:
        """Enrich a single Billboard chart entry with MusicBrainz data"""
        song = billboard_entry.get('song', '')
        artist = billboard_entry.get('artist', '')

        print(f"  Enriching: {song} by {artist}")

        # Search for the recording
        recording = self.search_recording(song, artist)

        enriched = {
            **billboard_entry,  # Keep original Billboard data
            'musicbrainz': {
                'found': False,
                'mbid': None,
                'isrc': None,
                'length_ms': None,
                'genres': [],
                'tags': [],
                'releases': []
            }
        }

        if recording:
            enriched['musicbrainz']['found'] = True
            enriched['musicbrainz']['mbid'] = recording.get('id')
            enriched['musicbrainz']['length_ms'] = recording.get('length')

            # Get detailed info
            if recording.get('id'):
                details = self.get_recording_details(recording['id'])
                if details:
                    # Extract ISRCs
                    if 'isrcs' in details:
                        enriched['musicbrainz']['isrc'] = details['isrcs'][0] if details['isrcs'] else None

                    # Extract tags/genres
                    if 'tags' in details:
                        enriched['musicbrainz']['tags'] = [
                            tag['name'] for tag in details['tags'][:10]
                        ]

                    # Extract release info
                    if 'releases' in details:
                        enriched['musicbrainz']['releases'] = [
                            {
                                'title': rel.get('title'),
                                'date': rel.get('date'),
                                'country': rel.get('country')
                            }
                            for rel in details['releases'][:5]
                        ]

        return enriched


class BillboardMusicBrainzAnalyzer:
    """Combined analysis of Billboard and MusicBrainz data"""

    def __init__(self, billboard_data: Dict):
        self.billboard_data = billboard_data
        self.enricher = MusicBrainzEnricher()

    def enrich_top_songs(self, date: str, top_n: int = 10) -> List[Dict]:
        """Enrich top N songs from a specific chart date"""
        if date not in self.billboard_data:
            print(f"No data found for {date}")
            return []

        chart = self.billboard_data[date]
        top_songs = sorted(chart, key=lambda x: x.get('position', 999))[:top_n]

        print(f"Enriching top {top_n} songs from {date}...")
        print("-" * 60)

        enriched_songs = []
        for song in top_songs:
            enriched = self.enricher.enrich_billboard_song(song)
            enriched_songs.append(enriched)

        return enriched_songs

    def analyze_artist_metadata(self, artist_name: str) -> Dict:
        """Get comprehensive metadata for an artist"""
        print(f"Fetching MusicBrainz metadata for: {artist_name}")

        artist_data = self.enricher.get_artist_details(artist_name)

        if not artist_data:
            return {'error': 'Artist not found in MusicBrainz'}

        # Extract key information
        analysis = {
            'name': artist_data.get('name'),
            'mbid': artist_data.get('id'),
            'type': artist_data.get('type'),
            'country': artist_data.get('country'),
            'begin_date': artist_data.get('life-span', {}).get('begin'),
            'genres': [genre['name'] for genre in artist_data.get('genres', [])[:5]],
            'tags': [tag['name'] for tag in artist_data.get('tags', [])[:10]],
        }

        return analysis

    def find_data_gaps(self, enriched_songs: List[Dict]) -> Dict:
        """Analyze what data is missing from MusicBrainz"""
        total = len(enriched_songs)
        found = sum(1 for s in enriched_songs if s['musicbrainz']['found'])
        with_isrc = sum(1 for s in enriched_songs if s['musicbrainz'].get('isrc'))
        with_genres = sum(1 for s in enriched_songs if s['musicbrainz'].get('tags'))

        return {
            'total_songs': total,
            'found_in_musicbrainz': found,
            'match_rate': f"{(found/total*100):.1f}%" if total > 0 else "0%",
            'with_isrc': with_isrc,
            'with_genre_tags': with_genres,
            'missing_from_musicbrainz': total - found
        }


def demo_enrichment():
    """Demonstrate Billboard + MusicBrainz enrichment"""
    print("=" * 70)
    print("BILLBOARD + MUSICBRAINZ DATA ENRICHMENT DEMO")
    print("=" * 70)
    print()

    # First, try to load existing Billboard data
    try:
        print("Loading Billboard chart data...")
        with open('billboard_recent.json', 'r') as f:
            billboard_data = json.load(f)
        print(f"✓ Loaded {len(billboard_data)} weeks of chart data")
    except FileNotFoundError:
        print("Billboard data not found. Run billboard_downloader.py first!")
        print("Creating sample data for demo...")

        # Create sample data for demo
        billboard_data = {
            "2024-01-06": [
                {"position": 1, "song": "Last Night", "artist": "Morgan Wallen"},
                {"position": 2, "song": "Cruel Summer", "artist": "Taylor Swift"},
                {"position": 3, "song": "Paint The Town Red", "artist": "Doja Cat"},
                {"position": 4, "song": "Greedy", "artist": "Tate McRae"},
                {"position": 5, "song": "Snooze", "artist": "SZA"},
            ]
        }

    print()

    # Initialize analyzer
    analyzer = BillboardMusicBrainzAnalyzer(billboard_data)

    # Get most recent chart date
    latest_date = sorted(billboard_data.keys())[-1]

    print(f"Enriching top 5 songs from {latest_date}")
    print("This will take ~6 seconds due to MusicBrainz rate limits (1 req/sec)")
    print("=" * 70)
    print()

    # Enrich top 5 songs
    enriched = analyzer.enrich_top_songs(latest_date, top_n=5)

    # Display results
    print()
    print("=" * 70)
    print("ENRICHMENT RESULTS")
    print("=" * 70)
    print()

    for song in enriched:
        print(f"#{song['position']}: {song['song']} - {song['artist']}")
        mb = song['musicbrainz']

        if mb['found']:
            print(f"  ✓ Found in MusicBrainz")
            print(f"  MBID: {mb['mbid']}")
            if mb['isrc']:
                print(f"  ISRC: {mb['isrc']}")
            if mb['length_ms']:
                minutes = mb['length_ms'] // 60000
                seconds = (mb['length_ms'] % 60000) // 1000
                print(f"  Length: {minutes}:{seconds:02d}")
            if mb['tags']:
                print(f"  Tags: {', '.join(mb['tags'][:5])}")
        else:
            print(f"  ✗ Not found in MusicBrainz")

        print()

    # Analyze data gaps
    gaps = analyzer.find_data_gaps(enriched)
    print("=" * 70)
    print("DATA COMPLETENESS ANALYSIS")
    print("=" * 70)
    print(f"Total songs analyzed: {gaps['total_songs']}")
    print(f"Found in MusicBrainz: {gaps['found_in_musicbrainz']} ({gaps['match_rate']})")
    print(f"With ISRC codes: {gaps['with_isrc']}")
    print(f"With genre tags: {gaps['with_genre_tags']}")
    print()

    # Save enriched data
    output_file = f"enriched_chart_{latest_date}.json"
    with open(output_file, 'w') as f:
        json.dump(enriched, f, indent=2)

    print(f"✓ Enriched data saved to: {output_file}")
    print()


if __name__ == "__main__":
    demo_enrichment()
