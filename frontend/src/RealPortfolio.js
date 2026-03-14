import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { DollarSign, TrendingUp, TrendingDown, Eye, EyeOff, RefreshCw, Plus, Target, ChevronDown, ChevronUp, Clock } from 'lucide-react';
import MarketStatus from './components/MarketStatus';
import ConfirmationModal from './components/ConfirmationModal';
import NotificationModal from './components/NotificationModal';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const RealPortfolio = () => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showValues, setShowValues] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [showTradeModal, setShowTradeModal] = useState(false);
  const [tradeForm, setTradeForm] = useState({
    symbol: '',
    action: 'BUY',
    quantity: 1,
    orderType: 'market'
  });
  const [currentPrice, setCurrentPrice] = useState(null);
  const [loadingPrice, setLoadingPrice] = useState(false);
  const [tradeLoading, setTradeLoading] = useState(false);
  const [marketStatus, setMarketStatus] = useState(null);
  const [pendingOrders, setPendingOrders] = useState([]);
  const [showPendingOrders, setShowPendingOrders] = useState(true);
  const [showHoldings, setShowHoldings] = useState(true);
  const [watchlist, setWatchlist] = useState([]);
  const [newWatchSymbol, setNewWatchSymbol] = useState('');
  
  // Modal states
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmModalConfig, setConfirmModalConfig] = useState({});
  const [showNotification, setShowNotification] = useState(false);
  const [notificationConfig, setNotificationConfig] = useState({});

  const fetchPortfolioData = async () => {
    try {
      setError(null);
      const response = await fetch(`${API_BASE_URL}/api/v1/alpaca/live/portfolio`, {
        signal: AbortSignal.timeout(10000)
      });
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch portfolio data');
      }
      
      setPortfolioData(data);
      setRetryCount(0);
    } catch (err) {
      setError(err.message || 'Failed to connect to backend server.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchPortfolioData();
    fetchMarketStatus();
    fetchPendingOrders();
    loadWatchlist();
  }, []);

  // Fetch price when symbol changes in trade modal
  useEffect(() => {
    if (showTradeModal && tradeForm.symbol && tradeForm.symbol.length >= 1) {
      const debounce = setTimeout(() => {
        fetchStockPrice(tradeForm.symbol);
      }, 500);
      return () => clearTimeout(debounce);
    } else {
      setCurrentPrice(null);
    }
  }, [tradeForm.symbol, showTradeModal]);

  const fetchStockPrice = async (symbol) => {
    try {
      setLoadingPrice(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/quotes/${symbol}`);
      const data = await response.json();
      if (response.ok && data.price) {
        setCurrentPrice(data.price);
      }
    } catch (error) {
      console.error('Error fetching price:', error);
    } finally {
      setLoadingPrice(false);
    }
  };

  const fetchMarketStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/market/status`);
      const data = await response.json();
      if (data.success) {
        setMarketStatus(data);
      }
    } catch (error) {
      console.error('Error fetching market status:', error);
    }
  };

  const fetchPendingOrders = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/alpaca/live/orders`);
      if (response.ok) {
        const data = await response.json();
        // Filter for pending orders (not filled or cancelled)
        const pending = (data.orders || []).filter(order => 
          ['new', 'accepted', 'pending_new', 'partially_filled'].includes(order.status)
        );
        setPendingOrders(pending);
      }
    } catch (error) {
      console.error('Error fetching pending orders:', error);
    }
  };

  // Watchlist functions
  const loadWatchlist = () => {
    const saved = localStorage.getItem('liveWatchlist');
    if (saved) {
      setWatchlist(JSON.parse(saved));
    }
  };

  const saveWatchlist = (list) => {
    localStorage.setItem('liveWatchlist', JSON.stringify(list));
    setWatchlist(list);
  };

  const addToWatchlist = async () => {
    const symbol = newWatchSymbol.trim().toUpperCase();
    if (!symbol || watchlist.some(w => w.symbol === symbol)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/quotes/${symbol}`);
      const data = await response.json();
      
      if (response.ok && data.price) {
        const newWatch = {
          symbol,
          price: data.price,
          change: data.change || 0,
          changePercent: data.changePercent || 0,
          lastUpdated: new Date().toISOString()
        };
        
        const updated = [...watchlist, newWatch];
        saveWatchlist(updated);
        setNewWatchSymbol('');
        
        setNotificationConfig({
          title: 'Added to Watchlist',
          message: `${symbol} added successfully`,
          type: 'success'
        });
        setShowNotification(true);
      } else {
        setNotificationConfig({
          title: 'Invalid Symbol',
          message: 'Invalid symbol or unable to fetch price',
          type: 'error'
        });
        setShowNotification(true);
      }
    } catch (error) {
      console.error('Error adding to watchlist:', error);
      setNotificationConfig({
        title: 'Error',
        message: 'Error adding symbol to watchlist',
        type: 'error'
      });
      setShowNotification(true);
    }
  };

  const removeFromWatchlist = (symbol) => {
    const updated = watchlist.filter(w => w.symbol !== symbol);
    saveWatchlist(updated);
  };

  const executeTrade = async () => {
    if (!tradeForm.symbol || tradeForm.quantity <= 0) {
      setNotificationConfig({
        title: 'Invalid Input',
        message: 'Please enter a valid symbol and quantity',
        type: 'error'
      });
      setShowNotification(true);
      return;
    }

    // Check if markets are closed for live trading
    if (marketStatus && !marketStatus.is_open) {
      setConfirmModalConfig({
        title: 'Markets Are Closed',
        message: (
          <div>
            <p className="mb-2">The markets are currently closed.</p>
            <p className="mb-2">Your order will be queued and executed when markets open.</p>
            <p className="font-semibold">Do you want to continue?</p>
          </div>
        ),
        type: 'warning',
        confirmText: 'Queue Order',
        onConfirm: () => executeTradeConfirmed()
      });
      setShowConfirmModal(true);
      return;
    }

    // Execute immediately if markets are open
    await executeTradeConfirmed();
  };

  const executeTradeConfirmed = async () => {
    try {
      setTradeLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/alpaca/live/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: tradeForm.symbol,
          quantity: parseFloat(tradeForm.quantity),
          side: tradeForm.action,
          type: tradeForm.orderType
        })
      });

      const data = await response.json();

      if (response.ok) {
        setNotificationConfig({
          title: 'Trade Executed Successfully',
          message: `Order ID: ${data.order?.id || 'N/A'}`,
          type: 'success'
        });
        setShowNotification(true);
        setShowTradeModal(false);
        setTradeForm({ symbol: '', action: 'BUY', quantity: 1, orderType: 'market' });
        await fetchPortfolioData();
        await fetchPendingOrders();
      } else {
        setNotificationConfig({
          title: 'Trade Failed',
          message: data.detail || 'Unknown error',
          type: 'error'
        });
        setShowNotification(true);
      }
    } catch (error) {
      console.error('Error executing trade:', error);
      setNotificationConfig({
        title: 'Error',
        message: error.message,
        type: 'error'
      });
      setShowNotification(true);
    } finally {
      setTradeLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([
      fetchPortfolioData(),
      fetchPendingOrders()
    ]);
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
    // Check if this is an authorization error (paper-only API keys)
    const isAuthError = error.includes('not authorized') || error.includes('authorization');
    
    return (
      <div className="p-6">
        <div className={`${isAuthError ? 'bg-yellow-50 border-yellow-200' : 'bg-red-50 border-red-200'} border rounded-lg p-6 text-center`}>
          <h2 className={`text-xl font-semibold ${isAuthError ? 'text-yellow-800' : 'text-red-800'} mb-2`}>
            {isAuthError ? 'Live Trading Not Available' : 'Error Loading Portfolio'}
          </h2>
          <p className={`${isAuthError ? 'text-yellow-700' : 'text-red-600'} mb-4`}>
            {isAuthError ? (
              <>Your API keys are configured for <strong>Paper Trading only</strong>. To enable live trading, you need separate live trading API keys from Alpaca.</>
            ) : (
              error
            )}
          </p>
          {isAuthError ? (
            <div className="text-sm text-gray-700 mb-4 p-4 bg-white rounded border border-yellow-300">
              <p className="font-medium mb-3">📋 To Enable Live Trading:</p>
              <ol className="text-left list-decimal list-inside space-y-2">
                <li>Go to <a href="https://app.alpaca.markets/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Alpaca Dashboard</a></li>
                <li>Navigate to <strong>Your Account → API Keys</strong></li>
                <li>Generate <strong>Live Trading</strong> API keys (separate from paper keys)</li>
                <li>Update your <code className="bg-gray-100 px-1 rounded">.env</code> file with live keys</li>
                <li>Restart the backend server</li>
              </ol>
              <div className="mt-3 pt-3 border-t border-yellow-200">
                <p className="text-xs text-gray-600">💡 <strong>For now:</strong> Use the <strong>Paper Portfolio</strong> tab to practice trading with $100,000 virtual cash!</p>
              </div>
            </div>
          ) : (
            <div className="text-sm text-gray-600 mb-4 p-3 bg-gray-50 rounded">
              <p className="font-medium mb-2">Troubleshooting steps:</p>
              <ol className="text-left list-decimal list-inside space-y-1">
                <li>Make sure the backend server is running</li>
                <li>Check terminal for any backend errors</li>
                <li>Try restarting the backend: <code className="bg-gray-200 px-1 rounded">uvicorn app.main:app --reload</code></li>
              </ol>
            </div>
          )}
          <button
            onClick={() => {
              setLoading(true);
              setRetryCount(retryCount + 1);
              fetchPortfolioData();
            }}
            className={`${isAuthError ? 'bg-yellow-600 hover:bg-yellow-700' : 'bg-red-600 hover:bg-red-700'} text-white px-4 py-2 rounded-lg transition-colors`}
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
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg text-white p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-2">Live Trading Portfolio</h1>
            <p className="text-blue-100">Real money trading with your Alpaca brokerage account</p>
          </div>
          <div className="text-right space-y-2">
            <div>
              <div className="text-3xl font-bold">
                {formatCurrency(totalValue)}
              </div>
              {account.equity > 0 && (
                <div className={`text-lg font-medium ${
                  account.equity >= (account.cash || 500) ? 'text-blue-200' : 'text-red-200'
                }`}>
                  {account.equity >= (account.cash || 500) ? '+' : ''}
                  ${Math.abs(account.equity - (account.cash || 500)).toLocaleString()}
                </div>
              )}
            </div>
            <MarketStatus />
          </div>
        </div>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3">
            <DollarSign className="w-8 h-8 text-blue-600" />
            <div>
              <p className="text-sm font-medium text-gray-600">Available Cash</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(account.cash)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-8 h-8 text-purple-600" />
            <div>
              <p className="text-sm font-medium text-gray-600">Positions Value</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(metrics.total_market_value || 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3">
            <Target className="w-8 h-8 text-indigo-600" />
            <div>
              <p className="text-sm font-medium text-gray-600">Active Positions</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.position_count || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3">
            {(metrics.total_unrealized_pl || 0) >= 0 ? 
              <TrendingUp className="w-8 h-8 text-green-600" /> : 
              <TrendingDown className="w-8 h-8 text-red-600" />
            }
            <div>
              <p className="text-sm font-medium text-gray-600">Unrealized P&L</p>
              <p className={`text-2xl font-bold ${
                (metrics.total_unrealized_pl || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {(metrics.total_unrealized_pl || 0) >= 0 ? '+' : ''}
                {formatCurrency(Math.abs(metrics.total_unrealized_pl || 0))}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4">
        <button
          onClick={() => setShowTradeModal(true)}
          className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Execute Trade</span>
        </button>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-2 px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
        >
          <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
        <button
          onClick={() => setShowValues(!showValues)}
          className="flex items-center space-x-2 px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
        >
          {showValues ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          <span>{showValues ? 'Hide Values' : 'Show Values'}</span>
        </button>
      </div>

      {/* Pending Orders Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div 
          className="p-6 border-b border-gray-200 flex items-center justify-between cursor-pointer hover:bg-gray-50"
          onClick={() => setShowPendingOrders(!showPendingOrders)}
        >
          <div className="flex items-center space-x-3">
            <Clock className="w-5 h-5 text-orange-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Pending Orders {pendingOrders.length > 0 && `(${pendingOrders.length})`}
            </h2>
          </div>
          {showPendingOrders ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
        </div>
        {showPendingOrders && (
          <div className="overflow-x-auto">
            {pendingOrders.length > 0 ? (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Side</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Limit Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Submitted</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pendingOrders.map((order) => (
                    <tr key={order.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{order.symbol}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                          order.side === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {order.side.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-gray-900">
                        {parseFloat(order.qty).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                        {order.type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-gray-900">
                        {order.limit_price ? formatCurrency(parseFloat(order.limit_price)) : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium rounded bg-yellow-100 text-yellow-800">
                          {order.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {order.submitted_at ? new Date(order.submitted_at).toLocaleString() : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-12 text-center">
                <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 font-medium">No pending orders</p>
                <p className="text-gray-400 text-sm mt-1">Orders will appear here when submitted</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Holdings Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div 
          className="p-6 border-b border-gray-200 flex items-center justify-between cursor-pointer hover:bg-gray-50"
          onClick={() => setShowHoldings(!showHoldings)}
        >
          <h2 className="text-xl font-semibold text-gray-900">Current Holdings</h2>
          {showHoldings ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
        </div>
        {showHoldings && (
          <div className="overflow-x-auto">
          {positions && positions.length > 0 ? (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Price</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Current Price</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Market Value</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Unrealized P&L</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {positions.map((position, idx) => {
                  const unrealizedPL = parseFloat(position.unrealized_pl || 0);
                  const unrealizedPLPercent = parseFloat(position.unrealized_plpc || 0) * 100;
                  return (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{position.symbol}</div>
                        <div className="text-sm text-gray-500">{position.asset_class || 'Stock'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right font-medium text-gray-900">
                        {parseFloat(position.qty).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-gray-900">
                        {formatCurrency(parseFloat(position.avg_entry_price))}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-gray-900">
                        {formatCurrency(parseFloat(position.current_price))}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right font-medium text-gray-900">
                        {formatCurrency(parseFloat(position.market_value))}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className={`font-medium ${unrealizedPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {unrealizedPL >= 0 ? '+' : ''}{formatCurrency(Math.abs(unrealizedPL))}
                        </div>
                        <div className={`text-sm ${unrealizedPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          ({unrealizedPLPercent >= 0 ? '+' : ''}{unrealizedPLPercent.toFixed(2)}%)
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div className="p-12 text-center">
              <Eye className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 font-medium">No positions yet</p>
              <p className="text-gray-400 text-sm mt-1">Execute your first trade to get started!</p>
            </div>
          )}
        </div>
        )}
      </div>

      {/* Watchlist Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Watchlist</h2>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={newWatchSymbol}
                onChange={(e) => setNewWatchSymbol(e.target.value.toUpperCase())}
                onKeyPress={(e) => e.key === 'Enter' && addToWatchlist()}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-32"
                placeholder="AAPL"
              />
              <button
                onClick={addToWatchlist}
                disabled={!newWatchSymbol}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors disabled:opacity-50"
              >
                Add
              </button>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          {watchlist.length > 0 ? (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Change</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {watchlist.map((item) => (
                  <tr key={item.symbol} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${item.price?.toFixed(2) || '0.00'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`${(item.changePercent || 0) >= 0 ? 'text-green-600' : 'text-red-600'} font-medium`}>
                        {(item.changePercent || 0) >= 0 ? '+' : ''}{(item.changePercent || 0).toFixed(2)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm space-x-3">
                      <button
                        onClick={() => {
                          setTradeForm({ ...tradeForm, symbol: item.symbol });
                          setShowTradeModal(true);
                        }}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Trade
                      </button>
                      <button
                        onClick={() => removeFromWatchlist(item.symbol)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-center py-12">
              <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No symbols in watchlist</p>
              <p className="text-gray-400">Add symbols to monitor their prices</p>
            </div>
          )}
        </div>
      </div>

      {/* Trade Modal */}
      {showTradeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Execute Live Trade</h2>
            
            <div className="space-y-4">
              {/* Symbol Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Stock Symbol
                </label>
                <input
                  type="text"
                  value={tradeForm.symbol}
                  onChange={(e) => setTradeForm({...tradeForm, symbol: e.target.value.toUpperCase()})}
                  placeholder="e.g. AAPL"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Current Price Display */}
              {tradeForm.symbol && (
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-600">Current Price</p>
                  <p className="text-xl font-bold">
                    {loadingPrice ? 'Loading...' : currentPrice ? `$${currentPrice.toFixed(2)}` : 'N/A'}
                  </p>
                </div>
              )}

              {/* Buy/Sell Toggle */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Action
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setTradeForm({...tradeForm, action: 'BUY'})}
                    className={`py-2 px-4 rounded-lg font-medium ${
                      tradeForm.action === 'BUY'
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Buy
                  </button>
                  <button
                    onClick={() => setTradeForm({...tradeForm, action: 'SELL'})}
                    className={`py-2 px-4 rounded-lg font-medium ${
                      tradeForm.action === 'SELL'
                        ? 'bg-red-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Sell
                  </button>
                </div>
              </div>

              {/* Quantity Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantity
                </label>
                <input
                  type="number"
                  value={tradeForm.quantity}
                  onChange={(e) => setTradeForm({...tradeForm, quantity: e.target.value})}
                  placeholder="Number of shares"
                  min="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Order Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Order Type
                </label>
                <select
                  value={tradeForm.orderType}
                  onChange={(e) => setTradeForm({...tradeForm, orderType: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="market">Market Order</option>
                  <option value="limit">Limit Order</option>
                </select>
              </div>

              {/* Estimated Total */}
              {currentPrice && tradeForm.quantity && (
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm text-blue-600">Estimated Total</p>
                  <p className="text-xl font-bold text-blue-700">
                    ${(currentPrice * parseFloat(tradeForm.quantity)).toFixed(2)}
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowTradeModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={executeTrade}
                  disabled={!tradeForm.symbol || !tradeForm.quantity || tradeLoading}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors font-medium"
                >
                  {tradeLoading ? 'Executing...' : 'Execute Trade'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={confirmModalConfig.onConfirm}
        title={confirmModalConfig.title}
        message={confirmModalConfig.message}
        type={confirmModalConfig.type}
        confirmText={confirmModalConfig.confirmText}
        cancelText={confirmModalConfig.cancelText}
      />

      {/* Notification Modal */}
      <NotificationModal
        isOpen={showNotification}
        onClose={() => setShowNotification(false)}
        title={notificationConfig.title}
        message={notificationConfig.message}
        type={notificationConfig.type}
      />
    </div>
  );
};

export default RealPortfolio;
