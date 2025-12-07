"""
Portfolio Model
Handles portfolio creation and management
"""

from datetime import datetime
from database.connection import execute_query
import logging

logger = logging.getLogger(__name__)


class Portfolio:
    """
    Portfolio model for managing user portfolios
    """
    
    def __init__(self, portfolio_id=None, user_id=None, portfolio_name=None,
                 description=None, created_at=None):
        self.portfolio_id = portfolio_id
        self.user_id = user_id
        self.portfolio_name = portfolio_name
        self.description = description
        self.created_at = created_at

    @classmethod
    def create(cls, user_id, portfolio_name, description=None):
        """
        Create a new portfolio
        
        Args:
            user_id (int): User ID who owns the portfolio
            portfolio_name (str): Name of the portfolio
            description (str): Optional description
            
        Returns:
            Portfolio: Newly created portfolio object or None if failed
        """
        try:
            query = """
                INSERT INTO Portfolio (user_id, portfolio_name, description)
                VALUES (%s, %s, %s)
            """
            portfolio_id = execute_query(
                query, 
                (user_id, portfolio_name, description)
            )
            
            logger.info(f"✅ Portfolio '{portfolio_name}' created with ID: {portfolio_id}")
            
            return cls.get_by_id(portfolio_id)
            
        except Exception as e:
            logger.error(f"❌ Error creating portfolio: {e}")
            return None

    @classmethod
    def get_by_id(cls, portfolio_id):
        """
        Get portfolio by ID
        
        Args:
            portfolio_id (int): Portfolio ID
            
        Returns:
            Portfolio: Portfolio object or None if not found
        """
        query = "SELECT * FROM Portfolio WHERE portfolio_id = %s"
        result = execute_query(query, (portfolio_id,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_by_user(cls, user_id):
        """
        Get all portfolios for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of Portfolio objects
        """
        query = """
            SELECT * FROM Portfolio 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """
        results = execute_query(query, (user_id,), fetch_all=True)
        
        return [cls(**row) for row in results] if results else []

    def update(self, **kwargs):
        """
        Update portfolio information
        
        Args:
            **kwargs: Fields to update (portfolio_name, description)
            
        Returns:
            bool: True if update successful
        """
        try:
            fields = []
            values = []
            
            if 'portfolio_name' in kwargs:
                fields.append("portfolio_name = %s")
                values.append(kwargs['portfolio_name'])
                
            if 'description' in kwargs:
                fields.append("description = %s")
                values.append(kwargs['description'])
            
            if not fields:
                return False
            
            values.append(self.portfolio_id)
            query = f"UPDATE Portfolio SET {', '.join(fields)} WHERE portfolio_id = %s"
            
            execute_query(query, tuple(values))
            
            # Update object attributes
            for key, value in kwargs.items():
                setattr(self, key, value)
            
            logger.info(f"✅ Portfolio {self.portfolio_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating portfolio: {e}")
            return False

    def delete(self):
        """
        Delete portfolio (cascade will delete all holdings and transactions)
        
        Returns:
            bool: True if deletion successful
        """
        try:
            query = "DELETE FROM Portfolio WHERE portfolio_id = %s"
            execute_query(query, (self.portfolio_id,))
            
            logger.info(f"✅ Portfolio {self.portfolio_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting portfolio: {e}")
            return False

    def get_total_value(self):
        """
        Calculate total current value of portfolio
        Requires current prices from Price table
        
        Returns:
            float: Total portfolio value in USD
        """
        try:
            query = """
                SELECT 
                    SUM(ph.quantity * p.price) as total_value
                FROM PortfolioHolding ph
                INNER JOIN CryptoCurrency c ON ph.crypto_id = c.crypto_id
                LEFT JOIN (
                    SELECT crypto_id, price
                    FROM Price
                    WHERE (crypto_id, datetime) IN (
                        SELECT crypto_id, MAX(datetime)
                        FROM Price
                        GROUP BY crypto_id
                    )
                ) p ON c.crypto_id = p.crypto_id
                WHERE ph.portfolio_id = %s AND ph.quantity > 0
            """
            result = execute_query(query, (self.portfolio_id,), fetch_one=True)
            
            return float(result['total_value']) if result and result['total_value'] else 0.0
            
        except Exception as e:
            logger.error(f"❌ Error calculating portfolio value: {e}")
            return 0.0

    def get_total_invested(self):
        """
        Get total amount invested in portfolio
        
        Returns:
            float: Total invested amount
        """
        try:
            query = """
                SELECT SUM(total_invested) as total
                FROM PortfolioHolding
                WHERE portfolio_id = %s AND quantity > 0
            """
            result = execute_query(query, (self.portfolio_id,), fetch_one=True)
            
            return float(result['total']) if result and result['total'] else 0.0
            
        except Exception as e:
            logger.error(f"❌ Error getting total invested: {e}")
            return 0.0

    def get_profit_loss(self):
        """
        Calculate profit/loss for portfolio
        
        Returns:
            dict: {'amount': float, 'percentage': float}
        """
        total_value = self.get_total_value()
        total_invested = self.get_total_invested()
        
        if total_invested == 0:
            return {'amount': 0.0, 'percentage': 0.0}
        
        profit_loss = total_value - total_invested
        percentage = (profit_loss / total_invested) * 100
        
        return {
            'amount': profit_loss,
            'percentage': percentage
        }

    def get_holdings(self):
        """
        Get all holdings in this portfolio
        
        Returns:
            list: List of holdings with crypto info
        """
        try:
            query = """
                SELECT 
                    ph.*,
                    c.symbol,
                    c.name,
                    c.logo_url
                FROM PortfolioHolding ph
                INNER JOIN CryptoCurrency c ON ph.crypto_id = c.crypto_id
                WHERE ph.portfolio_id = %s AND ph.quantity > 0
                ORDER BY ph.total_invested DESC
            """
            results = execute_query(query, (self.portfolio_id,), fetch_all=True)
            
            return results if results else []
            
        except Exception as e:
            logger.error(f"❌ Error getting holdings: {e}")
            return []

    def get_holdings_count(self):
        """
        Get number of different cryptocurrencies in portfolio
        
        Returns:
            int: Number of holdings
        """
        query = """
            SELECT COUNT(*) as count
            FROM PortfolioHolding
            WHERE portfolio_id = %s AND quantity > 0
        """
        result = execute_query(query, (self.portfolio_id,), fetch_one=True)
        
        return result['count'] if result else 0

    def to_dict(self):
        """
        Convert portfolio object to dictionary
        
        Returns:
            dict: Portfolio data with calculated values
        """
        return {
            'portfolio_id': self.portfolio_id,
            'user_id': self.user_id,
            'portfolio_name': self.portfolio_name,
            'description': self.description,
            'created_at': self.created_at,
            'total_value': self.get_total_value(),
            'total_invested': self.get_total_invested(),
            'profit_loss': self.get_profit_loss(),
            'holdings_count': self.get_holdings_count()
        }

    def __repr__(self):
        return f"<Portfolio(id={self.portfolio_id}, name='{self.portfolio_name}')>"


# Test functions
def test_portfolio_model():
    """
    Test the Portfolio model
    """
    from models.user import User
    
    print("\n" + "="*50)
    print("Testing Portfolio Model")
    print("="*50)
    
    # Create test user first
    print("\n0. Creating test user...")
    user = User.create("portfoliotest", "pass123", "portfolio@test.com")
    if not user:
        # User might already exist, try to get it
        user = User.get_by_username("portfoliotest")
    print(f"✅ Using user: {user}")
    
    # Test 1: Create portfolio
    print("\n1. Creating new portfolio...")
    portfolio = Portfolio.create(
        user_id=user.user_id,
        portfolio_name="My Crypto Portfolio",
        description="Long-term holdings"
    )
    
    if portfolio:
        print(f"✅ Portfolio created: {portfolio}")
        print(f"   - ID: {portfolio.portfolio_id}")
        print(f"   - Name: {portfolio.portfolio_name}")
        print(f"   - Description: {portfolio.description}")
    else:
        print("❌ Portfolio creation failed")
        return
    
    # Test 2: Create another portfolio
    print("\n2. Creating second portfolio...")
    portfolio2 = Portfolio.create(
        user_id=user.user_id,
        portfolio_name="Day Trading",
        description="Short-term trades"
    )
    print(f"✅ Second portfolio created: {portfolio2}")
    
    # Test 3: Get portfolio by ID
    print("\n3. Getting portfolio by ID...")
    found = Portfolio.get_by_id(portfolio.portfolio_id)
    print(f"✅ Found portfolio: {found}")
    
    # Test 4: Get all portfolios for user
    print("\n4. Getting all portfolios for user...")
    user_portfolios = Portfolio.get_by_user(user.user_id)
    print(f"✅ User has {len(user_portfolios)} portfolio(s):")
    for p in user_portfolios:
        print(f"   - {p}")
    
    # Test 5: Update portfolio
    print("\n5. Updating portfolio name...")
    if portfolio.update(portfolio_name="Updated Portfolio Name"):
        print(f"✅ Name updated to: {portfolio.portfolio_name}")
    
    # Test 6: Get portfolio stats
    print("\n6. Getting portfolio statistics...")
    stats = portfolio.to_dict()
    print(f"✅ Portfolio stats:")
    print(f"   - Total Value: ${stats['total_value']:.2f}")
    print(f"   - Total Invested: ${stats['total_invested']:.2f}")
    print(f"   - Holdings Count: {stats['holdings_count']}")
    
    # Test 7: Delete portfolios
    print("\n7. Deleting test portfolios...")
    portfolio.delete()
    portfolio2.delete()
    print("✅ Portfolios deleted")
    
    # Cleanup: Delete test user
    print("\n8. Cleaning up test user...")
    user.delete()
    print("✅ Test user deleted")
    
    print("\n" + "="*50)
    print("Portfolio Model Tests Complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_portfolio_model()