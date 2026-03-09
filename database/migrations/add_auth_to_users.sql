-- Migration: Add password_hash column to users table
-- Run once on Railway PostgreSQL

ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
