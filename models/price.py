"""
Price Model
Handles cryptocurrency price data storage and retrieval
"""

from datetime import datetime, timedelta
from database.connection import execute_query
import logging

logger = logging.getLogger(__name__)


class Price:
    """
    Price model for storing historical price data
    """
    
    def __init__(self, price_id=None, crypto_id=None, datetime=None,
                 price=None, volume=None, market_cap=None, source=None):
        self.price_id = price_id
        self.crypto_id = crypto_id
        self.datetime = datetime
        self.price = float(price) if price else 0.0
        self.volume = float(volume) if volume else 0.0
        self.market_cap = float(market_cap) if market_cap else 0.0
        self.source = source

    @classmethod
    def create(cls, crypto_id, price, volume=None, market_cap=None, source='CoinMarketCap', price_datetime=None):
        """
        Create a new price record
        
        Args:
            crypto_id (int): Cryptocurrency ID
            price (float): Price in USD
            volume (float): 24h trading volume
            market_cap (float): Market capitalization
            source (str): Data source
            price_datetime (datetime): Price timestamp
            
        Returns:
            Price: Newly created price object or None if failed
        """
        try:
            if price_datetime is None:
                price_datetime = datetime.now()
            
            query = """
                INSERT INTO price (crypto_id, datetime, price, volume, market_cap, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    price = VALUES(price),
                    volume = VALUES(volume),
                    market_cap = VALUES(market_cap),
                    source = VALUES(source)
            """
            price_id = execute_query(
                query,
                (crypto_id, price_datetime, price, volume, market_cap, source)
            )
            
            logger.info(f"✅ Price record created for crypto_id={crypto_id}: ${price}")
            
            return cls.get_by_id(price_id)
            
        except Exception as e:
            logger.error(f"❌ Error creating price record: {e}")
            return None

    @classmethod
    def get_by_id(cls, price_id):
        """
        Get price by ID
        
        Args:
            price_id (int): Price ID
            
        Returns:
            Price: Price object or None
        """
        query = "SELECT * FROM price WHERE price_id = %s"
        result = execute_query(query, (price_id,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_latest(cls, crypto_id):
        """
        Get latest price for a cryptocurrency
        
        Args:
            crypto_id (int): Cryptocurrency ID
            
        Returns:
            Price: Latest price object or None
        """
        query = """
            SELECT * FROM price 
            WHERE crypto_id = %s 
            ORDER BY datetime DESC 
            LIMIT 1
        """
        result = execute_query(query, (crypto_id,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_history(cls, crypto_id, days=30):
        """
        Get price history for specified days
        
        Args:
            crypto_id (int): Cryptocurrency ID
            days (int): Number of days to retrieve
            
        Returns:
            list: List of Price objects
        """
        query = """
            SELECT * FROM price 
            WHERE crypto_id = %s 
            AND datetime >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY datetime ASC
        """
        results = execute_query(query, (crypto_id, days), fetch_all=True)
        
        return [cls(**row) for row in results] if results else []

    @classmethod
    def get_range(cls, crypto_id, start_date, end_date):
        """
        Get prices within a date range
        
        Args:
            crypto_id (int): Cryptocurrency ID
            start_date (datetime): Start date
            end_date (datetime): End date
            
        Returns:
            list: List of Price objects
        """
        query = """
            SELECT * FROM price 
            WHERE crypto_id = %s 
            AND datetime BETWEEN %s AND %s
            ORDER BY datetime ASC
        """
        results = execute_query(query, (crypto_id, start_date, end_date), fetch_all=True)
        
        return [cls(**row) for row in results] if results else []

    @classmethod
    def bulk_insert(cls, price_records):
        """
        Insert multiple price records at once
        
        Args:
            price_records (list): List of tuples (crypto_id, datetime, price, volume, market_cap, source)
            
        Returns:
            int: Number of records inserted
        """
        try:
            query = """
                INSERT INTO price (crypto_id, datetime, price, volume, market_cap, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    price = VALUES(price),
                    volume = VALUES(volume),
                    market_cap = VALUES(market_cap)
            """
            from database.connection import execute_many
            count = execute_many(query, price_records)
            
            logger.info(f"✅ Bulk inserted {count} price records")
            return count
            
        except Exception as e:
            logger.error(f"❌ Error bulk inserting prices: {e}")
            return 0

    @classmethod
    def get_all_latest_prices(cls):
        """
        Get latest prices for all cryptocurrencies
        
        Returns:
            list: List of latest prices with crypto info
        """
        query = """
            SELECT p.*, c.symbol, c.name
            FROM price p
            INNER JOIN CryptoCurrency c ON p.crypto_id = c.crypto_id
            WHERE (p.crypto_id, p.datetime) IN (
                SELECT crypto_id, MAX(datetime)
                FROM price
                GROUP BY crypto_id
            )
            ORDER BY c.market_cap_rank
        """
        results = execute_query(query, fetch_all=True)
        return results if results else []

    def to_dict(self):
        """
        Convert to dictionary
        
        Returns:
            dict: Price data
        """
        return {
            'price_id': self.price_id,
            'crypto_id': self.crypto_id,
            'datetime': self.datetime,
            'price': self.price,
            'volume': self.volume,
            'market_cap': self.market_cap,
            'source': self.source
        }

    def __repr__(self):
        return f"<Price(crypto_id={self.crypto_id}, price=${self.price:.2f}, time={self.datetime})>"


if __name__ == "__main__":
    print("Price model loaded. Use via API integration.")