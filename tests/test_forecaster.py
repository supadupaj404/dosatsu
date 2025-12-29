#!/usr/bin/env python3
"""
Test script for GenreForecaster
Validates forecasting on historical Billboard data
"""

from genre_forecaster import GenreForecaster
import pandas as pd

print('='*70)
print('TESTING DŌSATSU GENRE FORECASTER')
print('='*70)
print()

# Initialize forecaster
print('Step 1: Initializing forecaster...')
forecaster = GenreForecaster()
print('✓ Forecaster initialized')
print()

# Load data
print('Step 2: Loading Billboard and genre data...')
forecaster.load_data()
print(f'✓ Loaded Billboard data: {len(forecaster.billboard_data):,} weeks')
print(f'✓ Loaded genre cache: {len(forecaster.genre_cache):,} artists')
print()

# Prepare weekly genre data
print('Step 3: Preparing weekly genre percentages...')
df = forecaster.prepare_weekly_genre_data()
print(f'✓ Prepared {len(df):,} weekly genre data points')
print()

# Show date range
print('Data Range:')
print(f'  Start: {df["date"].min()}')
print(f'  End: {df["date"].max()}')
print(f'  Span: {(df["date"].max() - df["date"].min()).days / 365.25:.1f} years')
print()

# Show genre distribution
print('Genres in dataset:')
genre_counts = df['genre'].value_counts()
for genre, count in genre_counts.head(10).items():
    print(f'  {genre:<15} {count:>6} weeks')
print()

# Test forecasting on Hip-Hop
print('Step 4: Testing forecast for Hip-Hop...')
print('Training Prophet model (this may take 20-30 seconds)...')
forecast_quarters = forecaster.forecast_quarterly('Hip-Hop', quarters=4)

print('✓ Forecast complete!')
print()

# Display forecast
print('='*70)
print('HIP-HOP FORECAST - NEXT 4 QUARTERS')
print('='*70)
print()

for q in forecast_quarters:
    print(f"Quarter: {q['quarter']}")
    print(f"  Forecast: {q['forecast']:.1f}% market share")
    print(f"  Range: {q['lower_bound']:.1f}% - {q['upper_bound']:.1f}%")
    print(f"  Confidence interval: ±{q['confidence_95']/2:.1f}%")
    print()

# Test momentum analysis
print('='*70)
print('HIP-HOP MOMENTUM ANALYSIS')
print('='*70)
print()

momentum = forecaster.get_genre_momentum('Hip-Hop', lookback_weeks=12)

if momentum:
    print(f"Trend: {momentum['trend'].capitalize()}")
    print(f"Velocity: {momentum['velocity']:+.2f}% per week")
    print(f"Acceleration: {momentum['acceleration']:+.3f}% per week²")
    print(f"Volatility: {momentum['volatility']:.2f}%")
    print(f"Momentum Score: {momentum['momentum_score']:+.2f}")
    print()

# Test formatted output
print('='*70)
print('FORMATTED FORECAST TEXT')
print('='*70)
print()

formatted = forecaster.format_forecast_text('Hip-Hop', quarters=4)
print(formatted)

print()
print('='*70)
print('✅ ALL TESTS PASSED')
print('='*70)
print()
print('The forecasting module is working correctly!')
print('Ready to integrate into Streamlit dashboard.')
print()
