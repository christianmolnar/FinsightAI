-- Migration: 003_strategy_parameters
-- Create tables for strategy parameters with AI optimization support
-- Phase 1: Enhanced Configuration System

-- Create enum types
CREATE TYPE strategy_type AS ENUM ('earnings', 'seasonality', 'macro', 'sentiment', 'ipo');
CREATE TYPE parameter_type AS ENUM ('integer', 'float', 'percentage', 'boolean');

-- =====================
-- Strategy Parameters Table
-- =====================
CREATE TABLE IF NOT EXISTS strategy_parameters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Parameter identification
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    strategy strategy_type NOT NULL,
    parameter_type parameter_type NOT NULL,
    
    -- Value constraints
    min_value DECIMAL(15, 4),
    max_value DECIMAL(15, 4),
    default_value DECIMAL(15, 4) NOT NULL,
    current_value DECIMAL(15, 4) NOT NULL,
    
    -- AI optimization
    ai_optimizable BOOLEAN NOT NULL DEFAULT TRUE,
    ai_suggested_value DECIMAL(15, 4),
    last_optimized_at TIMESTAMPTZ,
    optimization_performance DECIMAL(8, 4),
    
    -- Metadata
    unit VARCHAR(20),
    category VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_value_in_range CHECK (
        current_value >= COALESCE(min_value, current_value) AND 
        current_value <= COALESCE(max_value, current_value)
    ),
    CONSTRAINT unique_parameter_per_user UNIQUE (user_id, strategy, name)
);

-- Index for fast queries
CREATE INDEX idx_strategy_parameters_user_strategy ON strategy_parameters(user_id, strategy);
CREATE INDEX idx_strategy_parameters_ai_optimizable ON strategy_parameters(user_id, ai_optimizable) WHERE ai_optimizable = TRUE;

-- =====================
-- Stock Parameter Overrides Table
-- =====================
CREATE TABLE IF NOT EXISTS stock_parameter_overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parameter_id UUID NOT NULL REFERENCES strategy_parameters(id) ON DELETE CASCADE,
    
    -- Stock identification
    symbol VARCHAR(20) NOT NULL,
    
    -- Override value
    override_value DECIMAL(15, 4) NOT NULL,
    reason VARCHAR(500),
    
    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_symbol_uppercase CHECK (symbol = UPPER(symbol))
);

-- Unique index for active overrides only
CREATE UNIQUE INDEX idx_unique_active_override 
    ON stock_parameter_overrides(parameter_id, symbol) 
    WHERE is_active = TRUE;

-- Index for fast queries
CREATE INDEX idx_stock_overrides_parameter ON stock_parameter_overrides(parameter_id);
CREATE INDEX idx_stock_overrides_symbol ON stock_parameter_overrides(symbol);

-- =====================
-- Optimization History Table
-- =====================
CREATE TABLE IF NOT EXISTS optimization_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parameter_id UUID NOT NULL REFERENCES strategy_parameters(id) ON DELETE CASCADE,
    
    -- Optimization details
    old_value DECIMAL(15, 4) NOT NULL,
    new_value DECIMAL(15, 4) NOT NULL,
    ai_rationale TEXT,
    
    -- Performance tracking
    trades_count INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 4),
    avg_return DECIMAL(8, 4),
    sharpe_ratio DECIMAL(8, 4),
    
    -- Approval
    status VARCHAR(20) DEFAULT 'pending',
    approved_by_user BOOLEAN DEFAULT FALSE,
    approved_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_win_rate_range CHECK (win_rate >= 0 AND win_rate <= 1),
    CONSTRAINT check_status_values CHECK (status IN ('pending', 'approved', 'rejected', 'testing'))
);

-- Index for fast queries
CREATE INDEX idx_optimization_history_parameter ON optimization_history(parameter_id, created_at DESC);
CREATE INDEX idx_optimization_history_status ON optimization_history(status);

-- =====================
-- Default Parameters for Testing
-- =====================
-- Insert a default user if one doesn't exist (for testing)
INSERT INTO users (id, username, email, created_at, updated_at)
VALUES (
    '00000000-0000-0000-0000-000000000001'::UUID,
    'default_user',
    'user@finsight.ai',
    NOW(),
    NOW()
)
ON CONFLICT (username) DO NOTHING;

-- Insert default parameters for Earnings strategy
INSERT INTO strategy_parameters (
    user_id, name, display_name, description, strategy, parameter_type,
    min_value, max_value, default_value, current_value, 
    ai_optimizable, unit, category, is_active
) VALUES
-- Earnings Strategy Parameters
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'min_eps_growth',
    'Minimum EPS Growth',
    'Minimum year-over-year EPS growth rate to trigger a buy signal',
    'earnings',
    'percentage',
    5.0, 50.0, 10.0, 10.0,
    TRUE, '%', 'entry_criteria', TRUE
),
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'min_revenue_growth',
    'Minimum Revenue Growth',
    'Minimum year-over-year revenue growth rate',
    'earnings',
    'percentage',
    5.0, 50.0, 8.0, 8.0,
    TRUE, '%', 'entry_criteria', TRUE
),
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'earnings_beat_threshold',
    'Earnings Beat Threshold',
    'Percentage by which actual earnings must beat estimates',
    'earnings',
    'percentage',
    0.0, 20.0, 3.0, 3.0,
    TRUE, '%', 'entry_criteria', TRUE
),
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'days_before_earnings',
    'Days Before Earnings to Enter',
    'How many days before earnings to enter position',
    'earnings',
    'integer',
    1.0, 30.0, 7.0, 7.0,
    TRUE, 'days', 'timing', TRUE
),
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'max_position_size',
    'Max Position Size',
    'Maximum percentage of portfolio for earnings plays',
    'earnings',
    'percentage',
    1.0, 10.0, 5.0, 5.0,
    TRUE, '%', 'risk_management', TRUE
),

-- Seasonality Strategy Parameters
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'lookback_years',
    'Historical Lookback Period',
    'Number of years of historical data to analyze for seasonal patterns',
    'seasonality',
    'integer',
    3.0, 10.0, 5.0, 5.0,
    TRUE, 'years', 'analysis', TRUE
),
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'min_win_rate',
    'Minimum Historical Win Rate',
    'Minimum required win rate for historical pattern to be valid',
    'seasonality',
    'percentage',
    50.0, 90.0, 60.0, 60.0,
    TRUE, '%', 'entry_criteria', TRUE
),
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'min_avg_return',
    'Minimum Average Return',
    'Minimum average historical return for the seasonal period',
    'seasonality',
    'percentage',
    2.0, 20.0, 5.0, 5.0,
    TRUE, '%', 'entry_criteria', TRUE
),

-- Macro Strategy Parameters
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'fed_rate_sensitivity',
    'Fed Rate Sensitivity',
    'How sensitive to react to Fed rate changes (0-1 scale)',
    'macro',
    'float',
    0.1, 1.0, 0.7, 0.7,
    TRUE, 'ratio', 'weighting', TRUE
),
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'gdp_threshold',
    'GDP Growth Threshold',
    'Minimum GDP growth rate to stay bullish',
    'macro',
    'percentage',
    0.0, 5.0, 2.0, 2.0,
    TRUE, '%', 'entry_criteria', TRUE
),

-- Sentiment Strategy Parameters
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'social_sentiment_threshold',
    'Social Sentiment Threshold',
    'Minimum social media sentiment score (-1 to 1)',
    'sentiment',
    'float',
    0.0, 1.0, 0.6, 0.6,
    TRUE, 'score', 'entry_criteria', TRUE
),
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'news_sentiment_threshold',
    'News Sentiment Threshold',
    'Minimum news sentiment score (-1 to 1)',
    'sentiment',
    'float',
    0.0, 1.0, 0.5, 0.5,
    TRUE, 'score', 'entry_criteria', TRUE
),
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'sentiment_lookback_days',
    'Sentiment Lookback Period',
    'Number of days to analyze sentiment',
    'sentiment',
    'integer',
    1.0, 30.0, 7.0, 7.0,
    TRUE, 'days', 'analysis', TRUE
),

-- IPO Strategy Parameters
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'min_ipo_quality_score',
    'Minimum IPO Quality Score',
    'Minimum quality score for IPO to be considered (0-100)',
    'ipo',
    'float',
    50.0, 90.0, 70.0, 70.0,
    TRUE, 'score', 'entry_criteria', TRUE
),
(
    '00000000-0000-0000-0000-000000000001'::UUID,
    'lock_up_buffer_days',
    'Lock-up Period Buffer',
    'Days before lock-up expiration to exit',
    'ipo',
    'integer',
    0.0, 90.0, 30.0, 30.0,
    TRUE, 'days', 'exit_rules', TRUE
);

-- Add update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_strategy_parameters_updated_at BEFORE UPDATE ON strategy_parameters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stock_overrides_updated_at BEFORE UPDATE ON stock_parameter_overrides
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$ 
BEGIN
    RAISE NOTICE 'Migration 003_strategy_parameters completed successfully!';
    RAISE NOTICE 'Created tables: strategy_parameters, stock_parameter_overrides, optimization_history';
    RAISE NOTICE 'Inserted % default parameters', (SELECT COUNT(*) FROM strategy_parameters);
END $$;
