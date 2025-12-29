#!/usr/bin/env python3
"""
Fetch YouTube data for current Billboard Top 40
"""

import json
from youtube_data_fetcher import YouTubeDataFetcher

def main():
    print("="*70)
    print("FETCHING YOUTUBE DATA FOR BILLBOARD TOP 40")
    print("="*70)
    print()

    # Get YouTube API key from user
    api_key = input("Enter your YouTube API key: ").strip()

    if not api_key:
        print("❌ YouTube API key required")
        return

    # Initialize fetcher
    fetcher = YouTubeDataFetcher(api_key)

    # Load Billboard data
    print("\nLoading Billboard data...")
    with open('billboard_67years.json', 'r') as f:
        data = json.load(f)

    # Get most recent week
    recent_date = max(data.keys())
    print(f"Most recent chart date: {recent_date}")

    # Get Top 40 from most recent week
    chart = data[recent_date]
    top_40 = [song for song in chart if song.get('position', 999) <= 40]

    print(f"Found {len(top_40)} songs in Top 40")
    print()

    # Prepare songs list
    songs = []
    for song in top_40:
        artist = song.get('artist', '')
        title = song.get('song', '')  # Billboard data uses 'song' not 'title'
        position = song.get('position', 0)

        if artist and title:
            songs.append((artist, title, position))

    print(f"Processing {len(songs)} songs...")
    print(f"Estimated quota: {len(songs)} × 101 = {len(songs) * 101:,} units")
    print()

    # Process songs
    results = {
        'processed': 0,
        'found': 0,
        'not_found': 0,
        'songs': []
    }

    for artist, title, position in songs:
        print(f"\n#{position:2d}. {artist} - {title}")

        # Get YouTube data
        data = fetcher.get_song_data(artist, title)

        results['processed'] += 1

        if data:
            results['found'] += 1
            results['songs'].append({
                'position': position,
                'artist': artist,
                'title': title,
                'youtube_data': data
            })

            # Show stats
            views = data['view_count']
            likes = data['like_count']
            print(f"     Views: {views:,}")
            print(f"     Likes: {likes:,}")
            print(f"     URL: {data['video_url']}")
        else:
            results['not_found'] += 1
            print(f"     ✗ No YouTube video found")

        # Show quota status
        quota = fetcher.get_quota_status()
        print(f"     Quota: {quota['quota_used']:,} / 10,000 ({quota['percentage_used']:.1f}%)")

        # Stop if approaching limit
        if quota['quota_remaining'] < 200:
            print("\n⚠️  Approaching quota limit, stopping early")
            break

    # Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Processed: {results['processed']} songs")
    print(f"Found: {results['found']} videos")
    print(f"Not found: {results['not_found']} videos")
    print(f"Success rate: {(results['found']/results['processed']*100):.1f}%")
    print()

    quota = fetcher.get_quota_status()
    print(f"Quota used: {quota['quota_used']:,} / 10,000")
    print(f"Quota remaining: {quota['quota_remaining']:,}")
    print()

    # Save results
    output_file = 'youtube_top40_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to: {output_file}")
    print(f"✓ YouTube cache saved to: youtube_cache.json")
    print()

    # Show top 5 by views
    if results['songs']:
        print("="*70)
        print("TOP 5 BY YOUTUBE VIEWS")
        print("="*70)

        sorted_songs = sorted(
            results['songs'],
            key=lambda x: x['youtube_data']['view_count'],
            reverse=True
        )

        for i, song in enumerate(sorted_songs[:5], 1):
            yt = song['youtube_data']
            print(f"{i}. {song['artist']} - {song['title']}")
            print(f"   Views: {yt['view_count']:,}")
            print(f"   Chart Position: #{song['position']}")
            print()

if __name__ == "__main__":
    main()
