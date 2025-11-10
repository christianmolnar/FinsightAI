import React from 'react';

const TradesTable = ({ trades, loading }) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value || 0);
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      filled: { bg: 'bg-green-100', text: 'text-green-800', label: 'Filled' },
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pending' },
      cancelled: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Cancelled' },
      rejected: { bg: 'bg-red-100', text: 'text-red-800', label: 'Rejected' },
      partial: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Partial' },
    };

    const config = statusConfig[status] || statusConfig.pending;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const getSideBadge = (side) => {
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
        side === 'buy' 
          ? 'bg-green-100 text-green-700' 
          : 'bg-red-100 text-red-700'
      }`}>
        {side?.toUpperCase()}
      </span>
    );
  };

  const getStrategyBadge = (strategy) => {
    if (!strategy) return null;
    
    const strategyColors = {
      momentum: 'bg-blue-100 text-blue-700',
      mean_reversion: 'bg-purple-100 text-purple-700',
      sentiment: 'bg-indigo-100 text-indigo-700',
      earnings: 'bg-orange-100 text-orange-700',
      technical: 'bg-teal-100 text-teal-700',
      fundamental: 'bg-emerald-100 text-emerald-700',
    };

    const colorClass = strategyColors[strategy] || 'bg-gray-100 text-gray-700';
    
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${colorClass}`}>
        {strategy.replace('_', ' ')}
      </span>
    );
  };

  if (loading) {
    return <TradesTableSkeleton />;
  }

  if (!trades || trades.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Trades</h3>
        </div>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No trades yet</h3>
          <p className="mt-1 text-sm text-gray-500">Trading activity will appear here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Recent Trades</h3>
        <p className="text-sm text-gray-500 mt-1">{trades.length} recent trade{trades.length !== 1 ? 's' : ''}</p>
      </div>

      <div className="overflow-hidden">
        <div className="max-h-96 overflow-y-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Symbol
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Side
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Strategy
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {trades.map((trade) => (
                <tr key={trade.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {trade.symbol}
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    {getSideBadge(trade.side)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                    {trade.quantity?.toLocaleString()}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                    {formatCurrency(trade.price)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                    {formatCurrency(trade.total_amount)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    {getStatusBadge(trade.status)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    {getStrategyBadge(trade.strategy)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDateTime(trade.executed_at || trade.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const TradesTableSkeleton = () => {
  return (
    <div className="card">
      <div className="card-header">
        <div className="loading-skeleton h-6 w-32"></div>
        <div className="loading-skeleton h-4 w-24 mt-1"></div>
      </div>
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex justify-between items-center">
            <div className="loading-skeleton h-4 w-16"></div>
            <div className="loading-skeleton h-6 w-12 rounded-full"></div>
            <div className="loading-skeleton h-4 w-16"></div>
            <div className="loading-skeleton h-4 w-20"></div>
            <div className="loading-skeleton h-4 w-20"></div>
            <div className="loading-skeleton h-6 w-16 rounded-full"></div>
            <div className="loading-skeleton h-6 w-20 rounded-full"></div>
            <div className="loading-skeleton h-4 w-16"></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TradesTable;
