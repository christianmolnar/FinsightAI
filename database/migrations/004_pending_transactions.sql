-- Migration: Create pending_transactions table
-- Purpose: Store AI-proposed trades awaiting user approval
-- Created: 2025-12-24
-- Phase: 3 - Transaction Queue System

-- Create pending_transactions table
CREATE TABLE IF NOT EXISTS pending_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    
    -- Transaction details
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('buy', 'sell')),
    symbol VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    proposed_price DECIMAL(10, 2) NOT NULL CHECK (proposed_price > 0),
    
    -- Risk management (optional for buy orders)
    stop_loss DECIMAL(10, 2) CHECK (stop_loss IS NULL OR stop_loss > 0),
    profit_target DECIMAL(10, 2) CHECK (profit_target IS NULL OR profit_target > 0),
    
    -- AI analysis results
    confidence_score INTEGER NOT NULL CHECK (confidence_score BETWEEN 0 AND 100),
    ai_reasoning JSONB NOT NULL DEFAULT '{}',  -- Stores both AI recommendations
    risk_factors TEXT[],  -- Array of identified risks
    catalysts TEXT[],  -- Array of positive catalysts
    
    -- Queue management
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'executed', 'expired', 'cancelled')),
    scheduled_time TIMESTAMP,  -- When to auto-execute (if enabled)
    auto_execute BOOLEAN DEFAULT false,  -- Whether to auto-execute at scheduled_time
    
    -- User interaction
    reason_for_trade TEXT,  -- User's reason for initiating this trade
    user_notes TEXT,  -- Additional user notes
    created_by VARCHAR(50) DEFAULT 'ai_agent',  -- 'user' or 'ai_agent'
    
    -- Execution tracking
    executed_at TIMESTAMP,
    execution_price DECIMAL(10, 2),
    execution_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP  -- Auto-reject if not acted upon by this time
);

-- Create indexes for common queries
CREATE INDEX idx_pending_transactions_portfolio ON pending_transactions(portfolio_id);
CREATE INDEX idx_pending_transactions_status ON pending_transactions(status);
CREATE INDEX idx_pending_transactions_symbol ON pending_transactions(symbol);
CREATE INDEX idx_pending_transactions_scheduled ON pending_transactions(scheduled_time) WHERE auto_execute = true;
CREATE INDEX idx_pending_transactions_created ON pending_transactions(created_at DESC);

-- Create function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_pending_transactions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER trigger_pending_transactions_updated_at
    BEFORE UPDATE ON pending_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_pending_transactions_updated_at();

-- Add comments for documentation
COMMENT ON TABLE pending_transactions IS 'Stores AI-proposed trades awaiting user approval or scheduled for auto-execution';
COMMENT ON COLUMN pending_transactions.transaction_type IS 'Type of transaction: buy or sell';
COMMENT ON COLUMN pending_transactions.confidence_score IS 'AI confidence score from 0-100, higher = more confident';
COMMENT ON COLUMN pending_transactions.ai_reasoning IS 'JSONB object with both OpenAI and Claude recommendations';
COMMENT ON COLUMN pending_transactions.auto_execute IS 'If true, will auto-execute at scheduled_time';
COMMENT ON COLUMN pending_transactions.created_by IS 'Source: user (manual) or ai_agent (autonomous)';
COMMENT ON COLUMN pending_transactions.status IS 'Current state: pending, approved, rejected, executed, expired, cancelled';

-- Sample query to get pending trades for a portfolio
-- SELECT * FROM pending_transactions 
-- WHERE portfolio_id = 'your-portfolio-id' 
-- AND status = 'pending' 
-- ORDER BY confidence_score DESC, created_at DESC;

-- Sample query to get auto-execute queue
-- SELECT * FROM pending_transactions 
-- WHERE status = 'pending' 
-- AND auto_execute = true 
-- AND scheduled_time <= NOW() 
-- ORDER BY scheduled_time ASC;
