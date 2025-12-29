#!/usr/bin/env python3
"""
Hip-Hop Trend Analyzer
Deep dive into hip-hop/rap representation on Billboard Hot 100 over last 5 years
Tracks growth, decline, and generates social media insights
"""

import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple
import statistics

class HipHopTrendAnalyzer:
    """Analyze hip-hop trends with focus on growth and decline patterns"""

    def __init__(self, billboard_data: Dict, genre_mapping: Dict):
        self.data = billboard_data
        self.dates = sorted(billboard_data.keys())
        self.genre_mapping = genre_mapping

    def analyze_weekly_presence(self, top_n: int = 40) -> Dict[str, Dict]:
        """
        Analyze hip-hop presence week by week
        Returns weekly breakdown with counts, percentages, and songs
        """
        weekly_analysis = {}

        for date in self.dates:
            chart = self.data[date]
            top_songs = [s for s in chart if s.get('position', 999) <= top_n]

            hiphop_songs = []
            for song in top_songs:
                artist = song.get('artist')
                if self._is_hiphop(artist):
                    hiphop_songs.append({
                        'position': song.get('position'),
                        'song': song.get('song'),
                        'artist': artist,
                        'weeks_on_chart': song.get('weeks_on_chart')
                    })

            weekly_analysis[date] = {
                'count': len(hiphop_songs),
                'percentage': (len(hiphop_songs) / len(top_songs) * 100) if top_songs else 0,
                'songs': hiphop_songs,
                'total_in_range': len(top_songs)
            }

        return weekly_analysis

    def _is_hiphop(self, artist: str) -> bool:
        """Check if artist is hip-hop/rap"""
        if not artist:
            return False

        genre = self.genre_mapping.get(artist, '').lower()
        return 'hip-hop' in genre or 'rap' in genre or 'hip hop' in genre

    def calculate_yearly_trends(self, weekly_data: Dict) -> Dict:
        """
        Calculate year-by-year statistics
        Shows growth or decline pattern
        """
        yearly_stats = defaultdict(lambda: {
            'weeks': [],
            'counts': [],
            'percentages': [],
            'unique_artists': set(),
            'unique_songs': set(),
            'total_chart_appearances': 0
        })

        for date, data in weekly_data.items():
            year = date[:4]

            yearly_stats[year]['weeks'].append(date)
            yearly_stats[year]['counts'].append(data['count'])
            yearly_stats[year]['percentages'].append(data['percentage'])
            yearly_stats[year]['total_chart_appearances'] += data['count']

            for song in data['songs']:
                yearly_stats[year]['unique_artists'].add(song['artist'])
                yearly_stats[year]['unique_songs'].add((song['song'], song['artist']))

        # Calculate summary metrics
        summary = {}
        for year, stats in yearly_stats.items():
            summary[year] = {
                'avg_count': statistics.mean(stats['counts']) if stats['counts'] else 0,
                'avg_percentage': statistics.mean(stats['percentages']) if stats['percentages'] else 0,
                'max_count': max(stats['counts']) if stats['counts'] else 0,
                'min_count': min(stats['counts']) if stats['counts'] else 0,
                'weeks_with_zero': stats['counts'].count(0),
                'unique_artists': len(stats['unique_artists']),
                'unique_songs': len(stats['unique_songs']),
                'total_appearances': stats['total_chart_appearances'],
                'weeks_analyzed': len(stats['weeks'])
            }

        return summary

    def find_turning_points(self, weekly_data: Dict, window_weeks: int = 12) -> List[Dict]:
        """
        Find significant turning points (peaks and valleys)
        Uses moving average to identify trend changes
        """
        # Calculate moving average
        dates = sorted(weekly_data.keys())
        moving_avg = []

        for i in range(len(dates)):
            start_idx = max(0, i - window_weeks // 2)
            end_idx = min(len(dates), i + window_weeks // 2)

            window = dates[start_idx:end_idx]
            avg = statistics.mean([weekly_data[d]['percentage'] for d in window])
            moving_avg.append((dates[i], avg))

        # Find peaks (local maxima) and valleys (local minima)
        turning_points = []

        for i in range(1, len(moving_avg) - 1):
            prev_avg = moving_avg[i-1][1]
            curr_avg = moving_avg[i][1]
            next_avg = moving_avg[i+1][1]

            # Peak: higher than both neighbors by significant margin
            if curr_avg > prev_avg + 2 and curr_avg > next_avg + 2:
                turning_points.append({
                    'date': moving_avg[i][0],
                    'type': 'peak',
                    'percentage': curr_avg,
                    'count': weekly_data[moving_avg[i][0]]['count'],
                    'insight': f"📈 Peak: {curr_avg:.1f}% hip-hop in top 40 ({moving_avg[i][0]})"
                })

            # Valley: lower than both neighbors
            elif curr_avg < prev_avg - 2 and curr_avg < next_avg - 2:
                turning_points.append({
                    'date': moving_avg[i][0],
                    'type': 'valley',
                    'percentage': curr_avg,
                    'count': weekly_data[moving_avg[i][0]]['count'],
                    'insight': f"📉 Valley: {curr_avg:.1f}% hip-hop in top 40 ({moving_avg[i][0]})"
                })

        return turning_points

    def find_drought_periods(self, weekly_data: Dict) -> List[Dict]:
        """
        Find all weeks with zero hip-hop in top 40
        Calculates "first time since X" for each
        """
        droughts = []
        last_drought_date = None

        for date in sorted(weekly_data.keys()):
            if weekly_data[date]['count'] == 0:
                # Calculate time since last drought
                if last_drought_date:
                    last_date_obj = datetime.strptime(last_drought_date, "%Y-%m-%d")
                    curr_date_obj = datetime.strptime(date, "%Y-%m-%d")
                    weeks_since = (curr_date_obj - last_date_obj).days // 7
                    years = weeks_since / 52
                else:
                    years = None

                droughts.append({
                    'date': date,
                    'formatted_date': self._format_date(date),
                    'years_since_last': round(years, 1) if years else 'First in dataset',
                    'insight': self._generate_drought_insight(date, years)
                })

                last_drought_date = date

        return droughts

    def _generate_drought_insight(self, date: str, years_since: float = None) -> str:
        """Generate social media ready drought insight"""
        formatted = self._format_date(date)

        if years_since and years_since >= 1:
            return (f"🚨 For the first time in {int(years_since)} years, "
                   f"NO hip-hop tracks in Billboard Hot 100 top 40.\n\n"
                   f"Week of {formatted}\n\n"
                   f"#MusicIndustry #HipHop #Billboard")
        else:
            return (f"🚨 NO hip-hop tracks in Billboard Hot 100 top 40.\n\n"
                   f"Week of {formatted}\n\n"
                   f"#MusicIndustry #HipHop #Billboard")

    def compare_year_over_year(self, yearly_stats: Dict) -> List[Dict]:
        """
        Generate year-over-year comparison insights
        Shows growth or decline trends
        """
        years = sorted(yearly_stats.keys())
        comparisons = []

        for i in range(1, len(years)):
            prev_year = years[i-1]
            curr_year = years[i]

            prev = yearly_stats[prev_year]
            curr = yearly_stats[curr_year]

            # Calculate changes
            avg_change = curr['avg_percentage'] - prev['avg_percentage']
            artist_change = curr['unique_artists'] - prev['unique_artists']
            appearance_change = curr['total_appearances'] - prev['total_appearances']

            # Determine trend
            if avg_change > 2:
                trend = "📈 Growing"
            elif avg_change < -2:
                trend = "📉 Declining"
            else:
                trend = "➡️ Stable"

            comparisons.append({
                'period': f"{prev_year} → {curr_year}",
                'trend': trend,
                'avg_percentage_change': round(avg_change, 2),
                'prev_avg': round(prev['avg_percentage'], 1),
                'curr_avg': round(curr['avg_percentage'], 1),
                'unique_artists_change': artist_change,
                'total_appearances_change': appearance_change,
                'insight': f"{trend} Hip-hop representation: {prev['avg_percentage']:.1f}% ({prev_year}) → "
                          f"{curr['avg_percentage']:.1f}% ({curr_year}) - "
                          f"{'+' if avg_change > 0 else ''}{avg_change:.1f}pp change"
            })

        return comparisons

    def generate_executive_summary(self, top_n: int = 40) -> Dict:
        """
        Generate complete analysis summary
        Perfect for LinkedIn posts or reports
        """
        print("Analyzing 5 years of hip-hop trends...")

        weekly_data = self.analyze_weekly_presence(top_n)
        yearly_stats = self.calculate_yearly_trends(weekly_data)
        droughts = self.find_drought_periods(weekly_data)
        turning_points = self.find_turning_points(weekly_data)
        yoy_comparison = self.compare_year_over_year(yearly_stats)

        # Overall metrics
        all_percentages = [w['percentage'] for w in weekly_data.values()]
        overall_avg = statistics.mean(all_percentages) if all_percentages else 0

        return {
            'period': f"{self.dates[0]} to {self.dates[-1]}",
            'weeks_analyzed': len(weekly_data),
            'overall_avg_percentage': round(overall_avg, 2),
            'yearly_breakdown': yearly_stats,
            'year_over_year': yoy_comparison,
            'drought_weeks': droughts,
            'turning_points': turning_points,
            'key_findings': self._generate_key_findings(yearly_stats, droughts, yoy_comparison)
        }

    def _generate_key_findings(self, yearly_stats: Dict, droughts: List, yoy_comp: List) -> List[str]:
        """Extract the most important insights"""
        findings = []

        # Overall trend
        years = sorted(yearly_stats.keys())
        if len(years) >= 2:
            first_year_avg = yearly_stats[years[0]]['avg_percentage']
            last_year_avg = yearly_stats[years[-1]]['avg_percentage']
            total_change = last_year_avg - first_year_avg

            if total_change < -5:
                findings.append(f"Sharp decline: Hip-hop representation dropped {abs(total_change):.1f}pp from {years[0]} to {years[-1]}")
            elif total_change > 5:
                findings.append(f"Strong growth: Hip-hop representation increased {total_change:.1f}pp from {years[0]} to {years[-1]}")

        # Drought analysis
        if droughts:
            findings.append(f"Found {len(droughts)} weeks with zero hip-hop in top 40")

        # Peak year
        peak_year = max(yearly_stats.items(), key=lambda x: x[1]['avg_percentage'])
        findings.append(f"Peak year: {peak_year[0]} ({peak_year[1]['avg_percentage']:.1f}% average)")

        # Lowest year
        lowest_year = min(yearly_stats.items(), key=lambda x: x[1]['avg_percentage'])
        findings.append(f"Lowest year: {lowest_year[0]} ({lowest_year[1]['avg_percentage']:.1f}% average)")

        return findings

    def _format_date(self, date_str: str) -> str:
        """Format date as 'October 30, 2024'"""
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")

    def export_for_visualization(self, weekly_data: Dict, output_file: str = "hiphop_trends_data.json"):
        """Export data in format ready for charts/graphs"""
        export_data = []

        for date, data in sorted(weekly_data.items()):
            export_data.append({
                'date': date,
                'percentage': round(data['percentage'], 2),
                'count': data['count'],
                'year': date[:4],
                'month': date[5:7]
            })

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"✓ Visualization data exported to: {output_file}")
        return export_data


# Comprehensive hip-hop/rap artist mapping
HIPHOP_ARTISTS = {
    # Major hip-hop artists (2020-2025)
    "Drake": "Hip-Hop",
    "21 Savage": "Hip-Hop",
    "Travis Scott": "Hip-Hop",
    "Lil Baby": "Hip-Hop",
    "Lil Durk": "Hip-Hop",
    "Lil Uzi Vert": "Hip-Hop",
    "Future": "Hip-Hop",
    "Gunna": "Hip-Hop",
    "Young Thug": "Hip-Hop",
    "Rod Wave": "Hip-Hop",
    "NBA YoungBoy": "Hip-Hop",
    "Polo G": "Hip-Hop",
    "Pop Smoke": "Hip-Hop",
    "Juice WRLD": "Hip-Hop",
    "Lil Tjay": "Hip-Hop",
    "A Boogie Wit da Hoodie": "Hip-Hop",
    "Roddy Ricch": "Hip-Hop",
    "DaBaby": "Hip-Hop",
    "Megan Thee Stallion": "Hip-Hop",
    "Cardi B": "Hip-Hop",
    "Nicki Minaj": "Hip-Hop",
    "Saweetie": "Hip-Hop",
    "Doja Cat": "Hip-Hop/Pop",  # Crossover
    "Jack Harlow": "Hip-Hop",
    "Lil Nas X": "Hip-Hop/Pop",
    "Tyler, The Creator": "Hip-Hop",
    "Kendrick Lamar": "Hip-Hop",
    "J. Cole": "Hip-Hop",
    "Big Sean": "Hip-Hop",
    "2 Chainz": "Hip-Hop",
    "Kodak Black": "Hip-Hop",
    "YoungBoy Never Broke Again": "Hip-Hop",
    "Moneybagg Yo": "Hip-Hop",
    "EST Gee": "Hip-Hop",
    "42 Dugg": "Hip-Hop",
    "Pooh Shiesty": "Hip-Hop",
    "Fivio Foreign": "Hip-Hop",
    "Lil Tecca": "Hip-Hop",
    "Trippie Redd": "Hip-Hop",
    "Playboi Carti": "Hip-Hop",
    "Yeat": "Hip-Hop",
    "Central Cee": "Hip-Hop",
    "GloRilla": "Hip-Hop",
    "Ice Spice": "Hip-Hop",
    "Sexyy Red": "Hip-Hop",
    "Metro Boomin": "Hip-Hop",  # Producer but charts as artist
    "DJ Khaled": "Hip-Hop",
    "Kanye West": "Hip-Hop",
    "Ye": "Hip-Hop",  # Kanye's new name
    "Eminem": "Hip-Hop",
    "50 Cent": "Hip-Hop",
    "Snoop Dogg": "Hip-Hop",
    "Wiz Khalifa": "Hip-Hop",
    "Ty Dolla $ign": "Hip-Hop/R&B",
    "Chris Brown": "R&B/Hip-Hop",
    "SZA": "R&B/Hip-Hop",
    "Summer Walker": "R&B/Hip-Hop",
    "Bryson Tiller": "R&B/Hip-Hop",
    "6LACK": "R&B/Hip-Hop",
    "Brent Faiyaz": "R&B/Hip-Hop",
    "The Weeknd": "R&B/Pop",  # More R&B/Pop but influenced
    "Post Malone": "Hip-Hop/Pop",  # Crossover
    "Machine Gun Kelly": "Hip-Hop/Rock",
    "Swae Lee": "Hip-Hop",
    "Offset": "Hip-Hop",
    "Quavo": "Hip-Hop",
    "Takeoff": "Hip-Hop",
    "Migos": "Hip-Hop",
    "Mustard": "Hip-Hop",  # Producer
    "Mike WiLL Made-It": "Hip-Hop",  # Producer
    "Southside": "Hip-Hop",
    "Rae Sremmurd": "Hip-Hop",
    "A$AP Rocky": "Hip-Hop",
    "A$AP Ferg": "Hip-Hop",
    "Lil Wayne": "Hip-Hop",
    "Rick Ross": "Hip-Hop",
    "Gucci Mane": "Hip-Hop",
    "Meek Mill": "Hip-Hop",
    "French Montana": "Hip-Hop",
    "Tory Lanez": "Hip-Hop/R&B",
    "Don Toliver": "Hip-Hop",
    "Sheck Wes": "Hip-Hop",
    "Ski Mask The Slump God": "Hip-Hop",
    "XXXTentacion": "Hip-Hop",
    "Lil Pump": "Hip-Hop",
    "Smokepurpp": "Hip-Hop",
    "6ix9ine": "Hip-Hop",
    "Tekashi 6ix9ine": "Hip-Hop",
    "Blueface": "Hip-Hop",
    "YG": "Hip-Hop",
    "Tyga": "Hip-Hop",
    "Joyner Lucas": "Hip-Hop",
    "Logic": "Hip-Hop",
    "NLE Choppa": "Hip-Hop",
    "JID": "Hip-Hop",
    "Denzel Curry": "Hip-Hop",
    "Cordae": "Hip-Hop",
    "Baby Keem": "Hip-Hop",
    "Vince Staples": "Hip-Hop",
    "Ski Mask": "Hip-Hop",
    "Key Glock": "Hip-Hop",
    "Dolph": "Hip-Hop",
    "Young Dolph": "Hip-Hop",
}


def demo():
    """Run comprehensive hip-hop trend analysis"""
    print("=" * 70)
    print("HIP-HOP TREND ANALYSIS (Last 5 Years)")
    print("=" * 70)
    print()

    # Load Billboard data
    try:
        with open('billboard_5years.json', 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded {len(data)} weeks of Billboard data")
    except FileNotFoundError:
        print("❌ Data file not found! Run billboard_downloader.py first.")
        return

    print()

    # Initialize analyzer
    analyzer = HipHopTrendAnalyzer(data, HIPHOP_ARTISTS)

    # Generate full analysis
    print("Generating comprehensive analysis...")
    print()
    summary = analyzer.generate_executive_summary(top_n=40)

    # Display results
    print("=" * 70)
    print("EXECUTIVE SUMMARY")
    print("=" * 70)
    print(f"Period: {summary['period']}")
    print(f"Weeks Analyzed: {summary['weeks_analyzed']}")
    print(f"Overall Average Hip-Hop Representation: {summary['overall_avg_percentage']}%")
    print()

    print("KEY FINDINGS:")
    print("-" * 70)
    for finding in summary['key_findings']:
        print(f"• {finding}")
    print()

    print("=" * 70)
    print("YEAR-BY-YEAR BREAKDOWN")
    print("=" * 70)
    for year, stats in sorted(summary['yearly_breakdown'].items()):
        print(f"\n{year}:")
        print(f"  Average: {stats['avg_percentage']:.1f}% of top 40")
        print(f"  Range: {stats['min_count']}-{stats['max_count']} songs per week")
        print(f"  Unique Artists: {stats['unique_artists']}")
        print(f"  Unique Songs: {stats['unique_songs']}")
        print(f"  Total Chart Appearances: {stats['total_appearances']}")
        print(f"  Weeks with Zero Hip-Hop: {stats['weeks_with_zero']}")

    print()
    print("=" * 70)
    print("YEAR-OVER-YEAR TRENDS")
    print("=" * 70)
    for comp in summary['year_over_year']:
        print(f"\n{comp['period']}")
        print(f"  {comp['trend']}")
        print(f"  {comp['prev_avg']}% → {comp['curr_avg']}% "
              f"({'+' if comp['avg_percentage_change'] > 0 else ''}{comp['avg_percentage_change']}pp)")
        print(f"  Unique Artists: {'+' if comp['unique_artists_change'] >= 0 else ''}{comp['unique_artists_change']}")

    print()
    print("=" * 70)
    print("🚨 DROUGHT PERIODS (Zero Hip-Hop in Top 40)")
    print("=" * 70)
    if summary['drought_weeks']:
        print(f"Found {len(summary['drought_weeks'])} drought weeks:\n")
        for drought in summary['drought_weeks']:
            print(f"📅 {drought['formatted_date']}")
            print(f"   Years since last: {drought['years_since_last']}")
            print()
    else:
        print("No drought periods found in this timeframe")

    print()

    # Export for visualization
    weekly_data = analyzer.analyze_weekly_presence(40)
    analyzer.export_for_visualization(weekly_data)

    # Save full report
    with open('hiphop_analysis_report.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print()
    print("=" * 70)
    print("✓ Analysis complete!")
    print("  • Full report: hiphop_analysis_report.json")
    print("  • Visualization data: hiphop_trends_data.json")
    print("=" * 70)


if __name__ == "__main__":
    demo()
