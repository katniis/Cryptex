"""
PortfolioHolding Model
Manages current holdings in portfolios (junction table with aggregated data)
"""

from database.connection import execute_query
import logging

logger = logging.getLogger(__name__)


class PortfolioHolding:
    """
    PortfolioHolding model - tracks current cryptocurrency holdings in portfolios
    """
    
    def __init__(self, holding_id=None, portfolio_id=None, crypto_id=None,
                 quantity=0.0, average_buy_price=0.0, total_invested=0.0, 
                 last_updated=None):
        self.holding_id = holding_id
        self.portfolio_id = portfolio_id
        self.crypto_id = crypto_id
        self.quantity = float(quantity) if quantity else 0.0
        self.average_buy_price = float(average_buy_price) if average_buy_price else 0.0
        self.total_invested = float(total_invested) if total_invested else 0.0
        self.last_updated = last_updated

    @classmethod
    def get_or_create(cls, portfolio_id, crypto_id):
        """
        Get existing holding or create new one
        
        Args:
            portfolio_id (int): Portfolio ID
            crypto_id (int): Cryptocurrency ID
            
        Returns:
            PortfolioHolding: Holding object
        """
        holding = cls.get_by_portfolio_and_crypto(portfolio_id, crypto_id)
        
        if not holding:
            try:
                query = """
                    INSERT INTO PortfolioHolding (portfolio_id, crypto_id, quantity, average_buy_price, total_invested)
                    VALUES (%s, %s, 0, 0, 0)
                """
                holding_id = execute_query(query, (portfolio_id, crypto_id))
                holding = cls.get_by_id(holding_id)
                logger.info(f"✅ New holding created: Portfolio {portfolio_id}, Crypto {crypto_id}")
            except Exception as e:
                logger.error(f"❌ Error creating holding: {e}")
                return None
        
        return holding

    @classmethod
    def get_by_id(cls, holding_id):
        """
        Get holding by ID
        
        Args:
            holding_id (int): Holding ID
            
        Returns:
            PortfolioHolding: Holding object or None
        """
        query = "SELECT * FROM PortfolioHolding WHERE holding_id = %s"
        result = execute_query(query, (holding_id,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_by_portfolio_and_crypto(cls, portfolio_id, crypto_id):
        """
        Get holding for specific portfolio and crypto
        
        Args:
            portfolio_id (int): Portfolio ID
            crypto_id (int): Cryptocurrency ID
            
        Returns:
            PortfolioHolding: Holding object or None
        """
        query = """
            SELECT * FROM PortfolioHolding 
            WHERE portfolio_id = %s AND crypto_id = %s
        """
        result = execute_query(query, (portfolio_id, crypto_id), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_by_portfolio(cls, portfolio_id, active_only=True):
        """
        Get all holdings for a portfolio
        
        Args:
            portfolio_id (int): Portfolio ID
            active_only (bool): Only return holdings with quantity > 0
            
        Returns:
            list: List of PortfolioHolding objects with crypto info
        """
        if active_only:
            query = """
                SELECT ph.*, c.symbol, c.name, c.logo_url
                FROM PortfolioHolding ph
                INNER JOIN CryptoCurrency c ON ph.crypto_id = c.crypto_id
                WHERE ph.portfolio_id = %s AND ph.quantity > 0
                ORDER BY ph.total_invested DESC
            """
        else:
            query = """
                SELECT ph.*, c.symbol, c.name, c.logo_url
                FROM PortfolioHolding ph
                INNER JOIN CryptoCurrency c ON ph.crypto_id = c.crypto_id
                WHERE ph.portfolio_id = %s
                ORDER BY ph.total_invested DESC
            """
        
        results = execute_query(query, (portfolio_id,), fetch_all=True)
        return results if results else []

    def update_holding(self, quantity_change, price_per_unit, is_buy=True):
        """
        Update holding after a transaction
        
        Args:
            quantity_change (float): Amount bought or sold
            price_per_unit (float): Price per unit
            is_buy (bool): True for buy, False for sell
            
        Returns:
            bool: True if successful
        """
        try:
            if is_buy:
                # Calculate new average buy price
                new_quantity = self.quantity + quantity_change
                new_invested = self.total_invested + (quantity_change * price_per_unit)
                new_avg_price = new_invested / new_quantity if new_quantity > 0 else 0
                
                query = """
                    UPDATE PortfolioHolding 
                    SET quantity = %s, 
                        average_buy_price = %s, 
                        total_invested = %s,
                        last_updated = NOW()
                    WHERE holding_id = %s
                """
                execute_query(query, (new_quantity, new_avg_price, new_invested, self.holding_id))
                
                # Update object
                self.quantity = new_quantity
                self.average_buy_price = new_avg_price
                self.total_invested = new_invested
                
            else:  # Sell
                new_quantity = self.quantity - quantity_change
                
                if new_quantity < 0:
                    logger.error("❌ Cannot sell more than owned")
                    return False
                
                # Proportionally reduce total_invested
                if self.quantity > 0:
                    reduction_ratio = quantity_change / self.quantity
                    new_invested = self.total_invested * (1 - reduction_ratio)
                else:
                    new_invested = 0
                
                query = """
                    UPDATE PortfolioHolding 
                    SET quantity = %s, 
                        total_invested = %s,
                        last_updated = NOW()
                    WHERE holding_id = %s
                """
                execute_query(query, (new_quantity, new_invested, self.holding_id))
                
                # Update object
                self.quantity = new_quantity
                self.total_invested = new_invested
            
            logger.info(f"✅ Holding {self.holding_id} updated: quantity={self.quantity}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating holding: {e}")
            return False

    def get_current_value(self):
        """
        Get current value of holding based on latest price
        
        Returns:
            float: Current value in USD
        """
        try:
            query = """
                SELECT price FROM Price 
                WHERE crypto_id = %s 
                ORDER BY datetime DESC 
                LIMIT 1
            """
            result = execute_query(query, (self.crypto_id,), fetch_one=True)
            
            if result:
                return self.quantity * float(result['price'])
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Error getting current value: {e}")
            return 0.0

    def get_profit_loss(self):
        """
        Calculate profit/loss for this holding
        
        Returns:
            dict: {'amount': float, 'percentage': float}
        """
        current_value = self.get_current_value()
        
        if self.total_invested == 0:
            return {'amount': 0.0, 'percentage': 0.0}
        
        profit_loss = current_value - self.total_invested
        percentage = (profit_loss / self.total_invested) * 100
        
        return {
            'amount': profit_loss,
            'percentage': percentage
        }

    def delete(self):
        """
        Delete holding
        
        Returns:
            bool: True if successful
        """
        try:
            query = "DELETE FROM PortfolioHolding WHERE holding_id = %s"
            execute_query(query, (self.holding_id,))
            logger.info(f"✅ Holding {self.holding_id} deleted")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting holding: {e}")
            return False

    def to_dict(self):
        """
        Convert to dictionary
        
        Returns:
            dict: Holding data with calculated values
        """
        return {
            'holding_id': self.holding_id,
            'portfolio_id': self.portfolio_id,
            'crypto_id': self.crypto_id,
            'quantity': self.quantity,
            'average_buy_price': self.average_buy_price,
            'total_invested': self.total_invested,
            'current_value': self.get_current_value(),
            'profit_loss': self.get_profit_loss(),
            'last_updated': self.last_updated
        }

    def __repr__(self):
        return f"<PortfolioHolding(id={self.holding_id}, portfolio={self.portfolio_id}, crypto={self.crypto_id}, qty={self.quantity})>"


# Test functions
def test_portfolio_holding_model():
    """
    Test the PortfolioHolding model
    """
    from models.user import User
    from models.portfolio import Portfolio
    from models.cryptocurrency import CryptoCurrency
    
    print("\n" + "="*50)
    print("Testing PortfolioHolding Model")
    print("="*50)
    
    # Setup: Create test user and portfolio
    print("\n0. Setting up test data...")
    user = User.create("holdingtest", "pass123", "holding@test.com")
    if not user:
        user = User.get_by_username("holdingtest")
    
    portfolio = Portfolio.create(user.user_id, "Test Holdings Portfolio")
    btc = CryptoCurrency.get_by_symbol("BTC")
    eth = CryptoCurrency.get_by_symbol("ETH")
    
    print(f"✅ Setup complete: Portfolio {portfolio.portfolio_id}")
    
    # Test 1: Get or create holding
    print("\n1. Creating BTC holding...")
    btc_holding = PortfolioHolding.get_or_create(portfolio.portfolio_id, btc.crypto_id)
    print(f"✅ BTC holding: {btc_holding}")
    
    # Test 2: Buy BTC
    print("\n2. Buying 0.5 BTC at $50,000...")
    btc_holding.update_holding(quantity_change=0.5, price_per_unit=50000, is_buy=True)
    print(f"✅ After buy: quantity={btc_holding.quantity}, avg_price=${btc_holding.average_buy_price:.2f}")
    
    # Test 3: Buy more BTC
    print("\n3. Buying 0.3 more BTC at $55,000...")
    btc_holding.update_holding(quantity_change=0.3, price_per_unit=55000, is_buy=True)
    print(f"✅ After 2nd buy: quantity={btc_holding.quantity}, avg_price=${btc_holding.average_buy_price:.2f}")
    
    # Test 4: Create ETH holding
    print("\n4. Creating ETH holding and buying...")
    eth_holding = PortfolioHolding.get_or_create(portfolio.portfolio_id, eth.crypto_id)
    eth_holding.update_holding(quantity_change=2.0, price_per_unit=3000, is_buy=True)
    print(f"✅ ETH holding: quantity={eth_holding.quantity}, invested=${eth_holding.total_invested:.2f}")
    
    # Test 5: Get all holdings
    print("\n5. Getting all portfolio holdings...")
    holdings = PortfolioHolding.get_by_portfolio(portfolio.portfolio_id)
    print(f"✅ Found {len(holdings)} holdings:")
    for h in holdings:
        print(f"   - {h.get('name')}: {h.get('quantity')} @ ${h.get('average_buy_price'):.2f}")
    
    # Test 6: Sell some BTC
    print("\n6. Selling 0.2 BTC...")
    btc_holding.update_holding(quantity_change=0.2, price_per_unit=60000, is_buy=False)
    print(f"✅ After sell: quantity={btc_holding.quantity}, invested=${btc_holding.total_invested:.2f}")
    
    # Test 7: Get holding details
    print("\n7. Getting holding details...")
    holding_dict = btc_holding.to_dict()
    print(f"✅ BTC Holding details:")
    for key, value in holding_dict.items():
        if isinstance(value, dict):
            print(f"   - {key}: {value}")
        elif isinstance(value, float):
            print(f"   - {key}: {value:.4f}")
        else:
            print(f"   - {key}: {value}")
    
    # Cleanup
    print("\n8. Cleaning up...")
    portfolio.delete()
    user.delete()
    print("✅ Cleanup complete")
    
    print("\n" + "="*50)
    print("PortfolioHolding Model Tests Complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_portfolio_holding_model()