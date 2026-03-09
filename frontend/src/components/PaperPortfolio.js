import React, { useState, useEffect } from 'react';
import SellValidation from './SellValidation';
import MarketStatus from './MarketStatus';
import ConfirmationModal from './ConfirmationModal';
import NotificationModal from './NotificationModal';
import { apiClient } from '../utils/apiClient';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Target, 
  RefreshCw,
  Plus,
  Minus,
  Calendar,
  Eye,
  Brain,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Clock
} from 'lucide-react';

const PaperPortfolio = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [showTradeModal, setShowTradeModal] = useState(false);
  const [tradeForm, setTradeForm] = useState({
    symbol: '',
    action: 'BUY',
    quantity: 10,
    strategy_used: 'manual'
  });
  const [currentPrice, setCurrentPrice] = useState(null);
  const [loadingPrice, setLoadingPrice] = useState(false);
  const [watchlist, setWatchlist] = useState([]);
  const [newWatchSymbol, setNewWatchSymbol] = useState('');
  const [successMessage, setSuccessMessage] = useState(null);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [showSellValidation, setShowSellValidation] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [pendingOrders, setPendingOrders] = useState([]);
  const [showPendingOrders, setShowPendingOrders] = useState(true);
  const [showHoldings, setShowHoldings] = useState(true);
  
  // Modal states
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmModalConfig, setConfirmModalConfig] = useState({});
  const [showNotification, setShowNotification] = useState(false);
  const [notificationConfig, setNotificationConfig] = useState({});

  useEffect(() => {
    fetchPortfolio();
    loadWatchlist();
    fetchTransactions();
    fetchPendingOrders();
    
    // Auto-refresh disabled - use manual refresh button instead
    // Users can refresh manually when needed to avoid constant reloading
    
    // Optional: Uncomment for auto-refresh every 2 minutes
    // const interval = setInterval(() => {
    //   fetchPortfolio();
    //   refreshWatchlist();
    //   fetchTransactions();
    //   fetchMarketStatus();
    // }, 120000); // 2 minutes
    // return () => clearInterval(interval);
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

  const fetchPortfolio = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.get('/api/v1/alpaca/paper/portfolio');
      const transformedData = {
        total_value: data.account?.portfolio_value || 0,
        cash_balance: data.account?.cash || 0,
        invested_value: data.metrics?.total_market_value || 0,
        unrealized_pnl: data.metrics?.total_unrealized_pl || 0,
        positions: data.positions || [],
        account: data.account,
        metrics: data.metrics
      };
      setPortfolio(transformedData);
      setError(null);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      setError(error.message || 'Failed to load paper portfolio.');
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingOrders = async () => {
    try {
      const data = await apiClient.get('/api/v1/alpaca/paper/orders');
      const pending = (data.orders || []).filter(order =>
        ['new', 'accepted', 'pending_new', 'partially_filled'].includes(order.status)
      );
      setPendingOrders(pending);
    } catch (err) {
      console.error('Failed to fetch pending orders:', err);
    }
  };

  const fetchTransactions = async () => {
    try {
      // Alpaca doesn't have a transactions endpoint in the same way
      // For now, skip this or we'll need to implement order history
      // const response = await axios.get(`${API_BASE_URL}/api/v1/alpaca/paper/orders`);
      // setTransactions(response.data);
      setTransactions([]); // Empty for now
    } catch (err) {
      console.error('Error fetching transactions:', err);
      setTransactions([]);
    }
  };

  const fetchStockPrice = async (symbol) => {
    if (!symbol) return;
    setLoadingPrice(true);
    try {
      const data = await apiClient.get(`/api/v1/quotes/${symbol}`);
      if (data.price) {
        setCurrentPrice(data.price);
      } else {
        setCurrentPrice(null);
      }
    } catch (error) {
      console.error('Error fetching stock price:', error);
      setCurrentPrice(null);
    } finally {
      setLoadingPrice(false);
    }
  };

  const loadWatchlist = () => {
    const saved = localStorage.getItem('paperWatchlist');
    if (saved) {
      setWatchlist(JSON.parse(saved));
    }
  };

  const saveWatchlist = (list) => {
    localStorage.setItem('paperWatchlist', JSON.stringify(list));
    setWatchlist(list);
  };

  const addToWatchlist = async () => {
    const symbol = newWatchSymbol.trim().toUpperCase();
    if (!symbol || watchlist.some(w => w.symbol === symbol)) {
      return;
    }

    try {
      const data = await apiClient.get(`/api/v1/quotes/${symbol}`);
      
      if (data.price) {
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

  const refreshWatchlist = async () => {
    if (watchlist.length === 0) return;

    const updated = await Promise.all(
      watchlist.map(async (item) => {
        try {
          const data = await apiClient.get(`/api/v1/quotes/${item.symbol}`);
          if (data.price) {
            return {
              ...item,
              price: data.price,
              change: data.change || 0,
              changePercent: data.changePercent || 0,
              lastUpdated: new Date().toISOString()
            };
          }
        } catch (error) {
          console.error(`Error refreshing ${item.symbol}:`, error);
        }
        return item;
      })
    );
    
    saveWatchlist(updated);
  };

  const executeTrade = async () => {
    if (!tradeForm.symbol || !tradeForm.quantity) {
      setNotificationConfig({
        title: 'Invalid Input',
        message: 'Please fill in all fields',
        type: 'error'
      });
      setShowNotification(true);
      return;
    }

    try {
      const result = await apiClient.post('/api/v1/paper/trade', {
        symbol: tradeForm.symbol.toUpperCase(),
        side: tradeForm.action.toLowerCase(),
        quantity: parseFloat(tradeForm.quantity),
        order_type: 'market'
      });

      if (result.status === 'error') {
        setNotificationConfig({ title: 'Trade Failed', message: result.message || 'Unknown error', type: 'error' });
        setShowNotification(true);
        return;
      }

      setNotificationConfig({ title: 'Trade Executed', message: result.message || 'Trade executed successfully', type: 'success' });
      setShowNotification(true);
      setShowTradeModal(false);
      setTradeForm({ symbol: '', action: 'BUY', quantity: 10, strategy_used: 'manual' });
      fetchPortfolio();
      fetchTransactions();
      fetchPendingOrders();
    } catch (error) {
      console.error('Error executing trade:', error);
      setNotificationConfig({ title: 'Trade Failed', message: error.message || 'Trade execution failed', type: 'error' });
      setShowNotification(true);
    }
  };

  const resetPortfolio = async () => {
    setConfirmModalConfig({
      title: 'Reset Portfolio',
      message: 'Are you sure you want to reset your paper portfolio to $10,000? This will close all positions.',
      type: 'warning',
      confirmText: 'Reset Portfolio',
      cancelText: 'Cancel',
      confirmButtonClass: 'bg-red-600 hover:bg-red-700',
      onConfirm: async () => {
        try {
          await apiClient.post('/api/v1/paper/reset');
          await fetchPortfolio();
          await fetchTransactions();
          setNotificationConfig({ title: 'Portfolio Reset', message: 'Your paper portfolio has been reset to $10,000', type: 'success' });
          setShowNotification(true);
        } catch (err) {
          setNotificationConfig({ title: 'Reset Failed', message: 'Failed to reset portfolio', type: 'error' });
          setShowNotification(true);
        }
      }
    });
    setShowConfirmModal(true);
  };

  const handleGetAIAnalysis = (position) => {
    setSelectedPosition({
      symbol: position.symbol,
      quantity: position.quantity,
      avg_price: position.avg_price,
      current_price: position.avg_price, // Using avg_price as current for now
      market_value: position.market_value,
      unrealized_pnl: position.unrealized_pnl,
      purchase_date: new Date().toISOString() // Placeholder - should come from first transaction
    });
    setShowSellValidation(true);
  };

  const handleCloseSellValidation = () => {
    setShowSellValidation(false);
    setSelectedPosition(null);
  };

  const handleSellExecuted = () => {
    // Refresh portfolio after sell
    fetchPortfolio();
    fetchTransactions();
    setShowSellValidation(false);
    setSelectedPosition(null);
  };

  const filteredTransactions = transactions.filter(t => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'buy') return t.type === 'buy';
    if (activeFilter === 'sell') return t.type === 'sell';
    return true;
  });

  // Convert positions object to array
  const currentPositions = portfolio?.positions 
    ? Object.entries(portfolio.positions).map(([symbol, data]) => ({
        symbol,
        ...data
      })).filter(p => p.quantity > 0)
    : [];
  const hasPositions = currentPositions.length > 0;

  if (loading && !portfolio) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-skeleton w-8 h-8 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Paper Portfolio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-500 to-blue-600 rounded-lg text-white p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-2">Paper Trading Portfolio</h1>
            <p className="text-green-100">Safe environment to test trading strategies with virtual money</p>
          </div>
          <div className="text-right space-y-2">
            <div>
              <div className="text-3xl font-bold">
                {portfolio?.total_value ? `$${portfolio.total_value.toLocaleString()}` : 'N/A'}
              </div>
              {portfolio?.total_value && (
                <div className={`text-lg font-medium ${
                  portfolio.total_value >= 100000 ? 'text-green-200' : 'text-red-200'
                }`}>
                  {portfolio.total_value >= 100000 ? '+' : ''}
                  ${Math.abs(portfolio.total_value - 100000).toLocaleString()}
                  ({((portfolio.total_value - 100000) / 100000 * 100).toFixed(2)}%)
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
            <DollarSign className="w-8 h-8 text-green-600" />
            <div>
              <p className="text-sm font-medium text-gray-600">Available Cash</p>
              <p className="text-2xl font-bold text-gray-900">
                {portfolio?.cash_balance ? `$${portfolio.cash_balance.toLocaleString()}` : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            <div>
              <p className="text-sm font-medium text-gray-600">Positions Value</p>
              <p className="text-2xl font-bold text-gray-900">
                {portfolio ? `$${((portfolio.total_value || 0) - (portfolio.cash_balance || 0)).toLocaleString()}` : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3">
            <Target className="w-8 h-8 text-purple-600" />
            <div>
              <p className="text-sm font-medium text-gray-600">Active Positions</p>
              <p className="text-2xl font-bold text-gray-900">{currentPositions.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3">
            {(portfolio?.unrealized_pnl || 0) >= 0 ? 
              <TrendingUp className="w-8 h-8 text-green-600" /> : 
              <TrendingDown className="w-8 h-8 text-red-600" />
            }
            <div>
              <p className="text-sm font-medium text-gray-600">Unrealized P&L</p>
              <p className={`text-2xl font-bold ${
                (portfolio?.unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {(portfolio?.unrealized_pnl || 0) >= 0 ? '+' : ''}${(portfolio?.unrealized_pnl || 0).toLocaleString()}
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
          onClick={fetchPortfolio}
          disabled={loading}
          className="flex items-center space-x-2 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
        <button
          onClick={resetPortfolio}
          className="flex items-center space-x-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
        >
          <AlertTriangle className="w-5 h-5" />
          <span>Reset Portfolio</span>
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6 mb-6">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-yellow-900 mb-2">Paper Trading Connection Issue</h3>
              <p className="text-yellow-800 mb-4 leading-relaxed">{error}</p>
              
              {error.includes('PK') && (
                <div className="bg-white border border-yellow-200 rounded p-4 text-sm">
                  <p className="font-semibold text-gray-900 mb-2">📋 To fix this:</p>
                  <ol className="list-decimal list-inside space-y-1 text-gray-700">
                    <li>Go to <a href="https://app.alpaca.markets/paper/dashboard/overview" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">Alpaca Paper Trading Dashboard</a></li>
                    <li>Navigate to "Your API Keys" section</li>
                    <li>Generate new Paper Trading keys (they'll start with "PK")</li>
                    <li>Update <code className="bg-gray-100 px-1 py-0.5 rounded">ALPACA_PAPER_API_KEY_ID</code> and <code className="bg-gray-100 px-1 py-0.5 rounded">ALPACA_PAPER_API_SECRET_KEY</code> in your .env file</li>
                    <li>Restart the backend server</li>
                  </ol>
                </div>
              )}
              
              <button
                onClick={fetchPortfolio}
                className="mt-4 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors font-medium"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pending Orders Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        <div 
          className="p-6 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors flex items-center justify-between"
          onClick={() => setShowPendingOrders(!showPendingOrders)}
        >
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-yellow-500" />
            <h2 className="text-xl font-semibold text-gray-900">Pending Orders</h2>
            {pendingOrders.length > 0 && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                {pendingOrders.length}
              </span>
            )}
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
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Limit Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Submitted</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pendingOrders.map((order, index) => (
                    <tr key={order.id || index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{order.symbol}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          order.side === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {order.side?.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{order.qty}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{order.type}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {order.limit_price ? `$${parseFloat(order.limit_price).toFixed(2)}` : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          {order.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {order.submitted_at ? new Date(order.submitted_at).toLocaleString() : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-12 text-center">
                <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No pending orders</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Holdings Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div 
          className="p-6 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors flex items-center justify-between"
          onClick={() => setShowHoldings(!showHoldings)}
        >
          <h2 className="text-xl font-semibold text-gray-900">Current Holdings</h2>
          {showHoldings ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
        </div>
        {showHoldings && (
          <div className="overflow-x-auto">
            {hasPositions ? (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Cost</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Market Value</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P&L</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Days Held</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strategy</th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">AI Analysis</th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Close Position</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentPositions.map((position, index) => {
                  // Handle both old format and Alpaca format
                  const qty = parseFloat(position.qty || position.quantity || 0);
                  const avgPrice = parseFloat(position.avg_entry_price || position.avg_price || 0);
                  const currentPrice = parseFloat(position.current_price || avgPrice);
                  const marketValue = parseFloat(position.market_value || (qty * currentPrice));
                  const unrealizedPL = parseFloat(position.unrealized_pl || position.unrealized_pnl || 0);
                  const unrealizedPLPercent = parseFloat(position.unrealized_plpc || 0) * 100;
                  
                  return (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {position.symbol}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {qty.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${avgPrice.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${currentPrice.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${marketValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`${unrealizedPL >= 0 ? 'text-green-600' : 'text-red-600'} font-medium`}>
                          {unrealizedPL >= 0 ? '+' : ''}${unrealizedPL.toFixed(2)}
                          <br />
                          <span className="text-xs">
                            ({unrealizedPLPercent >= 0 ? '+' : ''}{unrealizedPLPercent.toFixed(2)}%)
                          </span>
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        -
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          manual
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                        <button
                          onClick={() => handleGetAIAnalysis(position)}
                          className="inline-flex items-center justify-center px-3 py-1.5 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md font-medium transition-colors"
                          title="Get AI analysis for this position"
                        >
                          <Brain className="w-4 h-4 mr-1.5" />
                          AI Analysis
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center align-middle">
                        <button
                          onClick={() => {
                            setTradeForm({ 
                              symbol: position.symbol, 
                              action: 'SELL', 
                              quantity: qty,
                              strategy_used: 'manual'
                            });
                            setShowTradeModal(true);
                          }}
                          className="inline-flex items-center justify-center px-3 py-1.5 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md font-medium transition-colors leading-tight"
                        >
                          Close<br/>Position
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div className="text-center py-12">
              <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No positions yet</p>
              <p className="text-gray-400">Execute your first trade to get started!</p>
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

      {/* Transaction History */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Transaction History</h2>
            <div className="flex space-x-2">
              {['all', 'buy', 'sell'].map((filter) => (
                <button
                  key={filter}
                  onClick={() => setActiveFilter(filter)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeFilter === filter
                      ? 'bg-blue-100 text-blue-800 border border-blue-200'
                      : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                  }`}
                >
                  {filter.charAt(0).toUpperCase() + filter.slice(1)} Trades
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          {filteredTransactions.length > 0 ? (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strategy</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredTransactions.slice(0, 20).map((transaction) => (
                  <tr key={transaction.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(transaction.timestamp).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {transaction.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        transaction.type === 'buy' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {transaction.type.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {transaction.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${transaction.price?.toFixed(2) || '0.00'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${transaction.total?.toLocaleString() || '0'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      manual
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No transactions yet</p>
              <p className="text-gray-400">Your trading history will appear here</p>
            </div>
          )}
        </div>
      </div>

      {/* Trade Modal */}
      {showTradeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Execute Paper Trade</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Symbol</label>
                <input
                  type="text"
                  value={tradeForm.symbol}
                  onChange={(e) => setTradeForm({ ...tradeForm, symbol: e.target.value.toUpperCase() })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="AAPL"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Action</label>
                <select
                  value={tradeForm.action}
                  onChange={(e) => setTradeForm({ ...tradeForm, action: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="BUY">Buy</option>
                  <option value="SELL">Sell</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                <input
                  type="number"
                  value={tradeForm.quantity}
                  onChange={(e) => setTradeForm({ ...tradeForm, quantity: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                />
              </div>

              {/* Price Display */}
              {tradeForm.symbol && (
                <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Current Price:</span>
                    {loadingPrice ? (
                      <span className="text-sm text-gray-500">Loading...</span>
                    ) : currentPrice ? (
                      <span className="text-lg font-bold text-gray-900">${currentPrice.toFixed(2)}</span>
                    ) : (
                      <span className="text-sm text-red-500">Price unavailable</span>
                    )}
                  </div>
                  {currentPrice && tradeForm.quantity && (
                    <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                      <span className="text-sm font-medium text-gray-700">Estimated Total:</span>
                      <span className="text-lg font-bold text-blue-600">
                        ${(currentPrice * parseFloat(tradeForm.quantity || 0)).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                      </span>
                    </div>
                  )}
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Strategy</label>
                <select
                  value={tradeForm.strategy_used}
                  onChange={(e) => setTradeForm({ ...tradeForm, strategy_used: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="manual">Manual Trade</option>
                  <option value="earnings">Earnings Strategy</option>
                  <option value="seasonality">Seasonality Strategy</option>
                  <option value="macro">Macro Strategy</option>
                  <option value="sentiment">Sentiment Strategy</option>
                </select>
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={executeTrade}
                disabled={!tradeForm.symbol || loading}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors disabled:opacity-50"
              >
                Execute Trade
              </button>
              <button
                onClick={() => setShowTradeModal(false)}
                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-md transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Success Message Dialog */}
      {successMessage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-2xl p-6 max-w-md w-full mx-4 animate-bounce-in">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">Trade Executed!</h3>
                <p className="text-gray-600 mt-1">{successMessage}</p>
              </div>
              <button
                onClick={() => setSuccessMessage(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sell Validation Modal */}
      {showSellValidation && selectedPosition && (
        <SellValidation
          position={selectedPosition}
          onClose={handleCloseSellValidation}
          onConfirmSell={handleSellExecuted}
        />
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
        confirmButtonClass={confirmModalConfig.confirmButtonClass}
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

export default PaperPortfolio;
