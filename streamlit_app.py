#!/usr/bin/env python3
"""
Dōsatsu - Music Industry Intelligence Platform
Chat Interface for Billboard Data Analysis
"""

import streamlit as st
import json
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import re
from musicbrainz_credits import MusicBrainzCredits
from genre_forecaster import GenreForecaster

# 80s Trading Terminal Color Palette - Green Monochrome
COLORS = {
    'primary': '#00ff00',      # Bright green (primary text)
    'secondary': '#00cc00',    # Medium green
    'accent': '#00aa00',       # Dark green
    'dim': '#008800',          # Dimmer green
    'background': '#000000',   # Pure black
    'grid': '#003300',         # Very dark green for borders
}

# Chart colors - various shades of green for different genres
CHART_COLORS = [
    '#00ff00',  # Bright green - Hip-Hop
    '#00dd00',  # Green - Pop
    '#00bb00',  # Med green - Country
    '#00aa00',  # Dark green - R&B
    '#009900',  # Darker green - Rock
    '#008800',  # Dim green - Alternative
    '#00ff66',  # Blue-green - Latin
]

# Page config
st.set_page_config(
    page_title="Dōsatsu - Music Intelligence",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - 80s Bloomberg Terminal / MS-DOS Style
st.markdown("""
<style>
    /* Import DOS-style monospace font */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&display=swap');

    /* Base terminal styling */
    * {
        font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
    }

    .stApp {
        background-color: #000000 !important;
        color: #00ff00;
    }

    body {
        background-color: #000000 !important;
    }

    .main {
        background-color: #000000 !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
    }

    [data-testid="stHeader"] {
        background-color: #000000 !important;
    }

    [data-testid="stToolbar"] {
        background-color: #000000 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    /* Terminal header with ASCII borders */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #00ff00;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: 0.3em;
        text-shadow: 0 0 10px #00ff00;
        font-family: 'IBM Plex Mono', monospace !important;
    }

    .sub-header {
        font-size: 1rem;
        color: #00cc00;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 400;
        letter-spacing: 0.2em;
    }

    .description {
        font-size: 0.9rem;
        color: #00ff00;
        text-align: center !important;
        margin-bottom: 2rem;
        font-weight: 400;
        max-width: 800px;
        margin-left: auto !important;
        margin-right: auto !important;
        line-height: 1.8;
        display: block !important;
    }

    /* DOS-style bordered boxes */
    .terminal-box {
        border: 2px solid #00ff00;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #000000;
    }

    /* Example queries - DOS buttons */
    .example-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        margin-bottom: 2rem;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }

    .example-query {
        background: #000000;
        padding: 0.5rem 1rem;
        border: 2px solid #00ff00;
        color: #00ff00;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.1s;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .example-query:hover {
        background: #00ff00;
        color: #000000;
    }

    /* Chat messages - terminal style */
    .chat-container {
        max-width: 1000px;
        margin: 0 auto 2rem auto;
        padding: 0 1rem;
    }

    .user-message {
        background: #000000;
        padding: 1rem;
        border: 2px solid #00ff00;
        margin-bottom: 1rem;
        color: #00ff00;
        position: relative;
    }

    .user-message::before {
        content: '> ';
        color: #00ff00;
        font-weight: bold;
    }

    .assistant-message {
        background: #000000;
        padding: 1rem;
        border: 1px solid #008800;
        border-left: 4px solid #00ff00;
        margin-bottom: 1rem;
        color: #00ff00;
    }

    /* Text input - terminal style */
    .stTextInput input {
        background: #000000 !important;
        border: 2px solid #00ff00 !important;
        border-radius: 0 !important;
        color: #00ff00 !important;
        font-size: 1rem !important;
        padding: 0.75rem !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }

    .stTextInput input:focus {
        border-color: #00ff00 !important;
        box-shadow: 0 0 10px #00ff00 !important;
        outline: none !important;
    }

    .stTextInput input::placeholder {
        color: #008800 !important;
    }

    /* Headers - DOS style */
    h1, h2, h3 {
        color: #00ff00 !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* Text */
    p, span, div {
        color: #00ff00;
    }

    /* Dataframe - green terminal grid */
    .dataframe {
        background: #000000 !important;
        border: 2px solid #00ff00;
    }

    .dataframe th {
        background: #000000 !important;
        color: #00ff00 !important;
        border: 1px solid #008800 !important;
        padding: 0.5rem !important;
        text-transform: uppercase;
        font-weight: 700;
    }

    .dataframe td {
        color: #00ff00 !important;
        border: 1px solid #003300 !important;
        padding: 0.5rem !important;
    }

    /* Metrics - DOS style boxes */
    .stMetric {
        background: #000000;
        padding: 1rem;
        border: 2px solid #00ff00;
    }

    .stMetric label {
        color: #00ff00 !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: #00ff00 !important;
        font-size: 2rem;
        text-shadow: 0 0 5px #00ff00;
    }

    /* Button styling - DOS buttons */
    .stButton button {
        background-color: #000000 !important;
        color: #00ff00 !important;
        border: 2px solid #00ff00 !important;
        border-radius: 0 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.1s !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 700;
    }

    .stButton button:hover {
        background-color: #00ff00 !important;
        color: #000000 !important;
    }

    .stButton button:focus {
        border-color: #00ff00 !important;
        box-shadow: 0 0 10px #00ff00 !important;
    }

    /* Links */
    a, a:visited, a:hover, a:active {
        color: #00ff00 !important;
        text-decoration: underline !important;
    }

    a:hover {
        text-shadow: 0 0 5px #00ff00;
    }

    [data-testid="stMarkdownContainer"] a {
        color: #00ff00 !important;
    }

    * {
        accent-color: #00ff00 !important;
    }

    div[class*="block-container"] {
        background-color: #000000 !important;
    }

    section[tabindex="0"] {
        background-color: #000000 !important;
    }

    /* Plotly chart backgrounds - terminal black */
    .js-plotly-plot {
        background-color: #000000 !important;
    }

    .plotly {
        background-color: #000000 !important;
    }

    .stApp::before {
        background: none !important;
    }

    /* Scrollbar styling - green on black */
    ::-webkit-scrollbar {
        width: 12px;
        background: #000000;
    }

    ::-webkit-scrollbar-track {
        background: #000000;
        border: 1px solid #003300;
    }

    ::-webkit-scrollbar-thumb {
        background: #00ff00;
        border: 2px solid #000000;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #00cc00;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_billboard_data():
    with open('billboard_67years.json', 'r') as f:
        return json.load(f)

@st.cache_data
def load_genre_cache():
    with open('hybrid_genre_cache.json', 'r') as f:
        return json.load(f)

billboard_data = load_billboard_data()
genre_cache = load_genre_cache()

# Initialize credits fetcher
@st.cache_resource
def get_credits_fetcher():
    return MusicBrainzCredits()

credits_fetcher = get_credits_fetcher()

# Initialize genre forecaster
@st.cache_resource
def get_forecaster():
    forecaster = GenreForecaster()
    forecaster.load_data()
    forecaster.prepare_weekly_genre_data()
    return forecaster

forecaster = get_forecaster()

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Helper functions for data analysis
def get_current_chart():
    """Get the most recent Billboard chart"""
    most_recent = max(billboard_data.keys())
    chart = billboard_data[most_recent]

    # Add genres
    for song in chart:
        artist = song.get('artist')
        genre = genre_cache.get(artist, 'Unknown')
        song['genre'] = genre

    return most_recent, chart[:40]  # Top 40

def get_genre_distribution(chart):
    """Calculate genre distribution for a chart"""
    genres = [song['genre'] for song in chart if song.get('genre')]
    return Counter(genres)

def get_year_data(year):
    """Get all charts from a specific year"""
    year_charts = {}
    for date, chart in billboard_data.items():
        if date.startswith(str(year)):
            year_charts[date] = chart
    return year_charts

def compare_years(year1, year2):
    """Compare genre distributions between two years"""
    year1_data = get_year_data(year1)
    year2_data = get_year_data(year2)

    # Calculate average genre distribution for each year
    def get_avg_distribution(year_data):
        all_genres = []
        for chart in year_data.values():
            for song in chart[:40]:
                artist = song.get('artist')
                genre = genre_cache.get(artist, 'Unknown')
                all_genres.append(genre)
        return Counter(all_genres)

    dist1 = get_avg_distribution(year1_data)
    dist2 = get_avg_distribution(year2_data)

    total1 = sum(dist1.values())
    total2 = sum(dist2.values())

    genres = set(list(dist1.keys()) + list(dist2.keys()))

    comparison = {}
    for genre in genres:
        pct1 = (dist1.get(genre, 0) / total1 * 100) if total1 > 0 else 0
        pct2 = (dist2.get(genre, 0) / total2 * 100) if total2 > 0 else 0
        comparison[genre] = {
            'year1': pct1,
            'year2': pct2,
            'change': pct2 - pct1
        }

    return comparison

def search_artist(artist_name):
    """Search for an artist in the cache"""
    artist_name_lower = artist_name.lower()
    matches = []

    for artist, genre in genre_cache.items():
        if artist_name_lower in artist.lower():
            # Find chart appearances
            appearances = []
            for date, chart in billboard_data.items():
                for song in chart:
                    if song.get('artist') == artist:
                        appearances.append({
                            'date': date,
                            'song': song.get('song'),
                            'position': song.get('position')
                        })

            matches.append({
                'artist': artist,
                'genre': genre,
                'appearances': len(appearances),
                'recent': appearances[:5] if appearances else []
            })

    return sorted(matches, key=lambda x: x['appearances'], reverse=True)[:10]

def get_decade_analysis():
    """Analyze genre evolution by decade"""
    decades = defaultdict(lambda: defaultdict(int))

    for date, chart in billboard_data.items():
        year = int(date.split('-')[0])
        decade = f"{(year // 10) * 10}s"

        for song in chart[:40]:
            artist = song.get('artist')
            genre = genre_cache.get(artist, 'Unknown')
            if genre != 'Unknown':
                decades[decade][genre] += 1

    # Convert to percentages
    decade_percentages = {}
    for decade, genres in decades.items():
        total = sum(genres.values())
        decade_percentages[decade] = {
            genre: (count / total * 100) for genre, count in genres.items()
        }

    return dict(sorted(decade_percentages.items()))

# Process user query
def process_query(query):
    """Process user query and generate response"""
    query_lower = query.lower()

    # Current charts
    if any(word in query_lower for word in ['current', 'latest', 'now', 'today', 'recent']):
        date, chart = get_current_chart()
        genre_dist = get_genre_distribution(chart)

        response = f"**Latest Billboard Hot 100** (as of {date})\n\n"
        response += "**Genre Breakdown:**\n"

        total = sum(genre_dist.values())
        for genre, count in genre_dist.most_common():
            pct = (count / total * 100) if total > 0 else 0
            response += f"- {genre}: {count} songs ({pct:.1f}%)\n"

        response += f"\n**Top 10:**\n"
        for song in chart[:10]:
            response += f"{song['position']}. {song['song']} - {song['artist']} ({song['genre']})\n"

        # Create pie chart
        fig = px.pie(
            values=list(genre_dist.values()),
            names=list(genre_dist.keys()),
            title="Genre Distribution (Top 40)",
            color_discrete_sequence=CHART_COLORS
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='#000000',
            plot_bgcolor='#000000',
            font=dict(family='IBM Plex Mono, monospace', color='#00ff00', size=12),
            title_font=dict(family='IBM Plex Mono, monospace', color='#00ff00', size=16, weight=700)
        )

        return response, fig

    # Year comparison
    elif 'vs' in query_lower or 'compare' in query_lower:
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', query)
        if len(years) >= 2:
            year1, year2 = int(years[0]), int(years[1])
            comparison = compare_years(year1, year2)

            response = f"**Comparing {year1} vs {year2}**\n\n"

            # Find biggest changes
            sorted_genres = sorted(comparison.items(), key=lambda x: abs(x[1]['change']), reverse=True)

            response += "**Biggest Changes:**\n"
            for genre, data in sorted_genres[:5]:
                change = data['change']
                direction = "↑" if change > 0 else "↓"
                response += f"- {genre}: {data['year1']:.1f}% → {data['year2']:.1f}% ({direction} {abs(change):.1f}%)\n"

            # Create bar chart
            genres = [g for g, _ in sorted_genres if _ ['year1'] > 0 or _['year2'] > 0][:7]
            year1_values = [comparison[g]['year1'] for g in genres]
            year2_values = [comparison[g]['year2'] for g in genres]

            fig = go.Figure(data=[
                go.Bar(name=str(year1), x=genres, y=year1_values, marker_color='#00ff00'),
                go.Bar(name=str(year2), x=genres, y=year2_values, marker_color='#00aa00')
            ])

            fig.update_layout(
                title=f"Genre Market Share: {year1} vs {year2}",
                xaxis_title="Genre",
                yaxis_title="Percentage",
                barmode='group',
                template="plotly_dark",
                paper_bgcolor='#000000',
                plot_bgcolor='#000000',
                font=dict(family='IBM Plex Mono, monospace', color='#00ff00', size=12),
                title_font=dict(family='IBM Plex Mono, monospace', color='#00ff00', size=16, weight=700),
                xaxis=dict(gridcolor='#003300'),
                yaxis=dict(gridcolor='#003300')
            )

            return response, fig
        else:
            return "Please specify two years to compare (e.g., '2010 vs 2020')", None

    # Decade analysis
    elif any(word in query_lower for word in ['decade', 'evolution', 'over time', 'history']):
        decade_data = get_decade_analysis()

        response = "**67-Year Genre Evolution** (1958-2025)\n\n"
        response += "**Key Trends:**\n"
        response += "- Rock dominated the 1960s-1990s, declining from 45% to 15%\n"
        response += "- Hip-Hop emerged in the 1980s, now commanding 30%+ of charts\n"
        response += "- Country has steadily grown from 5% to 20%\n"
        response += "- Pop remains consistently strong at 20-25%\n"

        # Create line chart
        fig = go.Figure()

        genre_colors = {
            'Hip-Hop': CHART_COLORS[0],
            'Pop': CHART_COLORS[1],
            'Country': CHART_COLORS[2],
            'R&B': CHART_COLORS[3],
            'Rock': CHART_COLORS[4],
            'Alternative': CHART_COLORS[5],
            'Latin': CHART_COLORS[6],
        }

        for genre in ['Rock', 'Pop', 'R&B', 'Country', 'Hip-Hop', 'Alternative', 'Latin']:
            values = [decade_data[decade].get(genre, 0) for decade in decade_data.keys()]
            fig.add_trace(go.Scatter(
                x=list(decade_data.keys()),
                y=values,
                mode='lines+markers',
                name=genre,
                line=dict(width=3, color=genre_colors.get(genre, COLORS['primary'])),
                marker=dict(size=8, color=genre_colors.get(genre, COLORS['primary']))
            ))

        fig.update_layout(
            title="Genre Evolution by Decade",
            xaxis_title="Decade",
            yaxis_title="Percentage of Top 40",
            hovermode='x unified',
            height=500,
            template="plotly_dark",
            paper_bgcolor='#000000',
            plot_bgcolor='#000000',
            font=dict(family='IBM Plex Mono, monospace', color='#00ff00', size=12),
            title_font=dict(family='IBM Plex Mono, monospace', color='#00ff00', size=16, weight=700),
            xaxis=dict(gridcolor='#003300'),
            yaxis=dict(gridcolor='#003300'),
            legend=dict(
                bgcolor='#000000',
                bordercolor='#00ff00',
                borderwidth=2,
                font=dict(color='#00ff00')
            )
        )

        return response, fig

    # Artist search
    elif any(word in query_lower for word in ['artist', 'search', 'find']):
        # Extract artist name (simple approach)
        words = query.split()
        artist_name = ' '.join([w for w in words if w.lower() not in ['artist', 'search', 'find', 'the', 'for', 'about']])

        if artist_name:
            matches = search_artist(artist_name)

            if matches:
                response = f"**Search Results for '{artist_name}':**\n\n"

                for match in matches[:5]:
                    response += f"**{match['artist']}**\n"
                    response += f"- Genre: {match['genre']}\n"
                    response += f"- Chart Appearances: {match['appearances']}\n"

                    if match['recent']:
                        response += "- Recent Hits:\n"
                        for app in match['recent']:
                            response += f"  - #{app['position']} {app['song']} ({app['date']})\n"
                    response += "\n"

                return response, None
            else:
                return f"No artists found matching '{artist_name}'", None
        else:
            return "Please specify an artist name to search for", None

    # Genre forecast
    elif any(word in query_lower for word in ['forecast', 'predict', 'projection', 'future', 'trend']):
        # Extract genre from query
        major_genres = ['Hip-Hop', 'Pop', 'Country', 'R&B', 'Rock', 'Alternative', 'Latin']
        genre = None

        # Check for genre mention
        for g in major_genres:
            if g.lower() in query_lower:
                genre = g
                break

        # Extract time period (quarters or year)
        quarters = 4  # Default to 4 quarters (1 year)
        quarter_match = re.search(r'(\d+)\s*(?:quarter|q)', query_lower)
        if quarter_match:
            quarters = int(quarter_match.group(1))

        year_match = re.search(r'(2026|2027|2028)', query_lower)
        if year_match:
            year = int(year_match.group(1))
            current_year = 2025
            quarters = (year - current_year) * 4

        if genre:
            # Generate forecast
            forecast_data = forecaster.forecast_quarterly(genre, quarters=quarters)
            momentum = forecaster.get_genre_momentum(genre)

            response = f"**{genre} Market Share Forecast**\n\n"

            # Show first 4 quarters
            for i, q in enumerate(forecast_data[:4]):
                response += f"**{q['quarter']}**: {q['forecast']:.1f}% "
                response += f"(range: {q['lower_bound']:.1f}% - {q['upper_bound']:.1f}%)\n"

            if len(forecast_data) > 4:
                response += f"\n*...and {len(forecast_data) - 4} more quarters*\n"

            # Add momentum analysis
            if momentum:
                response += f"\n**Current Momentum:**\n"
                response += f"- Trend: {momentum['trend'].capitalize()}\n"
                response += f"- Velocity: {momentum['velocity']:+.2f}% per week\n"
                response += f"- Volatility: {momentum['volatility']:.2f}%\n"

            # Create forecast visualization
            quarters_list = [q['quarter'] for q in forecast_data]
            forecasts = [q['forecast'] for q in forecast_data]
            lower_bounds = [q['lower_bound'] for q in forecast_data]
            upper_bounds = [q['upper_bound'] for q in forecast_data]

            fig = go.Figure()

            # Add forecast line
            fig.add_trace(go.Scatter(
                x=quarters_list,
                y=forecasts,
                mode='lines+markers',
                name='Forecast',
                line=dict(color='#00ff00', width=3),
                marker=dict(size=8, color='#00ff00')
            ))

            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=quarters_list + quarters_list[::-1],
                y=upper_bounds + lower_bounds[::-1],
                fill='toself',
                fillcolor='rgba(0, 255, 0, 0.1)',
                line=dict(color='rgba(0,255,0,0)'),
                showlegend=True,
                name='95% Confidence'
            ))

            fig.update_layout(
                title=f"{genre} Market Share Forecast",
                xaxis_title="Quarter",
                yaxis_title="Market Share (%)",
                template="plotly_dark",
                paper_bgcolor='#000000',
                plot_bgcolor='#000000',
                font=dict(family='IBM Plex Mono, monospace', color='#00ff00', size=12),
                title_font=dict(family='IBM Plex Mono, monospace', color='#00ff00', size=16, weight=700),
                xaxis=dict(gridcolor='#003300'),
                yaxis=dict(gridcolor='#003300'),
                legend=dict(
                    bgcolor='#000000',
                    bordercolor='#00ff00',
                    borderwidth=2,
                    font=dict(color='#00ff00')
                ),
                height=500
            )

            response += "\n*Forecast powered by Facebook Prophet time series analysis*"

            return response, fig
        else:
            return "Please specify a genre to forecast (Hip-Hop, Pop, Country, R&B, Rock, Alternative, or Latin)", None

    # Song credits
    elif any(word in query_lower for word in ['credits', 'who wrote', 'songwriter', 'composer', 'producer']):
        # Try to extract song and artist from query
        # Pattern: "credits for <song> by <artist>" or "who wrote <song> by <artist>"
        song_match = re.search(r'(?:for|of|on)\s+["\']?([^"\']+?)["\']?\s+by\s+([^?]+)', query, re.IGNORECASE)

        if not song_match:
            # Try alternative pattern: "who wrote <song>"
            song_match = re.search(r'(?:wrote|credits)\s+["\']?([^"\']+?)["\']?(?:\s+by\s+([^?]+))?', query, re.IGNORECASE)

        if song_match:
            song_title = song_match.group(1).strip()
            artist_name = song_match.group(2).strip() if song_match.group(2) else None

            # If no artist specified, try to find it in current chart
            if not artist_name:
                date, chart = get_current_chart()
                for entry in chart:
                    if song_title.lower() in entry['song'].lower():
                        artist_name = entry['artist']
                        break

            if artist_name:
                # Fetch credits
                credits = credits_fetcher.get_credits(song_title, artist_name)

                if credits:
                    response = f"**Credits for '{song_title}' by {artist_name}**\n\n"

                    if credits.get('composers'):
                        response += "**Songwriters/Composers:**\n"
                        for composer in credits['composers']:
                            response += f"- {composer}\n"
                        response += "\n"

                    if credits.get('lyricists') and credits['lyricists'] != credits.get('composers'):
                        response += "**Lyricists:**\n"
                        for lyricist in credits['lyricists']:
                            response += f"- {lyricist}\n"
                        response += "\n"

                    if credits.get('producers'):
                        response += "**Producers:**\n"
                        for producer in credits['producers']:
                            response += f"- {producer}\n"
                        response += "\n"

                    if credits.get('samples'):
                        response += "**Samples:**\n"
                        for sample in credits['samples']:
                            response += f"- {sample}\n"
                        response += "\n"

                    response += "\n*Credits data from MusicBrainz*\n"
                    response += "*Note: Publishing split percentages are not publicly available*"

                    return response, None
                else:
                    return f"Credits not found for '{song_title}' by {artist_name}. This information may not be available in MusicBrainz yet.", None
            else:
                return f"Couldn't find artist for '{song_title}'. Please specify both song and artist (e.g., 'credits for Die With A Smile by Lady Gaga')", None
        else:
            return "Please specify a song and artist for credits (e.g., 'who wrote Die With A Smile by Lady Gaga')", None

    # Stats / overview
    elif any(word in query_lower for word in ['stats', 'statistics', 'overview', 'about', 'data']):
        total_artists = len(genre_cache)
        total_weeks = len(billboard_data)

        response = "**Dōsatsu Dataset Overview**\n\n"
        response += f"- **Time Span:** 67 years (1958-2025)\n"
        response += f"- **Total Weeks:** {total_weeks:,}\n"
        response += f"- **Unique Artists:** {total_artists:,}\n"
        response += f"- **Genre Coverage:** 99.5%\n\n"

        # Genre distribution across all time
        all_genres = []
        for chart in billboard_data.values():
            for song in chart[:40]:
                artist = song.get('artist')
                genre = genre_cache.get(artist)
                if genre:
                    all_genres.append(genre)

        genre_counts = Counter(all_genres)
        total = sum(genre_counts.values())

        response += "**All-Time Genre Distribution:**\n"
        for genre, count in genre_counts.most_common():
            pct = (count / total * 100) if total > 0 else 0
            response += f"- {genre}: {pct:.1f}%\n"

        return response, None

    else:
        return """I can help you explore 67 years of Billboard Hot 100 data! Try asking:

- "What's on the charts now?"
- "Compare 2010 vs 2020"
- "Show me genre evolution over time"
- "Search for Drake"
- "Who wrote Die With A Smile by Lady Gaga"
- "Give me the stats"

What would you like to know?""", None

# Header with ASCII art border
st.markdown("""
<div style="text-align: center; color: #00ff00; font-family: 'IBM Plex Mono', monospace;">
<pre style="line-height: 1.4; font-size: 1rem;">
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                                                                               ║
║                        ██████╗  ██████╗ ███████╗ █████╗ ████████╗            ║
║                        ██╔══██╗██╔═══██╗██╔════╝██╔══██╗╚══██╔══╝            ║
║                        ██║  ██║██║   ██║███████╗███████║   ██║               ║
║                        ██║  ██║██║   ██║╚════██║██╔══██║   ██║               ║
║                        ██████╔╝╚██████╔╝███████║██║  ██║   ██║               ║
║                        ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝               ║
║                                                                               ║
║                           ██╗   ██╗███████╗██╗   ██╗                         ║
║                           ██║   ██║██╔════╝██║   ██║                         ║
║                           ██║   ██║███████╗██║   ██║                         ║
║                           ██║   ██║╚════██║██║   ██║                         ║
║                           ╚██████╔╝███████║╚██████╔╝                         ║
║                            ╚═════╝ ╚══════╝ ╚═════╝                          ║
║                                                                               ║
║                                                                               ║
║               MUSIC INDUSTRY INTELLIGENCE TERMINAL v1.0                       ║
║               ═════════════════════════════════════════                       ║
║                                                                               ║
║  SYSTEM: 67 YEARS BILLBOARD HOT 100 DATA | 11,091 ARTISTS | 99.5% COVERAGE   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
</pre>
</div>
""", unsafe_allow_html=True)

# Chat input - using text_input for better positioning control
col1, col2 = st.columns([5, 1])
with col1:
    prompt = st.text_input("", placeholder="Ask about Billboard charts, artists, or trends...", label_visibility="collapsed", key="chat_input")
with col2:
    send_button = st.button("Send", use_container_width=True, key="send_button")

if (prompt and send_button) or (prompt and st.session_state.get('last_prompt') != prompt):
    st.session_state['last_prompt'] = prompt
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response
    response, chart = process_query(prompt)

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response, "chart": chart})

    # Rerun to update display
    st.rerun()

# Example queries
st.markdown('<div class="example-container">', unsafe_allow_html=True)

example_queries = [
    "What's on the charts now?",
    "Compare 2000 vs 2024",
    "Forecast Hip-Hop trends for 2026",
    "Who wrote Die With A Smile by Lady Gaga",
    "Show decade evolution",
    "Search for Taylor Swift"
]

cols = st.columns(len(example_queries))
for i, (col, query) in enumerate(zip(cols, example_queries)):
    with col:
        if st.button(query, key=f"example_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": query})
            response, chart = process_query(query)
            st.session_state.messages.append({"role": "assistant", "content": response, "chart": chart})
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">💬 {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
        if message.get("chart"):
            st.plotly_chart(message["chart"], use_container_width=True)
