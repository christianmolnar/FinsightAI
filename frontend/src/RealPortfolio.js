import React, { useState, useEffect } from 'react';
import { DollarSign, TrendingUp, TrendingDown, Eye, EyeOff, RefreshCw } from 'lucide-react';

const RealPortfolio = () => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showValues, setShowValues] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchPortfolioData = async () => {
    try {
      setError(null);
      const response = await fetch('http://localhost:8000/api/v1/schwab/portfolio/overview');
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch portfolio data');
      }
      
      setPortfolioData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
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
          <button
            onClick={fetchPortfolioData}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!portfolioData || portfolioData.total_accounts === 0) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-yellow-800 mb-2">No Accounts Found</h2>
          <p className="text-yellow-600">Please make sure you're authenticated with Schwab API and have linked accounts.</p>
        </div>
      </div>
    );
  }

  const totalValue = portfolioData.total_market_value || 0;
  const totalDayPL = portfolioData.total_day_pl || 0;
  const dayPLPercent = portfolioData.day_pl_percent || 0;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Christian's Portfolio</h1>
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
              <p className="text-sm font-medium text-gray-600">Today's P&L</p>
              <p className={`text-2xl font-bold ${totalDayPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(totalDayPL)}
              </p>
            </div>
            {totalDayPL >= 0 ? 
              <TrendingUp className="w-8 h-8 text-green-600" /> : 
              <TrendingDown className="w-8 h-8 text-red-600" />
            }
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Today's Return</p>
              <p className={`text-2xl font-bold ${dayPLPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatPercent(dayPLPercent)}
              </p>
            </div>
            {dayPLPercent >= 0 ? 
              <TrendingUp className="w-8 h-8 text-green-600" /> : 
              <TrendingDown className="w-8 h-8 text-red-600" />
            }
          </div>
        </div>
      </div>

      {/* Accounts */}
      <div className="space-y-6">
        {portfolioData.accounts.map((account, index) => (
          <div key={account.accountHash} className="bg-white rounded-lg shadow">
            <div className="p-6 border-b">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">
                    Account {account.accountNumber} {account.isDayTrader && <span className="text-orange-600">(Day Trader)</span>}
                  </h3>
                  <p className="text-gray-600">{account.type}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-900">{formatCurrency(account.marketValue)}</p>
                  <p className={`text-sm ${account.dayPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(account.dayPL)} today
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t">
                <div>
                  <p className="text-xs text-gray-500">Cash Balance</p>
                  <p className="text-sm font-medium">{formatCurrency(account.cashBalance)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Buying Power</p>
                  <p className="text-sm font-medium">{formatCurrency(account.buyingPower)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Positions</p>
                  <p className="text-sm font-medium">{account.positionCount}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Market Value</p>
                  <p className="text-sm font-medium">{formatCurrency(account.marketValue)}</p>
                </div>
              </div>
            </div>

            {/* Positions */}
            {account.positions && account.positions.length > 0 && (
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
                        <th className="px-4 py-3 text-right font-medium text-gray-600">Day P&L</th>
                        <th className="px-4 py-3 text-right font-medium text-gray-600">Total P&L</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {account.positions.map((position, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-4 py-3">
                            <div>
                              <p className="font-medium text-gray-900">{position.symbol}</p>
                              <p className="text-xs text-gray-500">{position.assetType}</p>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-right font-medium">
                            {position.quantity.toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {formatCurrency(position.averagePrice)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {formatCurrency(position.currentPrice)}
                          </td>
                          <td className="px-4 py-3 text-right font-medium">
                            {formatCurrency(position.marketValue)}
                          </td>
                          <td className={`px-4 py-3 text-right font-medium ${position.dayPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatCurrency(position.dayPL)}
                            <br />
                            <span className="text-xs">
                              {formatPercent(position.dayPLPercent)}
                            </span>
                          </td>
                          <td className={`px-4 py-3 text-right font-medium ${position.totalPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatCurrency(position.totalPL)}
                            <br />
                            <span className="text-xs">
                              {formatPercent(position.totalPLPercent)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RealPortfolio;
