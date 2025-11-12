#!/usr/bin/env python3
"""
Genre Tracking & Anomaly Detection
Find genre droughts and historic firsts like "First time in 35 years no hip-hop in top 40"
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

class GenreTracker:
    """
    Track genre representation in Billboard charts
    Identify droughts, historic firsts, and trend shifts
    """

    def __init__(self, billboard_data: Dict, genre_mapping: Optional[Dict] = None):
        """
        Initialize with Billboard data and optional genre mapping

        Args:
            billboard_data: Billboard chart data by date
            genre_mapping: Dict mapping artist names to genres
                          Example: {"Drake": "Hip-Hop", "Taylor Swift": "Pop"}
        """
        self.data = billboard_data
        self.dates = sorted(billboard_data.keys())
        self.genre_mapping = genre_mapping or {}

    def load_genre_mapping(self, file_path: str):
        """Load genre mapping from JSON file"""
        with open(file_path, 'r') as f:
            self.genre_mapping = json.load(f)

    def save_genre_mapping(self, file_path: str):
        """Save current genre mapping to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(self.genre_mapping, f, indent=2)

    def classify_artist(self, artist: str) -> Optional[str]:
        """Get genre for artist"""
        return self.genre_mapping.get(artist)

    def analyze_genre_presence_by_week(self, genre: str, top_n: int = 40) -> Dict:
        """
        Analyze genre presence in top N for each week
        Returns weekly breakdown with counts and songs
        """
        weekly_data = {}

        for date in self.dates:
            chart = self.data[date]
            top_songs = [s for s in chart if s.get('position', 999) <= top_n]

            genre_songs = []
            for song in top_songs:
                artist = song.get('artist')
                artist_genre = self.classify_artist(artist)

                if artist_genre and artist_genre.lower() == genre.lower():
                    genre_songs.append({
                        'position': song.get('position'),
                        'song': song.get('song'),
                        'artist': artist
                    })

            weekly_data[date] = {
                'count': len(genre_songs),
                'percentage': (len(genre_songs) / len(top_songs) * 100) if top_songs else 0,
                'songs': genre_songs,
                'total_in_range': len(top_songs)
            }

        return weekly_data

    def find_genre_droughts(self, genre: str, top_n: int = 40) -> List[Dict]:
        """
        Find weeks with ZERO genre representation
        Calculates "first time in X years" insights
        """
        weekly_data = self.analyze_genre_presence_by_week(genre, top_n)
        droughts = []

        for date, data in weekly_data.items():
            if data['count'] == 0:
                years_since = self._calculate_years_since_last_drought(date, weekly_data)

                droughts.append({
                    'date': date,
                    'genre': genre,
                    'position_range': f"top {top_n}",
                    'years_since_last_drought': years_since,
                    'insight': f"🚨 FIRST TIME IN {years_since} YEARS: "
                              f"No {genre} tracks in top {top_n} (Week of {self._format_date(date)})",
                    'tweet': f"For the first time in {years_since} years, there are no {genre} tracks "
                            f"in the Billboard Hot 100 top {top_n}.\n\n"
                            f"Week of {self._format_date(date)}\n\n"
                            f"A significant shift in the music landscape.\n\n"
                            f"#MusicIndustry #Billboard #{genre.replace(' ', '')}"
                })

        return droughts

    def _calculate_years_since_last_drought(self, current_date: str, weekly_data: Dict) -> int:
        """Calculate years since previous zero-count week"""
        current = datetime.strptime(current_date, "%Y-%m-%d")

        # Look backwards
        for date in reversed([d for d in self.dates if d < current_date]):
            if weekly_data[date]['count'] == 0:
                previous = datetime.strptime(date, "%Y-%m-%d")
                years = (current - previous).days / 365.25
                return int(years)

        # No previous drought found - return years since data start
        first_date = datetime.strptime(self.dates[0], "%Y-%m-%d")
        return int((current - first_date).days / 365.25)

    def analyze_genre_trends(self, genre: str, top_n: int = 40) -> Dict:
        """
        Comprehensive genre trend analysis
        Returns peaks, valleys, averages
        """
        weekly_data = self.analyze_genre_presence_by_week(genre, top_n)

        counts = [data['count'] for data in weekly_data.values()]
        percentages = [data['percentage'] for data in weekly_data.values()]

        # Find peaks and valleys
        peak_count = max(counts)
        peak_dates = [date for date, data in weekly_data.items() if data['count'] == peak_count]

        zero_weeks = [date for date, data in weekly_data.items() if data['count'] == 0]

        # Calculate averages by year
        yearly_averages = defaultdict(list)
        for date, data in weekly_data.items():
            year = date[:4]
            yearly_averages[year].append(data['percentage'])

        yearly_avg = {
            year: sum(percs) / len(percs)
            for year, percs in yearly_averages.items()
        }

        return {
            'genre': genre,
            'position_range': f"top {top_n}",
            'date_range': f"{self.dates[0]} to {self.dates[-1]}",
            'total_weeks_analyzed': len(weekly_data),
            'average_representation': sum(percentages) / len(percentages) if percentages else 0,
            'peak': {
                'count': peak_count,
                'dates': peak_dates[:3],  # Show first 3 peak dates
                'insight': f"{genre} peaked with {peak_count} songs in top {top_n}"
            },
            'droughts': {
                'total_zero_weeks': len(zero_weeks),
                'most_recent_drought': zero_weeks[-1] if zero_weeks else None
            },
            'yearly_trends': yearly_avg
        }

    def compare_genres(self, genres: List[str], top_n: int = 40) -> Dict:
        """
        Compare multiple genres side-by-side
        Returns comparative analysis
        """
        comparison = {}

        for genre in genres:
            trends = self.analyze_genre_trends(genre, top_n)
            comparison[genre] = {
                'avg_representation': trends['average_representation'],
                'peak_count': trends['peak']['count'],
                'zero_weeks': trends['droughts']['total_zero_weeks']
            }

        return comparison

    def generate_genre_report(self, genre: str, top_n: int = 40) -> str:
        """
        Generate a comprehensive report for a genre
        Suitable for LinkedIn posts
        """
        trends = self.analyze_genre_trends(genre, top_n)
        droughts = self.find_genre_droughts(genre, top_n)

        report = f"📊 {genre} on the Billboard Hot 100: A Data Analysis\n"
        report += "=" * 70 + "\n\n"

        report += f"Date Range: {trends['date_range']}\n"
        report += f"Position Range: {trends['position_range']}\n\n"

        report += f"Key Findings:\n"
        report += f"• Average Representation: {trends['average_representation']:.1f}%\n"
        report += f"• Peak Performance: {trends['peak']['count']} songs ({trends['peak']['dates'][0]})\n"
        report += f"• Weeks with Zero Representation: {trends['droughts']['total_zero_weeks']}\n\n"

        if droughts:
            report += f"🚨 Notable Droughts:\n"
            for drought in droughts[-3:]:  # Show last 3 droughts
                report += f"• {drought['insight']}\n"

        report += f"\nYear-by-Year Average Representation:\n"
        for year, avg in sorted(trends['yearly_trends'].items()):
            report += f"  {year}: {avg:.1f}%\n"

        return report

    def _format_date(self, date_str: str) -> str:
        """Format date as 'October 30, 2024'"""
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")

    def build_genre_mapping_from_data(self, sample_weeks: int = 4) -> Dict:
        """
        Create a starter genre mapping for manual curation
        Returns artists found in recent weeks for manual classification
        """
        artists = set()

        # Get artists from recent weeks
        recent_dates = self.dates[-sample_weeks:]

        for date in recent_dates:
            chart = self.data[date]
            for song in chart:
                artist = song.get('artist')
                if artist:
                    artists.add(artist)

        # Create template
        mapping = {artist: "UNCATEGORIZED" for artist in sorted(artists)}

        return mapping


def create_sample_genre_mapping():
    """
    Create a sample genre mapping to get started
    Users should customize this with their own classifications
    """
    return {
        # Hip-Hop/Rap
        "Drake": "Hip-Hop",
        "Kendrick Lamar": "Hip-Hop",
        "Travis Scott": "Hip-Hop",
        "21 Savage": "Hip-Hop",
        "Metro Boomin": "Hip-Hop",
        "Future": "Hip-Hop",
        "Lil Baby": "Hip-Hop",
        "Gunna": "Hip-Hop",
        "Rod Wave": "Hip-Hop",
        "NBA YoungBoy": "Hip-Hop",
        "SZA": "R&B/Hip-Hop",
        "Doja Cat": "Pop/Hip-Hop",

        # Pop
        "Taylor Swift": "Pop",
        "Ariana Grande": "Pop",
        "Olivia Rodrigo": "Pop",
        "Billie Eilish": "Pop",
        "Dua Lipa": "Pop",
        "The Weeknd": "Pop/R&B",
        "Harry Styles": "Pop",
        "Miley Cyrus": "Pop",
        "Selena Gomez": "Pop",

        # Country
        "Morgan Wallen": "Country",
        "Luke Combs": "Country",
        "Zach Bryan": "Country",
        "Jelly Roll": "Country",
        "Kane Brown": "Country",

        # R&B
        "Beyoncé": "R&B",
        "Usher": "R&B",
        "Chris Brown": "R&B",

        # Latin
        "Bad Bunny": "Latin",
        "Peso Pluma": "Latin",
        "Karol G": "Latin",

        # Rock/Alternative
        "Imagine Dragons": "Rock",
        "OneRepublic": "Pop/Rock",
    }


def demo():
    """Run demo analysis"""
    print("=" * 70)
    print("GENRE TRACKING & DROUGHT DETECTION")
    print("=" * 70)
    print()

    # Load Billboard data
    try:
        print("Loading Billboard data...")
        with open('billboard_recent.json', 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded {len(data)} weeks of chart data")
    except FileNotFoundError:
        print("❌ Billboard data not found!")
        print("Run 'python3 billboard_downloader.py' first.")
        return

    print()

    # Create sample genre mapping
    print("Creating sample genre mapping...")
    genre_mapping = create_sample_genre_mapping()
    print(f"✓ Sample mapping created for {len(genre_mapping)} artists")

    # Save sample mapping
    with open('genre_mapping_sample.json', 'w') as f:
        json.dump(genre_mapping, f, indent=2)
    print("✓ Saved to: genre_mapping_sample.json")
    print("  (Edit this file to add more artists and genres)")
    print()

    # Initialize tracker
    tracker = GenreTracker(data, genre_mapping)

    # Analyze Hip-Hop
    print("=" * 70)
    print("ANALYZING HIP-HOP REPRESENTATION")
    print("=" * 70)
    print()

    trends = tracker.analyze_genre_trends("Hip-Hop", top_n=40)
    print(f"Average Hip-Hop representation in top 40: {trends['average_representation']:.1f}%")
    print(f"Peak: {trends['peak']['count']} songs")
    print(f"Weeks with zero Hip-Hop: {trends['droughts']['total_zero_weeks']}")
    print()

    # Find droughts
    print("🚨 DETECTING HIP-HOP DROUGHTS (Top 40)")
    print("-" * 70)
    droughts = tracker.find_genre_droughts("Hip-Hop", top_n=40)

    if droughts:
        print(f"Found {len(droughts)} drought weeks\n")
        print("Most recent droughts:")
        for drought in droughts[-3:]:
            print(f"  {drought['insight']}")
            print()
    else:
        print("No droughts detected in the analyzed period")

    print()
    print("=" * 70)
    print("💡 TIP: To improve accuracy:")
    print("  1. Edit 'genre_mapping_sample.json' to add more artists")
    print("  2. Or integrate with Spotify/MusicBrainz for automatic genre data")
    print("=" * 70)


if __name__ == "__main__":
    demo()
