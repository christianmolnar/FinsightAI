import React from 'react';

const PositionsTable = ({ positions, loading }) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value || 0);
  };

  const getChangeClass = (value) => {
    if (value > 0) return 'positive';
    if (value < 0) return 'negative';
    return 'neutral';
  };

  if (loading) {
    return <PositionsTableSkeleton />;
  }

  if (!positions || positions.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Current Positions</h3>
        </div>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No positions</h3>
          <p className="mt-1 text-sm text-gray-500">Start trading to see your positions here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Current Positions</h3>
        <p className="text-sm text-gray-500 mt-1">{positions.length} active position{positions.length !== 1 ? 's' : ''}</p>
      </div>

      <div className="overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Shares
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Avg Cost
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Current
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Market Value
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                P&L
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {positions.map((position, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="text-sm font-medium text-gray-900">
                      {position.symbol}
                    </div>
                  </div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {position.shares?.toLocaleString()}
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {formatCurrency(position.avg_cost)}
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {formatCurrency(position.current_price)}
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                  {formatCurrency(position.market_value)}
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-right text-sm">
                  <span className={`font-medium ${getChangeClass(position.unrealized_pnl)}`}>
                    {position.unrealized_pnl >= 0 ? '+' : ''}{formatCurrency(position.unrealized_pnl)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const PositionsTableSkeleton = () => {
  return (
    <div className="card">
      <div className="card-header">
        <div className="loading-skeleton h-6 w-32"></div>
        <div className="loading-skeleton h-4 w-24 mt-1"></div>
      </div>
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex justify-between">
            <div className="loading-skeleton h-4 w-16"></div>
            <div className="loading-skeleton h-4 w-16"></div>
            <div className="loading-skeleton h-4 w-20"></div>
            <div className="loading-skeleton h-4 w-20"></div>
            <div className="loading-skeleton h-4 w-24"></div>
            <div className="loading-skeleton h-4 w-20"></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PositionsTable;
