import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import MarketDataDashboard from './components/MarketDataDashboard';
import StrategyConfig from './components/StrategyConfig';
import PaperPortfolio from './components/PaperPortfolio';
import RealPortfolio from './RealPortfolio';
import TransactionQueue from './components/TransactionQueue';
import Navbar from './components/Navbar';
import './index.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [portfolioData, setPortfolioData] = useState(null);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false); // Changed to false - no initial load needed
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('schwab');

  // Removed auto-fetch - each tab manages its own data
  // useEffect(() => {
  //   fetchData();
  //   const interval = setInterval(fetchData, 30000);
  //   return () => clearInterval(interval);
  // }, []);

  const refreshData = () => {
    // Each tab component handles its own refresh
    window.location.reload();
  };

  if (loading && !portfolioData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-skeleton w-8 h-8 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading FInsightAI...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onRefresh={refreshData} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('schwab')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'schwab'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Schwab Portfolio
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
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'schwab' && (
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
      </main>
    </div>
  );
}

export default App;
