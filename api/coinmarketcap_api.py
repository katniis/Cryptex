"""
CoinMarketCap API Wrapper
Handles all API calls to CoinMarketCap
"""

import requests
import time
from datetime import datetime
from config.api_config import CMC_API_KEY, CMC_BASE_URL, CMC_HEADERS, CMC_ENDPOINTS
from models.price import Price
from models.cryptocurrency import CryptoCurrency
import logging

logger = logging.getLogger(__name__)


class CoinMarketCapAPI:
    """
    Wrapper for CoinMarketCap API
    """
    
    def __init__(self):
        self.base_url = CMC_BASE_URL
        self.headers = CMC_HEADERS
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._last_call_time = 0
        self._min_call_interval = 2  # Minimum 2 seconds between calls (rate limiting)
    
    def _rate_limit(self):
        """
        Enforce rate limiting between API calls
        """
        current_time = time.time()
        time_since_last_call = current_time - self._last_call_time
        
        if time_since_last_call < self._min_call_interval:
            sleep_time = self._min_call_interval - time_since_last_call
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self._last_call_time = time.time()
    
    def _make_request(self, endpoint, params=None):
        """
        Make API request with error handling
        
        Args:
            endpoint (str): API endpoint
            params (dict): Query parameters
            
        Returns:
            dict: API response data or None if failed
        """
        try:
            self._rate_limit()
            
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params)
            
            # Check response status
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 401:
                logger.error("❌ API Key is invalid or missing")
                return None
            elif response.status_code == 429:
                logger.error("❌ Rate limit exceeded")
                return None
            else:
                logger.error(f"❌ API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return None
    
    def get_latest_listings(self, limit=100, convert='USD'):
        """
        Get latest cryptocurrency listings
        
        Args:
            limit (int): Number of results (1-5000)
            convert (str): Currency to convert to
            
        Returns:
            list: List of cryptocurrency data
        """
        endpoint = CMC_ENDPOINTS['listings_latest']
        params = {
            'limit': limit,
            'convert': convert,
            'sort': 'market_cap',
            'sort_dir': 'desc'
        }
        
        response = self._make_request(endpoint, params)
        
        if response and response.get('status', {}).get('error_code') == 0:
            return response.get('data', [])
        
        return []
    
    def get_quotes_by_symbol(self, symbols, convert='USD'):
        """
        Get latest quotes for specific cryptocurrencies by symbol
        
        Args:
            symbols (list or str): Cryptocurrency symbols (e.g., ['BTC', 'ETH'])
            convert (str): Currency to convert to
            
        Returns:
            dict: Dictionary of cryptocurrency data by symbol
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        endpoint = CMC_ENDPOINTS['quotes_latest']
        params = {
            'symbol': symbols,
            'convert': convert
        }
        
        response = self._make_request(endpoint, params)
        
        if response and response.get('status', {}).get('error_code') == 0:
            return response.get('data', {})
        
        return {}
    
    def get_quotes_by_id(self, crypto_ids, convert='USD'):
        """
        Get latest quotes for specific cryptocurrencies by CMC ID
        
        Args:
            crypto_ids (list or str): CoinMarketCap IDs
            convert (str): Currency to convert to
            
        Returns:
            dict: Dictionary of cryptocurrency data by ID
        """
        if isinstance(crypto_ids, list):
            crypto_ids = ','.join(map(str, crypto_ids))
        
        endpoint = CMC_ENDPOINTS['quotes_latest']
        params = {
            'id': crypto_ids,
            'convert': convert
        }
        
        response = self._make_request(endpoint, params)
        
        if response and response.get('status', {}).get('error_code') == 0:
            return response.get('data', {})
        
        return {}
    
    def get_crypto_info(self, symbols):
        """
        Get metadata information about cryptocurrencies
        
        Args:
            symbols (list or str): Cryptocurrency symbols
            
        Returns:
            dict: Cryptocurrency metadata
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        endpoint = CMC_ENDPOINTS['info']
        params = {'symbol': symbols}
        
        response = self._make_request(endpoint, params)
        
        if response and response.get('status', {}).get('error_code') == 0:
            return response.get('data', {})
        
        return {}
    
    def update_database_prices(self, symbols=None):
        """
        Fetch latest prices and update database
        
        Args:
            symbols (list): List of symbols to update (None = all active cryptos)
            
        Returns:
            int: Number of prices updated
        """
        try:
            # Get symbols from database if not provided
            if symbols is None:
                all_cryptos = CryptoCurrency.get_all(active_only=True)
                symbols = [crypto.symbol for crypto in all_cryptos]
            
            if not symbols:
                logger.warning("No cryptocurrencies to update")
                return 0
            
            # Fetch quotes in batches (API limit: ~120 symbols per request)
            batch_size = 100
            updated_count = 0
            
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                
                logger.info(f"Fetching prices for {len(batch)} cryptocurrencies...")
                quotes = self.get_quotes_by_symbol(batch)
                
                if not quotes:
                    logger.error("Failed to fetch quotes")
                    continue
                
                # Update each cryptocurrency price
                for symbol, data in quotes.items():
                    try:
                        # Get crypto from database
                        crypto = CryptoCurrency.get_by_symbol(symbol)
                        if not crypto:
                            continue
                        
                        # Extract price data
                        quote = data.get('quote', {}).get('USD', {})
                        price = quote.get('price', 0)
                        volume_24h = quote.get('volume_24h', 0)
                        market_cap = quote.get('market_cap', 0)
                        
                        if price > 0:
                            # Create price record
                            Price.create(
                                crypto_id=crypto.crypto_id,
                                price=price,
                                volume=volume_24h,
                                market_cap=market_cap,
                                source='CoinMarketCap'
                            )
                            updated_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error updating price for {symbol}: {e}")
                        continue
            
            logger.info(f"✅ Updated {updated_count} cryptocurrency prices")
            return updated_count
            
        except Exception as e:
            logger.error(f"❌ Error updating database prices: {e}")
            return 0
    
    def sync_cryptocurrencies(self, limit=100):
        """
        Sync top cryptocurrencies to database
        
        Args:
            limit (int): Number of top cryptos to sync
            
        Returns:
            int: Number of cryptos synced
        """
        try:
            logger.info(f"Syncing top {limit} cryptocurrencies...")
            
            listings = self.get_latest_listings(limit=limit)
            
            if not listings:
                logger.error("Failed to fetch listings")
                return 0
            
            synced_count = 0
            
            for crypto_data in listings:
                try:
                    symbol = crypto_data.get('symbol')
                    name = crypto_data.get('name')
                    cmc_id = crypto_data.get('id')
                    rank = crypto_data.get('cmc_rank')
                    
                    # Check if exists
                    existing = CryptoCurrency.get_by_symbol(symbol)
                    
                    if existing:
                        # Update existing
                        existing.update(
                            api_id=str(cmc_id),
                            market_cap_rank=rank,
                            is_active=True
                        )
                    else:
                        # Create new
                        CryptoCurrency.create(
                            symbol=symbol,
                            name=name,
                            api_id=str(cmc_id),
                            market_cap_rank=rank
                        )
                    
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing {crypto_data.get('symbol')}: {e}")
                    continue
            
            logger.info(f"✅ Synced {synced_count} cryptocurrencies")
            return synced_count
            
        except Exception as e:
            logger.error(f"❌ Error syncing cryptocurrencies: {e}")
            return 0


# Test function
def test_api():
    """
    Test CoinMarketCap API connection
    """
    print("\n" + "="*50)
    print("Testing CoinMarketCap API")
    print("="*50)
    
    api = CoinMarketCapAPI()
    
    # Test 1: Get BTC and ETH quotes
    print("\n1. Getting BTC and ETH quotes...")
    quotes = api.get_quotes_by_symbol(['BTC', 'ETH'])
    
    if quotes:
        for symbol, data in quotes.items():
            quote = data.get('quote', {}).get('USD', {})
            price = quote.get('price', 0)
            volume = quote.get('volume_24h', 0)
            print(f"✅ {symbol}: ${price:,.2f} | 24h Volume: ${volume:,.0f}")
    else:
        print("❌ Failed to get quotes")
    
    # Test 2: Sync top 10 cryptocurrencies
    print("\n2. Syncing top 10 cryptocurrencies to database...")
    synced = api.sync_cryptocurrencies(limit=10)
    print(f"✅ Synced {synced} cryptocurrencies")
    
    # Test 3: Update prices in database
    print("\n3. Updating prices in database...")
    updated = api.update_database_prices(['BTC', 'ETH', 'USDT'])
    print(f"✅ Updated {updated} prices")
    
    # Test 4: Verify prices in database
    print("\n4. Checking prices in database...")
    btc = CryptoCurrency.get_by_symbol('BTC')
    if btc:
        latest_price = Price.get_latest(btc.crypto_id)
        if latest_price:
            print(f"✅ BTC in database: ${latest_price.price:,.2f}")
        else:
            print("⚠️ No price data for BTC")
    
    print("\n" + "="*50)
    print("API Tests Complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_api()