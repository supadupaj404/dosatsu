# Spotify API Setup Guide

## Step 1: Create Spotify Developer Account
1. Go to https://developer.spotify.com/dashboard
2. Click "Log In" (use your Spotify account or create one)
3. Accept the Spotify Developer Terms of Service

## Step 2: Create New App
1. Click "Create App" button
2. Fill in required information:
   - **App Name**: "BEAM Metadata Validator" (or similar)
   - **App Description**: "Testing music metadata accuracy for industry validation"
   - **Website**: Optional (you can use https://whetstoneent.com)
   - **Redirect URIs**: http://localhost:3000 (for testing)
   - **Which API/SDKs are you planning to use?**: Check "Web API"
   - **Commercial or Non-Commercial**: Select "Non-Commercial" for testing

## Step 3: Get Your Credentials
After creating the app:
1. Click on your new app in the dashboard
2. Go to "Settings" 
3. You'll see:
   - **Client ID**: Copy this (public, safe to use)
   - **Client Secret**: Click "View client secret" and copy (keep private!)

## Step 4: Update Your Script
Replace the placeholder values in spotify_test.py:

```python
# Replace these lines:
self.client_id = "your_client_id_here"
self.client_secret = "your_client_secret_here"

# With your actual credentials:
self.client_id = "your_actual_client_id"
self.client_secret = "your_actual_client_secret"
```

## Step 5: Test the Connection
Run the updated script:
```bash
python3 spotify_test.py
```

## What We'll Test
- Search for BEAM (Tyshane Thompson)
- Compare results vs MusicBrainz (which failed)
- Analyze Spotify's metadata completeness
- Document gaps vs your Epic Records/Warner Chappell access

## Expected Results
Since web search confirmed BEAM has 437K+ monthly listeners on Spotify, we should find him successfully, unlike MusicBrainz.

## Security Notes
- Never commit Client Secret to version control
- Client ID is public and safe to share
- Client Secret should be kept private

Ready to get your Spotify credentials?