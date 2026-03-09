"""
Universe Builder

Fetches and maintains lists of stocks from major indices:
- S&P 500 (~500 stocks)
- DOW 30 (30 stocks)
- NASDAQ 100 (~100 stocks)
- Russell 2000 (2000 stocks)

Provides unified interface for building scan universe.
"""

import logging
from typing import List, Dict, Set
import pandas as pd
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class UniverseBuilder:
    """
    Builds stock universe from major indices
    """
    
    # Cache fetched lists for 24 hours
    _cache: Dict[str, tuple[List[str], datetime]] = {}
    _cache_duration = timedelta(hours=24)
    
    def build_universe(
        self,
        include_indices: List[str] = ['SP500', 'DOW', 'NASDAQ100']
    ) -> List[str]:
        """
        Build stock universe from specified indices
        
        Args:
            include_indices: List of indices to include
                Options: 'SP500', 'DOW', 'NASDAQ100', 'RUSSELL2000', 'ALL'
        
        Returns:
            List of unique stock symbols
        """
        all_symbols: Set[str] = set()
        
        if 'ALL' in include_indices:
            include_indices = ['SP500', 'DOW', 'NASDAQ100', 'RUSSELL2000']
        
        for index in include_indices:
            try:
                symbols = self._fetch_index_constituents(index)
                all_symbols.update(symbols)
                logger.info(f"   Added {len(symbols)} stocks from {index}")
            except Exception as e:
                logger.error(f"   Failed to fetch {index}: {e}")
        
        return sorted(list(all_symbols))
    
    def _fetch_index_constituents(self, index: str) -> List[str]:
        """Fetch constituents for a specific index"""
        
        # Check cache first
        if index in self._cache:
            symbols, cached_time = self._cache[index]
            if datetime.now() - cached_time < self._cache_duration:
                logger.debug(f"   Using cached {index}")
                return symbols
        
        # Fetch based on index
        if index == 'SP500':
            symbols = self._fetch_sp500()
        elif index == 'DOW':
            symbols = self._fetch_dow()
        elif index == 'NASDAQ100':
            symbols = self._fetch_nasdaq100()
        elif index == 'RUSSELL2000':
            symbols = self._fetch_russell2000()
        else:
            raise ValueError(f"Unknown index: {index}")
        
        # Cache result
        self._cache[index] = (symbols, datetime.now())
        
        return symbols
    
    def _fetch_sp500(self) -> List[str]:
        """
        Fetch S&P 500 constituents from Wikipedia
        
        Returns:
            List of ~500 stock symbols
        """
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            
            # First table contains current constituents
            df = tables[0]
            symbols = df['Symbol'].str.replace('.', '-').tolist()
            
            logger.info(f"   Fetched {len(symbols)} S&P 500 stocks")
            return symbols
            
        except Exception as e:
            logger.error(f"Failed to fetch S&P 500: {e}")
            # Fallback to hardcoded list of top stocks
            return self._get_fallback_sp500()
    
    def _fetch_dow(self) -> List[str]:
        """
        Fetch DOW 30 constituents from Wikipedia
        
        Returns:
            List of 30 stock symbols
        """
        try:
            url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
            tables = pd.read_html(url)
            
            # Find table with ticker symbols
            for table in tables:
                if 'Symbol' in table.columns or 'Ticker' in table.columns:
                    symbol_col = 'Symbol' if 'Symbol' in table.columns else 'Ticker'
                    symbols = table[symbol_col].str.replace('.', '-').tolist()
                    
                    # DOW should have exactly 30 stocks
                    if len(symbols) == 30:
                        logger.info(f"   Fetched {len(symbols)} DOW stocks")
                        return symbols
            
            # Fallback
            return self._get_fallback_dow()
            
        except Exception as e:
            logger.error(f"Failed to fetch DOW: {e}")
            return self._get_fallback_dow()
    
    def _fetch_nasdaq100(self) -> List[str]:
        """
        Fetch NASDAQ 100 constituents from Wikipedia
        
        Returns:
            List of ~100 stock symbols
        """
        try:
            url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            tables = pd.read_html(url)
            
            # First table contains constituents
            df = tables[3]  # Usually the 4th table
            symbols = df['Ticker'].str.replace('.', '-').tolist()
            
            logger.info(f"   Fetched {len(symbols)} NASDAQ-100 stocks")
            return symbols
            
        except Exception as e:
            logger.error(f"Failed to fetch NASDAQ-100: {e}")
            return self._get_fallback_nasdaq100()
    
    def _fetch_russell2000(self) -> List[str]:
        """
        Fetch US equity universe via Alpaca Assets API.
        Returns all active, fractionable US equities — a superset of Russell 2000.
        Filters out ETFs, warrants, and very small/illiquid names.
        """
        try:
            import os
            api_key = os.getenv("ALPACA_API_KEY") or os.getenv("ALPACA_PAPER_API_KEY")
            api_secret = os.getenv("ALPACA_SECRET_KEY") or os.getenv("ALPACA_PAPER_SECRET_KEY")

            if not api_key or not api_secret:
                logger.warning("Alpaca keys not set — skipping extended universe")
                return []

            url = "https://paper-api.alpaca.markets/v2/assets"
            headers = {
                "APCA-API-KEY-ID": api_key,
                "APCA-API-SECRET-KEY": api_secret,
            }
            params = {
                "status": "active",
                "asset_class": "us_equity",
                "exchange": "NYSE,NASDAQ,ARCA",  # Exclude OTC/pink sheets
            }
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            assets = response.json()

            # Filter: tradable, fractionable (liquid), no special characters
            symbols = [
                a['symbol'] for a in assets
                if a.get('tradable') and a.get('fractionable')
                and a.get('symbol', '').isalpha()          # No slash/dot symbols
                and len(a.get('symbol', '')) <= 5          # No long OTC symbols
            ]

            logger.info(f"   Fetched {len(symbols)} stocks from Alpaca US equity universe")
            return symbols

        except Exception as e:
            logger.error(f"Failed to fetch Alpaca universe: {e}")
            return []
    
    def _get_fallback_sp500(self) -> List[str]:
        """Fallback S&P 500 list (top 50 stocks)"""
        return [
            # Tech
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA',
            'AVGO', 'ORCL', 'CSCO', 'ADBE', 'CRM', 'INTC', 'AMD', 'QCOM',
            # Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP',
            # Healthcare
            'UNH', 'JNJ', 'LLY', 'PFE', 'ABBV', 'TMO', 'MRK', 'ABT', 'DHR',
            # Consumer
            'WMT', 'HD', 'PG', 'COST', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW',
            # Industrials
            'BA', 'HON', 'UPS', 'CAT', 'GE', 'RTX', 'LMT', 'DE',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG',
            # Telecom/Media
            'DIS', 'NFLX', 'CMCSA', 'T', 'VZ', 'TMUS',
        ]
    
    def _get_fallback_dow(self) -> List[str]:
        """Fallback DOW 30 list"""
        return [
            'AAPL', 'MSFT', 'UNH', 'GS', 'HD', 'MCD', 'CAT', 'V',
            'BA', 'AXP', 'TRV', 'JPM', 'IBM', 'AMGN', 'HON', 'CRM',
            'CVX', 'NKE', 'WMT', 'JNJ', 'KO', 'MRK', 'PG', 'DIS',
            'MMM', 'DOW', 'CSCO', 'INTC', 'WBA', 'VZ'
        ]
    
    def _get_fallback_nasdaq100(self) -> List[str]:
        """Fallback NASDAQ-100 list (top 40 tech stocks)"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA',
            'AVGO', 'COST', 'PEP', 'CSCO', 'ADBE', 'NFLX', 'CMCSA', 'INTC',
            'AMD', 'QCOM', 'TXN', 'INTU', 'AMGN', 'HON', 'SBUX', 'AMAT',
            'ISRG', 'ADI', 'GILD', 'MDLZ', 'REGN', 'PYPL', 'BKNG', 'ADP',
            'VRTX', 'LRCX', 'PANW', 'ABNB', 'SNPS', 'KLAC', 'MELI', 'MNST'
        ]


# Convenience functions
def get_sp500_list() -> List[str]:
    """Get S&P 500 constituent list"""
    builder = UniverseBuilder()
    return builder._fetch_sp500()


def get_dow_list() -> List[str]:
    """Get DOW 30 constituent list"""
    builder = UniverseBuilder()
    return builder._fetch_dow()


def get_nasdaq100_list() -> List[str]:
    """Get NASDAQ-100 constituent list"""
    builder = UniverseBuilder()
    return builder._fetch_nasdaq100()


def get_full_universe() -> List[str]:
    """Get complete universe (S&P 500 + DOW + NASDAQ-100)"""
    builder = UniverseBuilder()
    return builder.build_universe(['SP500', 'DOW', 'NASDAQ100'])
