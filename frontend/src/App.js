import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import MarketDataDashboard from './components/MarketDataDashboard';
import StrategyConfig from './components/StrategyConfig';
import PaperPortfolio from './components/PaperPortfolio';
import RealPortfolio from './RealPortfolio';
import TransactionQueue from './components/TransactionQueue';
import Backtesting from './components/Backtesting';
import PaperLoop from './components/PaperLoop';
import Navbar from './components/Navbar';
import Login from './components/Login';
import { AuthProvider, useAuth } from './context/AuthContext';
import './index.css';

function AppContent() {
  const { user, loading, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('live');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Show spinner while restoring session from localStorage
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400 text-sm">Loading…</p>
        </div>
      </div>
    );
  }

  // Not authenticated — show login
  if (!user) {
    return <Login />;
  }

  const tabs = [
    { id: 'live', label: 'Live Portfolio', activeClass: 'bg-indigo-50 text-indigo-600 border-l-indigo-500', borderClass: 'border-indigo-500 text-indigo-600' },
    { id: 'paper', label: 'Paper Portfolio', activeClass: 'bg-green-50 text-green-600 border-l-green-500', borderClass: 'border-green-500 text-green-600' },
    { id: 'queue', label: 'Transaction Queue', activeClass: 'bg-orange-50 text-orange-600 border-l-orange-500', borderClass: 'border-orange-500 text-orange-600' },
    { id: 'market', label: 'Market Data', activeClass: 'bg-indigo-50 text-indigo-600 border-l-indigo-500', borderClass: 'border-indigo-500 text-indigo-600' },
    { id: 'config', label: 'Strategy Config', activeClass: 'bg-indigo-50 text-indigo-600 border-l-indigo-500', borderClass: 'border-indigo-500 text-indigo-600' },
    { id: 'backtest', label: 'Backtesting', activeClass: 'bg-purple-50 text-purple-600 border-l-purple-500', borderClass: 'border-purple-500 text-purple-600' },
    { id: 'ai-loop', label: 'AI Paper Loop', activeClass: 'bg-indigo-50 text-indigo-600 border-l-indigo-500', borderClass: 'border-indigo-500 text-indigo-600' }
  ];

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onRefresh={() => window.location.reload()} onLogout={logout} user={user} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-6">
          {/* Mobile: Hamburger + Active Tab Display */}
          <div className="lg:hidden">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                {tabs.find(t => t.id === activeTab)?.label}
              </h2>
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-lg bg-white border border-gray-300 shadow-sm hover:bg-gray-50 transition-colors"
                aria-label="Toggle menu"
              >
                <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {mobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>

            {/* Mobile Menu Dropdown */}
            {mobileMenuOpen && (
              <div className="mb-4 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden animate-fadeIn">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => handleTabChange(tab.id)}
                    className={`w-full text-left px-4 py-3 border-b border-gray-100 last:border-b-0 font-medium transition-colors ${
                      activeTab === tab.id
                        ? `${tab.activeClass} border-l-4`
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Desktop: Horizontal Tabs */}
          <div className="hidden lg:block border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                    activeTab === tab.id
                      ? tab.borderClass
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'live' && (
          <RealPortfolio />
        )}
        
        {activeTab === 'paper' && (
          <PaperPortfolio />
        )}
        
        {activeTab === 'queue' && (
          <TransactionQueue />
        )}
        
        {activeTab === 'market' && (
          <MarketDataDashboard />
        )}
        
        {activeTab === 'config' && (
          <StrategyConfig />
        )}
        
        {activeTab === 'backtest' && (
          <Backtesting />
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
