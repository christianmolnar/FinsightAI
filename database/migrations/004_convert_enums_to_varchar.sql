-- Migration: Convert enum columns to VARCHAR for flexibility
-- Date: 2024-12-23
-- Reason: SQLAlchemy String type compatibility, easier parameter validation

-- Convert strategy column from strategy_type enum to VARCHAR
ALTER TABLE strategy_parameters 
    ALTER COLUMN strategy TYPE VARCHAR(50) USING strategy::text;

-- Convert parameter_type column from parameter_type enum to VARCHAR
ALTER TABLE strategy_parameters 
    ALTER COLUMN parameter_type TYPE VARCHAR(50) USING parameter_type::text;

-- Note: Keeping the enum types in database for reference, but columns now use VARCHAR
-- This allows more flexible validation in application layer while maintaining data integrity

-- Verify the changes
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'strategy_parameters' 
  AND column_name IN ('strategy', 'parameter_type');
