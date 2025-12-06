-- Crypto Portfolio Tracker Database Schema
-- Drop database if exists (USE WITH CAUTION!)
-- DROP DATABASE IF EXISTS crypto_portfolio_tracker;

-- Create database
CREATE DATABASE IF NOT EXISTS cryptex;
USE cryptex;

-- =====================================================
-- User Table
-- =====================================================
CREATE TABLE IF NOT EXISTS User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_address VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Portfolio Table
-- =====================================================
CREATE TABLE IF NOT EXISTS Portfolio (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    portfolio_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- CryptoCurrency Table
-- =====================================================
CREATE TABLE IF NOT EXISTS CryptoCurrency (
    crypto_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    logo_url VARCHAR(255),
    api_id VARCHAR(50),
    market_cap_rank INT,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_symbol (symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- PortfolioHolding Table (Junction table for current holdings)
-- =====================================================
CREATE TABLE IF NOT EXISTS PortfolioHolding (
    holding_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    crypto_id INT NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL DEFAULT 0,
    average_buy_price DECIMAL(20, 2) NOT NULL DEFAULT 0,
    total_invested DECIMAL(20, 2) NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES Portfolio(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (crypto_id) REFERENCES CryptoCurrency(crypto_id) ON DELETE CASCADE,
    UNIQUE KEY unique_portfolio_crypto (portfolio_id, crypto_id),
    INDEX idx_portfolio_id (portfolio_id),
    INDEX idx_crypto_id (crypto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Transaction Table
-- =====================================================
CREATE TABLE IF NOT EXISTS Transaction (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    portfolio_id INT NOT NULL,
    crypto_id INT NOT NULL,
    type ENUM('buy', 'sell') NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    price_per_unit DECIMAL(20, 2) NOT NULL,
    fee DECIMAL(20, 2) DEFAULT 0,
    exchange VARCHAR(50),
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (portfolio_id) REFERENCES Portfolio(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (crypto_id) REFERENCES CryptoCurrency(crypto_id) ON DELETE CASCADE,
    INDEX idx_portfolio_id (portfolio_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_crypto_id (crypto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Price Table (Historical price data)
-- =====================================================
CREATE TABLE IF NOT EXISTS Price (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    crypto_id INT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    price DECIMAL(20, 2) NOT NULL,
    volume DECIMAL(30, 2),
    market_cap DECIMAL(30, 2),
    source VARCHAR(50),
    FOREIGN KEY (crypto_id) REFERENCES CryptoCurrency(crypto_id) ON DELETE CASCADE,
    UNIQUE KEY unique_crypto_datetime (crypto_id, datetime),
    INDEX idx_crypto_id (crypto_id),
    INDEX idx_datetime (datetime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Watchlist Table
-- =====================================================
CREATE TABLE IF NOT EXISTS Watchlist (
    watchlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    crypto_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (crypto_id) REFERENCES CryptoCurrency(crypto_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_crypto (user_id, crypto_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Alert Table
-- =====================================================
CREATE TABLE IF NOT EXISTS Alert (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    crypto_id INT NOT NULL,
    alert_condition ENUM('above', 'below') NOT NULL,
    target_price DECIMAL(20, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (crypto_id) REFERENCES CryptoCurrency(crypto_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Insert Sample Cryptocurrencies
-- =====================================================
INSERT INTO CryptoCurrency (symbol, name, api_id, market_cap_rank, is_active) VALUES
('BTC', 'Bitcoin', '1', 1, TRUE),
('ETH', 'Ethereum', '1027', 2, TRUE),
('USDT', 'Tether', '825', 3, TRUE),
('BNB', 'BNB', '1839', 4, TRUE),
('SOL', 'Solana', '5426', 5, TRUE),
('XRP', 'XRP', '52', 6, TRUE),
('USDC', 'USD Coin', '3408', 7, TRUE),
('ADA', 'Cardano', '2010', 8, TRUE),
('DOGE', 'Dogecoin', '74', 9, TRUE),
('TRX', 'TRON', '1958', 10, TRUE)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- =====================================================
-- Useful Views (Optional but helpful)
-- =====================================================

-- View: Portfolio Summary
CREATE OR REPLACE VIEW vw_portfolio_summary AS
SELECT 
    p.portfolio_id,
    p.user_id,
    p.portfolio_name,
    COUNT(DISTINCT ph.crypto_id) as total_coins,
    SUM(ph.total_invested) as total_invested,
    p.created_at
FROM Portfolio p
LEFT JOIN PortfolioHolding ph ON p.portfolio_id = ph.portfolio_id
WHERE ph.quantity > 0
GROUP BY p.portfolio_id, p.user_id, p.portfolio_name, p.created_at;

-- View: Asset Holdings with Current Info
CREATE OR REPLACE VIEW vw_asset_holdings AS
SELECT 
    ph.holding_id,
    ph.portfolio_id,
    ph.crypto_id,
    c.symbol,
    c.name,
    c.logo_url,
    ph.quantity,
    ph.average_buy_price,
    ph.total_invested,
    ph.last_updated
FROM PortfolioHolding ph
INNER JOIN CryptoCurrency c ON ph.crypto_id = c.crypto_id
WHERE ph.quantity > 0;

-- =====================================================
-- End of Schema
-- =====================================================