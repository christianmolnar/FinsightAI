"""
Configuration Loader for Autonomous Trading Bot

Loads configuration from:
1. YAML file (trading_config.yaml) - Trading parameters, committed to git
2. .env file - Secrets (API keys), NEVER committed to git

Usage:
    from config.config_loader import config
    
    # Access trading config
    position_size = config.trading.position_size_pct
    
    # Access secrets (from .env)
    api_key = config.alpaca_paper_api_key
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv
from dataclasses import dataclass, field

# Load environment variables from .env file
load_dotenv()


@dataclass
class TradingConfig:
    """Trading parameters from YAML"""
    initial_capital: float
    position_size_pct: float
    scan_interval: int
    position_check_interval: int
    min_confidence: int
    profit_target_pct: float
    stop_loss_pct: float
    trailing_stop_enabled: bool
    trailing_stop_pct: float
    market_open_hour: int
    market_open_minute: int
    market_close_hour: int
    market_close_minute: int
    paper_trading: bool


@dataclass
class RiskConfig:
    """Risk management parameters from YAML"""
    max_position_pct: float
    max_positions: int
    min_cash_reserve: float
    daily_loss_limit_pct: float
    max_drawdown_pct: float
    consecutive_loss_limit: int
    vix_threshold: float
    vix_position_reduction: float
    max_sector_exposure_pct: float
    auto_resume_after_pause: bool
    pause_cooldown_minutes: int


@dataclass
class ScannerConfig:
    """Scanner parameters from YAML"""
    min_price: float
    max_price: float
    min_volume: int
    max_spread_pct: float
    strategy_weights: Dict[str, float]


@dataclass
class TechnicalFiltersConfig:
    """Technical filters from YAML"""
    min_required_filters: int
    rsi_min: int
    rsi_max: int
    volume_multiplier: float
    price_above_ma50: bool
    ma50_above_ma200: bool
    min_distance_above_ma200_pct: float


@dataclass
class LoggingConfig:
    """Logging configuration from YAML"""
    console_level: str
    file_level: str
    log_dir: str
    max_log_size_mb: int
    max_log_files: int
    log_all_scans: bool
    log_all_decisions: bool
    log_all_risk_checks: bool


@dataclass
class MonitoringConfig:
    """Monitoring and alerting from YAML"""
    heartbeat_interval: int
    daily_summary_time: str
    alert_on_pause: bool
    alert_on_daily_loss_pct: float
    alert_on_position_loss_pct: float
    email_enabled: bool
    slack_enabled: bool
    sms_enabled: bool


@dataclass
class BacktestingConfig:
    """Backtesting parameters from YAML"""
    default_lookback_days: int
    commission_per_trade: float
    slippage_pct: float


@dataclass
class StrategiesConfig:
    """Strategy-specific parameters from YAML"""
    earnings: Dict[str, Any]
    breakout: Dict[str, Any]
    seasonality: Dict[str, Any]
    sentiment: Dict[str, Any]


class Config:
    """
    Main configuration class that combines YAML config and environment variables
    """
    
    def __init__(self):
        # Load YAML configuration
        config_path = Path(__file__).parent / "trading_config.yaml"
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
        
        # Parse YAML sections into dataclasses
        self.trading = TradingConfig(**yaml_config['trading'])
        self.risk = RiskConfig(**yaml_config['risk'])
        self.scanner = ScannerConfig(**yaml_config['scanner'])
        self.technical_filters = TechnicalFiltersConfig(**yaml_config['technical_filters'])
        self.logging = LoggingConfig(**yaml_config['logging'])
        self.monitoring = MonitoringConfig(**yaml_config['monitoring'])
        self.backtesting = BacktestingConfig(**yaml_config['backtesting'])
        self.strategies = StrategiesConfig(**yaml_config['strategies'])
        
        # Load secrets from environment variables
        self._load_secrets()
        
        # Validate configuration
        self._validate()
    
    def _load_secrets(self):
        """Load sensitive data from environment variables"""
        # Alpaca API credentials — support both naming conventions
        self.alpaca_paper_api_key = (
            os.getenv('ALPACA_PAPER_API_KEY_ID') or os.getenv('ALPACA_PAPER_API_KEY')
        )
        self.alpaca_paper_secret_key = (
            os.getenv('ALPACA_PAPER_API_SECRET_KEY') or os.getenv('ALPACA_PAPER_SECRET_KEY')
        )
        self.alpaca_live_api_key = (
            os.getenv('ALPACA_LIVE_API_KEY_ID') or os.getenv('ALPACA_LIVE_API_KEY')
        )
        self.alpaca_live_secret_key = (
            os.getenv('ALPACA_LIVE_API_SECRET_KEY') or os.getenv('ALPACA_LIVE_SECRET_KEY')
        )
        
        # Database
        self.database_url = os.getenv('DATABASE_URL')
        
        # Optional notification services
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_to = os.getenv('EMAIL_TO')
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = os.getenv('SMTP_PORT')
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_from_number = os.getenv('TWILIO_FROM_NUMBER')
        self.twilio_to_number = os.getenv('TWILIO_TO_NUMBER')
        
        # Application settings
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    def _validate(self):
        """Validate configuration values — warn on missing keys, never crash."""
        import logging
        _log = logging.getLogger(__name__)
        if self.trading.paper_trading:
            if not self.alpaca_paper_api_key or not self.alpaca_paper_secret_key:
                _log.warning(
                    "Paper trading enabled but ALPACA_PAPER_API_KEY_ID / "
                    "ALPACA_PAPER_API_SECRET_KEY not set — paper trading will fail"
                )
        else:
            if not self.alpaca_live_api_key or not self.alpaca_live_secret_key:
                _log.warning(
                    "Live trading enabled but ALPACA_LIVE_API_KEY_ID / "
                    "ALPACA_LIVE_API_SECRET_KEY not set — live trading will fail"
                )
        
        # Validate position sizing
        if not 0.01 <= self.trading.position_size_pct <= 0.25:
            raise ValueError(
                f"position_size_pct must be between 1% and 25%, got {self.trading.position_size_pct}"
            )
        
        # Validate strategy weights sum to 1.0
        weights_sum = sum(self.scanner.strategy_weights.values())
        if not 0.99 <= weights_sum <= 1.01:  # Allow for floating point errors
            raise ValueError(
                f"Strategy weights must sum to 1.0, got {weights_sum}"
            )
        
        # Validate risk limits are sane
        # Check if values are in percentage format (>1) or decimal format (<1)
        max_pos = self.risk.max_position_pct
        if max_pos > 1:  # Percentage format (e.g., 10 = 10%)
            if max_pos > 25:
                raise ValueError(
                    f"max_position_pct too high: {max_pos}%. "
                    "Maximum allowed is 25%"
                )
        else:  # Decimal format (e.g., 0.10 = 10%)
            if max_pos > 0.25:
                raise ValueError(
                    f"max_position_pct too high: {max_pos * 100}%. "
                    "Maximum allowed is 25%"
                )
        
        if self.risk.max_positions > 10:
            raise ValueError(
                f"max_positions too high: {self.risk.max_positions}. "
                "Maximum allowed is 10"
            )
    
    def get_alpaca_credentials(self) -> tuple[str, str]:
        """
        Get appropriate Alpaca credentials based on paper_trading setting
        
        Returns:
            tuple: (api_key, secret_key)
        """
        if self.trading.paper_trading:
            return self.alpaca_paper_api_key, self.alpaca_paper_secret_key
        else:
            return self.alpaca_live_api_key, self.alpaca_live_secret_key
    
    def to_dict(self) -> dict:
        """
        Convert config to dictionary (excluding secrets)
        Useful for logging configuration state
        """
        return {
            'trading': {
                'initial_capital': self.trading.initial_capital,
                'position_size_pct': self.trading.position_size_pct,
                'paper_trading': self.trading.paper_trading,
                # ... other non-sensitive fields
            },
            'risk': {
                'max_positions': self.risk.max_positions,
                'daily_loss_limit_pct': self.risk.daily_loss_limit_pct,
                # ... other fields
            },
            # Secrets are NOT included in this output
            'environment': self.environment
        }


# Global configuration instance
# Import this in other modules: from config.config_loader import config
config = Config()


# Convenience function for testing
def reload_config():
    """Reload configuration (useful for testing)"""
    global config
    config = Config()
    return config


if __name__ == "__main__":
    # Test configuration loading
    print("Configuration loaded successfully!")
    print(f"Paper trading: {config.trading.paper_trading}")
    print(f"Position size: {config.trading.position_size_pct * 100}%")
    print(f"Max positions: {config.risk.max_positions}")
    print(f"Alpaca credentials loaded: {bool(config.alpaca_paper_api_key)}")
