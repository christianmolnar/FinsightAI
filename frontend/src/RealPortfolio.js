import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { DollarSign, TrendingUp, TrendingDown, Eye, EyeOff, RefreshCw } from 'lucide-react';
import MarketStatus from './components/MarketStatus';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const RealPortfolio = () => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showValues, setShowValues] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const fetchPortfolioData = async (tryAlternatePorts = true) => {
    const portsToTry = tryAlternatePorts ? [8000, 8001] : [8000];
    
    for (const port of portsToTry) {
      try {
        setError(null);
        const baseUrl = `http://localhost:${port}`;
        const response = await fetch(`${baseUrl}/api/v1/alpaca/portfolio`, {
          signal: AbortSignal.timeout(5000) // 5 second timeout
        });
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.detail || 'Failed to fetch portfolio data');
        }
        
        setPortfolioData(data);
        setRetryCount(0);
        return; // Success, exit function
      } catch (err) {
        // If this was the last port to try, set the error
        if (port === portsToTry[portsToTry.length - 1]) {
          const isConnectionRefused = err.message.includes('fetch') || err.name === 'TypeError';
          if (isConnectionRefused) {
            setError('Cannot connect to backend server. Please ensure the backend is running on port 8000 or 8001.');
          } else if (err.name === 'TimeoutError') {
            setError('Backend server is not responding. Please check if it\'s running.');
          } else {
            setError(err.message);
          }
        }
        // Continue to next port
        continue;
      }
    }
    
    setLoading(false);
    setRefreshing(false);
  };

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchPortfolioData();
  };

  const formatCurrency = (value) => {
    if (!showValues) return '••••••';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value || 0);
  };

  const formatPercent = (value) => {
    if (!showValues) return '••••';
    return `${(value || 0).toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Portfolio</h2>
          <p className="text-red-600 mb-4">{error}</p>
          {error.includes('backend') && (
            <div className="text-sm text-gray-600 mb-4 p-3 bg-gray-50 rounded">
              <p className="font-medium mb-2">Troubleshooting steps:</p>
              <ol className="text-left list-decimal list-inside space-y-1">
                <li>Make sure the backend server is running</li>
                <li>Check terminal for any backend errors</li>
                <li>Try restarting the backend: <code className="bg-gray-200 px-1 rounded">uvicorn app.main:app --reload --port 8000</code></li>
              </ol>
            </div>
          )}
          <button
            onClick={() => {
              setLoading(true);
              setRetryCount(retryCount + 1);
              fetchPortfolioData();
            }}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Try Again {retryCount > 0 && `(Attempt ${retryCount + 1})`}
          </button>
        </div>
      </div>
    );
  }

  if (!portfolioData || !portfolioData.account) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-yellow-800 mb-2">No Account Found</h2>
          <p className="text-yellow-600">Please make sure you're authenticated with Alpaca API and have linked your account.</p>
        </div>
      </div>
    );
  }

  const account = portfolioData.account;
  const positions = portfolioData.positions || [];
  const metrics = portfolioData.metrics || {};
  
  const totalValue = metrics.total_portfolio_value || account.portfolio_value || 0;
  const totalDayPL = 0; // Alpaca doesn't provide daily P&L in same way
  const dayPLPercent = 0;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-4">
          <h1 className="text-3xl font-bold text-gray-900">Christian's Portfolio</h1>
          <MarketStatus />
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowValues(!showValues)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            {showValues ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            {showValues ? 'Hide Values' : 'Show Values'}
          </button>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Portfolio Value</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalValue)}</p>
            </div>
            <DollarSign className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cash Balance</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(account.cash)}
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Buying Power</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(account.buying_power)}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* Account Details */}
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Alpaca Account {account.pattern_day_trader && <span className="text-orange-600">(Day Trader)</span>}
                </h3>
                <p className="text-gray-600">{account.status}</p>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-gray-900">{formatCurrency(account.portfolio_value)}</p>
                <p className="text-sm text-gray-500">Portfolio Value</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t">
              <div>
                <p className="text-xs text-gray-500">Cash Balance</p>
                <p className="text-sm font-medium">{formatCurrency(account.cash)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Buying Power</p>
                <p className="text-sm font-medium">{formatCurrency(account.buying_power)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Positions</p>
                <p className="text-sm font-medium">{metrics.position_count || 0}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Equity</p>
                <p className="text-sm font-medium">{formatCurrency(account.equity)}</p>
              </div>
            </div>
          </div>

          {/* Positions */}
          {positions && positions.length > 0 ? (
            <div className="p-6">
              <h4 className="text-lg font-semibold mb-4">Positions</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-medium text-gray-600">Symbol</th>
                      <th className="px-4 py-3 text-right font-medium text-gray-600">Quantity</th>
                      <th className="px-4 py-3 text-right font-medium text-gray-600">Avg Price</th>
                      <th className="px-4 py-3 text-right font-medium text-gray-600">Current Price</th>
                      <th className="px-4 py-3 text-right font-medium text-gray-600">Market Value</th>
                      <th className="px-4 py-3 text-right font-medium text-gray-600">Unrealized P&L</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {positions.map((position, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <div>
                            <p className="font-medium text-gray-900">{position.symbol}</p>
                            <p className="text-xs text-gray-500">{position.asset_class || 'Stock'}</p>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-right font-medium">
                          {parseFloat(position.qty).toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {formatCurrency(parseFloat(position.avg_entry_price))}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {formatCurrency(parseFloat(position.current_price))}
                        </td>
                        <td className="px-4 py-3 text-right font-medium">
                          {formatCurrency(parseFloat(position.market_value))}
                        </td>
                        <td className={`px-4 py-3 text-right font-medium ${parseFloat(position.unrealized_pl) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(parseFloat(position.unrealized_pl))}
                          <br />
                          <span className="text-xs">
                            {formatPercent(parseFloat(position.unrealized_plpc) * 100)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-gray-500">
              <p>No open positions</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RealPortfolio;
