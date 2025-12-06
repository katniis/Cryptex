"""
Transaction Model
Handles buy and sell transactions
"""

from datetime import datetime
from database.connection import execute_query
from models.portfolio_holding import PortfolioHolding
import logging

logger = logging.getLogger(__name__)


class Transaction:
    """
    Transaction model for recording buy/sell trades
    """
    
    def __init__(self, transaction_id=None, user_id=None, portfolio_id=None,
                 crypto_id=None, type=None, quantity=None, price_per_unit=None,
                 fee=0.0, exchange=None, notes=None, timestamp=None):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.portfolio_id = portfolio_id
        self.crypto_id = crypto_id
        self.type = type
        self.quantity = float(quantity) if quantity else 0.0
        self.price_per_unit = float(price_per_unit) if price_per_unit else 0.0
        self.fee = float(fee) if fee else 0.0
        self.exchange = exchange
        self.notes = notes
        self.timestamp = timestamp

    @classmethod
    def create(cls, user_id, portfolio_id, crypto_id, transaction_type, 
               quantity, price_per_unit, fee=0.0, exchange=None, notes=None, timestamp=None):
        """
        Create a new transaction and update portfolio holdings
        
        Args:
            user_id (int): User ID
            portfolio_id (int): Portfolio ID
            crypto_id (int): Cryptocurrency ID
            transaction_type (str): 'buy' or 'sell'
            quantity (float): Amount of crypto
            price_per_unit (float): Price per unit
            fee (float): Transaction fee
            exchange (str): Exchange name
            notes (str): Transaction notes
            timestamp (datetime): Transaction timestamp (default: now)
            
        Returns:
            Transaction: Newly created transaction or None if failed
        """
        try:
            # Validate transaction type
            if transaction_type not in ['buy', 'sell']:
                logger.error("Invalid transaction type. Must be 'buy' or 'sell'")
                return None
            
            # For sell transactions, check if user has enough
            if transaction_type == 'sell':
                holding = PortfolioHolding.get_by_portfolio_and_crypto(portfolio_id, crypto_id)
                if not holding or holding.quantity < quantity:
                    logger.error(f"❌ Insufficient balance. Have: {holding.quantity if holding else 0}, Trying to sell: {quantity}")
                    return None
            
            # Use current timestamp if not provided
            if timestamp is None:
                timestamp = datetime.now()
            
            # Insert transaction
            query = """
                INSERT INTO Transaction 
                (user_id, portfolio_id, crypto_id, type, quantity, price_per_unit, fee, exchange, notes, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            transaction_id = execute_query(
                query,
                (user_id, portfolio_id, crypto_id, transaction_type, quantity, 
                 price_per_unit, fee, exchange, notes, timestamp)
            )
            
            # Update portfolio holding
            holding = PortfolioHolding.get_or_create(portfolio_id, crypto_id)
            is_buy = (transaction_type == 'buy')
            holding.update_holding(quantity, price_per_unit, is_buy)
            
            logger.info(f"✅ Transaction created: {transaction_type.upper()} {quantity} crypto_id={crypto_id}")
            
            return cls.get_by_id(transaction_id)
            
        except Exception as e:
            logger.error(f"❌ Error creating transaction: {e}")
            return None

    @classmethod
    def get_by_id(cls, transaction_id):
        """
        Get transaction by ID
        
        Args:
            transaction_id (int): Transaction ID
            
        Returns:
            Transaction: Transaction object or None
        """
        query = "SELECT * FROM Transaction WHERE transaction_id = %s"
        result = execute_query(query, (transaction_id,), fetch_one=True)
        
        if result:
            return cls(**result)
        return None

    @classmethod
    def get_by_portfolio(cls, portfolio_id, limit=None):
        """
        Get all transactions for a portfolio
        
        Args:
            portfolio_id (int): Portfolio ID
            limit (int): Optional limit on number of results
            
        Returns:
            list: List of transactions with crypto info
        """
        if limit:
            query = """
                SELECT t.*, c.symbol, c.name, c.logo_url
                FROM Transaction t
                INNER JOIN CryptoCurrency c ON t.crypto_id = c.crypto_id
                WHERE t.portfolio_id = %s
                ORDER BY t.timestamp DESC
                LIMIT %s
            """
            results = execute_query(query, (portfolio_id, limit), fetch_all=True)
        else:
            query = """
                SELECT t.*, c.symbol, c.name, c.logo_url
                FROM Transaction t
                INNER JOIN CryptoCurrency c ON t.crypto_id = c.crypto_id
                WHERE t.portfolio_id = %s
                ORDER BY t.timestamp DESC
            """
            results = execute_query(query, (portfolio_id,), fetch_all=True)
        
        return results if results else []

    @classmethod
    def get_by_user(cls, user_id, limit=None):
        """
        Get all transactions for a user (across all portfolios)
        
        Args:
            user_id (int): User ID
            limit (int): Optional limit
            
        Returns:
            list: List of transactions
        """
        if limit:
            query = """
                SELECT t.*, c.symbol, c.name, p.portfolio_name
                FROM Transaction t
                INNER JOIN CryptoCurrency c ON t.crypto_id = c.crypto_id
                INNER JOIN Portfolio p ON t.portfolio_id = p.portfolio_id
                WHERE t.user_id = %s
                ORDER BY t.timestamp DESC
                LIMIT %s
            """
            results = execute_query(query, (user_id, limit), fetch_all=True)
        else:
            query = """
                SELECT t.*, c.symbol, c.name, p.portfolio_name
                FROM Transaction t
                INNER JOIN CryptoCurrency c ON t.crypto_id = c.crypto_id
                INNER JOIN Portfolio p ON t.portfolio_id = p.portfolio_id
                WHERE t.user_id = %s
                ORDER BY t.timestamp DESC
            """
            results = execute_query(query, (user_id,), fetch_all=True)
        
        return results if results else []

    @classmethod
    def get_by_crypto(cls, portfolio_id, crypto_id):
        """
        Get all transactions for a specific crypto in a portfolio
        
        Args:
            portfolio_id (int): Portfolio ID
            crypto_id (int): Cryptocurrency ID
            
        Returns:
            list: List of transactions
        """
        query = """
            SELECT t.*, c.symbol, c.name
            FROM Transaction t
            INNER JOIN CryptoCurrency c ON t.crypto_id = c.crypto_id
            WHERE t.portfolio_id = %s AND t.crypto_id = %s
            ORDER BY t.timestamp DESC
        """
        results = execute_query(query, (portfolio_id, crypto_id), fetch_all=True)
        return results if results else []

    def update(self, **kwargs):
        """
        Update transaction (limited fields - quantity changes affect holdings)
        
        Args:
            **kwargs: Fields to update (notes, exchange, fee)
            
        Returns:
            bool: True if successful
        """
        try:
            fields = []
            values = []
            
            # Only allow updating certain fields
            allowed_fields = ['notes', 'exchange', 'fee']
            
            for field in allowed_fields:
                if field in kwargs:
                    fields.append(f"{field} = %s")
                    values.append(kwargs[field])
            
            if not fields:
                return False
            
            values.append(self.transaction_id)
            query = f"UPDATE Transaction SET {', '.join(fields)} WHERE transaction_id = %s"
            
            execute_query(query, tuple(values))
            
            # Update object attributes
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(self, key, value)
            
            logger.info(f"✅ Transaction {self.transaction_id} updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating transaction: {e}")
            return False

    def delete(self):
        """
        Delete transaction and reverse its effect on holdings
        WARNING: This reverses the transaction from holdings
        
        Returns:
            bool: True if successful
        """
        try:
            # Get holding
            holding = PortfolioHolding.get_by_portfolio_and_crypto(
                self.portfolio_id, 
                self.crypto_id
            )
            
            if holding:
                # Reverse the transaction
                if self.type == 'buy':
                    # Reverse buy = sell the amount
                    holding.update_holding(self.quantity, self.price_per_unit, is_buy=False)
                else:
                    # Reverse sell = buy back the amount
                    holding.update_holding(self.quantity, self.price_per_unit, is_buy=True)
            
            # Delete transaction record
            query = "DELETE FROM Transaction WHERE transaction_id = %s"
            execute_query(query, (self.transaction_id,))
            
            logger.info(f"✅ Transaction {self.transaction_id} deleted and reversed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting transaction: {e}")
            return False

    def get_total_cost(self):
        """
        Calculate total cost/revenue including fees
        
        Returns:
            float: Total amount (positive for buy, negative for sell)
        """
        base_amount = self.quantity * self.price_per_unit
        
        if self.type == 'buy':
            return base_amount + self.fee
        else:  # sell
            return base_amount - self.fee

    def to_dict(self):
        """
        Convert to dictionary
        
        Returns:
            dict: Transaction data
        """
        return {
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'portfolio_id': self.portfolio_id,
            'crypto_id': self.crypto_id,
            'type': self.type,
            'quantity': self.quantity,
            'price_per_unit': self.price_per_unit,
            'fee': self.fee,
            'exchange': self.exchange,
            'notes': self.notes,
            'timestamp': self.timestamp,
            'total_cost': self.get_total_cost()
        }

    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, type='{self.type}', qty={self.quantity})>"


# Test functions
def test_transaction_model():
    """
    Test the Transaction model
    """
    from models.user import User
    from models.portfolio import Portfolio
    from models.cryptocurrency import CryptoCurrency
    
    print("\n" + "="*50)
    print("Testing Transaction Model")
    print("="*50)
    
    # Setup
    print("\n0. Setting up test data...")
    user = User.create("transtest", "pass123", "trans@test.com")
    if not user:
        user = User.get_by_username("transtest")
    
    portfolio = Portfolio.create(user.user_id, "Trading Portfolio")
    btc = CryptoCurrency.get_by_symbol("BTC")
    eth = CryptoCurrency.get_by_symbol("ETH")
    
    print(f"✅ Setup complete")
    
    # Test 1: Buy BTC
    print("\n1. Creating BUY transaction for 0.5 BTC...")
    tx1 = Transaction.create(
        user_id=user.user_id,
        portfolio_id=portfolio.portfolio_id,
        crypto_id=btc.crypto_id,
        transaction_type='buy',
        quantity=0.5,
        price_per_unit=50000,
        fee=25,
        exchange='Binance',
        notes='First BTC purchase'
    )
    if tx1:
        print(f"✅ Transaction created: {tx1}")
        print(f"   Total cost: ${tx1.get_total_cost():.2f}")
    
    # Test 2: Buy more BTC
    print("\n2. Buying more BTC...")
    tx2 = Transaction.create(
        user_id=user.user_id,
        portfolio_id=portfolio.portfolio_id,
        crypto_id=btc.crypto_id,
        transaction_type='buy',
        quantity=0.3,
        price_per_unit=55000,
        fee=15
    )
    print(f"✅ Second buy: {tx2}")
    
    # Test 3: Buy ETH
    print("\n3. Buying ETH...")
    tx3 = Transaction.create(
        user_id=user.user_id,
        portfolio_id=portfolio.portfolio_id,
        crypto_id=eth.crypto_id,
        transaction_type='buy',
        quantity=2.0,
        price_per_unit=3000,
        fee=10,
        exchange='Coinbase'
    )
    print(f"✅ ETH buy: {tx3}")
    
    # Test 4: Sell some BTC
    print("\n4. Selling 0.2 BTC...")
    tx4 = Transaction.create(
        user_id=user.user_id,
        portfolio_id=portfolio.portfolio_id,
        crypto_id=btc.crypto_id,
        transaction_type='sell',
        quantity=0.2,
        price_per_unit=60000,
        fee=10,
        notes='Taking profits'
    )
    print(f"✅ Sell transaction: {tx4}")
    
    # Test 5: Get all portfolio transactions
    print("\n5. Getting all transactions for portfolio...")
    transactions = Transaction.get_by_portfolio(portfolio.portfolio_id)
    print(f"✅ Found {len(transactions)} transactions:")
    for tx in transactions:
        print(f"   - {tx.get('type').upper()}: {tx.get('quantity')} {tx.get('symbol')} @ ${tx.get('price_per_unit')}")
    
    # Test 6: Get BTC transactions only
    print("\n6. Getting BTC transactions only...")
    btc_txs = Transaction.get_by_crypto(portfolio.portfolio_id, btc.crypto_id)
    print(f"✅ Found {len(btc_txs)} BTC transactions")
    
    # Test 7: Try to sell more than owned (should fail)
    print("\n7. Testing insufficient balance check...")
    tx_fail = Transaction.create(
        user_id=user.user_id,
        portfolio_id=portfolio.portfolio_id,
        crypto_id=btc.crypto_id,
        transaction_type='sell',
        quantity=10.0,  # More than we have
        price_per_unit=60000
    )
    if not tx_fail:
        print("✅ Correctly prevented selling more than owned")
    
    # Test 8: Update transaction notes
    print("\n8. Updating transaction notes...")
    if tx1:
        tx1.update(notes="Updated: My first BTC!")
        print(f"✅ Notes updated: {tx1.notes}")
    
    # Test 9: Delete a transaction
    print("\n9. Deleting a transaction...")
    if tx2:
        tx2.delete()
        print("✅ Transaction deleted and reversed from holdings")
    
    # Cleanup
    print("\n10. Cleaning up...")
    portfolio.delete()
    user.delete()
    print("✅ Cleanup complete")
    
    print("\n" + "="*50)
    print("Transaction Model Tests Complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_transaction_model()