-- Phase 3.5: Data Persistence & Advanced Tables
-- Migration: Add user_watchlists and user_preferences tables
-- Date: January 13, 2026

-- =====================================================
-- 1. USER_WATCHLISTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS user_watchlists (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Price tracking
    price DECIMAL(10, 2),
    initial_price DECIMAL(10, 2),  -- Price when first added (for change calculation)
    change DECIMAL(10, 2),
    change_percent DECIMAL(5, 2),
    last_updated TIMESTAMP,
    
    -- Alpaca sync
    alpaca_synced BOOLEAN DEFAULT FALSE,
    alpaca_watchlist_id VARCHAR(50),
    
    -- Constraints
    CONSTRAINT unique_user_symbol UNIQUE (user_id, symbol)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_watchlist_user ON user_watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_symbol ON user_watchlists(symbol);
CREATE INDEX IF NOT EXISTS idx_watchlist_alpaca_id ON user_watchlists(alpaca_watchlist_id);

COMMENT ON TABLE user_watchlists IS 'User watchlist with Alpaca sync support';
COMMENT ON COLUMN user_watchlists.initial_price IS 'Price when symbol was first added to watchlist';
COMMENT ON COLUMN user_watchlists.alpaca_synced IS 'Whether this symbol has been synced to Alpaca watchlist';
COMMENT ON COLUMN user_watchlists.alpaca_watchlist_id IS 'ID of the Alpaca watchlist containing this symbol';

-- =====================================================
-- 2. USER_PREFERENCES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- Auto-refresh settings (in milliseconds)
    auto_refresh_enabled BOOLEAN DEFAULT TRUE,
    refresh_interval_watchlist INTEGER DEFAULT 15000,  -- 15 seconds
    refresh_interval_portfolio INTEGER DEFAULT 30000,  -- 30 seconds
    refresh_interval_orders INTEGER DEFAULT 20000,     -- 20 seconds
    
    -- Table display settings
    default_rows_per_page INTEGER DEFAULT 10,
    
    -- UI preferences
    theme VARCHAR(20) DEFAULT 'light',
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_preferences_user ON user_preferences(user_id);

COMMENT ON TABLE user_preferences IS 'User preferences for auto-refresh intervals and UI settings';
COMMENT ON COLUMN user_preferences.auto_refresh_enabled IS 'Global toggle for auto-refresh functionality';
COMMENT ON COLUMN user_preferences.refresh_interval_watchlist IS 'Watchlist auto-refresh interval in milliseconds';
COMMENT ON COLUMN user_preferences.refresh_interval_portfolio IS 'Portfolio auto-refresh interval in milliseconds';
COMMENT ON COLUMN user_preferences.refresh_interval_orders IS 'Pending orders auto-refresh interval in milliseconds';
COMMENT ON COLUMN user_preferences.default_rows_per_page IS 'Default number of rows per page in data tables';

-- =====================================================
-- 3. TRIGGER FOR UPDATED_AT
-- =====================================================
-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to user_preferences table
DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 4. DEFAULT PREFERENCES FOR EXISTING USERS
-- =====================================================
-- Insert default preferences for any existing users who don't have preferences yet
INSERT INTO user_preferences (user_id, auto_refresh_enabled, refresh_interval_watchlist, refresh_interval_portfolio, refresh_interval_orders, default_rows_per_page, theme)
SELECT 
    id as user_id,
    TRUE as auto_refresh_enabled,
    15000 as refresh_interval_watchlist,
    30000 as refresh_interval_portfolio,
    20000 as refresh_interval_orders,
    10 as default_rows_per_page,
    'light' as theme
FROM users
WHERE id NOT IN (SELECT user_id FROM user_preferences);

-- =====================================================
-- ROLLBACK SCRIPT (if needed)
-- =====================================================
-- DROP TABLE IF EXISTS user_watchlists CASCADE;
-- DROP TABLE IF EXISTS user_preferences CASCADE;
-- DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
