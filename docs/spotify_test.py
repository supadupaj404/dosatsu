#!/usr/bin/env python3
"""
Spotify API Test Script
Test script to pull artist and track data from Spotify
Note: This uses client credentials flow (no user auth required)
"""

import requests
import json
import base64
from typing import Dict, List, Optional

class SpotifyAPI:
    def __init__(self):
        """Initialize Spotify API client"""
        self.base_url = "https://api.spotify.com/v1"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.access_token = None
        
        # Spotify API credentials
        self.client_id = "aa1081b8022840b88335f1c699cf1230"
        self.client_secret = "144f9a11593043ccb85ceed2e3fb5a39"
        
    def get_access_token(self) -> bool:
        """Get access token using client credentials flow"""
        if not self.client_id or self.client_id == "your_client_id_here":
            print("ERROR: Spotify Client ID not configured")
            print("To use Spotify API:")
            print("1. Go to https://developer.spotify.com/dashboard")
            print("2. Create an app")
            print("3. Copy Client ID and Client Secret")
            print("4. Update this script with your credentials")
            return False
            
        # Encode credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"grant_type": "client_credentials"}
        
        try:
            response = requests.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            return True
            
        except requests.RequestException as e:
            print(f"Error getting access token: {e}")
            return False
    
    def search_artist(self, artist_name: str) -> Optional[Dict]:
        """Search for artist by name"""
        if not self.access_token:
            if not self.get_access_token():
                return None
                
        url = f"{self.base_url}/search"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "q": artist_name,
            "type": "artist",
            "limit": 10
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["artists"]["items"]:
                return data["artists"]["items"][0]  # Return most relevant match
            return None
            
        except requests.RequestException as e:
            print(f"Error searching for artist: {e}")
            return None
    
    def get_artist_albums(self, artist_id: str) -> List[Dict]:
        """Get all albums for an artist"""
        if not self.access_token:
            return []
            
        url = f"{self.base_url}/artists/{artist_id}/albums"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "include_groups": "album,single,compilation",
            "market": "US",
            "limit": 50
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
            
        except requests.RequestException as e:
            print(f"Error getting albums: {e}")
            return []
    
    def get_album_tracks(self, album_id: str) -> List[Dict]:
        """Get all tracks from an album"""
        if not self.access_token:
            return []
            
        url = f"{self.base_url}/albums/{album_id}/tracks"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
            
        except requests.RequestException as e:
            print(f"Error getting tracks: {e}")
            return []

def analyze_spotify_data(artist_name: str) -> Dict:
    """Comprehensive analysis of an artist's data in Spotify"""
    spotify = SpotifyAPI()
    
    print(f"Analyzing {artist_name} in Spotify...")
    
    # Search for artist
    artist = spotify.search_artist(artist_name)
    if not artist:
        return {"error": f"Artist '{artist_name}' not found"}
    
    artist_id = artist["id"]
    print(f"Found artist: {artist['name']} (Spotify ID: {artist_id})")
    print(f"Followers: {artist['followers']['total']:,}")
    print(f"Popularity: {artist['popularity']}/100")
    
    # Get albums
    albums = spotify.get_artist_albums(artist_id)
    print(f"Found {len(albums)} releases")
    
    # Analyze data completeness
    analysis = {
        "artist_name": artist["name"],
        "artist_id": artist_id,
        "followers": artist["followers"]["total"],
        "popularity": artist["popularity"],
        "genres": artist.get("genres", []),
        "total_albums": len(albums),
        "album_types": {},
        "labels": set(),
        "missing_data": {
            "albums_without_date": 0,
            "albums_without_type": 0
        }
    }
    
    for album in albums[:20]:  # Analyze first 20 albums
        # Count album types
        album_type = album.get("album_type", "Unknown")
        analysis["album_types"][album_type] = analysis["album_types"].get(album_type, 0) + 1
        
        # Check for missing dates
        if not album.get("release_date"):
            analysis["missing_data"]["albums_without_date"] += 1
            
        # Track labels (not available in basic album data)
        if "label" in album:
            analysis["labels"].add(album["label"])
    
    analysis["labels"] = list(analysis["labels"])
    return analysis

def run_spotify_test(artist_name: str):
    """Run comprehensive Spotify test for a specific artist"""
    print("=" * 50)
    print("SPOTIFY API TEST")
    print("=" * 50)
    
    results = analyze_spotify_data(artist_name)
    
    print(f"\nRESULTS FOR: {artist_name}")
    print("-" * 30)
    print(json.dumps(results, indent=2))
    
    return results

if __name__ == "__main__":
    print("Spotify API Test Script")
    print("Testing with BEAM (Tyshane Thompson)")
    print("This will compare Spotify data vs MusicBrainz vs your ground truth")
    print()
    
    # Test multiple variations
    test_variations = ["BEAM", "BEAM rapper", "Tyshane Thompson"]
    
    for variation in test_variations:
        print(f"\nTesting: {variation}")
        print("="*50)
        run_spotify_test(variation)