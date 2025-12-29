#!/usr/bin/env python3
"""
Dōsatsu Genre Forecaster
Prophet-based forecasting for Billboard genre trends
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from prophet import Prophet
from collections import Counter
import warnings
import os
warnings.filterwarnings('ignore')

class GenreForecaster:
    """Forecast genre market share using Prophet"""

    def __init__(self, billboard_data_file=None, genre_cache_file=None):
        # Use absolute paths relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if billboard_data_file is None:
            billboard_data_file = os.path.join(project_root, 'data', 'billboard', 'billboard_67years.json')
        if genre_cache_file is None:
            genre_cache_file = os.path.join(project_root, 'data', 'billboard', 'hybrid_genre_cache.json')

        self.billboard_data_file = billboard_data_file
        self.genre_cache_file = genre_cache_file
        self.billboard_data = None
        self.genre_cache = None
        self.weekly_genre_data = None
        self.models = {}

    def load_data(self):
        """Load Billboard and genre cache data"""
        with open(self.billboard_data_file, 'r') as f:
            self.billboard_data = json.load(f)

        with open(self.genre_cache_file, 'r') as f:
            self.genre_cache = json.load(f)

    def prepare_weekly_genre_data(self):
        """
        Convert Billboard data to weekly genre percentages
        Returns DataFrame with columns: date, genre, percentage
        """
        weekly_data = []

        for date_str, chart in self.billboard_data.items():
            date = pd.to_datetime(date_str)

            # Count genres for this week (top 40)
            genre_counts = Counter()
            for song in chart[:40]:
                artist = song.get('artist')
                artist_data = self.genre_cache.get(artist)
                if artist_data:
                    genre = artist_data.get('dosatsu_genre', 'Unknown')
                else:
                    genre = 'Unknown'

                if genre and genre != 'Unknown':
                    genre_counts[genre] += 1

            # Calculate percentages
            total = sum(genre_counts.values())
            if total > 0:
                for genre, count in genre_counts.items():
                    percentage = (count / total) * 100
                    weekly_data.append({
                        'date': date,
                        'genre': genre,
                        'percentage': percentage
                    })

        self.weekly_genre_data = pd.DataFrame(weekly_data)
        return self.weekly_genre_data

    def train_genre_model(self, genre, train_until_date=None):
        """
        Train Prophet model for a specific genre

        Args:
            genre: Genre name (e.g., 'Hip-Hop', 'Pop')
            train_until_date: Train only up to this date (for backtesting)

        Returns:
            Fitted Prophet model
        """
        # Filter data for this genre
        genre_data = self.weekly_genre_data[
            self.weekly_genre_data['genre'] == genre
        ].copy()

        if train_until_date:
            genre_data = genre_data[genre_data['date'] <= train_until_date]

        # Prepare for Prophet (requires 'ds' and 'y' columns)
        df = pd.DataFrame({
            'ds': genre_data['date'],
            'y': genre_data['percentage']
        })

        # Fill missing weeks with interpolation
        df = df.set_index('ds').resample('W').mean().interpolate(method='linear').reset_index()

        # Train Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,  # Flexibility for trend changes
            seasonality_mode='multiplicative'
        )

        # Suppress Prophet's verbose output
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model.fit(df)

        self.models[genre] = model
        return model

    def forecast_genre(self, genre, periods=52, frequency='W'):
        """
        Generate forecast for a genre

        Args:
            genre: Genre name
            periods: Number of periods to forecast (default 52 weeks = 1 year)
            frequency: 'W' for weekly, 'M' for monthly, 'Q' for quarterly

        Returns:
            DataFrame with forecast including confidence intervals
        """
        if genre not in self.models:
            self.train_genre_model(genre)

        model = self.models[genre]

        # Create future dataframe
        future = model.make_future_dataframe(periods=periods, freq=frequency)

        # Generate forecast
        forecast = model.predict(future)

        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)

    def forecast_quarterly(self, genre, quarters=4):
        """
        Forecast quarterly averages for a genre

        Args:
            genre: Genre name
            quarters: Number of quarters to forecast

        Returns:
            Dict with quarterly forecasts
        """
        # Forecast weekly for next year
        weekly_forecast = self.forecast_genre(genre, periods=quarters*13)

        # Aggregate to quarters
        weekly_forecast['quarter'] = pd.PeriodIndex(weekly_forecast['ds'], freq='Q')

        quarterly = weekly_forecast.groupby('quarter').agg({
            'yhat': 'mean',
            'yhat_lower': 'mean',
            'yhat_upper': 'mean'
        }).reset_index()

        results = []
        for _, row in quarterly.iterrows():
            results.append({
                'quarter': str(row['quarter']),
                'forecast': row['yhat'],
                'lower_bound': row['yhat_lower'],
                'upper_bound': row['yhat_upper'],
                'confidence_95': row['yhat_upper'] - row['yhat_lower']
            })

        return results

    def get_all_genres_forecast(self, quarters=4):
        """
        Forecast all major genres

        Returns:
            Dict mapping genre to forecast data
        """
        major_genres = ['Hip-Hop', 'Pop', 'Country', 'R&B', 'Rock', 'Alternative', 'Latin']

        all_forecasts = {}

        for genre in major_genres:
            # Check if we have data for this genre
            if genre in self.weekly_genre_data['genre'].values:
                try:
                    forecast = self.forecast_quarterly(genre, quarters)
                    all_forecasts[genre] = forecast
                except Exception as e:
                    print(f"Could not forecast {genre}: {e}")
                    all_forecasts[genre] = None

        return all_forecasts

    def get_genre_momentum(self, genre, lookback_weeks=12):
        """
        Calculate momentum indicators for a genre

        Returns:
            Dict with velocity, acceleration, and momentum score
        """
        genre_data = self.weekly_genre_data[
            self.weekly_genre_data['genre'] == genre
        ].sort_values('date').tail(lookback_weeks * 2)

        if len(genre_data) < lookback_weeks:
            return None

        # Calculate velocity (1st derivative)
        genre_data['velocity'] = genre_data['percentage'].diff()

        # Calculate acceleration (2nd derivative)
        genre_data['acceleration'] = genre_data['velocity'].diff()

        # Recent metrics
        recent_velocity = genre_data['velocity'].tail(lookback_weeks).mean()
        recent_acceleration = genre_data['acceleration'].tail(lookback_weeks).mean()
        volatility = genre_data['percentage'].tail(lookback_weeks).std()

        # Momentum score (higher = stronger positive momentum)
        momentum_score = (
            recent_acceleration * 0.5 +
            recent_velocity * 0.3 -
            volatility * 0.2
        )

        return {
            'velocity': recent_velocity,
            'acceleration': recent_acceleration,
            'volatility': volatility,
            'momentum_score': momentum_score,
            'trend': 'accelerating' if recent_acceleration > 0.1 else ('decelerating' if recent_acceleration < -0.1 else 'stable')
        }

    def format_forecast_text(self, genre, quarters=4):
        """
        Generate human-readable forecast summary
        """
        forecast = self.forecast_quarterly(genre, quarters)

        if not forecast or len(forecast) == 0:
            return f"Insufficient data to forecast {genre}"

        # Get Q1 forecast (first quarter)
        q1 = forecast[0]

        # Get momentum
        momentum = self.get_genre_momentum(genre)

        text = f"**{genre} Forecast:**\n\n"
        text += f"**{q1['quarter']}**: {q1['forecast']:.1f}% (±{q1['confidence_95']/2:.1f}%)\n"
        text += f"  Range: {q1['lower_bound']:.1f}% - {q1['upper_bound']:.1f}%\n\n"

        if momentum:
            text += f"**Momentum Analysis:**\n"
            text += f"  Trend: {momentum['trend'].capitalize()}\n"
            text += f"  Velocity: {momentum['velocity']:+.2f}% per week\n"
            text += f"  Volatility: {momentum['volatility']:.2f}%\n"

        return text
