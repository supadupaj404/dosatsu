#!/usr/bin/env python3
"""
Billboard Insights Generator for Social Media
Find interesting trends, anomalies, and "first time in X years" moments
Perfect for Twitter/LinkedIn content
"""

import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics

class BillboardInsightsGenerator:
    """Generate shareable insights from Billboard chart data"""

    def __init__(self, billboard_data: Dict):
        self.data = billboard_data
        self.dates = sorted(billboard_data.keys())

    # ============================================
    # GENRE ANALYSIS
    # ============================================

    def analyze_genre_presence(self, genre_keywords: List[str], position_threshold: int = 40) -> Dict:
        """
        Track genre presence in top N positions over time
        Example: Hip-hop's presence in top 40
        """
        weekly_analysis = {}

        for date in self.dates:
            chart = self.data[date]
            top_songs = [s for s in chart if s.get('position', 999) <= position_threshold]

            genre_count = 0
            genre_songs = []

            for song in top_songs:
                artist = song.get('artist', '').lower()
                song_title = song.get('song', '').lower()

                # Simple keyword matching (can be enhanced with Spotify/MusicBrainz genre data)
                # This would need to be enriched with actual genre data for accuracy
                genre_songs.append({
                    'position': song.get('position'),
                    'song': song.get('song'),
                    'artist': song.get('artist')
                })
                genre_count += 1

            weekly_analysis[date] = {
                'count': genre_count,
                'percentage': (genre_count / len(top_songs) * 100) if top_songs else 0,
                'songs': genre_songs
            }

        return weekly_analysis

    def find_genre_droughts(self, weekly_genre_data: Dict, genre_name: str = "Hip-Hop") -> List[Dict]:
        """
        Find weeks with zero genre representation
        Returns "first time in X years" type insights
        """
        droughts = []

        for date, data in weekly_genre_data.items():
            if data['count'] == 0:
                # Find how long since last drought
                date_obj = datetime.strptime(date, "%Y-%m-%d")

                # Look backwards for previous drought
                years_since_last = self._years_since_previous_drought(date, weekly_genre_data)

                droughts.append({
                    'date': date,
                    'genre': genre_name,
                    'years_since_last_drought': years_since_last,
                    'insight': f"First time in {years_since_last} years: No {genre_name} in top 40 (Week of {date})"
                })

        return droughts

    def _years_since_previous_drought(self, current_date: str, weekly_data: Dict) -> float:
        """Calculate years since previous zero-count week"""
        current = datetime.strptime(current_date, "%Y-%m-%d")

        for date in reversed(self.dates):
            if date >= current_date:
                continue

            if weekly_data[date]['count'] == 0:
                previous = datetime.strptime(date, "%Y-%m-%d")
                years = (current - previous).days / 365.25
                return round(years, 1)

        # If no previous drought found, return years since data start
        first_date = datetime.strptime(self.dates[0], "%Y-%m-%d")
        return round((current - first_date).days / 365.25, 1)

    # ============================================
    # ARTIST DOMINANCE ANALYSIS
    # ============================================

    def find_artist_dominance_weeks(self, min_songs: int = 5) -> List[Dict]:
        """
        Find weeks where one artist had multiple songs in top 40
        Example: "Drake has 7 songs in top 40 this week"
        """
        dominance_weeks = []

        for date in self.dates:
            chart = self.data[date]
            top_40 = [s for s in chart if s.get('position', 999) <= 40]

            # Count songs per artist
            artist_counts = defaultdict(list)
            for song in top_40:
                artist = song.get('artist')
                if artist:
                    artist_counts[artist].append({
                        'position': song.get('position'),
                        'song': song.get('song')
                    })

            # Find artists with multiple songs
            for artist, songs in artist_counts.items():
                if len(songs) >= min_songs:
                    dominance_weeks.append({
                        'date': date,
                        'artist': artist,
                        'song_count': len(songs),
                        'songs': songs,
                        'insight': f"{artist} has {len(songs)} songs in top 40 (Week of {date})"
                    })

        return sorted(dominance_weeks, key=lambda x: x['song_count'], reverse=True)

    # ============================================
    # LONGEVITY & RECORDS
    # ============================================

    def find_longest_chart_runs(self, top_n: int = 10) -> List[Dict]:
        """
        Find songs with longest chart runs
        Example: "Old Town Road spent 19 weeks at #1"
        """
        song_runs = defaultdict(list)

        for date in self.dates:
            chart = self.data[date]
            for song in chart:
                key = (song.get('song'), song.get('artist'))
                song_runs[key].append({
                    'date': date,
                    'position': song.get('position'),
                    'weeks_on_chart': song.get('weeks_on_chart')
                })

        # Analyze runs
        run_analysis = []
        for (song, artist), appearances in song_runs.items():
            appearances.sort(key=lambda x: x['date'])

            peak = min(a['position'] for a in appearances)
            total_weeks = len(appearances)
            weeks_at_one = sum(1 for a in appearances if a['position'] == 1)

            run_analysis.append({
                'song': song,
                'artist': artist,
                'total_weeks': total_weeks,
                'peak_position': peak,
                'weeks_at_number_one': weeks_at_one,
                'first_chart_date': appearances[0]['date'],
                'last_chart_date': appearances[-1]['date'],
                'insight': f"'{song}' by {artist}: {total_weeks} weeks on chart" +
                          (f", {weeks_at_one} weeks at #1" if weeks_at_one > 0 else "")
            })

        return sorted(run_analysis, key=lambda x: x['total_weeks'], reverse=True)[:top_n]

    # ============================================
    # TREND DETECTION
    # ============================================

    def analyze_chart_velocity(self) -> List[Dict]:
        """
        Find songs with fastest climbs
        Example: "Song jumped 45 positions this week"
        """
        velocity_insights = []

        for date in self.dates:
            chart = self.data[date]

            for song in chart:
                current_pos = song.get('position')
                last_week_pos = song.get('last_week')

                if current_pos and last_week_pos and last_week_pos != '-':
                    try:
                        last_pos = int(last_week_pos)
                        jump = last_pos - current_pos

                        if jump >= 20:  # Significant jump
                            velocity_insights.append({
                                'date': date,
                                'song': song.get('song'),
                                'artist': song.get('artist'),
                                'current_position': current_pos,
                                'previous_position': last_pos,
                                'jump': jump,
                                'insight': f"'{song.get('song')}' by {song.get('artist')} jumped {jump} spots "
                                          f"({last_pos} → {current_pos}) - Week of {date}"
                            })
                    except (ValueError, TypeError):
                        continue

        return sorted(velocity_insights, key=lambda x: x['jump'], reverse=True)

    def find_new_entry_debuts(self, position_threshold: int = 10) -> List[Dict]:
        """
        Find songs that debuted high on the chart
        Example: "Song debuts at #3 - highest debut this year"
        """
        debuts = []

        for date in self.dates:
            chart = self.data[date]

            for song in chart:
                position = song.get('position')
                weeks = song.get('weeks_on_chart', 0)
                last_week = song.get('last_week')

                # Check if this is a debut (weeks_on_chart = 1 or last_week is "New")
                if weeks == 1 or last_week == 'New':
                    if position and position <= position_threshold:
                        debuts.append({
                            'date': date,
                            'song': song.get('song'),
                            'artist': song.get('artist'),
                            'debut_position': position,
                            'insight': f"'{song.get('song')}' by {song.get('artist')} debuts at #{position} - Week of {date}"
                        })

        return sorted(debuts, key=lambda x: x['debut_position'])

    # ============================================
    # COMPARATIVE ANALYSIS
    # ============================================

    def compare_year_over_year(self, metric: str = "turnover") -> List[Dict]:
        """
        Compare metrics across years
        Example: "2023 had 40% more #1 songs than 2022"
        """
        yearly_stats = defaultdict(lambda: {
            'unique_number_ones': set(),
            'unique_artists': set(),
            'total_songs': set()
        })

        for date in self.dates:
            year = date[:4]
            chart = self.data[date]

            for song in chart:
                song_key = (song.get('song'), song.get('artist'))
                yearly_stats[year]['total_songs'].add(song_key)
                yearly_stats[year]['unique_artists'].add(song.get('artist'))

                if song.get('position') == 1:
                    yearly_stats[year]['unique_number_ones'].add(song_key)

        # Generate insights
        insights = []
        years = sorted(yearly_stats.keys())

        for i in range(1, len(years)):
            prev_year = years[i-1]
            curr_year = years[i]

            prev_ones = len(yearly_stats[prev_year]['unique_number_ones'])
            curr_ones = len(yearly_stats[curr_year]['unique_number_ones'])

            if prev_ones > 0:
                change = ((curr_ones - prev_ones) / prev_ones) * 100

                insights.append({
                    'comparison': f"{prev_year} vs {curr_year}",
                    'metric': '#1 songs',
                    'previous': prev_ones,
                    'current': curr_ones,
                    'change_percent': round(change, 1),
                    'insight': f"{curr_year} had {curr_ones} different #1 songs vs {prev_ones} in {prev_year} "
                              f"({'+' if change > 0 else ''}{round(change, 1)}% change)"
                })

        return insights

    # ============================================
    # SOCIAL MEDIA FORMATTING
    # ============================================

    def format_for_twitter(self, insight: Dict) -> str:
        """Format insight as tweet-ready text (280 char limit)"""
        text = insight.get('insight', '')

        # Add hashtags
        text += "\n\n#MusicIndustry #Billboard #ChartData"

        if len(text) > 280:
            text = text[:277] + "..."

        return text

    def format_for_linkedin(self, insight: Dict, context: str = "") -> str:
        """Format insight for LinkedIn post with context"""
        post = f"📊 Music Industry Insight:\n\n"
        post += f"{insight.get('insight', '')}\n\n"

        if context:
            post += f"{context}\n\n"

        post += "What does this mean for the industry? "
        post += "[Add your analysis here]\n\n"
        post += "#MusicIndustry #DataAnalytics #Billboard #MusicBusiness"

        return post

    # ============================================
    # GENERATE TOP INSIGHTS
    # ============================================

    def generate_top_insights(self, insight_count: int = 10) -> List[Dict]:
        """
        Generate the most interesting insights for social media
        """
        all_insights = []

        print("Analyzing chart data for insights...")

        # 1. Velocity insights (big jumps)
        print("  → Finding biggest chart jumps...")
        velocity = self.analyze_chart_velocity()
        all_insights.extend([{**v, 'category': 'Chart Velocity'} for v in velocity[:5]])

        # 2. Artist dominance
        print("  → Finding artist dominance weeks...")
        dominance = self.find_artist_dominance_weeks()
        all_insights.extend([{**d, 'category': 'Artist Dominance'} for d in dominance[:5]])

        # 3. High debuts
        print("  → Finding high-position debuts...")
        debuts = self.find_new_entry_debuts()
        all_insights.extend([{**d, 'category': 'Hot Debut'} for d in debuts[:5]])

        # 4. Longevity records
        print("  → Finding longest chart runs...")
        longevity = self.find_longest_chart_runs()
        all_insights.extend([{**l, 'category': 'Chart Longevity'} for l in longevity[:5]])

        # 5. Year over year
        print("  → Comparing year-over-year trends...")
        yoy = self.compare_year_over_year()
        all_insights.extend([{**y, 'category': 'Year Comparison'} for y in yoy[:5]])

        return all_insights[:insight_count]


def demo():
    """Run demo with sample insights generation"""
    print("=" * 70)
    print("BILLBOARD INSIGHTS GENERATOR")
    print("Find shareable music industry insights for social media")
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
        print("Run 'python3 billboard_downloader.py' first to download chart data.")
        return

    print()
    print("=" * 70)
    print("GENERATING INSIGHTS")
    print("=" * 70)
    print()

    generator = BillboardInsightsGenerator(data)

    # Generate top insights
    insights = generator.generate_top_insights(insight_count=10)

    print()
    print("=" * 70)
    print(f"TOP {len(insights)} INSIGHTS FOR SOCIAL MEDIA")
    print("=" * 70)
    print()

    for i, insight in enumerate(insights, 1):
        print(f"{i}. [{insight['category']}]")
        print(f"   {insight['insight']}")
        print()

    # Save insights
    output_file = 'billboard_insights.json'
    with open(output_file, 'w') as f:
        json.dump(insights, f, indent=2)

    print("=" * 70)
    print(f"✓ Insights saved to: {output_file}")
    print()
    print("💡 TIP: Use these insights for Twitter/LinkedIn posts!")
    print("   Each insight is ready to share with your audience.")
    print("=" * 70)


if __name__ == "__main__":
    demo()
