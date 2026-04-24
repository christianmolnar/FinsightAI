import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MarketStatus from './MarketStatus';
import { apiClient } from '../utils/apiClient';
import { Clock, CheckCircle, XCircle, Edit3, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';

const TransactionQueue = () => {
  const [transactions, setTransactions] = useState([]);
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [portfolioFilter, setPortfolioFilter] = useState('all');
  const [symbolFilter, setSymbolFilter] = useState('');
  const [error, setError] = useState(null);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [showModifyModal, setShowModifyModal] = useState(false);
  const [modifyForm, setModifyForm] = useState({});

  useEffect(() => {
    fetchPortfolios();
  }, []);

  useEffect(() => {
    fetchTransactions();
    const interval = setInterval(fetchTransactions, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [filter, portfolioFilter, symbolFilter]);

  const fetchPortfolios = async () => {
    try {
      const data = await apiClient.get('/api/v1/portfolios');
      if (data) {
        setPortfolios(data);
      }
    } catch (err) {
      console.error('Error fetching portfolios:', err);
    }
  };

  const fetchTransactions = async () => {
    try {
      setError(null);
      const params = new URLSearchParams();
      
      // Add portfolio filter
      if (portfolioFilter !== 'all') {
        params.append('portfolio_id', portfolioFilter);
      }
      
      // Add status filter
      if (filter !== 'all') {
        params.append('status', filter);
      }
      
      const queryString = params.toString();
      const endpoint = `/api/queue/pending${queryString ? '?' + queryString : ''}`;
      const response = await apiClient.get(endpoint);
      
      if (response.success) {
        let filtered = response.transactions || [];
        
        // Apply symbol filter (frontend filtering)
        if (symbolFilter) {
          filtered = filtered.filter(t => 
            t.symbol.toLowerCase().includes(symbolFilter.toLowerCase())
          );
        }
        
        setTransactions(filtered);
      }
    } catch (err) {
      console.error('Error fetching transactions:', err);
      setError(err.message || 'Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (transactionId) => {
    try {
      const response = await apiClient.put(
        `/api/queue/pending/${transactionId}/approve`,
        { user_notes: 'Approved from queue UI' }
      );
      
      if (response.success) {
        alert('✅ Trade executed successfully!');
        fetchTransactions();
      }
    } catch (err) {
      alert(`❌ Error approving trade: ${err.message}`);
    }
  };

  const handleReject = async (transactionId) => {
    const reason = prompt('Reason for rejection (optional):');
    try {
      const response = await apiClient.put(
        `/api/queue/pending/${transactionId}/reject`,
        { reason: reason || 'Rejected by user' }
      );
      
      if (response.success) {
        alert('Transaction rejected');
        fetchTransactions();
      }
    } catch (err) {
      alert(`Error rejecting trade: ${err.message}`);
    }
  };

  const openModifyModal = (transaction) => {
    setSelectedTransaction(transaction);
    setModifyForm({
      quantity: transaction.quantity,
      proposed_price: transaction.proposed_price,
      stop_loss: transaction.stop_loss || '',
      profit_target: transaction.profit_target || ''
    });
    setShowModifyModal(true);
  };

  const handleModify = async () => {
    try {
      const response = await apiClient.put(
        `/api/queue/pending/${selectedTransaction.id}/modify`,
        modifyForm
      );
      
      if (response.success) {
        alert('✅ Transaction updated successfully!');
        setShowModifyModal(false);
        fetchTransactions();
      }
    } catch (err) {
      alert(`❌ Error modifying trade: ${err.message}`);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      executed: 'bg-blue-100 text-blue-800',
      expired: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-gray-100 text-gray-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || styles.pending}`}>
        {status.toUpperCase()}
      </span>
    );
  };

  const getConfidenceColor = (score) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const formatTimeUntil = (scheduledTime) => {
    if (!scheduledTime) return null;
    
    const now = new Date();
    const scheduled = new Date(scheduledTime);
    const diff = scheduled - now;
    
    if (diff <= 0) return 'Now';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow p-6 h-48"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Transaction Queue</h1>
          <p className="text-gray-600">Review and approve AI-proposed trades before execution</p>
        </div>
        <MarketStatus />
      </div>

      {/* Filters Row */}
      <div className="mb-6 flex gap-4 items-center">
        {/* Portfolio Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Portfolio:</label>
          <select
            value={portfolioFilter}
            onChange={(e) => setPortfolioFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="all">All Portfolios</option>
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.portfolio_type})
              </option>
            ))}
          </select>
        </div>

        {/* Symbol Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Symbol:</label>
          <input
            type="text"
            value={symbolFilter}
            onChange={(e) => setSymbolFilter(e.target.value)}
            placeholder="Filter by symbol..."
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-orange-500 focus:border-orange-500"
          />
        </div>

        {symbolFilter && (
          <button
            onClick={() => setSymbolFilter('')}
            className="text-sm text-orange-600 hover:text-orange-800"
          >
            Clear
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex space-x-2 mb-6 border-b border-gray-200">
        {['all', 'pending', 'approved', 'rejected', 'executed'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              filter === status
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
            {status === filter && transactions.length > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-600 rounded-full text-xs">
                {transactions.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Empty State */}
      {transactions.length === 0 && !loading && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Transactions in Queue</h3>
          <p className="text-gray-600 mb-4">
            {filter === 'all' 
              ? 'Your transaction queue is empty. Use the Research tab to analyze stocks and add trade proposals.'
              : `No ${filter} transactions found.`}
          </p>
        </div>
      )}

      {/* Transaction Cards */}
      <div className="space-y-4">
        {transactions.map((transaction) => (
          <div key={transaction.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
            <div className="p-6">
              {/* Header Row */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    {transaction.transaction_type === 'buy' ? (
                      <TrendingUp className="w-6 h-6 text-green-600 mr-2" />
                    ) : (
                      <TrendingDown className="w-6 h-6 text-red-600 mr-2" />
                    )}
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">
                        {transaction.transaction_type.toUpperCase()} {transaction.symbol}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {transaction.quantity} shares @ ${transaction.proposed_price?.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  {getStatusBadge(transaction.status)}
                  {transaction.auto_execute && transaction.scheduled_time && transaction.status === 'pending' && (
                    <div className="flex items-center space-x-1 text-sm text-orange-600">
                      <Clock className="w-4 h-4" />
                      <span className="font-medium">{formatTimeUntil(transaction.scheduled_time)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Confidence Score */}
              {transaction.confidence_score && (
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">AI Confidence</span>
                    <span className="font-bold text-gray-900">{transaction.confidence_score}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getConfidenceColor(transaction.confidence_score)}`}
                      style={{ width: `${transaction.confidence_score}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* AI Reasoning */}
              {transaction.ai_reasoning && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm font-medium text-blue-900 mb-1">AI Reasoning:</p>
                  <p className="text-sm text-blue-800">
                    {typeof transaction.ai_reasoning === 'string' 
                      ? transaction.ai_reasoning 
                      : JSON.stringify(transaction.ai_reasoning, null, 2)}
                  </p>
                </div>
              )}

              {/* Risk Factors & Catalysts */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                {transaction.risk_factors && Array.isArray(transaction.risk_factors) && transaction.risk_factors.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                      <AlertTriangle className="w-4 h-4 mr-1 text-orange-600" />
                      Risk Factors
                    </p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {transaction.risk_factors.slice(0, 3).map((risk, idx) => (
                        <li key={idx}>• {typeof risk === 'string' ? risk : JSON.stringify(risk)}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {transaction.catalysts && Array.isArray(transaction.catalysts) && transaction.catalysts.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                      <TrendingUp className="w-4 h-4 mr-1 text-green-600" />
                      Catalysts
                    </p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {transaction.catalysts.slice(0, 3).map((catalyst, idx) => (
                        <li key={idx}>• {typeof catalyst === 'string' ? catalyst : JSON.stringify(catalyst)}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Action Buttons - Only for pending transactions */}
              {transaction.status === 'pending' && (
                <div className="flex space-x-3 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => handleApprove(transaction.id)}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>Approve & Execute</span>
                  </button>
                  
                  <button
                    onClick={() => openModifyModal(transaction)}
                    className="flex items-center justify-center space-x-2 px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg transition-colors"
                  >
                    <Edit3 className="w-4 h-4" />
                    <span>Modify</span>
                  </button>
                  
                  <button
                    onClick={() => handleReject(transaction.id)}
                    className="flex items-center justify-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>Reject</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Modify Modal */}
      {showModifyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Modify Transaction
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantity
                </label>
                <input
                  type="number"
                  value={modifyForm.quantity}
                  onChange={(e) => setModifyForm({ ...modifyForm, quantity: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Proposed Price
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={modifyForm.proposed_price}
                  onChange={(e) => setModifyForm({ ...modifyForm, proposed_price: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Stop Loss (optional)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={modifyForm.stop_loss}
                  onChange={(e) => setModifyForm({ ...modifyForm, stop_loss: parseFloat(e.target.value) || null })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Profit Target (optional)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={modifyForm.profit_target}
                  onChange={(e) => setModifyForm({ ...modifyForm, profit_target: parseFloat(e.target.value) || null })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleModify}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Save Changes
              </button>
              <button
                onClick={() => setShowModifyModal(false)}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransactionQueue;
