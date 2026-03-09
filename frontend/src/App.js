import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import MarketDataDashboard from './components/MarketDataDashboard';
import StrategyConfig from './components/StrategyConfig';
import PaperPortfolio from './components/PaperPortfolio';
import RealPortfolio from './RealPortfolio';
import TransactionQueue from './components/TransactionQueue';
import Backtesting from './components/Backtesting';
import Navbar from './components/Navbar';
import Login from './components/Login';
import Register from './components/Register';
import { AuthProvider, useAuth } from './context/AuthContext';
import './index.css';

function AppContent() {
  const { user, loading, logout } = useAuth();
  const [authView, setAuthView] = useState('login'); // 'login' | 'register'
  const [activeTab, setActiveTab] = useState('live');

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

  // Not authenticated — show login / register
  if (!user) {
    if (authView === 'register') {
      return <Register onSwitchToLogin={() => setAuthView('login')} />;
    }
    return <Login onSwitchToRegister={() => setAuthView('register')} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onRefresh={() => window.location.reload()} onLogout={logout} user={user} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('live')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'live'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Live Portfolio
              </button>
              <button
                onClick={() => setActiveTab('paper')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'paper'
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Paper Portfolio
              </button>
              <button
                onClick={() => setActiveTab('queue')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'queue'
                    ? 'border-orange-500 text-orange-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Transaction Queue
              </button>
              <button
                onClick={() => setActiveTab('market')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'market'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Market Data
              </button>
              <button
                onClick={() => setActiveTab('config')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'config'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Strategy Config
              </button>
              <button
                onClick={() => setActiveTab('backtest')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'backtest'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Backtesting
              </button>
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
