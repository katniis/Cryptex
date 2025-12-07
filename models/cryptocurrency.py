"""
CryptoCurrency Model
Handles cryptocurrency data and information
"""

from database.connection import execute_query
import logging

logger = logging.getLogger(__name__)


class CryptoCurrency:
    """
    CryptoCurrency model for managing coin data
    """
    
    def __init__(self, crypto_id=None, symbol=None, name=None, 
                 logo_url=None, api_id=None, market_cap_rank=None, is_active=True):
        self.crypto_id = crypto_id
        self.symbol = symbol
        self.name = name
        self.logo_url = logo_url
        self.api_id = api_id
        self.market_cap_rank = market_cap_rank
        self.is_active = is_active

    @classmethod
    def create(cls, symbol, name, api_id=None, logo_url=None, market_cap_rank=None):
        """
        Create a new cryptocurrency entry
        
        Args:
            symbol (str): Ticker symbol (e.g., BTC, ETH)
            name (str): Full name (e.g., Bitcoin, Ethereum)
            api_id (str): CoinMarketCap API ID
            logo_url (str): URL to coin logo
            market_cap_rank (int): Market cap ranking
            
        Returns:
            CryptoCurrency: Newly created crypto object or None if failed
        """
        try:
            query = """
                INSERT INTO CryptoCurrency (symbol, name, api_id, logo_url, market_cap_rank)
                VALUES (%s, %s, %s, %s, %s)
            """
            crypto_id = execute_query(
                query, 
                (symbol, name, api_id, logo_url, market_cap_rank)
            )
            
            logger.info(f"✅ Cryptocurrency '{name}' ({symbol}) created with ID: {crypto_id}")
            
            return cls.get_by_id(crypto_id)
            
        except Exception as e:
            logger.error(f"❌ Error creating cryptocurrency: {e}")
            return None

    @classmethod
    def get_by_id(cls, crypto_id):
        """
        Get cryptocurrency by ID
        
        Args:
            crypto_id (int): Crypto ID
            
        Returns:
            CryptoCurrency: Crypto object or None if not found
        """
        query = "SELECT * FROM CryptoCurrency WHERE crypto_id = %s"
        result = execute_query(query, (crypto_id,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_by_symbol(cls, symbol):
        """
        Get cryptocurrency by symbol
        
        Args:
            symbol (str): Ticker symbol (e.g., BTC)
            
        Returns:
            CryptoCurrency: Crypto object or None if not found
        """
        query = "SELECT * FROM CryptoCurrency WHERE symbol = %s"
        result = execute_query(query, (symbol.upper(),), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_by_api_id(cls, api_id):
        """
        Get cryptocurrency by API ID
        
        Args:
            api_id (str): CoinMarketCap API ID
            
        Returns:
            CryptoCurrency: Crypto object or None if not found
        """
        query = "SELECT * FROM CryptoCurrency WHERE api_id = %s"
        result = execute_query(query, (api_id,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_all(cls, active_only=True):
        """
        Get all cryptocurrencies
        
        Args:
            active_only (bool): Only return active cryptocurrencies
            
        Returns:
            list: List of CryptoCurrency objects
        """
        if active_only:
            query = "SELECT * FROM CryptoCurrency WHERE is_active = TRUE ORDER BY market_cap_rank"
        else:
            query = "SELECT * FROM CryptoCurrency ORDER BY market_cap_rank"
            
        results = execute_query(query, fetch_all=True)
        
        return [cls(**row) for row in results] if results else []

    @classmethod
    def search(cls, search_term):
        """
        Search cryptocurrencies by name or symbol
        
        Args:
            search_term (str): Search query
            
        Returns:
            list: List of matching CryptoCurrency objects
        """
        query = """
            SELECT * FROM CryptoCurrency 
            WHERE (name LIKE %s OR symbol LIKE %s) AND is_active = TRUE
            ORDER BY market_cap_rank
            LIMIT 20
        """
        search_pattern = f"%{search_term}%"
        results = execute_query(query, (search_pattern, search_pattern), fetch_all=True)
        
        return [cls(**row) for row in results] if results else []

    def update(self, **kwargs):
        """
        Update cryptocurrency information
        
        Args:
            **kwargs: Fields to update
            
        Returns:
            bool: True if update successful
        """
        try:
            fields = []
            values = []
            
            allowed_fields = ['name', 'logo_url', 'api_id', 'market_cap_rank', 'is_active']
            
            for field in allowed_fields:
                if field in kwargs:
                    fields.append(f"{field} = %s")
                    values.append(kwargs[field])
            
            if not fields:
                return False
            
            values.append(self.crypto_id)
            query = f"UPDATE CryptoCurrency SET {', '.join(fields)} WHERE crypto_id = %s"
            
            execute_query(query, tuple(values))
            
            # Update object attributes
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(self, key, value)
            
            logger.info(f"✅ Cryptocurrency {self.crypto_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating cryptocurrency: {e}")
            return False

    def deactivate(self):
        """
        Mark cryptocurrency as inactive (delisted)
        
        Returns:
            bool: True if successful
        """
        return self.update(is_active=False)

    def activate(self):
        """
        Mark cryptocurrency as active
        
        Returns:
            bool: True if successful
        """
        return self.update(is_active=True)

    def get_current_price(self):
        """
        Get current price from Price table
        
        Returns:
            dict: Price data or None
        """
        query = """
            SELECT * FROM Price 
            WHERE crypto_id = %s 
            ORDER BY datetime DESC 
            LIMIT 1
        """
        result = execute_query(query, (self.crypto_id,), fetch_one=True)
        return result

    def get_price_history(self, days=30):
        """
        Get price history for specified days
        
        Args:
            days (int): Number of days to retrieve
            
        Returns:
            list: List of price records
        """
        query = """
            SELECT * FROM Price 
            WHERE crypto_id = %s 
            AND datetime >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY datetime ASC
        """
        results = execute_query(query, (self.crypto_id, days), fetch_all=True)
        return results if results else []

    def to_dict(self):
        """
        Convert cryptocurrency object to dictionary
        
        Returns:
            dict: Crypto data
        """
        current_price = self.get_current_price()
        
        return {
            'crypto_id': self.crypto_id,
            'symbol': self.symbol,
            'name': self.name,
            'logo_url': self.logo_url,
            'api_id': self.api_id,
            'market_cap_rank': self.market_cap_rank,
            'is_active': self.is_active,
            'current_price': current_price['price'] if current_price else None
        }

    def __repr__(self):
        return f"<CryptoCurrency(id={self.crypto_id}, symbol='{self.symbol}', name='{self.name}')>"


# Test functions
def test_cryptocurrency_model():
    """
    Test the CryptoCurrency model
    """
    print("\n" + "="*50)
    print("Testing CryptoCurrency Model")
    print("="*50)
    
    # Test 1: Get existing cryptocurrencies
    print("\n1. Getting all cryptocurrencies...")
    all_cryptos = CryptoCurrency.get_all()
    print(f"✅ Found {len(all_cryptos)} cryptocurrencies:")
    for crypto in all_cryptos[:5]:  # Show first 5
        print(f"   - {crypto}")
    
    # Test 2: Get by symbol
    print("\n2. Getting Bitcoin by symbol...")
    btc = CryptoCurrency.get_by_symbol("BTC")
    if btc:
        print(f"✅ Found: {btc}")
        print(f"   - Name: {btc.name}")
        print(f"   - Rank: {btc.market_cap_rank}")
    else:
        print("❌ Bitcoin not found")
    
    # Test 3: Get Ethereum
    print("\n3. Getting Ethereum...")
    eth = CryptoCurrency.get_by_symbol("ETH")
    if eth:
        print(f"✅ Found: {eth}")
    
    # Test 4: Search functionality
    print("\n4. Searching for 'coin'...")
    results = CryptoCurrency.search("coin")
    print(f"✅ Found {len(results)} matches:")
    for crypto in results[:3]:
        print(f"   - {crypto}")
    
    # Test 5: Create new cryptocurrency
    print("\n5. Creating test cryptocurrency...")
    test_crypto = CryptoCurrency.create(
        symbol="TEST",
        name="Test Coin",
        api_id="99999",
        market_cap_rank=999
    )
    if test_crypto:
        print(f"✅ Created: {test_crypto}")
    
    # Test 6: Update cryptocurrency
    if test_crypto:
        print("\n6. Updating test cryptocurrency...")
        test_crypto.update(name="Updated Test Coin", market_cap_rank=1000)
        print(f"✅ Updated: {test_crypto.name}, Rank: {test_crypto.market_cap_rank}")
    
    # Test 7: Deactivate
    if test_crypto:
        print("\n7. Deactivating test cryptocurrency...")
        test_crypto.deactivate()
        print(f"✅ Is active: {test_crypto.is_active}")
    
    # Test 8: Get crypto data as dict
    if btc:
        print("\n8. Getting Bitcoin data as dictionary...")
        btc_dict = btc.to_dict()
        print(f"✅ Bitcoin data:")
        for key, value in btc_dict.items():
            print(f"   - {key}: {value}")
    
    # Cleanup: Delete test crypto
    if test_crypto:
        print("\n9. Cleaning up test cryptocurrency...")
        query = "DELETE FROM CryptoCurrency WHERE crypto_id = %s"
        execute_query(query, (test_crypto.crypto_id,))
        print("✅ Test crypto deleted")
    
    print("\n" + "="*50)
    print("CryptoCurrency Model Tests Complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_cryptocurrency_model()