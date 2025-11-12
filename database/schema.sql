-- FInsightAI Database Schema for Supabase
-- Paper Trading with $10,000 starting balance

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (can integrate with Supabase Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    schwab_account_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolios table (live vs paper)
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    portfolio_type VARCHAR(20) NOT NULL CHECK (portfolio_type IN ('live', 'paper')),
    name VARCHAR(255) NOT NULL,
    starting_cash DECIMAL(15,2) NOT NULL DEFAULT 10000.00,
    current_cash DECIMAL(15,2) NOT NULL DEFAULT 10000.00,
    total_value DECIMAL(15,2) NOT NULL DEFAULT 10000.00,
    total_return DECIMAL(15,2) DEFAULT 0.00,
    total_return_percent DECIMAL(8,4) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Positions table (current holdings)
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(15,4) NOT NULL,
    average_cost DECIMAL(10,4) NOT NULL,
    current_price DECIMAL(10,4) DEFAULT 0.00,
    market_value DECIMAL(15,2) DEFAULT 0.00,
    cost_basis DECIMAL(15,2) NOT NULL,
    unrealized_pnl DECIMAL(15,2) DEFAULT 0.00,
    unrealized_pnl_percent DECIMAL(8,4) DEFAULT 0.00,
    purchase_date TIMESTAMP WITH TIME ZONE NOT NULL,
    strategy_used VARCHAR(50), -- 'earnings', 'sentiment', 'seasonality', 'macro'
    ai_confidence DECIMAL(3,2) CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    target_price DECIMAL(10,4),
    stop_loss DECIMAL(10,4),
    days_held INTEGER DEFAULT 0,
    is_open BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transactions table (all trade history)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('BUY', 'SELL')),
    quantity DECIMAL(15,4) NOT NULL,
    price DECIMAL(10,4) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    commission DECIMAL(10,2) DEFAULT 1.00,
    net_amount DECIMAL(15,2) NOT NULL, -- total_amount + commission
    strategy_used VARCHAR(50),
    ai_confidence DECIMAL(3,2) CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    ai_factors JSONB, -- Store all factors that influenced the decision
    notes TEXT,
    executed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Strategy configurations table
CREATE TABLE strategy_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    strategy_name VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    performance_metrics JSONB, -- Store backtest results, win rate, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trade factors table (detailed reasoning for each trade)
CREATE TABLE trade_factors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    factor_type VARCHAR(50) NOT NULL,
    factor_value DECIMAL(12,4),
    factor_description TEXT,
    weight DECIMAL(3,2), -- How much this factor influenced the decision (0.0 to 1.0)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market data cache table
CREATE TABLE market_data_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(10,4) NOT NULL,
    volume BIGINT,
    high DECIMAL(10,4),
    low DECIMAL(10,4),
    open DECIMAL(10,4),
    previous_close DECIMAL(10,4),
    change_amount DECIMAL(10,4),
    change_percent DECIMAL(8,4),
    market_cap BIGINT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(50) DEFAULT 'yahoo',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI optimization history table
CREATE TABLE ai_optimizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    strategy_type VARCHAR(50) NOT NULL,
    original_parameters JSONB NOT NULL,
    optimized_parameters JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    expected_return DECIMAL(8,4),
    expected_sharpe DECIMAL(6,4),
    expected_max_drawdown DECIMAL(8,4),
    reasoning TEXT,
    market_analysis TEXT,
    risk_assessment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio performance snapshots (daily)
CREATE TABLE portfolio_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    total_value DECIMAL(15,2) NOT NULL,
    cash_value DECIMAL(15,2) NOT NULL,
    positions_value DECIMAL(15,2) NOT NULL,
    total_return DECIMAL(15,2) NOT NULL,
    total_return_percent DECIMAL(8,4) NOT NULL,
    daily_return DECIMAL(15,2),
    daily_return_percent DECIMAL(8,4),
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX idx_portfolios_type ON portfolios(portfolio_type);
CREATE INDEX idx_positions_portfolio_id ON positions(portfolio_id);
CREATE INDEX idx_positions_symbol ON positions(symbol);
CREATE INDEX idx_positions_is_open ON positions(is_open);
CREATE INDEX idx_transactions_portfolio_id ON transactions(portfolio_id);
CREATE INDEX idx_transactions_symbol ON transactions(symbol);
CREATE INDEX idx_transactions_executed_at ON transactions(executed_at);
CREATE INDEX idx_market_data_symbol ON market_data_cache(symbol);
CREATE INDEX idx_market_data_timestamp ON market_data_cache(timestamp);
CREATE INDEX idx_trade_factors_transaction_id ON trade_factors(transaction_id);
CREATE INDEX idx_portfolio_snapshots_portfolio_date ON portfolio_snapshots(portfolio_id, snapshot_date);

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategy_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE trade_factors ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_optimizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_snapshots ENABLE ROW LEVEL SECURITY;

-- Policies (users can only access their own data)
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own portfolios" ON portfolios FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own portfolios" ON portfolios FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own positions" ON positions FOR SELECT USING (
  auth.uid() = (SELECT user_id FROM portfolios WHERE id = portfolio_id)
);
CREATE POLICY "Users can manage own positions" ON positions FOR ALL USING (
  auth.uid() = (SELECT user_id FROM portfolios WHERE id = portfolio_id)
);

CREATE POLICY "Users can view own transactions" ON transactions FOR SELECT USING (
  auth.uid() = (SELECT user_id FROM portfolios WHERE id = portfolio_id)
);
CREATE POLICY "Users can manage own transactions" ON transactions FOR ALL USING (
  auth.uid() = (SELECT user_id FROM portfolios WHERE id = portfolio_id)
);

-- Functions for automatic updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON portfolios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_strategy_configs_updated_at BEFORE UPDATE ON strategy_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate portfolio totals
CREATE OR REPLACE FUNCTION calculate_portfolio_totals(portfolio_uuid UUID)
RETURNS TABLE (
    total_positions_value DECIMAL(15,2),
    total_unrealized_pnl DECIMAL(15,2),
    total_portfolio_value DECIMAL(15,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(p.market_value), 0) as total_positions_value,
        COALESCE(SUM(p.unrealized_pnl), 0) as total_unrealized_pnl,
        port.current_cash + COALESCE(SUM(p.market_value), 0) as total_portfolio_value
    FROM portfolios port
    LEFT JOIN positions p ON p.portfolio_id = port.id AND p.is_open = true
    WHERE port.id = portfolio_uuid
    GROUP BY port.id, port.current_cash;
END;
$$ LANGUAGE plpgsql;

-- Insert default test user and paper portfolio with $10,000
INSERT INTO users (id, username, email) 
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'christian', 'christian@finsightai.com')
ON CONFLICT (username) DO NOTHING;

INSERT INTO portfolios (id, user_id, portfolio_type, name, starting_cash, current_cash, total_value)
VALUES (
    '660f9511-f3ac-42e5-b827-557766551111', 
    '550e8400-e29b-41d4-a716-446655440000',
    'paper',
    'Paper Trading Portfolio',
    10000.00,
    10000.00,
    10000.00
) ON CONFLICT DO NOTHING;

-- Insert default strategy configurations
INSERT INTO strategy_configs (user_id, strategy_name, parameters, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'earnings', '{
    "daysBeforeEarnings": 5,
    "minEpsGrowth": 15,
    "minRevenueGrowth": 10,
    "historicalBeatRate": 70,
    "profitTarget": 12,
    "stopLoss": 5,
    "maxPortfolioWeight": 20
}', true),
('550e8400-e29b-41d4-a716-446655440000', 'seasonality', '{
    "weeksBeforePeak": 3,
    "minHistoricalYears": 5,
    "minSeasonalReturn": 8,
    "profitTarget": 15,
    "stopLoss": 7,
    "maxPortfolioWeight": 15
}', true),
('550e8400-e29b-41d4-a716-446655440000', 'macro', '{
    "entryTimeframe": 48,
    "catalystStrengthMin": 70,
    "correlationThreshold": 0.6,
    "profitTarget": 8,
    "stopLoss": 6,
    "maxHoldDays": 30,
    "maxPortfolioWeight": 10
}', true),
('550e8400-e29b-41d4-a716-446655440000', 'sentiment', '{
    "minSentimentScore": 70,
    "volumeMultiplier": 1.5,
    "newsScoreMin": 80,
    "searchTrendIncrease": 50,
    "profitTarget": 8,
    "stopLoss": 4,
    "maxPortfolioWeight": 15
}', true)
ON CONFLICT DO NOTHING;
