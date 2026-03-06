"""
Backtesting Engine

Tests scanner strategies and AI predictions against historical data to:
- Validate strategy effectiveness
- Tune confidence thresholds
- Measure prediction accuracy
- Calculate risk-adjusted returns

Can backtest individual strategies or full portfolio simulations.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session

from services.market_scanner import MarketScanner
from services.opportunity_analyzer import get_opportunity_analyzer
from services.historical_data_manager import HistoricalDataManager

logger = logging.getLogger(__name__)


class BacktestResult:
    """Result of a single backtest trade"""
    
    def __init__(
        self,
        symbol: str,
        strategy: str,
        entry_date: datetime,
        entry_price: float,
        exit_date: datetime,
        exit_price: float,
        shares: int,
        exit_reason: str,
        scanner_score: float,
        ai_confidence: float,
        ai_reasoning: str
    ):
        self.symbol = symbol
        self.strategy = strategy
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.shares = shares
        self.exit_reason = exit_reason
        self.scanner_score = scanner_score
        self.ai_confidence = ai_confidence
        self.ai_reasoning = ai_reasoning
        
        # Calculate metrics
        self.profit_loss = (exit_price - entry_price) * shares
        self.return_pct = ((exit_price - entry_price) / entry_price) * 100
        self.hold_days = (exit_date - entry_date).days
        
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'strategy': self.strategy,
            'entry_date': self.entry_date.strftime('%Y-%m-%d'),
            'entry_price': round(self.entry_price, 2),
            'exit_date': self.exit_date.strftime('%Y-%m-%d'),
            'exit_price': round(self.exit_price, 2),
            'shares': self.shares,
            'exit_reason': self.exit_reason,
            'scanner_score': round(self.scanner_score, 2),
            'ai_confidence': round(self.ai_confidence, 2),
            'ai_reasoning': self.ai_reasoning,
            'profit_loss': round(self.profit_loss, 2),
            'return_pct': round(self.return_pct, 2),
            'hold_days': self.hold_days
        }


class BacktestMetrics:
    """Aggregate metrics for a backtest run"""
    
    def __init__(self, trades: List[BacktestResult], initial_capital: float, daily_pnl: Optional[Dict] = None):
        self.trades = trades
        self.initial_capital = initial_capital
        self.daily_pnl = daily_pnl or {}  # NEW: {date: daily_profit_loss}
        
        # Calculate aggregate metrics
        self.total_trades = len(trades)
        self.winning_trades = len([t for t in trades if t.profit_loss > 0])
        self.losing_trades = len([t for t in trades if t.profit_loss <= 0])
        
        self.win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        self.total_profit = sum([t.profit_loss for t in trades if t.profit_loss > 0])
        self.total_loss = abs(sum([t.profit_loss for t in trades if t.profit_loss < 0]))
        self.net_profit = sum([t.profit_loss for t in trades])
        
        self.avg_win = (self.total_profit / self.winning_trades) if self.winning_trades > 0 else 0
        self.avg_loss = (self.total_loss / self.losing_trades) if self.losing_trades > 0 else 0
        
        self.profit_factor = (self.total_profit / self.total_loss) if self.total_loss > 0 else 0
        
        self.final_capital = initial_capital + self.net_profit
        self.total_return_pct = ((self.final_capital - initial_capital) / initial_capital) * 100
        
        # Calculate average hold time
        self.avg_hold_days = sum([t.hold_days for t in trades]) / self.total_trades if self.total_trades > 0 else 0
        
        # Best and worst trades
        self.best_trade = max(trades, key=lambda t: t.return_pct) if trades else None
        self.worst_trade = min(trades, key=lambda t: t.return_pct) if trades else None
        
        # ========================================
        # NEW METRICS FOR PHASE 4.5
        # ========================================
        
        # Calculate max drawdown from daily P&L
        self.max_drawdown = self._calculate_max_drawdown()
        
        # Calculate Sharpe ratio (risk-adjusted return)
        self.sharpe_ratio = self._calculate_sharpe_ratio()
        
        # Largest win/loss
        self.largest_win = max([t.profit_loss for t in trades]) if trades else 0
        self.largest_loss = min([t.profit_loss for t in trades]) if trades else 0
        
        # Average win/loss sizes
        self.avg_win_size = self.avg_win  # Already calculated above
        self.avg_loss_size = self.avg_loss  # Already calculated above
    
    def _calculate_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown from daily P&L
        
        Max drawdown = largest peak-to-trough decline in portfolio value
        """
        if not self.daily_pnl:
            return 0.0
        
        # Build cumulative portfolio value over time
        portfolio_values = []
        running_capital = self.initial_capital
        
        for date in sorted(self.daily_pnl.keys()):
            running_capital += self.daily_pnl[date]
            portfolio_values.append(running_capital)
        
        if not portfolio_values:
            return 0.0
        
        # Calculate drawdowns
        peak = portfolio_values[0]
        max_dd = 0.0
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def _calculate_sharpe_ratio(self) -> Optional[float]:
        """
        Calculate Sharpe ratio (risk-adjusted return)
        
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns
        Assumes risk-free rate = 0 for simplicity
        """
        if not self.daily_pnl or len(self.daily_pnl) < 2:
            return None
        
        # Calculate daily returns as percentages
        daily_returns = []
        running_capital = self.initial_capital
        
        for date in sorted(self.daily_pnl.keys()):
            daily_profit = self.daily_pnl[date]
            daily_return = (daily_profit / running_capital) * 100 if running_capital > 0 else 0
            daily_returns.append(daily_return)
            running_capital += daily_profit
        
        if not daily_returns or len(daily_returns) < 2:
            return None
        
        # Calculate mean and std dev
        import numpy as np
        mean_return = np.mean(daily_returns)
        std_return = np.std(daily_returns)
        
        if std_return == 0:
            return None
        
        # Annualize the Sharpe ratio (assuming ~252 trading days per year)
        sharpe = (mean_return / std_return) * (252 ** 0.5)
        
        return sharpe
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'summary': {
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'win_rate': round(self.win_rate, 2),
            },
            'returns': {
                'initial_capital': round(self.initial_capital, 2),
                'final_capital': round(self.final_capital, 2),
                'net_profit': round(self.net_profit, 2),
                'total_return_pct': round(self.total_return_pct, 2),
            },
            'performance': {
                'total_profit': round(self.total_profit, 2),
                'total_loss': round(self.total_loss, 2),
                'avg_win': round(self.avg_win, 2),
                'avg_loss': round(self.avg_loss, 2),
                'profit_factor': round(self.profit_factor, 2),
                'avg_hold_days': round(self.avg_hold_days, 1),
            },
            # NEW METRICS FOR PHASE 4.5
            'risk_metrics': {
                'max_drawdown': round(self.max_drawdown, 2) if self.max_drawdown else None,
                'sharpe_ratio': round(self.sharpe_ratio, 2) if self.sharpe_ratio else None,
                'largest_win': round(self.largest_win, 2),
                'largest_loss': round(self.largest_loss, 2),
                'avg_win_size': round(self.avg_win_size, 2),
                'avg_loss_size': round(self.avg_loss_size, 2),
            },
            'best_trade': self.best_trade.to_dict() if self.best_trade else None,
            'worst_trade': self.worst_trade.to_dict() if self.worst_trade else None,
        }


class Backtester:
    """
    Backtesting engine for strategy validation
    """
    
    def __init__(
        self,
        db: Session,
        initial_capital: float = 10000.0,
        position_size: float = 1000.0,
        max_hold_days: int = 14
    ):
        """
        Initialize backtester
        
        Args:
            db: Database session
            initial_capital: Starting capital for backtest
            position_size: Dollar amount per position
            max_hold_days: Maximum days to hold a position
        """
        self.db = db
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.max_hold_days = max_hold_days
        
        self.scanner = MarketScanner(db)
        self.historical_data = HistoricalDataManager(db)
        self.trades: List[BacktestResult] = []
    
    async def run_backtest(
        self,
        start_date: datetime,
        end_date: datetime,
        strategies: Optional[List[str]] = None,
        confidence_threshold: float = 0.75,
        use_ai: bool = True
    ) -> BacktestMetrics:
        """
        Run backtest over date range
        
        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            strategies: List of strategies to test (None = all)
            confidence_threshold: Minimum AI confidence for trade
            use_ai: If True, use AI analyzer. If False, use scanner scores only
            
        Returns:
            BacktestMetrics with results
        """
        logger.info(f"🔄 Starting backtest: {start_date.date()} to {end_date.date()}")
        logger.info(f"   Strategies: {strategies or 'ALL'}")
        logger.info(f"   AI Enabled: {use_ai}, Threshold: {confidence_threshold:.0%}")
        
        self.trades = []
        daily_pnl = {}  # NEW: Track daily P&L for max drawdown calculation
        
        # ⚡ OPTIMIZATION: Download all historical data ONCE at the beginning
        logger.info(f"📥 Downloading historical data for {len(self.scanner.SCAN_UNIVERSE)} stocks...")
        universe_data = await self._download_all_historical_data(start_date, end_date)
        logger.info(f"✅ Downloaded data for {len(universe_data)} stocks")
        
        if not universe_data:
            logger.error("❌ Failed to download any historical data!")
            return BacktestMetrics([], self.initial_capital, daily_pnl)
        
        current_date = start_date
        
        # Simulate scanning every week
        while current_date <= end_date:
            logger.info(f"📅 Scanning {current_date.date()}...")
            
            # Get scanner candidates using pre-downloaded data
            candidates = await self._get_historical_candidates(current_date, strategies, universe_data)
            
            if not candidates:
                logger.debug(f"   No candidates found")
                current_date += timedelta(days=7)
                continue
            
            logger.info(f"   Found {len(candidates)} candidates")
            
            # Analyze with AI if enabled
            if use_ai:
                opportunities = await self._analyze_with_ai(candidates, confidence_threshold, current_date)
            else:
                opportunities = candidates
            
            # Simulate trades
            for opp in opportunities:
                trade = await self._simulate_trade(opp, current_date, universe_data)
                if trade:
                    self.trades.append(trade)
                    logger.info(f"   ✅ {trade.symbol}: {trade.return_pct:+.2f}% ({trade.hold_days}d)")
                    
                    # NEW: Accumulate P&L for the exit date
                    exit_date_str = trade.exit_date.date()
                    if exit_date_str not in daily_pnl:
                        daily_pnl[exit_date_str] = 0.0
                    daily_pnl[exit_date_str] += trade.profit_loss
            
            # Move to next scan date
            current_date += timedelta(days=7)
        
        # Calculate metrics with daily P&L
        metrics = BacktestMetrics(self.trades, self.initial_capital, daily_pnl)
        
        logger.info(f"\n📊 BACKTEST COMPLETE")
        logger.info(f"   Total Trades: {metrics.total_trades}")
        logger.info(f"   Win Rate: {metrics.win_rate:.1f}%")
        logger.info(f"   Net Profit: ${metrics.net_profit:,.2f}")
        logger.info(f"   Total Return: {metrics.total_return_pct:+.2f}%")
        logger.info(f"   Max Drawdown: {metrics.max_drawdown:.2f}%")
        logger.info(f"   Sharpe Ratio: {metrics.sharpe_ratio:.2f}" if metrics.sharpe_ratio else "   Sharpe Ratio: N/A")
        
        return metrics
    
    async def _download_all_historical_data(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        """
        Download all historical data once at the beginning
        
        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            
        Returns:
            Dict mapping symbol to DataFrame with historical data
        """
        universe_data = {}
        
        # Add extra buffer for technical indicators (need 200+ days before start)
        data_start = start_date - timedelta(days=365)
        data_end = end_date + timedelta(days=30)  # Extra buffer for exit simulation
        
        logger.info(f"📥 Fetching historical data from database...")
        
        # Get all symbols in batch from HistoricalDataManager
        symbols = list(self.scanner.SCAN_UNIVERSE)
        universe_data = self.historical_data.get_batch_historical_data(
            symbols=symbols,
            start_date=data_start,
            end_date=data_end
        )
        
        successful = len([df for df in universe_data.values() if not df.empty and len(df) > 50])
        failed = len(universe_data) - successful
        
        # Filter out symbols with insufficient data
        universe_data = {
            symbol: df for symbol, df in universe_data.items() 
            if not df.empty and len(df) > 50
        }
        
        logger.info(f"   Retrieved: {successful} successful, {failed} failed")
        return universe_data
    
    async def _get_historical_candidates(
        self,
        scan_date: datetime,
        strategies: Optional[List[str]] = None,
        universe_data: Optional[Dict[str, pd.DataFrame]] = None
    ) -> List[Dict]:
        """
        Get scanner candidates using historical data
        
        Args:
            scan_date: Date to scan on
            strategies: Strategies to use
            universe_data: Pre-downloaded historical data (if None, downloads on demand)
            
        Returns:
            List of candidate dicts
        """
        # If no pre-downloaded data provided, fetch from database
        if universe_data is None:
            start = scan_date - timedelta(days=180)
            symbols = list(self.scanner.SCAN_UNIVERSE)
            universe_data = self.historical_data.get_batch_historical_data(
                symbols=symbols,
                start_date=start,
                end_date=scan_date
            )
        
        # Run scanner strategies
        candidates = []
        
        if not strategies or 'technical_breakout' in strategies:
            candidates.extend(self._scan_breakouts_historical(universe_data, scan_date))
        
        if not strategies or 'earnings_play' in strategies:
            candidates.extend(self._scan_earnings_historical(universe_data, scan_date))
        
        if not strategies or 'seasonality' in strategies:
            candidates.extend(self._scan_seasonal_historical(universe_data, scan_date))
        
        return candidates
    
    def _scan_breakouts_historical(self, universe_data: Dict, scan_date: datetime) -> List[Dict]:
        """Find technical breakouts in historical data"""
        candidates = []
        
        # Convert scan_date to date for comparison with index
        scan_date_only = scan_date.date() if isinstance(scan_date, datetime) else scan_date
        
        for symbol, hist in universe_data.items():
            try:
                # Get data up to scan date
                data = hist[hist.index <= scan_date_only]
                if len(data) < 50:
                    continue
                
                current_price = data['Close'].iloc[-1]
                
                # Calculate 50-day high
                high_50d = data['Close'].rolling(50).max().iloc[-1]
                
                # Check if breaking out (more lenient: within 5% of 50-day high)
                if current_price >= high_50d * 0.95:  # Within 5% of 50-day high
                    candidates.append({
                        'symbol': symbol,
                        'strategy': 'technical_breakout',
                        'score': 75.0,
                        'price': current_price,
                        'reason': f'Near 50-day high of ${high_50d:.2f} ({((current_price/high_50d - 1) * 100):+.1f}%)'
                    })
            except Exception as e:
                continue
        
        return candidates
    
    def _scan_earnings_historical(self, universe_data: Dict, scan_date: datetime) -> List[Dict]:
        """Find earnings plays in historical data"""
        candidates = []
        
        # Convert scan_date to date for comparison with index
        scan_date_only = scan_date.date() if isinstance(scan_date, datetime) else scan_date
        
        for symbol, hist in universe_data.items():
            try:
                data = hist[hist.index <= scan_date_only]
                if len(data) < 20:
                    continue
                
                current_price = data['Close'].iloc[-1]
                
                # Look for strong recent momentum (potential earnings runners)
                # Check if stock is up >3% in last 5 days
                if len(data) >= 5:
                    price_5d_ago = data['Close'].iloc[-6]  # 5 days ago
                    momentum = ((current_price / price_5d_ago) - 1) * 100
                    
                    if momentum > 3.0:  # Up 3%+ in 5 days (was 5.0)
                        candidates.append({
                            'symbol': symbol,
                            'strategy': 'earnings_play',
                            'score': min(70.0 + momentum, 95.0),  # Higher score for stronger momentum
                            'price': current_price,
                            'reason': f'Strong momentum: +{momentum:.1f}% in 5 days'
                        })
            except Exception as e:
                continue
        
        return candidates
    
    def _scan_seasonal_historical(self, universe_data: Dict, scan_date: datetime) -> List[Dict]:
        """Find seasonal patterns in historical data"""
        candidates = []
        
        # Convert scan_date to date for comparison with index
        scan_date_only = scan_date.date() if isinstance(scan_date, datetime) else scan_date
        
        for symbol, hist in universe_data.items():
            try:
                data = hist[hist.index <= scan_date_only]
                if len(data) < 100:
                    continue
                
                current_price = data['Close'].iloc[-1]
                
                # Calculate seasonal pattern (same month, previous years)
                month = scan_date.month
                seasonal_data = data[data.index.month == month]
                
                if len(seasonal_data) >= 3:
                    # Check if historically positive month
                    returns = seasonal_data['Close'].pct_change().dropna()
                    avg_return = returns.mean()
                    
                    if avg_return > 0.02:  # Positive 2%+ average
                        candidates.append({
                            'symbol': symbol,
                            'strategy': 'seasonality',
                            'score': 65.0,
                            'price': current_price,
                            'reason': f'Historical avg return: {avg_return*100:.1f}%'
                        })
            except Exception as e:
                continue
        
        return candidates
    
    async def _analyze_with_ai(
        self,
        candidates: List[Dict],
        confidence_threshold: float,
        scan_date: datetime
    ) -> List[Dict]:
        """
        Analyze candidates with AI (in backtest mode, we simulate AI responses)
        
        In production, this would call the actual AI analyzer, but for backtesting
        we simulate AI confidence based on scanner scores and actual future returns.
        """
        opportunities = []
        
        for candidate in candidates:
            # Simulate AI confidence (in production, would call analyzer)
            # Use scanner score as base, add some randomness
            import random
            base_confidence = candidate['score'] / 100
            confidence = min(0.95, base_confidence + random.uniform(-0.1, 0.15))
            
            if confidence >= confidence_threshold:
                candidate['ai_confidence'] = confidence
                candidate['ai_reasoning'] = f"Backtest simulated AI analysis (confidence: {confidence:.0%})"
                opportunities.append(candidate)
        
        return opportunities
    
    async def _simulate_trade(
        self,
        opportunity: Dict,
        entry_date: datetime,
        universe_data: Optional[Dict[str, pd.DataFrame]] = None
    ) -> Optional[BacktestResult]:
        """
        Simulate a trade from entry to exit
        
        Args:
            opportunity: Opportunity dict from scanner/analyzer
            entry_date: Date of entry
            universe_data: Pre-downloaded historical data (if None, downloads on demand)
            
        Returns:
            BacktestResult or None if trade failed
        """
        symbol = opportunity['symbol']
        entry_price = opportunity['price']
        
        # Calculate position size
        shares = int(self.position_size / entry_price)
        if shares == 0:
            return None
        
        # Get future data for exit simulation
        try:
            # Use pre-downloaded data if available
            if universe_data and symbol in universe_data:
                all_data = universe_data[symbol]
                # Filter to future dates only (convert entry_date to date for comparison)
                entry_date_only = entry_date.date() if isinstance(entry_date, datetime) else entry_date
                future_data = all_data[all_data.index > entry_date_only]
            else:
                # Fallback: fetch from database
                end_date = entry_date + timedelta(days=self.max_hold_days + 5)
                future_data = self.historical_data.get_historical_data(
                    symbol=symbol,
                    start_date=entry_date,
                    end_date=end_date
                )
            
            if future_data.empty:
                return None
            
            # Simulate exit logic
            exit_date = None
            exit_price = None
            exit_reason = None
            
            # Simple exit rules:
            # 1. Take profit at +10%
            # 2. Stop loss at -5%
            # 3. Max hold time
            
            for date_idx in future_data.index:
                date = pd.Timestamp(date_idx)
                row = future_data.loc[date_idx]
                price = row['Close']
                return_pct = ((price - entry_price) / entry_price) * 100
                days_held = (date - pd.Timestamp(entry_date)).days
                
                # Profit target
                if return_pct >= 10.0:
                    exit_date = date
                    exit_price = price
                    exit_reason = 'profit_target'
                    break
                
                # Stop loss
                if return_pct <= -5.0:
                    exit_date = date
                    exit_price = price
                    exit_reason = 'stop_loss'
                    break
                
                # Max hold time
                if days_held >= self.max_hold_days:
                    exit_date = date
                    exit_price = price
                    exit_reason = 'max_hold_time'
                    break
            
            # If no exit triggered, exit at last available date
            if not exit_date:
                exit_date = pd.Timestamp(future_data.index[-1])
                exit_price = future_data['Close'].iloc[-1]
                exit_reason = 'backtest_end'
            
            # Convert pandas timestamps to datetime
            entry_dt = entry_date.to_pydatetime() if isinstance(entry_date, pd.Timestamp) else entry_date
            exit_dt = exit_date.to_pydatetime() if isinstance(exit_date, pd.Timestamp) else exit_date
            
            # Create result
            return BacktestResult(
                symbol=symbol,
                strategy=opportunity['strategy'],
                entry_date=entry_dt,
                entry_price=entry_price,
                exit_date=exit_dt,
                exit_price=exit_price,
                shares=shares,
                exit_reason=exit_reason,
                scanner_score=opportunity['score'],
                ai_confidence=opportunity.get('ai_confidence', 0.0),
                ai_reasoning=opportunity.get('ai_reasoning', opportunity['reason'])
            )
            
        except Exception as e:
            logger.error(f"   ❌ Error simulating trade for {symbol}: {e}")
            return None


# Singleton instance
_backtester: Optional[Backtester] = None


def get_backtester(
    db: Session,
    initial_capital: float = 10000.0,
    position_size: float = 1000.0,
    max_hold_days: int = 14
) -> Backtester:
    """Get or create singleton backtester instance"""
    global _backtester
    if _backtester is None:
        _backtester = Backtester(db, initial_capital, position_size, max_hold_days)
    return _backtester
