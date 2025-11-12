#!/usr/bin/env python3
"""
Billboard Chart Data Downloader
Downloads and analyzes Billboard Hot 100 chart data from public sources
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class BillboardDataDownloader:
    """Download Billboard Hot 100 data from GitHub repository"""

    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main"

    def download_all_charts(self, save_path: str = "billboard_all_charts.json") -> Dict:
        """Download complete Billboard Hot 100 history"""
        print("Downloading complete Billboard Hot 100 history...")
        print("(This is a large file, may take a moment)")

        try:
            response = requests.get(f"{self.base_url}/all.json", timeout=60)
            response.raise_for_status()
            raw_data = response.json()

            # Convert list format to dict format for easier processing
            # Raw format: [{"date": "2024-01-01", "data": [songs...]}, ...]
            # Output format: {"2024-01-01": [songs...], ...}
            if isinstance(raw_data, list):
                data = {}
                for chart in raw_data:
                    date = chart.get('date')
                    songs = chart.get('data', [])

                    # Normalize field names: this_week -> position
                    normalized_songs = []
                    for song in songs:
                        normalized_songs.append({
                            'position': song.get('this_week'),
                            'song': song.get('song'),
                            'artist': song.get('artist'),
                            'last_week': song.get('last_week'),
                            'peak_position': song.get('peak_position'),
                            'weeks_on_chart': song.get('weeks_on_chart')
                        })

                    data[date] = normalized_songs
            else:
                data = raw_data

            # Save to file
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"✓ Downloaded {len(data)} weeks of chart data")
            print(f"✓ Saved to: {save_path}")
            return data

        except requests.RequestException as e:
            print(f"Error downloading data: {e}")
            return {}

    def download_recent_charts(self, years: int = 10, save_path: str = "billboard_recent.json") -> Dict:
        """Download charts from the last N years"""
        print(f"Downloading Billboard Hot 100 data from last {years} years...")

        all_data = self.download_all_charts("temp_all_charts.json")

        # Calculate cutoff date
        cutoff_date = (datetime.now() - timedelta(days=years*365)).strftime("%Y-%m-%d")

        # Filter recent data
        recent_data = {
            date: chart
            for date, chart in all_data.items()
            if date >= cutoff_date
        }

        # Save filtered data
        with open(save_path, 'w') as f:
            json.dump(recent_data, f, indent=2)

        print(f"✓ Filtered to {len(recent_data)} weeks ({cutoff_date} to present)")
        print(f"✓ Saved to: {save_path}")

        return recent_data

    def get_chart_by_date(self, date: str) -> Optional[Dict]:
        """Get specific chart by date (YYYY-MM-DD format)"""
        try:
            response = requests.get(f"{self.base_url}/{date}.json")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching chart for {date}: {e}")
            return None


class BillboardAnalyzer:
    """Analyze Billboard chart data"""

    def __init__(self, chart_data: Dict):
        self.data = chart_data

    def get_artist_chart_history(self, artist_name: str) -> List[Dict]:
        """Get all chart appearances for an artist"""
        appearances = []

        for date, chart in self.data.items():
            for song in chart:
                # Check if artist name matches (case-insensitive, partial match)
                if artist_name.lower() in song.get('artist', '').lower():
                    appearances.append({
                        'date': date,
                        'song': song.get('song'),
                        'position': song.get('position'),
                        'artist': song.get('artist'),
                        'last_week': song.get('last_week'),
                        'peak_position': song.get('peak_position'),
                        'weeks_on_chart': song.get('weeks_on_chart')
                    })

        return sorted(appearances, key=lambda x: x['date'], reverse=True)

    def get_number_one_hits(self, artist_name: Optional[str] = None) -> List[Dict]:
        """Get all #1 hits, optionally filtered by artist"""
        number_ones = []

        for date, chart in self.data.items():
            for song in chart:
                if song.get('position') == 1:
                    if artist_name is None or artist_name.lower() in song.get('artist', '').lower():
                        number_ones.append({
                            'date': date,
                            'song': song.get('song'),
                            'artist': song.get('artist'),
                            'weeks_on_chart': song.get('weeks_on_chart')
                        })

        return sorted(number_ones, key=lambda x: x['date'], reverse=True)

    def get_top_artists(self, limit: int = 50) -> List[Dict]:
        """Get artists with most chart appearances"""
        artist_counts = {}

        for date, chart in self.data.items():
            for song in chart:
                artist = song.get('artist', 'Unknown')
                if artist not in artist_counts:
                    artist_counts[artist] = {
                        'appearances': 0,
                        'songs': set(),
                        'peak_positions': []
                    }

                artist_counts[artist]['appearances'] += 1
                artist_counts[artist]['songs'].add(song.get('song'))
                artist_counts[artist]['peak_positions'].append(song.get('position', 101))

        # Format results
        results = []
        for artist, data in artist_counts.items():
            results.append({
                'artist': artist,
                'total_appearances': data['appearances'],
                'unique_songs': len(data['songs']),
                'best_position': min(data['peak_positions']) if data['peak_positions'] else None
            })

        # Sort by appearances
        results.sort(key=lambda x: x['total_appearances'], reverse=True)
        return results[:limit]

    def analyze_song_trajectory(self, song_title: str, artist: str) -> Dict:
        """Analyze a specific song's chart performance"""
        trajectory = []

        for date, chart in self.data.items():
            for song in chart:
                if (song_title.lower() in song.get('song', '').lower() and
                    artist.lower() in song.get('artist', '').lower()):
                    trajectory.append({
                        'date': date,
                        'position': song.get('position'),
                        'peak_position': song.get('peak_position'),
                        'weeks_on_chart': song.get('weeks_on_chart')
                    })

        if not trajectory:
            return {'error': 'Song not found in chart data'}

        trajectory.sort(key=lambda x: x['date'])

        return {
            'song': song_title,
            'artist': artist,
            'first_chart_date': trajectory[0]['date'],
            'last_chart_date': trajectory[-1]['date'],
            'peak_position': min(t['position'] for t in trajectory),
            'total_weeks': len(trajectory),
            'trajectory': trajectory
        }

    def get_date_range(self) -> Dict:
        """Get the date range of available data"""
        dates = sorted(self.data.keys())
        return {
            'earliest': dates[0] if dates else None,
            'latest': dates[-1] if dates else None,
            'total_weeks': len(dates)
        }


def demo_analysis():
    """Run demonstration analysis"""
    print("=" * 60)
    print("BILLBOARD HOT 100 DATA DOWNLOADER & ANALYZER")
    print("=" * 60)
    print()

    # Download data
    downloader = BillboardDataDownloader()
    recent_data = downloader.download_recent_charts(years=10)

    print()
    print("=" * 60)
    print("ANALYZING CHART DATA")
    print("=" * 60)
    print()

    # Create analyzer
    analyzer = BillboardAnalyzer(recent_data)

    # Show date range
    date_range = analyzer.get_date_range()
    print(f"Data Range: {date_range['earliest']} to {date_range['latest']}")
    print(f"Total Weeks: {date_range['total_weeks']}")
    print()

    # Example: Top artists in last 10 years
    print("Top 10 Artists (Most Chart Appearances - Last 10 Years):")
    print("-" * 60)
    top_artists = analyzer.get_top_artists(limit=10)
    for i, artist_data in enumerate(top_artists, 1):
        print(f"{i:2d}. {artist_data['artist']}")
        print(f"    Appearances: {artist_data['total_appearances']} | "
              f"Unique Songs: {artist_data['unique_songs']} | "
              f"Peak Position: #{artist_data['best_position']}")
    print()

    # Example: Search for specific artist
    artist_to_search = "Drake"  # Change this to test with different artists
    print(f"Chart History for {artist_to_search}:")
    print("-" * 60)
    history = analyzer.get_artist_chart_history(artist_to_search)

    if history:
        print(f"Total chart appearances: {len(history)}")
        print(f"\nMost recent 5 entries:")
        for entry in history[:5]:
            print(f"  {entry['date']}: #{entry['position']:2d} - {entry['song']}")

        # Count #1 hits
        number_ones = [h for h in history if h['position'] == 1]
        print(f"\n#{1} hits: {len(number_ones)}")
    else:
        print(f"No chart data found for {artist_to_search}")

    print()
    print("=" * 60)
    print("Analysis complete! Data saved locally for further use.")
    print("=" * 60)


if __name__ == "__main__":
    demo_analysis()
