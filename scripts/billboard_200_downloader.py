#!/usr/bin/env python3
"""
Billboard 200 Album Chart Data Downloader for Dōsatsu
Downloads and combines Billboard 200 chart data from multiple sources
"""

import pandas as pd
import json
import billboard
from datetime import datetime, timedelta
from typing import Dict, List
import time
import os

class Billboard200Downloader:
    """Download and process Billboard 200 album chart data"""

    def __init__(self):
        self.historical_csv = "billboard_200_historical.csv"
        self.output_json = "billboard_200_all_time.json"

    def load_historical_data(self) -> pd.DataFrame:
        """Load historical Billboard 200 data from CSV (1967-2020)"""
        print("Loading historical Billboard 200 data (1967-2020)...")

        if not os.path.exists(self.historical_csv):
            print(f"Error: {self.historical_csv} not found!")
            print("Please download it first with:")
            print('curl -o billboard_200_historical.csv "https://raw.githubusercontent.com/utdata/rwd-billboard-data/main/data-out/billboard-200-current.csv"')
            return pd.DataFrame()

        df = pd.read_csv(self.historical_csv)

        # Rename columns to match our format
        df = df.rename(columns={
            'chart_week': 'date',
            'current_week': 'position',
            'title': 'album',
            'performer': 'artist',
            'last_week': 'last_week',
            'peak_pos': 'peak_position',
            'wks_on_chart': 'weeks_on_chart'
        })

        print(f"✓ Loaded {len(df)} records from {df['date'].min()} to {df['date'].max()}")
        return df

    def scrape_recent_charts(self, start_date: str = "2021-01-09") -> List[Dict]:
        """Scrape Billboard 200 charts from start_date to present"""
        print(f"\nScraping recent Billboard 200 charts from {start_date} to present...")
        print("(This may take several minutes due to rate limiting)")

        all_records = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.now()

        weeks_to_scrape = ((end_date - current_date).days // 7) + 1
        print(f"Estimated {weeks_to_scrape} weeks to scrape...\n")

        week_count = 0
        failed_dates = []

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            week_count += 1

            try:
                # Fetch Billboard 200 chart for this date
                chart = billboard.ChartData('billboard-200', date=date_str)

                # Extract data
                for entry in chart:
                    all_records.append({
                        'date': date_str,
                        'position': entry.rank,
                        'album': entry.title,
                        'artist': entry.artist,
                        'last_week': entry.lastPos if entry.lastPos else 0,
                        'peak_position': entry.peakPos if entry.peakPos else entry.rank,
                        'weeks_on_chart': entry.weeks if entry.weeks else 1
                    })

                if week_count % 10 == 0:
                    print(f"Progress: {week_count}/{weeks_to_scrape} weeks ({week_count/weeks_to_scrape*100:.1f}%)")

                # Rate limiting - be respectful
                time.sleep(2)

            except Exception as e:
                print(f"Warning: Failed to fetch chart for {date_str}: {e}")
                failed_dates.append(date_str)

            # Move to next week
            current_date += timedelta(days=7)

        print(f"\n✓ Scraped {len(all_records)} records from {week_count} weeks")
        if failed_dates:
            print(f"⚠ Failed to fetch {len(failed_dates)} weeks: {failed_dates[:5]}...")

        return all_records

    def convert_to_json_format(self, df: pd.DataFrame, recent_records: List[Dict] = None) -> Dict:
        """Convert DataFrame and recent records to JSON format matching Hot 100 structure"""
        print("\nConverting to JSON format...")

        # Combine historical and recent data
        if recent_records:
            recent_df = pd.DataFrame(recent_records)
            df = pd.concat([df, recent_df], ignore_index=True)

        # Group by date
        data_by_date = {}

        for date, group in df.groupby('date'):
            # Sort by position
            group = group.sort_values('position')

            # Convert to list of dicts
            chart_data = []
            for _, row in group.iterrows():
                chart_data.append({
                    'position': int(row['position']),
                    'album': str(row['album']),
                    'artist': str(row['artist']),
                    'last_week': int(row['last_week']) if pd.notna(row['last_week']) else 0,
                    'peak_position': int(row['peak_position']) if pd.notna(row['peak_position']) else int(row['position']),
                    'weeks_on_chart': int(row['weeks_on_chart']) if pd.notna(row['weeks_on_chart']) else 1
                })

            data_by_date[date] = chart_data

        print(f"✓ Converted {len(data_by_date)} weeks of chart data")
        return data_by_date

    def save_json(self, data: Dict, output_file: str = None):
        """Save data to JSON file"""
        if output_file is None:
            output_file = self.output_json

        print(f"\nSaving to {output_file}...")

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Get file size
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ Saved {len(data)} weeks to {output_file} ({file_size_mb:.1f} MB)")

    def download_all_charts(self, scrape_recent: bool = True):
        """Complete pipeline: download historical + scrape recent + combine + save"""
        print("=" * 60)
        print("BILLBOARD 200 ALBUM CHART DATA DOWNLOADER")
        print("=" * 60)
        print()

        # Step 1: Load historical data
        historical_df = self.load_historical_data()

        if historical_df.empty:
            print("Error: Could not load historical data. Exiting.")
            return

        # Step 2: Scrape recent data (optional)
        recent_records = None
        if scrape_recent:
            recent_records = self.scrape_recent_charts(start_date="2021-01-09")
        else:
            print("\nSkipping recent data scraping (use scrape_recent=True to enable)")

        # Step 3: Convert to JSON format
        json_data = self.convert_to_json_format(historical_df, recent_records)

        # Step 4: Save
        self.save_json(json_data)

        # Summary
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        dates = sorted(json_data.keys())
        print(f"Date Range: {dates[0]} to {dates[-1]}")
        print(f"Total Weeks: {len(dates)}")
        print(f"Total Records: {sum(len(chart) for chart in json_data.values())}")

        # Count unique artists
        unique_artists = set()
        for chart in json_data.values():
            for entry in chart:
                unique_artists.add(entry['artist'])
        print(f"Unique Artists: {len(unique_artists)}")
        print()
        print("✓ Billboard 200 data ready for Dōsatsu!")
        print("=" * 60)

    def download_historical_only(self):
        """Quick download: historical data only (1967-2020)"""
        print("Downloading historical Billboard 200 data only (1967-2020)...")
        historical_df = self.load_historical_data()

        if not historical_df.empty:
            json_data = self.convert_to_json_format(historical_df)
            self.save_json(json_data, "billboard_200_1967_2020.json")


def main():
    """Main execution"""
    downloader = Billboard200Downloader()

    # Download everything (historical + recent)
    # This will take 10-15 minutes due to rate limiting
    downloader.download_all_charts(scrape_recent=True)

    # Or for quick testing, just download historical data:
    # downloader.download_historical_only()


if __name__ == "__main__":
    main()
