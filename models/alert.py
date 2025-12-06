"""
Watchlist and Alert Models
"""

from datetime import datetime
from database.connection import execute_query
import logging

logger = logging.getLogger(__name__)

class Alert:
    """
    Alert model for price notifications
    """
    
    def __init__(self, alert_id=None, user_id=None, crypto_id=None, 
                 condition=None, target_price=None, is_active=True, created_at=None):
        self.alert_id = alert_id
        self.user_id = user_id
        self.crypto_id = crypto_id
        self.condition = condition  # 'above' or 'below'
        self.target_price = float(target_price) if target_price else 0.0
        self.is_active = is_active
        self.created_at = created_at

    @classmethod
    def create(cls, user_id, crypto_id, condition, target_price):
        """
        Create a new price alert
        
        Args:
            user_id (int): User ID
            crypto_id (int): Cryptocurrency ID
            condition (str): 'above' or 'below'
            target_price (float): Target price in USD
            
        Returns:
            Alert: Alert object or None if failed
        """
        try:
            if condition not in ['above', 'below']:
                logger.error("Invalid condition. Must be 'above' or 'below'")
                return None
            
            query = """
                INSERT INTO Alert (user_id, crypto_id, condition, target_price)
                VALUES (%s, %s, %s, %s)
            """
            alert_id = execute_query(query, (user_id, crypto_id, condition, target_price))
            
            logger.info(f"✅ Alert created: crypto {crypto_id} {condition} ${target_price}")
            return cls.get_by_id(alert_id)
            
        except Exception as e:
            logger.error(f"❌ Error creating alert: {e}")
            return None

    @classmethod
    def get_by_id(cls, alert_id):
        """Get alert by ID"""
        query = "SELECT * FROM Alert WHERE alert_id = %s"
        result = execute_query(query, (alert_id,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_by_user(cls, user_id, active_only=True):
        """
        Get all alerts for a user
        
        Args:
            user_id (int): User ID
            active_only (bool): Only return active alerts
            
        Returns:
            list: List of alerts with crypto info and current price
        """
        if active_only:
            query = """
                SELECT 
                    a.*,
                    c.symbol,
                    c.name,
                    c.logo_url,
                    p.price as current_price
                FROM Alert a
                INNER JOIN CryptoCurrency c ON a.crypto_id = c.crypto_id
                LEFT JOIN (
                    SELECT crypto_id, price
                    FROM Price
                    WHERE (crypto_id, datetime) IN (
                        SELECT crypto_id, MAX(datetime)
                        FROM Price
                        GROUP BY crypto_id
                    )
                ) p ON a.crypto_id = p.crypto_id
                WHERE a.user_id = %s AND a.is_active = TRUE
                ORDER BY a.created_at DESC
            """
        else:
            query = """
                SELECT 
                    a.*,
                    c.symbol,
                    c.name,
                    p.price as current_price
                FROM Alert a
                INNER JOIN CryptoCurrency c ON a.crypto_id = c.crypto_id
                LEFT JOIN (
                    SELECT crypto_id, price
                    FROM Price
                    WHERE (crypto_id, datetime) IN (
                        SELECT crypto_id, MAX(datetime)
                        FROM Price
                        GROUP BY crypto_id
                    )
                ) p ON a.crypto_id = p.crypto_id
                WHERE a.user_id = %s
                ORDER BY a.created_at DESC
            """
        
        results = execute_query(query, (user_id,), fetch_all=True)
        return results if results else []

    @classmethod
    def get_triggered_alerts(cls):
        """
        Get all alerts that should be triggered based on current prices
        
        Returns:
            list: List of triggered alerts
        """
        query = """
            SELECT 
                a.*,
                c.symbol,
                c.name,
                p.price as current_price
            FROM Alert a
            INNER JOIN CryptoCurrency c ON a.crypto_id = c.crypto_id
            INNER JOIN (
                SELECT crypto_id, price
                FROM Price
                WHERE (crypto_id, datetime) IN (
                    SELECT crypto_id, MAX(datetime)
                    FROM Price
                    GROUP BY crypto_id
                )
            ) p ON a.crypto_id = p.crypto_id
            WHERE a.is_active = TRUE
            AND (
                (a.condition = 'above' AND p.price >= a.target_price)
                OR
                (a.condition = 'below' AND p.price <= a.target_price)
            )
        """
        results = execute_query(query, fetch_all=True)
        return results if results else []

    def update(self, **kwargs):
        """
        Update alert
        
        Args:
            **kwargs: Fields to update (condition, target_price, is_active)
            
        Returns:
            bool: True if successful
        """
        try:
            fields = []
            values = []
            
            allowed_fields = ['condition', 'target_price', 'is_active']
            
            for field in allowed_fields:
                if field in kwargs:
                    fields.append(f"{field} = %s")
                    values.append(kwargs[field])
            
            if not fields:
                return False
            
            values.append(self.alert_id)
            query = f"UPDATE Alert SET {', '.join(fields)} WHERE alert_id = %s"
            
            execute_query(query, tuple(values))
            
            # Update object
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(self, key, value)
            
            logger.info(f"✅ Alert {self.alert_id} updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating alert: {e}")
            return False

    def deactivate(self):
        """Deactivate alert"""
        return self.update(is_active=False)

    def activate(self):
        """Activate alert"""
        return self.update(is_active=True)

    def delete(self):
        """
        Delete alert
        
        Returns:
            bool: True if successful
        """
        try:
            query = "DELETE FROM Alert WHERE alert_id = %s"
            execute_query(query, (self.alert_id,))
            logger.info(f"✅ Alert {self.alert_id} deleted")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting alert: {e}")
            return False

    def is_triggered(self, current_price):
        """
        Check if alert should be triggered
        
        Args:
            current_price (float): Current cryptocurrency price
            
        Returns:
            bool: True if triggered
        """
        if not self.is_active:
            return False
        
        if self.condition == 'above':
            return current_price >= self.target_price
        else:  # below
            return current_price <= self.target_price

    def __repr__(self):
        return f"<Alert(id={self.alert_id}, crypto={self.crypto_id}, {self.condition} ${self.target_price})>"


if __name__ == "__main__":
    print("Alert models loaded.")