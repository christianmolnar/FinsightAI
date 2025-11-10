import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import MarketDataDashboard from './components/MarketDataDashboard';
import Navbar from './components/Navbar';
import './index.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [portfolioData, setPortfolioData] = useState(null);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('portfolio');

  useEffect(() => {
    fetchData();
    // Set up polling for real-time updates
    const interval = setInterval(fetchData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch portfolio data and trades in parallel
      const [portfolioResponse, tradesResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/v1/portfolio`),
        axios.get(`${API_BASE_URL}/api/v1/trades?limit=20`)
      ]);

      setPortfolioData(portfolioResponse.data);
      setTrades(tradesResponse.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load trading data. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const refreshData = () => {
    fetchData();
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
      
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                <button 
                  onClick={refreshData}
                  className="mt-2 bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded text-sm"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('portfolio')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'portfolio'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Portfolio Dashboard
              </button>
              <button
                onClick={() => setActiveTab('market')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'market'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Market Data (Schwab API)
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'portfolio' && (
          <Dashboard 
            portfolioData={portfolioData} 
            trades={trades}
            loading={loading}
            onRefresh={refreshData}
          />
        )}
        
        {activeTab === 'market' && (
          <MarketDataDashboard />
        )}
      </main>
    </div>
  );
}

export default App;
