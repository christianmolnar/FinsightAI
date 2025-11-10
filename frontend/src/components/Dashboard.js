import React from 'react';
import PortfolioOverview from './PortfolioOverview';
import PortfolioChart from './PortfolioChart';
import PositionsTable from './PositionsTable';
import TradesTable from './TradesTable';
import MarketOverview from './MarketOverview';

const Dashboard = ({ portfolioData, trades, loading, onRefresh }) => {
  if (loading && !portfolioData) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Trading Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Real-time portfolio performance and trading activity
          </p>
        </div>
      </div>

      {/* Portfolio Overview Cards */}
      <PortfolioOverview portfolioData={portfolioData} loading={loading} />

      {/* Charts and Market Data Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <PortfolioChart portfolioData={portfolioData} />
        </div>
        <div className="lg:col-span-1">
          <MarketOverview />
        </div>
      </div>

      {/* Tables Row */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <PositionsTable positions={portfolioData?.positions || []} loading={loading} />
        <TradesTable trades={trades} loading={loading} />
      </div>
    </div>
  );
};

const DashboardSkeleton = () => {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div>
        <div className="loading-skeleton h-8 w-64 mb-2"></div>
        <div className="loading-skeleton h-4 w-96"></div>
      </div>

      {/* Cards skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card">
            <div className="loading-skeleton h-6 w-24 mb-2"></div>
            <div className="loading-skeleton h-8 w-32"></div>
          </div>
        ))}
      </div>

      {/* Charts skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card">
          <div className="loading-skeleton h-64 w-full"></div>
        </div>
        <div className="lg:col-span-1 card">
          <div className="loading-skeleton h-64 w-full"></div>
        </div>
      </div>

      {/* Tables skeleton */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="card">
          <div className="loading-skeleton h-6 w-32 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="loading-skeleton h-12 w-full"></div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="loading-skeleton h-6 w-32 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="loading-skeleton h-12 w-full"></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
