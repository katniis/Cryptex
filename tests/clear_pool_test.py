from database.connection import DatabaseConnection
from api.coinmarketcap_api import CoinMarketCapAPI

# Force clear the connection pool
DatabaseConnection._connection_pool = None

print("Connection pool cleared!")

# Now test the API
api = CoinMarketCapAPI()
print("Updating prices...")
updated = api.update_database_prices(['BTC', 'ETH', 'USDT'])
print(f"✅ Updated {updated} prices")