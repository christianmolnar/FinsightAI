import React, { useState, useEffect } from 'react';

const MarketOverview = () => {
  const [marketData, setMarketData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock market data - this will be replaced with real market data API calls
  const mockMarketData = [
    { symbol: 'SPY', name: 'SPDR S&P 500', price: 421.50, change: 2.15, changePercent: 0.51 },
    { symbol: 'QQQ', name: 'Invesco QQQ Trust', price: 365.80, change: -1.25, changePercent: -0.34 },
    { symbol: 'IWM', name: 'iShares Russell 2000', price: 194.30, change: 0.85, changePercent: 0.44 },
    { symbol: 'GLD', name: 'SPDR Gold Shares', price: 185.45, change: -0.75, changePercent: -0.40 },
    { symbol: 'VIX', name: 'CBOE Volatility Index', price: 18.25, change: -1.10, changePercent: -5.68 },
  ];

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setMarketData(mockMarketData);
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercentage = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      signDisplay: 'always'
    }).format(value / 100);
  };

  const getChangeClass = (value) => {
    if (value > 0) return 'positive';
    if (value < 0) return 'negative';
    return 'neutral';
  };

  if (loading) {
    return <MarketOverviewSkeleton />;
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Market Overview</h3>
        <p className="text-sm text-gray-500 mt-1">Key market indicators</p>
      </div>

      <div className="space-y-4">
        {marketData.map((item, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-900">{item.symbol}</div>
              <div className="text-xs text-gray-500 truncate">{item.name}</div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">
                {item.symbol === 'VIX' ? item.price.toFixed(2) : formatCurrency(item.price)}
              </div>
              <div className={`text-xs font-medium ${getChangeClass(item.change)}`}>
                {item.change > 0 ? '+' : ''}{item.change.toFixed(2)} ({formatPercentage(item.changePercent)})
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>Market Status</span>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Open</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const MarketOverviewSkeleton = () => {
  return (
    <div className="card">
      <div className="card-header">
        <div className="loading-skeleton h-6 w-32"></div>
        <div className="loading-skeleton h-4 w-24 mt-1"></div>
      </div>
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <div className="loading-skeleton h-4 w-12 mb-1"></div>
              <div className="loading-skeleton h-3 w-24"></div>
            </div>
            <div className="text-right">
              <div className="loading-skeleton h-4 w-16 mb-1"></div>
              <div className="loading-skeleton h-3 w-20"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MarketOverview;
