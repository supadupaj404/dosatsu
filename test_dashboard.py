#!/usr/bin/env python3
"""
Quick test to validate the Streamlit dashboard can load data correctly
"""

import json
from pathlib import Path

print("="*70)
print("TESTING DŌSATSU DASHBOARD")
print("="*70)
print()

# Test 1: Check required files exist
print("Test 1: Checking required files...")
required_files = [
    'billboard_67years.json',
    'hybrid_genre_cache.json',
    'streamlit_app.py',
    'requirements.txt'
]

all_files_exist = True
for file in required_files:
    exists = Path(file).exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {file}")
    if not exists:
        all_files_exist = False

if all_files_exist:
    print("✓ All required files present")
else:
    print("✗ Some files missing!")
    exit(1)

print()

# Test 2: Load and validate Billboard data
print("Test 2: Loading Billboard data...")
try:
    with open('billboard_67years.json', 'r') as f:
        billboard_data = json.load(f)

    total_weeks = len(billboard_data)

    # Get all unique artists
    all_artists = set()
    for date, chart in billboard_data.items():
        for song in chart:
            artist = song.get('artist')
            if artist:
                all_artists.add(artist)

    print(f"  ✓ Loaded {total_weeks:,} weeks of data")
    print(f"  ✓ Found {len(all_artists):,} unique artists")
except Exception as e:
    print(f"  ✗ Error loading Billboard data: {e}")
    exit(1)

print()

# Test 3: Load and validate genre cache
print("Test 3: Loading genre cache...")
try:
    with open('hybrid_genre_cache.json', 'r') as f:
        genre_cache = json.load(f)

    classified = sum(1 for v in genre_cache.values() if v is not None)
    coverage = (classified / len(all_artists) * 100) if len(all_artists) > 0 else 0

    print(f"  ✓ Loaded {len(genre_cache):,} cached artists")
    print(f"  ✓ {classified:,} successfully classified")
    print(f"  ✓ Coverage: {coverage:.1f}%")
except Exception as e:
    print(f"  ✗ Error loading genre cache: {e}")
    exit(1)

print()

# Test 4: Validate data structure
print("Test 4: Validating data structure...")
try:
    # Get most recent chart
    most_recent = max(billboard_data.keys())
    recent_chart = billboard_data[most_recent]

    print(f"  ✓ Most recent chart: {most_recent}")
    print(f"  ✓ Songs in chart: {len(recent_chart)}")

    # Check song structure
    if recent_chart:
        sample_song = recent_chart[0]
        required_keys = ['song', 'artist', 'position']
        has_all_keys = all(key in sample_song for key in required_keys)

        if has_all_keys:
            print(f"  ✓ Song structure valid")
            print(f"    Example: #{sample_song['position']} - {sample_song['song']} by {sample_song['artist']}")
        else:
            print(f"  ✗ Song structure invalid - keys found: {list(sample_song.keys())}")
            exit(1)
except Exception as e:
    print(f"  ✗ Error validating data: {e}")
    exit(1)

print()

# Test 5: Syntax check Streamlit app
print("Test 5: Checking Streamlit app syntax...")
try:
    import py_compile
    py_compile.compile('streamlit_app.py', doraise=True)
    print(f"  ✓ streamlit_app.py has valid Python syntax")
except Exception as e:
    print(f"  ✗ Syntax error in streamlit_app.py: {e}")
    exit(1)

print()
print("="*70)
print("✅ ALL TESTS PASSED!")
print("="*70)
print()
print("Dashboard is ready to run. To start it:")
print("  streamlit run streamlit_app.py")
print()
print("It will automatically open in your browser at http://localhost:8501")
print()
