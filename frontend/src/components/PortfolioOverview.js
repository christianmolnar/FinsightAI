import React from 'react';

const PortfolioOverview = ({ portfolioData, loading }) => {
  if (loading && !portfolioData) {
    return <PortfolioOverviewSkeleton />;
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value || 0);
  };

  const formatPercentage = (value) => {
    const formatted = new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format((value || 0) / 100);
    
    return formatted;
  };

  const getChangeClass = (value) => {
    if (value > 0) return 'positive';
    if (value < 0) return 'negative';
    return 'neutral';
  };

  const performance = portfolioData?.performance || {};
  
  const metrics = [
    {
      label: 'Total Portfolio Value',
      value: formatCurrency(portfolioData?.total_value),
      icon: '💰',
      description: 'Total market value of all positions'
    },
    {
      label: 'Cash Balance',
      value: formatCurrency(portfolioData?.cash_balance),
      icon: '💵',
      description: 'Available cash for trading'
    },
    {
      label: 'Daily P&L',
      value: formatCurrency(performance.daily_pnl),
      change: formatPercentage(performance.daily_pnl_percent),
      changeClass: getChangeClass(performance.daily_pnl),
      icon: '📊',
      description: 'Today\'s profit and loss'
    },
    {
      label: 'Total P&L',
      value: formatCurrency(performance.total_pnl),
      change: formatPercentage(performance.total_pnl_percent),
      changeClass: getChangeClass(performance.total_pnl),
      icon: '📈',
      description: 'Overall profit and loss'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {metrics.map((metric, index) => (
        <MetricCard key={index} metric={metric} />
      ))}
    </div>
  );
};

const MetricCard = ({ metric }) => {
  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-2xl">{metric.icon}</span>
            <p className="metric-label">{metric.label}</p>
          </div>
          <div className="space-y-1">
            <p className="metric-value">{metric.value}</p>
            {metric.change && (
              <p className={`text-sm font-medium ${metric.changeClass}`}>
                {metric.change}
              </p>
            )}
          </div>
        </div>
      </div>
      
      {metric.description && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-500">{metric.description}</p>
        </div>
      )}
    </div>
  );
};

const PortfolioOverviewSkeleton = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="card">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <div className="loading-skeleton w-6 h-6 rounded"></div>
                <div className="loading-skeleton h-4 w-24"></div>
              </div>
              <div className="space-y-1">
                <div className="loading-skeleton h-8 w-32"></div>
                <div className="loading-skeleton h-4 w-16"></div>
              </div>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-100">
            <div className="loading-skeleton h-3 w-full"></div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PortfolioOverview;
