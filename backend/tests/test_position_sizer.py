"""
Unit tests for Position Sizer

Tests the core compounding logic and edge cases.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.position_sizer import PositionSizer, calculate_stop_loss_shares
from config.config_loader import config


class TestPositionSizer:
    """Test suite for PositionSizer class"""
    
    @pytest.fixture
    def sizer(self):
        """Create a PositionSizer instance for testing"""
        return PositionSizer(config)
    
    def test_basic_position_sizing(self, sizer):
        """Test basic position size calculation"""
        portfolio_value = 10000
        current_price = 100.0
        
        shares = sizer.calculate_position_size(portfolio_value, current_price)
        
        # Should be 10% of $10k = $1k / $100 = 10 shares
        assert shares == 10
    
    def test_compounding_on_growth(self, sizer):
        """Test that position size grows with portfolio (compounding)"""
        current_price = 100.0
        
        # Portfolio grows from $10k to $15k
        shares_at_10k = sizer.calculate_position_size(10000, current_price)
        shares_at_15k = sizer.calculate_position_size(15000, current_price)
        
        # Position should grow proportionally
        assert shares_at_10k == 10
        assert shares_at_15k == 15
        
        # 50% portfolio growth = 50% position growth
        assert shares_at_15k == shares_at_10k * 1.5
    
    def test_compounding_on_loss(self, sizer):
        """Test that position size shrinks with portfolio (risk management)"""
        current_price = 100.0
        
        # Portfolio shrinks from $10k to $8k
        shares_at_10k = sizer.calculate_position_size(10000, current_price)
        shares_at_8k = sizer.calculate_position_size(8000, current_price)
        
        # Position should shrink proportionally
        assert shares_at_10k == 10
        assert shares_at_8k == 8
        
        # 20% portfolio loss = 20% position reduction
        assert shares_at_8k == shares_at_10k * 0.8
    
    def test_minimum_one_share(self, sizer):
        """Test that position size is at least 1 share if affordable"""
        portfolio_value = 1000  # Small portfolio
        current_price = 500.0   # Expensive stock
        
        shares = sizer.calculate_position_size(portfolio_value, current_price)
        
        # 10% of $1k = $100, but we can afford 1 share at $500
        # Should return at least 1 share
        assert shares >= 1
    
    def test_zero_shares_when_cannot_afford(self, sizer):
        """Test that position size is 0 when cannot afford even 1 share"""
        portfolio_value = 1000
        current_price = 5000.0  # Too expensive
        
        shares = sizer.calculate_position_size(portfolio_value, current_price)
        
        # Cannot afford even 1 share
        assert shares == 0
    
    def test_fractional_shares_round_down(self, sizer):
        """Test that fractional shares are rounded down"""
        portfolio_value = 10000
        current_price = 333.33  # Creates fractional shares
        
        shares = sizer.calculate_position_size(portfolio_value, current_price)
        
        # 10% of $10k = $1000 / $333.33 = 3.0003 shares → 3 shares
        assert shares == 3
        assert isinstance(shares, int)
    
    def test_override_percentage(self, sizer):
        """Test position sizing with override percentage"""
        portfolio_value = 10000
        current_price = 100.0
        
        # Override to 5% instead of default 10%
        shares = sizer.calculate_position_size(
            portfolio_value, 
            current_price, 
            override_pct=0.05
        )
        
        # 5% of $10k = $500 / $100 = 5 shares
        assert shares == 5
    
    def test_max_position_limit(self, sizer):
        """Test that position size respects maximum limit"""
        portfolio_value = 10000
        current_price = 100.0
        
        # Try to override to 20% (but max is 10%)
        shares = sizer.calculate_position_size(
            portfolio_value,
            current_price,
            override_pct=0.20  # Exceeds max
        )
        
        # Should be capped at 10% max
        assert shares == 10
    
    def test_position_value_calculation(self, sizer):
        """Test position value calculation"""
        portfolio_value = 10000
        current_price = 100.0
        
        value = sizer.calculate_position_value(portfolio_value, current_price)
        
        # 10 shares * $100 = $1000
        assert value == 1000.0
    
    def test_max_positions_with_reserve(self, sizer):
        """Test max positions calculation with cash reserve"""
        portfolio_value = 10000
        cash_reserve = 1000
        
        max_pos = sizer.get_max_positions(portfolio_value, cash_reserve)
        
        # $9k available / $1k per position = 9 theoretical
        # But config max is 5
        assert max_pos == 5
    
    def test_max_positions_no_reserve(self, sizer):
        """Test max positions without cash reserve"""
        portfolio_value = 10000
        
        max_pos = sizer.get_max_positions(portfolio_value, cash_reserve=0)
        
        # $10k / $1k per position = 10 theoretical
        # But config max is 5
        assert max_pos == 5
    
    def test_position_validation_valid(self, sizer):
        """Test position validation for valid position"""
        portfolio_value = 10000
        position_value = 1000  # 10% - exactly at limit
        
        valid, reason = sizer.validate_position(portfolio_value, position_value)
        
        assert valid is True
        assert "valid" in reason.lower()
    
    def test_position_validation_too_large(self, sizer):
        """Test position validation for oversized position"""
        portfolio_value = 10000
        position_value = 1500  # 15% - exceeds 10% max
        
        valid, reason = sizer.validate_position(portfolio_value, position_value)
        
        assert valid is False
        assert "exceeds" in reason.lower()
        assert "15.0%" in reason
        assert "10.0%" in reason


class TestStopLossSizing:
    """Test suite for stop-loss based sizing"""
    
    def test_basic_stop_loss_sizing(self):
        """Test basic stop loss position sizing"""
        entry_price = 100.0
        stop_loss_pct = 0.05  # 5%
        max_loss_dollars = 500.0
        
        shares = calculate_stop_loss_shares(entry_price, stop_loss_pct, max_loss_dollars)
        
        # $500 max loss / ($100 * 5%) = $500 / $5 = 100 shares
        assert shares == 100
    
    def test_stop_loss_sizing_expensive_stock(self):
        """Test stop loss sizing for expensive stock"""
        entry_price = 500.0
        stop_loss_pct = 0.05
        max_loss_dollars = 500.0
        
        shares = calculate_stop_loss_shares(entry_price, stop_loss_pct, max_loss_dollars)
        
        # $500 / ($500 * 5%) = $500 / $25 = 20 shares
        assert shares == 20
    
    def test_stop_loss_sizing_minimum_one(self):
        """Test that at least 1 share is returned"""
        entry_price = 100.0
        stop_loss_pct = 0.05
        max_loss_dollars = 1.0  # Very small loss limit
        
        shares = calculate_stop_loss_shares(entry_price, stop_loss_pct, max_loss_dollars)
        
        # Should return at least 1 share
        assert shares >= 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
