"""
Watchlist and Alert Models
"""

from datetime import datetime
from database.connection import execute_query
import logging

logger = logging.getLogger(__name__)


# ==================== WATCHLIST MODEL ====================

class Watchlist:
    """
    Watchlist model for tracking cryptocurrencies user wants to monitor
    """
    
    def __init__(self, watchlist_id=None, user_id=None, crypto_id=None, added_at=None):
        self.watchlist_id = watchlist_id
        self.user_id = user_id
        self.crypto_id = crypto_id
        self.added_at = added_at

    @classmethod
    def add(cls, user_id, crypto_id):
        """
        Add cryptocurrency to watchlist
        
        Args:
            user_id (int): User ID
            crypto_id (int): Cryptocurrency ID
            
        Returns:
            Watchlist: Watchlist object or None if failed
        """
        try:
            # Check if already in watchlist
            if cls.is_in_watchlist(user_id, crypto_id):
                logger.info(f"Crypto {crypto_id} already in user {user_id}'s watchlist")
                return cls.get(user_id, crypto_id)
            
            query = """
                INSERT INTO Watchlist (user_id, crypto_id)
                VALUES (%s, %s)
            """
            watchlist_id = execute_query(query, (user_id, crypto_id))
            
            logger.info(f"✅ Added crypto {crypto_id} to watchlist")
            return cls.get_by_id(watchlist_id)
            
        except Exception as e:
            logger.error(f"❌ Error adding to watchlist: {e}")
            return None

    @classmethod
    def get_by_id(cls, watchlist_id):
        """Get watchlist entry by ID"""
        query = "SELECT * FROM Watchlist WHERE watchlist_id = %s"
        result = execute_query(query, (watchlist_id,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get(cls, user_id, crypto_id):
        """Get specific watchlist entry"""
        query = """
            SELECT * FROM Watchlist 
            WHERE user_id = %s AND crypto_id = %s
        """
        result = execute_query(query, (user_id, crypto_id), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_by_user(cls, user_id):
        """
        Get all watchlist entries for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of watchlist entries with crypto info and current price
        """
        query = """
            SELECT 
                w.*,
                c.symbol,
                c.name,
                c.logo_url,
                c.market_cap_rank,
                p.price as current_price,
                p.volume as volume_24h
            FROM Watchlist w
            INNER JOIN CryptoCurrency c ON w.crypto_id = c.crypto_id
            LEFT JOIN (
                SELECT crypto_id, price, volume
                FROM Price
                WHERE (crypto_id, datetime) IN (
                    SELECT crypto_id, MAX(datetime)
                    FROM Price
                    GROUP BY crypto_id
                )
            ) p ON w.crypto_id = p.crypto_id
            WHERE w.user_id = %s
            ORDER BY c.market_cap_rank
        """
        results = execute_query(query, (user_id,), fetch_all=True)
        return results if results else []

    @classmethod
    def is_in_watchlist(cls, user_id, crypto_id):
        """
        Check if crypto is in user's watchlist
        
        Args:
            user_id (int): User ID
            crypto_id (int): Crypto ID
            
        Returns:
            bool: True if in watchlist
        """
        query = """
            SELECT COUNT(*) as count 
            FROM Watchlist 
            WHERE user_id = %s AND crypto_id = %s
        """
        result = execute_query(query, (user_id, crypto_id), fetch_one=True)
        return result['count'] > 0 if result else False

    def remove(self):
        """
        Remove from watchlist
        
        Returns:
            bool: True if successful
        """
        try:
            query = "DELETE FROM Watchlist WHERE watchlist_id = %s"
            execute_query(query, (self.watchlist_id,))
            logger.info(f"✅ Removed from watchlist")
            return True
        except Exception as e:
            logger.error(f"❌ Error removing from watchlist: {e}")
            return False

    @classmethod
    def remove_by_ids(cls, user_id, crypto_id):
        """Remove using user_id and crypto_id"""
        try:
            query = "DELETE FROM Watchlist WHERE user_id = %s AND crypto_id = %s"
            execute_query(query, (user_id, crypto_id))
            logger.info(f"✅ Removed crypto {crypto_id} from user {user_id}'s watchlist")
            return True
        except Exception as e:
            logger.error(f"❌ Error removing from watchlist: {e}")
            return False

    def __repr__(self):
        return f"<Watchlist(id={self.watchlist_id}, user={self.user_id}, crypto={self.crypto_id})>"

if __name__ == "__main__":
    print("Watchlist models loaded.")