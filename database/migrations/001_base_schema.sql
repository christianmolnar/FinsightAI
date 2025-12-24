-- Migration: 001_base_schema
-- Create base tables for FinsightAI
-- Required before running other migrations

-- =====================
-- Users Table
-- =====================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    schwab_account_id VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================
-- Portfolios Table
-- =====================
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    portfolio_type VARCHAR(20) NOT NULL CHECK (portfolio_type IN ('live', 'paper')),
    name VARCHAR(255) NOT NULL,
    starting_cash DECIMAL(15, 2) NOT NULL DEFAULT 10000.00,
    current_cash DECIMAL(15, 2) NOT NULL DEFAULT 10000.00,
    total_value DECIMAL(15, 2) NOT NULL DEFAULT 10000.00,
    total_return DECIMAL(15, 2) DEFAULT 0.00,
    total_return_percent DECIMAL(8, 4) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_portfolios_user ON portfolios(user_id);

-- =====================
-- Positions Table
-- =====================
CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(15, 4) NOT NULL,
    average_cost DECIMAL(10, 4) NOT NULL,
    current_price DECIMAL(10, 4) DEFAULT 0.00,
    market_value DECIMAL(15, 2) DEFAULT 0.00,
    cost_basis DECIMAL(15, 2) NOT NULL,
    unrealized_pnl DECIMAL(15, 2) DEFAULT 0.00,
    unrealized_pnl_percent DECIMAL(8, 4) DEFAULT 0.00,
    purchase_date TIMESTAMPTZ NOT NULL,
    strategy_used VARCHAR(50),
    ai_confidence DECIMAL(3, 2) CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    target_price DECIMAL(10, 4),
    stop_loss DECIMAL(10, 4),
    days_held INTEGER DEFAULT 0,
    is_open BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_positions_portfolio ON positions(portfolio_id);
CREATE INDEX idx_positions_symbol ON positions(symbol);

-- =====================
-- Transactions Table
-- =====================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('buy', 'sell')),
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(15, 4) NOT NULL,
    price DECIMAL(10, 4) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    commission DECIMAL(10, 2) DEFAULT 0.00,
    strategy_used VARCHAR(50),
    ai_confidence DECIMAL(3, 2),
    notes TEXT,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transactions_portfolio ON transactions(portfolio_id);
CREATE INDEX idx_transactions_symbol ON transactions(symbol);
CREATE INDEX idx_transactions_date ON transactions(executed_at DESC);

-- =====================
-- Portfolio Snapshots Table
-- =====================
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    snapshot_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    total_value DECIMAL(15, 2) NOT NULL,
    cash_balance DECIMAL(15, 2) NOT NULL,
    total_return DECIMAL(15, 2) NOT NULL,
    total_return_percent DECIMAL(8, 4) NOT NULL,
    daily_change DECIMAL(15, 2),
    daily_change_percent DECIMAL(8, 4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_snapshots_portfolio_date ON portfolio_snapshots(portfolio_id, snapshot_date DESC);

-- =====================
-- Strategy Configs Table (legacy - will be replaced by strategy_parameters)
-- =====================
CREATE TABLE IF NOT EXISTS strategy_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    strategy_name VARCHAR(100) NOT NULL,
    config_json JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_strategy_configs_user ON strategy_configs(user_id);

-- =====================
-- AI Optimizations Table (legacy - will be replaced by optimization_history)
-- =====================
CREATE TABLE IF NOT EXISTS ai_optimizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    optimization_type VARCHAR(50) NOT NULL,
    parameters_json JSONB NOT NULL,
    result_json JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_ai_optimizations_user ON ai_optimizations(user_id);

-- =====================
-- Update Triggers
-- =====================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategy_configs_updated_at BEFORE UPDATE ON strategy_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================
-- Default Data
-- =====================
-- Insert a default user for testing
INSERT INTO users (id, username, email, created_at, updated_at)
VALUES (
    '00000000-0000-0000-0000-000000000001'::UUID,
    'default_user',
    'user@finsight.ai',
    NOW(),
    NOW()
)
ON CONFLICT (username) DO NOTHING;

-- Success message
DO $$ 
BEGIN
    RAISE NOTICE 'Migration 001_base_schema completed successfully!';
    RAISE NOTICE 'Created base tables: users, portfolios, positions, transactions, snapshots';
END $$;
