"""
Backtest Configuration and Debug Settings

Controls backtest behavior and logging levels
"""

import os
from typing import Dict, Any

# Debug mode - enables extensive logging
# Set via environment variable: BACKTEST_DEBUG=true
BACKTEST_DEBUG = os.getenv("BACKTEST_DEBUG", "false").lower() == "true"

# Exit rules configuration
EXIT_RULES = {
    "profit_target_pct": 15.0,  # Take profit at +15%
    "stop_loss_pct": -8.0,      # Stop loss at -8%
    "trailing_stop_pct": None,   # Trailing stop (None = disabled)
    "max_hold_days": 60          # Maximum calendar days to hold
}

# Position sizing configuration
POSITION_SIZING = {
    "min_pct": 0.05,  # Minimum 5% of portfolio per trade
    "max_pct": 0.15,  # Maximum 15% of portfolio per trade
    "default_pct": 0.10  # Default 10% if not specified
}

# Scanner configuration
SCANNER_CONFIG = {
    "min_confidence": 0.70,  # Minimum AI confidence to trade
    "strategies": ["technical_breakout", "earnings_play", "seasonality"]
}

def get_config() -> Dict[str, Any]:
    """Get complete backtest configuration"""
    return {
        "debug_mode": BACKTEST_DEBUG,
        "exit_rules": EXIT_RULES,
        "position_sizing": POSITION_SIZING,
        "scanner": SCANNER_CONFIG
    }

def enable_debug_mode():
    """Enable debug mode programmatically"""
    global BACKTEST_DEBUG
    BACKTEST_DEBUG = True

def disable_debug_mode():
    """Disable debug mode programmatically"""
    global BACKTEST_DEBUG
    BACKTEST_DEBUG = False
