#!/usr/bin/env python3
"""
MusicBrainz API Test Script
Test script to pull artist and release data from MusicBrainz
"""

import requests
import json
import time
from typing import Dict, List, Optional

class MusicBrainzAPI:
    def __init__(self, app_name: str = "RoyaltyGapDetector", version: str = "1.0", contact: str = "test@example.com"):
        """Initialize with proper user agent (required by MusicBrainz)"""
        self.base_url = "https://musicbrainz.org/ws/2"
        self.headers = {
            'User-Agent': f'{app_name}/{version} ({contact})'
        }
        
    def search_artist(self, artist_name: str) -> Optional[Dict]:
        """Search for artist by name"""
        url = f"{self.base_url}/artist"
        params = {
            'query': f'artist:"{artist_name}"',
            'fmt': 'json',
            'limit': 10
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['artists']:
                return data['artists'][0]  # Return most relevant match
            return None
            
        except requests.RequestException as e:
            print(f"Error searching for artist: {e}")
            return None
    
    def get_artist_releases(self, artist_mbid: str) -> List[Dict]:
        """Get all releases for an artist"""
        url = f"{self.base_url}/release"
        params = {
            'artist': artist_mbid,
            'fmt': 'json',
            'limit': 100,
            'inc': 'labels+recordings+artist-credits'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('releases', [])
            
        except requests.RequestException as e:
            print(f"Error getting releases: {e}")
            return []
    
    def get_recording_details(self, recording_mbid: str) -> Optional[Dict]:
        """Get detailed info about a specific recording"""
        url = f"{self.base_url}/recording/{recording_mbid}"
        params = {
            'fmt': 'json',
            'inc': 'artist-credits+releases+work-rels+artist-rels'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            print(f"Error getting recording details: {e}")
            return None

def analyze_artist_data(artist_name: str) -> Dict:
    """Comprehensive analysis of an artist's data in MusicBrainz"""
    mb = MusicBrainzAPI()
    
    print(f"Analyzing {artist_name} in MusicBrainz...")
    
    # Search for artist
    artist = mb.search_artist(artist_name)
    if not artist:
        return {"error": f"Artist '{artist_name}' not found"}
    
    artist_mbid = artist['id']
    print(f"Found artist: {artist['name']} (MBID: {artist_mbid})")
    
    # Get releases
    releases = mb.get_artist_releases(artist_mbid)
    print(f"Found {len(releases)} releases")
    
    # Analyze data completeness
    analysis = {
        "artist_name": artist['name'],
        "artist_mbid": artist_mbid,
        "total_releases": len(releases),
        "release_types": {},
        "labels": set(),
        "missing_data": {
            "releases_without_label": 0,
            "releases_without_date": 0,
            "songs_without_writers": 0
        }
    }
    
    for release in releases[:20]:  # Analyze first 20 releases
        # Count release types
        release_type = release.get('primary-type', 'Unknown')
        analysis["release_types"][release_type] = analysis["release_types"].get(release_type, 0) + 1
        
        # Track labels
        if 'label-info' in release:
            for label_info in release['label-info']:
                if label_info.get('label'):
                    analysis["labels"].add(label_info['label']['name'])
        else:
            analysis["missing_data"]["releases_without_label"] += 1
            
        # Check for missing dates
        if not release.get('date'):
            analysis["missing_data"]["releases_without_date"] += 1
    
    analysis["labels"] = list(analysis["labels"])
    return analysis

# Test function
def run_test(artist_name: str):
    """Run comprehensive test for a specific artist"""
    print("=" * 50)
    print("MUSICBRAINZ API TEST")
    print("=" * 50)
    
    results = analyze_artist_data(artist_name)
    
    print(f"\nRESULTS FOR: {artist_name}")
    print("-" * 30)
    print(json.dumps(results, indent=2))
    
    return results

if __name__ == "__main__":
    # BEAM - Tyshane Thompson
    test_artist = "BEAM"
    
    print("MusicBrainz API Test Script")
    print("Testing with BEAM (Tyshane Thompson)")
    print("This will help us understand what data is publicly available vs your ground truth")
    print()
    
    # Test multiple variations
    test_variations = ["BEAM", "Beam (US)", "BEAM rapper", "Tyshane Thompson"]
    
    for variation in test_variations:
        print(f"\nTesting: {variation}")
        print("="*50)
        run_test(variation)