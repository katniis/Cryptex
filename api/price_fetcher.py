"""
Price Fetcher
Background service to fetch and update cryptocurrency prices
"""

import threading
import time
from datetime import datetime
from api.coinmarketcap_api import CoinMarketCapAPI
from models.cryptocurrency import CryptoCurrency
import logging

logger = logging.getLogger(__name__)


class PriceFetcher:
    """
    Background service to automatically fetch cryptocurrency prices
    """
    
    def __init__(self, update_interval=5):
        """
        Initialize price fetcher
        
        Args:
            update_interval (int): Seconds between updates (default: 5)
        """
        self.update_interval = update_interval
        self.api = CoinMarketCapAPI()
        self.is_running = False
        self.thread = None
        self._symbols_to_track = []
        self._callbacks = []  # List of callback functions to call on price update
        
    def add_callback(self, callback):
        """
        Add a callback function to be called when prices are updated
        
        Args:
            callback (function): Function to call with updated prices
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback):
        """Remove a callback function"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def set_tracked_symbols(self, symbols):
        """
        Set which cryptocurrency symbols to track
        
        Args:
            symbols (list): List of symbols (e.g., ['BTC', 'ETH'])
        """
        self._symbols_to_track = symbols
        logger.info(f"Now tracking: {', '.join(symbols)}")
    
    def add_symbol(self, symbol):
        """Add a symbol to track"""
        if symbol not in self._symbols_to_track:
            self._symbols_to_track.append(symbol)
            logger.info(f"Added {symbol} to tracking")
    
    def remove_symbol(self, symbol):
        """Remove a symbol from tracking"""
        if symbol in self._symbols_to_track:
            self._symbols_to_track.remove(symbol)
            logger.info(f"Removed {symbol} from tracking")
    
    def _fetch_and_update(self):
        """
        Main update loop - fetches prices and updates database
        """
        while self.is_running:
            try:
                start_time = time.time()
                
                # Determine which symbols to update
                if self._symbols_to_track:
                    symbols = self._symbols_to_track
                else:
                    # Update all active cryptocurrencies
                    all_cryptos = CryptoCurrency.get_all(active_only=True)
                    symbols = [crypto.symbol for crypto in all_cryptos[:20]]  # Limit to top 20
                
                if symbols:
                    logger.info(f"🔄 Fetching prices for {len(symbols)} cryptocurrencies...")
                    
                    # Update prices
                    updated_count = self.api.update_database_prices(symbols)
                    
                    if updated_count > 0:
                        logger.info(f"✅ Updated {updated_count} prices")
                        
                        # Call all registered callbacks
                        for callback in self._callbacks:
                            try:
                                callback(symbols, updated_count)
                            except Exception as e:
                                logger.error(f"Error in callback: {e}")
                    else:
                        logger.warning("⚠️ No prices updated")
                
                # Calculate how long to sleep
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed)
                
                # Sleep until next update
                if self.is_running and sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"❌ Error in price fetch loop: {e}")
                time.sleep(self.update_interval)
    
    def start(self):
        """
        Start the background price fetching service
        """
        if self.is_running:
            logger.warning("Price fetcher is already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._fetch_and_update, daemon=True)
        self.thread.start()
        
        logger.info(f"✅ Price fetcher started (updating every {self.update_interval}s)")
    
    def stop(self):
        """
        Stop the background price fetching service
        """
        if not self.is_running:
            logger.warning("Price fetcher is not running")
            return
        
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("⏹️ Price fetcher stopped")
    
    def fetch_now(self):
        """
        Immediately fetch prices (don't wait for next interval)
        """
        if not self._symbols_to_track:
            logger.warning("No symbols to track")
            return 0
        
        logger.info("Fetching prices immediately...")
        return self.api.update_database_prices(self._symbols_to_track)


# Singleton instance
_price_fetcher_instance = None


def get_price_fetcher(update_interval=5):
    """
    Get or create the global price fetcher instance
    
    Args:
        update_interval (int): Update interval in seconds
        
    Returns:
        PriceFetcher: Global price fetcher instance
    """
    global _price_fetcher_instance
    
    if _price_fetcher_instance is None:
        _price_fetcher_instance = PriceFetcher(update_interval)
    
    return _price_fetcher_instance


# Test function
def test_price_fetcher():
    """
    Test the price fetcher
    """
    print("\n" + "="*50)
    print("Testing Price Fetcher")
    print("="*50)
    
    def on_price_update(symbols, count):
        """Callback function"""
        print(f"📊 Price update callback: {count} prices updated for {symbols}")
    
    # Get price fetcher
    fetcher = get_price_fetcher(update_interval=10)  # Update every 10 seconds for testing
    
    # Add callback
    fetcher.add_callback(on_price_update)
    
    # Set symbols to track
    print("\n1. Setting symbols to track...")
    fetcher.set_tracked_symbols(['BTC', 'ETH', 'USDT'])
    
    # Start fetcher
    print("\n2. Starting price fetcher...")
    fetcher.start()
    
    # Let it run for 30 seconds
    print("\n3. Running for 30 seconds... (watch for updates)")
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    # Stop fetcher
    print("\n4. Stopping price fetcher...")
    fetcher.stop()
    
    print("\n" + "="*50)
    print("Price Fetcher Test Complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_price_fetcher()