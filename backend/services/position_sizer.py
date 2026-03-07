"""
Position Sizing Service

Calculates position sizes based on portfolio value with proper compounding.
Fixes the broken flat $1000 position sizing in the backtester.

Key Features:
- Percentage-based sizing (compounds with portfolio growth)
- Respects maximum position limits
- Handles fractional shares
- Integrates with risk management

Usage:
    from services.position_sizer import PositionSizer
    from config.config_loader import config
    
    sizer = PositionSizer(config)
    shares = sizer.calculate_position_size(
        portfolio_value=10000,
        current_price=150.0
    )
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PositionSizer:
    """
    Calculates position sizes with proper compounding
    
    The core insight: Position size should be a PERCENTAGE of current portfolio value,
    not a fixed dollar amount. This allows the strategy to compound gains.
    
    Example:
        - Start: $10k portfolio, 10% = $1k per position (6.67 shares @ $150)
        - After growth: $15k portfolio, 10% = $1.5k per position (10 shares @ $150)
        - Position size grows WITH portfolio
    """
    
    def __init__(self, config):
        """
        Initialize position sizer with configuration
        
        Args:
            config: Configuration object with trading parameters
        """
        self.config = config
        
        # Get position sizing percentage from config
        # Handle both percentage format (10) and decimal format (0.10)
        pos_size = config.trading.position_size_pct
        if pos_size > 1:  # Percentage format
            self.position_size_pct = pos_size / 100.0
        else:  # Decimal format
            self.position_size_pct = pos_size
        
        # Get maximum position size from risk config
        max_pos = config.risk.max_position_pct
        if max_pos > 1:  # Percentage format
            self.max_position_pct = max_pos / 100.0
        else:  # Decimal format
            self.max_position_pct = max_pos
        
        logger.info(
            f"PositionSizer initialized: "
            f"position_size={self.position_size_pct*100:.1f}%, "
            f"max_position={self.max_position_pct*100:.1f}%"
        )
    
    def calculate_position_size(
        self, 
        portfolio_value: float, 
        current_price: float,
        override_pct: Optional[float] = None
    ) -> int:
        """
        Calculate number of shares to buy based on portfolio value
        
        This is the KEY function that enables compounding:
        - Uses percentage of CURRENT portfolio value (not initial capital)
        - Position size grows as portfolio grows
        - Position size shrinks if portfolio shrinks (risk management)
        
        Args:
            portfolio_value: Current total portfolio value ($)
            current_price: Current stock price ($)
            override_pct: Optional override percentage (for strategy-specific sizing)
        
        Returns:
            int: Number of shares to buy (minimum 1 if can afford)
        
        Example:
            >>> sizer = PositionSizer(config)  # 10% position size
            >>> sizer.calculate_position_size(10000, 100.0)
            10  # $10k * 10% = $1k / $100 = 10 shares
            >>> sizer.calculate_position_size(15000, 100.0)
            15  # $15k * 10% = $1.5k / $100 = 15 shares (compounding!)
        """
        # Determine sizing percentage (use override if provided)
        size_pct = override_pct if override_pct is not None else self.position_size_pct
        
        # Cap at maximum position size
        size_pct = min(size_pct, self.max_position_pct)
        
        # Calculate dollar amount for this position
        dollar_size = portfolio_value * size_pct
        
        # Convert to shares (round down to avoid over-sizing)
        shares = int(dollar_size / current_price)
        
        # Ensure at least 1 share if we can afford it from PORTFOLIO (not just position size)
        # This allows small portfolios to still take positions
        if shares == 0 and portfolio_value >= current_price:
            shares = 1
        
        logger.debug(
            f"Position sizing: ${portfolio_value:,.2f} portfolio * {size_pct*100:.1f}% "
            f"= ${dollar_size:,.2f} / ${current_price:.2f} = {shares} shares"
        )
        
        return shares
    
    def calculate_position_value(
        self, 
        portfolio_value: float, 
        current_price: float,
        override_pct: Optional[float] = None
    ) -> float:
        """
        Calculate dollar value of position (useful for checks)
        
        Args:
            portfolio_value: Current total portfolio value ($)
            current_price: Current stock price ($)
            override_pct: Optional override percentage
        
        Returns:
            float: Dollar value of position
        """
        shares = self.calculate_position_size(portfolio_value, current_price, override_pct)
        return shares * current_price
    
    def get_max_positions(
        self, 
        portfolio_value: float, 
        cash_reserve: Optional[float] = None
    ) -> int:
        """
        Calculate maximum number of positions portfolio can support
        
        Takes into account:
        - Position size percentage
        - Cash reserve requirements
        - Configured max position count
        
        Args:
            portfolio_value: Current portfolio value ($)
            cash_reserve: Required cash reserve ($ or None to use config)
        
        Returns:
            int: Maximum number of positions
        
        Example:
            >>> sizer = PositionSizer(config)  # 10% positions
            >>> sizer.get_max_positions(10000, cash_reserve=1000)
            9  # $9k available / $1k per position = 9 positions max
        """
        # Get cash reserve from config if not provided
        if cash_reserve is None:
            cash_reserve = self.config.risk.min_cash_reserve
        
        # Available capital for trading (after reserve)
        available = max(0, portfolio_value - cash_reserve)
        
        # Calculate theoretical max based on position size
        theoretical_max = int(available / (portfolio_value * self.position_size_pct))
        
        # Cap at configured max positions
        actual_max = min(theoretical_max, self.config.risk.max_positions)
        
        logger.debug(
            f"Max positions: ${portfolio_value:,.2f} portfolio - "
            f"${cash_reserve:,.2f} reserve = ${available:,.2f} available, "
            f"theoretical max {theoretical_max}, capped at {actual_max}"
        )
        
        return actual_max
    
    def validate_position(
        self, 
        portfolio_value: float, 
        position_value: float
    ) -> tuple[bool, str]:
        """
        Validate if a position size is acceptable
        
        Args:
            portfolio_value: Current portfolio value ($)
            position_value: Proposed position value ($)
        
        Returns:
            tuple: (is_valid, reason)
        
        Example:
            >>> sizer = PositionSizer(config)
            >>> sizer.validate_position(10000, 1500)
            (False, "Position 15.0% exceeds max 10.0%")
        """
        position_pct = position_value / portfolio_value
        
        if position_pct > self.max_position_pct:
            return False, f"Position {position_pct*100:.1f}% exceeds max {self.max_position_pct*100:.1f}%"
        
        return True, "Position size valid"


def calculate_stop_loss_shares(
    entry_price: float,
    stop_loss_pct: float,
    max_loss_dollars: float
) -> int:
    """
    Calculate position size based on risk (Kelly criterion approach)
    
    Alternative sizing method: Size position so max loss = specific dollar amount
    
    Args:
        entry_price: Entry price per share ($)
        stop_loss_pct: Stop loss percentage (e.g., 0.05 = 5%)
        max_loss_dollars: Maximum acceptable loss ($)
    
    Returns:
        int: Number of shares
    
    Example:
        >>> calculate_stop_loss_shares(100.0, 0.05, 500.0)
        100  # $500 max loss / ($100 * 5%) = 100 shares
    """
    loss_per_share = entry_price * stop_loss_pct
    shares = int(max_loss_dollars / loss_per_share)
    return max(1, shares)  # At least 1 share


if __name__ == "__main__":
    # Test position sizer
    from config.config_loader import config
    
    print("=" * 60)
    print("POSITION SIZER TEST")
    print("=" * 60)
    
    sizer = PositionSizer(config)
    
    # Test compounding
    print("\n1. Testing Compounding:")
    print("-" * 60)
    portfolio_values = [10000, 12000, 15000, 8000]
    price = 100.0
    
    for pv in portfolio_values:
        shares = sizer.calculate_position_size(pv, price)
        value = shares * price
        pct = (value / pv) * 100
        print(f"Portfolio: ${pv:>6,} → {shares:>3} shares @ ${price:.2f} = ${value:>6,.0f} ({pct:.1f}%)")
    
    # Test max positions
    print("\n2. Testing Max Positions:")
    print("-" * 60)
    max_pos = sizer.get_max_positions(10000, cash_reserve=1000)
    print(f"Max positions with $10k portfolio and $1k reserve: {max_pos}")
    
    # Test validation
    print("\n3. Testing Position Validation:")
    print("-" * 60)
    test_cases = [
        (10000, 1000, "Normal 10% position"),
        (10000, 1500, "15% position (exceeds 10% max)"),
        (10000, 500, "5% position (under limit)"),
    ]
    
    for pv, pos_val, desc in test_cases:
        valid, reason = sizer.validate_position(pv, pos_val)
        status = "✅ VALID" if valid else "❌ INVALID"
        print(f"{status}: {desc} - {reason}")
    
    print("\n" + "=" * 60)
    print("POSITION SIZER TEST COMPLETE")
    print("=" * 60)
