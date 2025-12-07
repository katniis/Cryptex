"""
Price Update Service
Manages automatic price updates for the UI
"""

from api.price_fetcher import get_price_fetcher
from models.cryptocurrency import CryptoCurrency
import logging

logger = logging.getLogger(__name__)


class PriceUpdateService:
    """
    Service to manage price updates for the UI
    """
    
    def __init__(self):
        self.fetcher = None
        self.update_callbacks = []
        self.is_running = False
    
    def start(self, update_interval=5):
        """
        Start the price update service
        
        Args:
            update_interval (int): Seconds between updates
        """
        if self.is_running:
            logger.warning("Price update service already running")
            return
        
        # Get all active cryptocurrencies
        all_cryptos = CryptoCurrency.get_all(active_only=True)
        symbols = [crypto.symbol for crypto in all_cryptos[:20]]  # Limit to top 20
        
        # Get fetcher instance
        self.fetcher = get_price_fetcher(update_interval)
        
        # Set symbols to track
        self.fetcher.set_tracked_symbols(symbols)
        
        # Add callback for UI updates
        self.fetcher.add_callback(self._on_prices_updated)
        
        # Start fetching
        self.fetcher.start()
        self.is_running = True
        
        logger.info(f"✅ Price update service started (updating every {update_interval}s)")
    
    def stop(self):
        """Stop the price update service"""
        if not self.is_running:
            return
        
        if self.fetcher:
            self.fetcher.stop()
        
        self.is_running = False
        logger.info("⏹️ Price update service stopped")
    
    def add_update_callback(self, callback):
        """
        Add a callback to be called when prices are updated
        
        Args:
            callback (function): Function to call on price update
        """
        if callback not in self.update_callbacks:
            self.update_callbacks.append(callback)
    
    def remove_update_callback(self, callback):
        """Remove a callback"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
    
    def _on_prices_updated(self, symbols, count):
        """Called when prices are updated from API"""
        logger.info(f"🔄 Prices updated: {count} cryptocurrencies")
        
        # Call all registered callbacks
        for callback in self.update_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in update callback: {e}")
    
    def fetch_now(self):
        """Trigger immediate price fetch"""
        if self.fetcher:
            self.fetcher.fetch_now()


# Global instance
_price_service = None


def get_price_service():
    """Get or create the global price service instance"""
    global _price_service
    
    if _price_service is None:
        _price_service = PriceUpdateService()
    
    return _price_service


if __name__ == "__main__":
    print("Price update service created")