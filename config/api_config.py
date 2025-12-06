"""
API Configuration
CoinMarketCap API settings and endpoints
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# CoinMarketCap API Configuration
CMC_API_KEY = os.getenv('CMC_API_KEY', '')
CMC_BASE_URL = os.getenv('CMC_BASE_URL', 'https://pro-api.coinmarketcap.com/v1')

# API Endpoints
CMC_ENDPOINTS = {
    'listings_latest': '/cryptocurrency/listings/latest',
    'quotes_latest': '/cryptocurrency/quotes/latest',
    'info': '/cryptocurrency/info',
    'map': '/cryptocurrency/map',
    'quotes_historical': '/cryptocurrency/quotes/historical',
}

# Request Headers
CMC_HEADERS = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': CMC_API_KEY,
}

# Request Parameters Defaults
DEFAULT_PARAMS = {
    'convert': 'USD',  # Convert prices to USD
    'limit': 100,      # Default number of results
}

# Rate limiting (free tier: 333 calls per day, ~14 per hour)
RATE_LIMIT = {
    'calls_per_minute': 30,
    'calls_per_day': 333,
    'calls_per_month': 10000
}

# Cache settings (to reduce API calls)
CACHE_DURATION = {
    'price_data': 60,      # Cache prices for 60 seconds
    'coin_info': 3600,     # Cache coin info for 1 hour
    'listings': 300,       # Cache listings for 5 minutes
}