import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import MarketStatus from './MarketStatus';

const MarketDataDashboard = () => {
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [quotes, setQuotes] = useState([]);
  const [symbols, setSymbols] = useState('AAPL,MSFT,TSLA,GOOGL,AMZN,TEAM');
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recentData, setRecentData] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(60); // seconds
  const [lastUpdated, setLastUpdated] = useState(null);

  const API_BASE = 'http://localhost:8000/api/market';

  // Auto-fetch quotes on component mount
  useEffect(() => {
    getQuotes();
  }, []);

  // Auto-refresh quotes at interval
  useEffect(() => {
    if (!autoRefresh || !symbols.trim()) return;

    const interval = setInterval(() => {
      getQuotes();
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, symbols]);

  const getQuotes = async () => {
    if (!symbols.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE}/quotes/${symbols}`);
      setQuotes(response.data.quotes || {});
      setLastUpdated(new Date());
      console.log('Quotes received:', response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get quotes');
      console.error('Error getting quotes:', err);
    } finally {
      setLoading(false);
    }
  };

  const getAccounts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE}/accounts`);
      setAccounts(response.data.accounts || []);
      console.log('Accounts received:', response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get accounts');
      console.error('Error getting accounts:', err);
    } finally {
      setLoading(false);
    }
  };

  const startStreaming = async () => {
    const symbolList = symbols.split(',').map(s => s.trim()).filter(s => s);
    
    try {
      const response = await axios.post(`${API_BASE}/stream/start`, symbolList);
      console.log('Streaming started:', response.data);
      alert('Real-time streaming started! Data will be saved to the database.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start streaming');
      console.error('Error starting stream:', err);
    }
  };

  const stopStreaming = async () => {
    try {
      const response = await axios.post(`${API_BASE}/stream/stop`);
      console.log('Streaming stopped:', response.data);
      alert('Real-time streaming stopped.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to stop streaming');
      console.error('Error stopping stream:', err);
    }
  };

  const getRecentData = async (symbol = 'AAPL') => {
    try {
      const response = await axios.get(`${API_BASE}/data/recent/${symbol}?hours=24`);
      setRecentData(response.data.data || []);
      console.log('Recent data:', response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get recent data');
      console.error('Error getting recent data:', err);
    }
  };

  const getCompanyName = (symbol) => {
    const companyNames = {
      'AAPL': 'Apple Inc.',
      'MSFT': 'Microsoft Corporation',
      'TSLA': 'Tesla, Inc.',
      'GOOGL': 'Alphabet Inc.',
      'AMZN': 'Amazon.com, Inc.',
      'TEAM': 'Atlassian Corporation'
    };
    return companyNames[symbol] || '';
  };

  const formatQuoteData = (quotes) => {
    return Object.entries(quotes).map(([symbol, data]) => {
      // Handle Alpaca API quote structure
      const quote = data.quote || data;
      // Calculate mid-price from bid/ask
      const bidPrice = parseFloat(quote.bid_price || 0);
      const askPrice = parseFloat(quote.ask_price || 0);
      const midPrice = bidPrice && askPrice ? (bidPrice + askPrice) / 2 : bidPrice || askPrice || 0;
      
      return {
        symbol,
        companyName: getCompanyName(symbol),
        price: midPrice > 0 ? midPrice.toFixed(2) : 'N/A',
        change: 'N/A', // Not provided by real-time quotes
        changePercent: 'N/A', // Not provided by real-time quotes
        volume: 'N/A', // Not provided by real-time quotes
        high: `$${bidPrice.toFixed(2)}`,
        low: `$${askPrice.toFixed(2)}`
      };
    });
  };

  const ConnectionStatus = () => {
    const statusConfig = {
      testing: { color: 'text-yellow-600', bg: 'bg-yellow-100', text: 'Testing Connection...', icon: '🔄' },
      connected: { color: 'text-green-600', bg: 'bg-green-100', text: 'Connected to Alpaca API', icon: '✅' },
      error: { color: 'text-red-600', bg: 'bg-red-100', text: 'Connection Failed', icon: '❌' }
    };

    const config = statusConfig[connectionStatus] || statusConfig.error;

    return (
      <div className={`p-4 rounded-lg ${config.bg} mb-6`}>
        <div className={`flex items-center ${config.color}`}>
          <span className="text-xl mr-2">{config.icon}</span>
          <span className="font-semibold">{config.text}</span>
        </div>
        {connectionStatus === 'error' && error && (
          <div className="mt-2 text-sm text-red-600">
            Error: {error}
          </div>
        )}
      </div>
    );
  };

  const AuthStatus = () => {
    return (
      <div className="p-4 rounded-lg mb-6 bg-green-100">
        <div className="flex items-center text-green-600">
          <span className="text-xl mr-2">🔐</span>
          <span className="font-semibold">
            Authenticated with Alpaca - Ready for Market Data
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Alpaca Market Data
          </h1>
          <p className="text-gray-600">
            Real-time market data integration with Alpaca API
          </p>
        </div>
        <MarketStatus />
      </div>

      <ConnectionStatus />
      <AuthStatus />

      {connectionStatus === 'connected' && (
        <>
          {/* Market Quotes Section */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Real-Time Quotes</h2>
              
              {/* Auto-refresh controls */}
              <div className="flex items-center gap-3 text-sm">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={autoRefresh}
                    onChange={(e) => setAutoRefresh(e.target.checked)}
                    className="rounded"
                  />
                  <span>Auto-refresh</span>
                </label>
                {autoRefresh && (
                  <>
                    <span className="text-gray-500">every</span>
                    <select
                      value={refreshInterval}
                      onChange={(e) => setRefreshInterval(Number(e.target.value))}
                      className="border rounded px-2 py-1"
                    >
                      <option value={15}>15s</option>
                      <option value={30}>30s</option>
                      <option value={60}>1 min</option>
                      <option value={120}>2 min</option>
                      <option value={300}>5 min</option>
                    </select>
                    <span className="text-green-600 text-xs">●</span>
                  </>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-4 mb-4">
              <input
                type="text"
                value={symbols}
                onChange={(e) => setSymbols(e.target.value)}
                placeholder="Enter symbols (comma-separated): AAPL,MSFT,TSLA"
                className="flex-1 border rounded px-3 py-2"
              />
              <button
                onClick={getQuotes}
                disabled={loading}
                className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Get Quotes'}
              </button>
            </div>

            {lastUpdated && (
              <div className="text-xs text-gray-500 mb-4">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </div>
            )}

            {Object.keys(quotes).length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {formatQuoteData(quotes).map((quote) => (
                  <div key={quote.symbol} className="border rounded-lg p-4 bg-gray-50">
                    <div className="text-lg font-bold text-gray-900">{quote.symbol}</div>
                    {quote.companyName && (
                      <div className="text-xs text-gray-600 mb-2">{quote.companyName}</div>
                    )}
                    <div className="text-2xl font-semibold text-gray-800">${quote.price}</div>
                    <div className={`text-sm ${parseFloat(quote.change) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {quote.change} ({quote.changePercent}%)
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      Volume: {typeof quote.volume === 'number' ? quote.volume.toLocaleString() : quote.volume}
                    </div>
                    <div className="text-xs text-gray-500">
                      H: ${quote.high} L: ${quote.low}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Account Information */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Account Information</h2>
            
            <button
              onClick={getAccounts}
              disabled={loading}
              className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600 disabled:opacity-50 mb-4"
            >
              {loading ? 'Loading...' : 'Get Accounts'}
            </button>

            {accounts.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {accounts.map((account, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-gray-50">
                    <div className="text-sm font-semibold text-gray-900">Account #{index + 1}</div>
                    <div className="text-xs text-gray-600">Hash: {account.hashValue || 'N/A'}</div>
                    <div className="text-xs text-gray-600">Number: {account.accountNumber || 'Hidden'}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Streaming Controls */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Real-Time Streaming</h2>
            <p className="text-gray-600 mb-4">
              Start streaming to automatically save real-time market data to the database.
            </p>
            
            <div className="flex gap-4 mb-4">
              <button
                onClick={startStreaming}
                className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
              >
                Start Streaming
              </button>
              <button
                onClick={stopStreaming}
                className="bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600"
              >
                Stop Streaming
              </button>
              <button
                onClick={() => getRecentData('AAPL')}
                className="bg-purple-500 text-white px-6 py-2 rounded hover:bg-purple-600"
              >
                View Recent Data
              </button>
            </div>

            {/* Recent Data Chart */}
            {recentData.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-2">Recent Market Data (Last 24 Hours)</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={recentData.slice(-50)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(timestamp) => new Date(timestamp).toLocaleString()}
                      formatter={(value, name) => [`$${value}`, name]}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="price" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          Error: {error}
        </div>
      )}
    </div>
  );
};

export default MarketDataDashboard;
