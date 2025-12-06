"""
Database Configuration
Contains MySQL database connection settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'cryptex'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'autocommit': True,
    'raise_on_warnings': True
}

# Connection Pool Settings
POOL_CONFIG = {
    'pool_name': 'crypto_pool',
    'pool_size': 5,
    'pool_reset_session': True
}