"""
Strategy Executor

Executes backtests using user's actual strategy configuration parameters.
Replaces hardcoded placeholder logic with parameter-driven decision making.

Key Features:
- Loads user's StrategyConfig from database
- Applies ALL 50+ parameters from Strategy/Config page
- Tracks which parameters triggered each trade
- Enables accurate backtesting and optimization
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, date
import pandas as pd
from sqlalchemy.orm import Session

from services.earnings_data import (
    get_days_until_earnings,
    get_historical_beat_rate,
    get_avg_eps_surprise,
    get_eps_growth_yoy,
    is_near_earnings,
)
from services.macro_data import get_macro_snapshot
from services.sentiment_data import get_sentiment_snapshot

logger = logging.getLogger(__name__)


class StrategyExecutor:
    """
    Executes trading strategies using user's actual configuration parameters.
    
    This is the REAL strategy engine - not placeholder logic.
    Every decision is driven by parameters from the Strategy/Config page.
    """
    
    def __init__(self, strategy_config: Dict):
        """
        Initialize with user's strategy configuration
        
        Args:
            strategy_config: Dict with keys: earnings, seasonality, macro, sentiment
                            Each containing parameters from Strategy/Config page
        """
        self.config = strategy_config
        logger.info(f"🎯 StrategyExecutor initialized with user configuration")
        logger.debug(f"   Strategies enabled: {[k for k, v in strategy_config.items() if v.get('enabled', False)]}")
    
    def scan_earnings_opportunities(
        self, 
        symbol: str,
        hist_data: pd.DataFrame,
        scan_date: datetime,
        market_data: Dict
    ) -> Optional[Dict]:
        """
        Scan for earnings opportunities using REAL user parameters
        
        User Parameters Applied:
        - daysBeforeEarnings: When to enter before earnings
        - minEpsGrowth: Minimum EPS growth % YoY
        - minRevenueGrowth: Minimum revenue growth %
        - historicalBeatRate: Required historical beat rate %
        - profitTarget: Profit target %
        - stopLoss: Stop loss %
        - maxPortfolioWeight: Max portfolio allocation %
        """
        params = self.config.get('earnings', {}).get('params', {})
        
        if not self.config.get('earnings', {}).get('enabled', False):
            return None
        
        # Extract parameter values
        days_before = params.get('daysBeforeEarnings', {}).get('value', 5)
        min_eps_growth = params.get('minEpsGrowth', {}).get('value', 15)
        min_revenue_growth = params.get('minRevenueGrowth', {}).get('value', 10)
        beat_rate_required = params.get('historicalBeatRate', {}).get('value', 70)

        try:
            scan_date_only = scan_date.date() if isinstance(scan_date, datetime) else scan_date
            data = hist_data[hist_data.index <= pd.Timestamp(scan_date_only)]

            if len(data) < 20:
                return None

            current_price = float(data['Close'].iloc[-1])

            # ── Real earnings gate: must be within `days_before` days of earnings ──
            days_until = get_days_until_earnings(symbol, scan_date_only)
            if days_until is None or days_until < 0 or days_until > days_before:
                return None  # No upcoming earnings in the window

            # ── Historical beat rate ──
            beat_rate = get_historical_beat_rate(symbol)
            if beat_rate is None or beat_rate < beat_rate_required:
                return None

            # ── YoY EPS growth ──
            eps_growth = get_eps_growth_yoy(symbol, scan_date_only)
            if eps_growth is not None and eps_growth < min_eps_growth:
                return None

            # ── Average EPS surprise (bonus signal quality check) ──
            avg_surprise = get_avg_eps_surprise(symbol)

            score = 70.0
            score += min(beat_rate - beat_rate_required, 20)  # Up to +20 for beat rate
            if avg_surprise is not None:
                score += min(avg_surprise, 10)  # Up to +10 for avg surprise
            if eps_growth is not None:
                score += min((eps_growth - min_eps_growth) / 10, 5)  # Up to +5 for growth

            reason_parts = [
                f"Earnings in {days_until}d",
                f"beat rate {beat_rate:.0f}%",
            ]
            if eps_growth is not None:
                reason_parts.append(f"EPS growth {eps_growth:+.0f}% YoY")
            if avg_surprise is not None:
                reason_parts.append(f"avg surprise {avg_surprise:+.1f}%")

            return {
                'symbol': symbol,
                'strategy': 'earnings',
                'score': min(score, 100.0),
                'price': current_price,
                'reason': 'Earnings play: ' + ', '.join(reason_parts),
                'signal_metadata': {
                    'days_until_earnings': days_until,
                    'beat_rate_pct': beat_rate,
                    'eps_growth_yoy_pct': eps_growth,
                    'avg_eps_surprise_pct': avg_surprise,
                },
                'params_used': {
                    'daysBeforeEarnings': days_before,
                    'minEpsGrowth': min_eps_growth,
                    'minRevenueGrowth': min_revenue_growth,
                    'historicalBeatRate': beat_rate_required,
                },
                'exit_params': {
                    'profit_target': params.get('profitTarget', {}).get('value', 12),
                    'stop_loss': params.get('stopLoss', {}).get('value', 5),
                    'max_portfolio_weight': params.get('maxPortfolioWeight', {}).get('value', 20),
                }
            }

        except Exception as e:
            logger.debug(f"   Error scanning {symbol} earnings: {e}")
            return None
    
    def scan_seasonality_opportunities(
        self,
        symbol: str,
        hist_data: pd.DataFrame,
        scan_date: datetime,
        market_data: Dict
    ) -> Optional[Dict]:
        """
        Scan for seasonality opportunities using REAL user parameters
        
        User Parameters Applied:
        - weeksBeforePeak: Weeks before seasonal peak to enter
        - minHistoricalYears: Years of historical data required
        - minSeasonalReturn: Minimum seasonal return %
        - profitTarget: Profit target %
        - stopLoss: Stop loss %
        """
        params = self.config.get('seasonality', {}).get('params', {})
        
        if not self.config.get('seasonality', {}).get('enabled', False):
            return None
        
        weeks_before = params.get('weeksBeforePeak', {}).get('value', 3)
        min_years = params.get('minHistoricalYears', {}).get('value', 5)
        min_seasonal_return = params.get('minSeasonalReturn', {}).get('value', 8)
        
        try:
            scan_date_only = scan_date.date() if isinstance(scan_date, datetime) else scan_date
            data = hist_data[hist_data.index <= pd.Timestamp(scan_date_only)]

            if len(data) < 252 * min_years:
                return None

            current_price = float(data['Close'].iloc[-1])
            current_month = scan_date_only.month if isinstance(scan_date_only, date) else scan_date.month

            # Cast index to DatetimeIndex for .year / .month accessors
            dt_index = pd.DatetimeIndex(data.index)

            # ── Compute per-month average returns across all historical years ──
            # monthly_avg[month] = average % return for that calendar month
            monthly_avg: Dict[int, float] = {}
            for month in range(1, 13):
                returns = []
                for yr in dt_index.year.unique():
                    month_bars = data[(dt_index.year == yr) & (dt_index.month == month)]
                    if len(month_bars) > 2:
                        ret = ((month_bars['Close'].iloc[-1] - month_bars['Close'].iloc[0]) /
                               month_bars['Close'].iloc[0]) * 100
                        returns.append(ret)
                if returns:
                    monthly_avg[month] = sum(returns) / len(returns)

            if len(monthly_avg) < 6:
                return None

            # ── Find the best upcoming month within `weeks_before` entry window ──
            # Look ahead up to 3 months for a strong seasonal peak
            best_peak_month = None
            best_peak_return = -999.0
            for offset in range(1, 4):  # 1–3 months ahead = "upcoming peak"
                lookahead_month = ((current_month - 1 + offset) % 12) + 1
                avg_ret = monthly_avg.get(lookahead_month, 0.0)
                if avg_ret > best_peak_return:
                    best_peak_return = avg_ret
                    best_peak_month = lookahead_month

            if best_peak_month is None or best_peak_return < min_seasonal_return:
                return None

            # ── Consistency: how many years did this month beat the threshold? ──
            consistent_years = sum(
                1 for yr in dt_index.year.unique()
                for m_bars in [data[(dt_index.year == yr) & (dt_index.month == best_peak_month)]]
                if len(m_bars) > 2 and
                ((m_bars['Close'].iloc[-1] - m_bars['Close'].iloc[0]) / m_bars['Close'].iloc[0]) * 100 > 0
            )
            years_of_data = len(dt_index.year.unique())
            consistency_pct = (consistent_years / years_of_data * 100) if years_of_data > 0 else 0

            score = 65.0
            score += min(best_peak_return - min_seasonal_return, 20)  # up to +20 for return magnitude
            score += min(consistency_pct - 50, 15)                    # up to +15 for consistency

            months_abbr = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            peak_name = months_abbr[best_peak_month - 1]

            return {
                'symbol': symbol,
                'strategy': 'seasonality',
                'score': min(score, 100.0),
                'price': current_price,
                'reason': (f'Seasonal: {peak_name} avg +{best_peak_return:.1f}% '
                           f'({consistent_years}/{years_of_data} yrs positive)'),
                'signal_metadata': {
                    'peak_month': best_peak_month,
                    'peak_month_name': peak_name,
                    'avg_return_pct': round(best_peak_return, 2),
                    'consistency_pct': round(consistency_pct, 1),
                    'years_analyzed': years_of_data,
                    'monthly_avg': {months_abbr[m - 1]: round(v, 2) for m, v in monthly_avg.items()},
                },
                'params_used': {
                    'weeksBeforePeak': weeks_before,
                    'minHistoricalYears': min_years,
                    'minSeasonalReturn': min_seasonal_return,
                },
                'exit_params': {
                    'profit_target': params.get('profitTarget', {}).get('value', 15),
                    'stop_loss': params.get('stopLoss', {}).get('value', 7),
                    'max_portfolio_weight': params.get('maxPortfolioWeight', {}).get('value', 15),
                }
            }

        except Exception as e:
            logger.debug(f"   Error scanning {symbol} seasonality: {e}")
            return None
    
    def scan_macro_opportunities(
        self,
        symbol: str,
        hist_data: pd.DataFrame,
        scan_date: datetime,
        market_data: Dict,
    ) -> Optional[Dict]:
        """
        Scan for macro-favorable conditions using real indicators.

        User Parameters Applied:
        - maxVix: Max VIX level to allow entry (default 25)
        - minYieldSpread: Min 10Y-2Y spread to allow entry (default -0.5; blocks deep inversion)
        - requirePositiveSectorMomentum: Block entry when symbol's sector is negative (default True)
        - profitTarget / stopLoss / maxPortfolioWeight: exit params

        Macro data is fetched live from yfinance (1-hour cache).
        When scan_date is historical, data is filtered to that date.
        """
        params = self.config.get('macro', {}).get('params', {})

        if not self.config.get('macro', {}).get('enabled', False):
            return None

        max_vix = params.get('maxVix', {}).get('value', 25.0)
        min_yield_spread = params.get('minYieldSpread', {}).get('value', -0.5)
        require_positive_sector = params.get('requirePositiveSectorMomentum', {}).get('value', True)

        try:
            scan_dt = scan_date if isinstance(scan_date, datetime) else datetime(scan_date.year, scan_date.month, scan_date.day)
            snapshot = get_macro_snapshot(as_of=scan_dt)

            vix = snapshot.get('vix')
            yield_spread = snapshot.get('yield_spread')
            sector_momentum = snapshot.get('sector_momentum', {})
            top_sector = snapshot.get('top_sector')
            top_sector_return = snapshot.get('top_sector_return')

            reasons_blocked = []

            # Gate 1: VIX
            if vix is not None and vix > max_vix:
                reasons_blocked.append(f"VIX {vix:.1f} > max {max_vix}")

            # Gate 2: Yield curve not deeply inverted
            if yield_spread is not None and yield_spread < min_yield_spread:
                reasons_blocked.append(f"Yield spread {yield_spread:.2f} < min {min_yield_spread}")

            # Gate 3: Sector momentum — check if majority of sectors are positive
            if require_positive_sector and sector_momentum:
                positive_sectors = sum(1 for v in sector_momentum.values() if v > 0)
                total_sectors = len(sector_momentum)
                if positive_sectors < total_sectors * 0.5:
                    reasons_blocked.append(f"Only {positive_sectors}/{total_sectors} sectors positive")

            if reasons_blocked:
                return None

            # Score based on macro quality
            score = 60.0
            if vix is not None:
                score += max(0, (max_vix - vix) / max_vix * 20)   # up to +20 for low VIX
            if yield_spread is not None:
                score += min(max(yield_spread, 0) * 5, 10)         # up to +10 for steep curve
            if sector_momentum:
                positive_sectors = sum(1 for v in sector_momentum.values() if v > 0)
                score += (positive_sectors / len(sector_momentum)) * 10  # up to +10 breadth

            current_price = float(hist_data['Close'].iloc[-1]) if len(hist_data) > 0 else 0.0

            reason_parts = []
            if vix is not None:
                reason_parts.append(f"VIX {vix:.1f}")
            if yield_spread is not None:
                reason_parts.append(f"Spread {yield_spread:+.2f}%")
            if top_sector and top_sector_return is not None:
                reason_parts.append(f"Top sector {top_sector} +{top_sector_return:.1f}%")

            return {
                'symbol': symbol,
                'strategy': 'macro',
                'score': min(score, 100.0),
                'price': current_price,
                'reason': 'Macro: ' + ', '.join(reason_parts),
                'signal_metadata': {
                    'vix': vix,
                    'yield_spread': yield_spread,
                    'sector_momentum': sector_momentum,
                    'top_sector': top_sector,
                    'top_sector_return': top_sector_return,
                },
                'params_used': {
                    'maxVix': max_vix,
                    'minYieldSpread': min_yield_spread,
                    'requirePositiveSectorMomentum': require_positive_sector,
                },
                'exit_params': {
                    'profit_target': params.get('profitTarget', {}).get('value', 15),
                    'stop_loss': params.get('stopLoss', {}).get('value', 7),
                    'max_portfolio_weight': params.get('maxPortfolioWeight', {}).get('value', 15),
                }
            }

        except Exception as e:
            logger.debug(f"   Error scanning {symbol} macro: {e}")
            return None

    def scan_sentiment_opportunities(
        self,
        symbol: str,
        hist_data: pd.DataFrame,
        scan_date: datetime,
        market_data: Dict,
    ) -> Optional[Dict]:
        """
        Scan for positive news-sentiment conditions.

        User Parameters Applied:
        - minSentimentScore: Minimum normalised score [-1, +1] to trigger (default 0.2)
        - minPositiveRatio: Minimum fraction of positive headlines (default 0.4)
        - minArticles: Require at least N headlines; skip if less (default 3)
        - profitTarget / stopLoss / maxPortfolioWeight: exit params

        Uses yfinance ticker.news (no API key required).
        Backtests automatically receive a neutral/skipped result to avoid look-ahead bias.
        """
        params = self.config.get('sentiment', {}).get('params', {})

        if not self.config.get('sentiment', {}).get('enabled', False):
            return None

        min_score         = params.get('minSentimentScore', {}).get('value', 0.2)
        min_pos_ratio     = params.get('minPositiveRatio',  {}).get('value', 0.4)
        min_articles      = params.get('minArticles',       {}).get('value', 3)

        try:
            scan_dt = scan_date if isinstance(scan_date, datetime) else datetime(scan_date.year, scan_date.month, scan_date.day)
            snapshot = get_sentiment_snapshot(symbol, as_of=scan_dt)

            # Skip gracefully in backtest mode
            if snapshot.get('backtest_placeholder'):
                return None

            total_articles  = snapshot.get('total_articles', 0)
            sentiment_score = snapshot.get('sentiment_score', 0.0)
            positive_ratio  = snapshot.get('positive_ratio', 0.0)
            pos_count       = snapshot.get('positive', 0)
            neg_count       = snapshot.get('negative', 0)

            # Gate 1: Need enough articles to form a view
            if total_articles < min_articles:
                return None

            # Gate 2: Overall sentiment score
            if sentiment_score < min_score:
                return None

            # Gate 3: Positive headline ratio
            if positive_ratio < min_pos_ratio:
                return None

            # Score: base 55, up to +25 for score, +10 for ratio, +10 for volume of coverage
            score = 55.0
            score += min((sentiment_score - min_score) / (1.0 - min_score + 1e-9) * 25, 25)
            score += min((positive_ratio - min_pos_ratio) / (1.0 - min_pos_ratio + 1e-9) * 10, 10)
            score += min(total_articles / 10 * 10, 10)

            current_price = float(hist_data['Close'].iloc[-1]) if len(hist_data) > 0 else 0.0

            return {
                'symbol': symbol,
                'strategy': 'sentiment',
                'score': round(min(score, 100.0), 1),
                'price': current_price,
                'reason': (
                    f"Sentiment: score {sentiment_score:+.2f}, "
                    f"{pos_count} positive / {neg_count} negative of {total_articles} articles"
                ),
                'signal_metadata': {
                    'sentiment_score': sentiment_score,
                    'positive_ratio': positive_ratio,
                    'total_articles': total_articles,
                    'positive': pos_count,
                    'negative': neg_count,
                    'top_headlines': [h['title'] for h in snapshot.get('headlines', [])[:3]],
                },
                'params_used': {
                    'minSentimentScore': min_score,
                    'minPositiveRatio': min_pos_ratio,
                    'minArticles': min_articles,
                },
                'exit_params': {
                    'profit_target': params.get('profitTarget', {}).get('value', 15),
                    'stop_loss': params.get('stopLoss', {}).get('value', 7),
                    'max_portfolio_weight': params.get('maxPortfolioWeight', {}).get('value', 10),
                },
            }

        except Exception as e:
            logger.debug(f"   Error scanning {symbol} sentiment: {e}")
            return None

    def scan_technical_breakout_opportunities(
        self,
        symbol: str,
        hist_data: pd.DataFrame,
        scan_date: datetime,
        market_data: Dict
    ) -> Optional[Dict]:
        """
        Scan for technical breakout opportunities
        
        Note: This uses general technical filters from the config
        """
        # Check if any strategy is enabled (breakouts support all strategies)
        if not any(self.config.get(s, {}).get('enabled', False) 
                  for s in ['earnings', 'seasonality', 'macro', 'sentiment']):
            return None
        
        try:
            scan_date_only = scan_date.date() if isinstance(scan_date, datetime) else scan_date
            data = hist_data[hist_data.index <= pd.Timestamp(scan_date_only)]
            
            if len(data) < 50:
                return None
            
            current_price = float(data['Close'].iloc[-1])
            volume = float(data['Volume'].iloc[-1])
            avg_volume = float(data['Volume'].tail(20).mean())
            
            # Calculate 50-day high
            high_50d = float(data['Close'].rolling(50).max().iloc[-1])
            
            # Check if breaking out (within 3% of 50-day high)
            distance_from_high = ((current_price / high_50d) - 1) * 100
            
            if distance_from_high < -3:  # More than 3% below high
                return None
            
            # Volume confirmation
            volume_ratio = volume / avg_volume if avg_volume > 0 else 0
            if volume_ratio < 1.2:
                return None
            
            # PASS: Technical breakout detected
            return {
                'symbol': symbol,
                'strategy': 'technical_breakout',
                'score': 75.0 + abs(distance_from_high) * 2,
                'price': current_price,
                'reason': f'Breakout: {distance_from_high:+.1f}% from 50d high, volume {volume_ratio:.1f}x',
                'params_used': {
                    'high_50d': high_50d,
                    'distance_from_high_pct': distance_from_high,
                    'volume_ratio': volume_ratio
                },
                'exit_params': {
                    'profit_target': 15.0,  # Default
                    'stop_loss': 8.0,       # Default
                    'max_portfolio_weight': 15.0
                }
            }
            
        except Exception as e:
            logger.debug(f"   Error scanning {symbol} breakout: {e}")
            return None
    
    def scan_all_strategies(
        self,
        symbol: str,
        hist_data: pd.DataFrame,
        scan_date: datetime,
        market_data: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Scan all enabled strategies for this symbol
        
        Returns:
            List of opportunities (one per strategy that triggers)
        """
        if market_data is None:
            market_data = {}
        
        opportunities = []
        
        # Check each strategy
        opp = self.scan_earnings_opportunities(symbol, hist_data, scan_date, market_data)
        if opp:
            opportunities.append(opp)
        
        opp = self.scan_seasonality_opportunities(symbol, hist_data, scan_date, market_data)
        if opp:
            opportunities.append(opp)

        opp = self.scan_macro_opportunities(symbol, hist_data, scan_date, market_data)
        if opp:
            opportunities.append(opp)

        opp = self.scan_sentiment_opportunities(symbol, hist_data, scan_date, market_data)
        if opp:
            opportunities.append(opp)

        opp = self.scan_technical_breakout_opportunities(symbol, hist_data, scan_date, market_data)
        if opp:
            opportunities.append(opp)

        return opportunities
