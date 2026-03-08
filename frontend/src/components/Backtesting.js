import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { PlayCircle, Clock, TrendingUp, TrendingDown, DollarSign, Target, Calendar, CheckCircle } from 'lucide-react';
import CalibrationModal from './CalibrationModal';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Backtesting = () => {
  const [loading, setLoading] = useState(false);
  const [backtestId, setBacktestId] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [showCalibrationModal, setShowCalibrationModal] = useState(false);

  // Form state
  const [startDate, setStartDate] = useState('2025-01-01');
  const [endDate, setEndDate] = useState('2026-03-01');
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.75);
  const [useAI, setUseAI] = useState(true);
  const [initialCapital, setInitialCapital] = useState(10000);
  const [positionSize, setPositionSize] = useState(1000);
  const [enableCompounding, setEnableCompounding] = useState(true); // NEW: Compounding control
  const [strategies, setStrategies] = useState({
    technical_breakout: true,
    earnings_play: true,
    seasonality: true
  });

  const runBacktest = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Get selected strategies
      const selectedStrategies = Object.keys(strategies).filter(s => strategies[s]);

      const response = await fetch(`${API_BASE_URL}/api/backtest/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_date: startDate,
          end_date: endDate,
          strategies: selectedStrategies.length === 3 ? null : selectedStrategies,
          confidence_threshold: confidenceThreshold / 100,
          use_ai: useAI,
          initial_capital: initialCapital,
          position_size: positionSize,
          max_hold_days: 14,
          enable_compounding: enableCompounding  // NEW: Pass compounding preference
        })
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Backtest failed');
      }

      setBacktestId(data.backtest_id);

      // Poll for results
      pollForResults(data.backtest_id);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const pollForResults = async (id) => {
    const maxAttempts = 60; // 5 minutes
    let attempts = 0;

    const poll = setInterval(async () => {
      attempts++;

      try {
        const statusResponse = await fetch(`${API_BASE_URL}/api/backtest/status/${id}`);
        
        if (!statusResponse.ok) {
          console.error('[Backtesting] Status check failed:', statusResponse.status);
          if (attempts >= maxAttempts) {
            clearInterval(poll);
            setError('Status check timed out');
            setLoading(false);
          }
          return; // Keep polling
        }

        const statusData = await statusResponse.json();
        console.log('[Backtesting] Poll attempt', attempts, 'status:', statusData.status);

        if (statusData.status === 'complete') {
          clearInterval(poll);
          
          // Get full results
          const resultsResponse = await fetch(`${API_BASE_URL}/api/backtest/results/${id}`);
          
          if (!resultsResponse.ok) {
            setError(`Failed to get results: ${resultsResponse.status}`);
            setLoading(false);
            return;
          }

          const resultsData = await resultsResponse.json();
          console.log('[Backtesting] Results received, success:', resultsData.success);
          console.log('[Backtesting] Results data:', JSON.stringify(resultsData).substring(0, 200));

          if (resultsData.success) {
            setResults(resultsData);
            setError(null);
            console.log('[Backtesting] ✅ Results set successfully!');
          } else {
            console.error('[Backtesting] Results success=false:', resultsData.error);
            setError(resultsData.error || 'Failed to get results');
          }
          setLoading(false);
        } else if (statusData.status === 'failed') {
          clearInterval(poll);
          setError(statusData.error || 'Backtest failed');
          setLoading(false);
        } else if (attempts >= maxAttempts) {
          clearInterval(poll);
          setError('Backtest timed out after 5 minutes');
          setLoading(false);
        }
      } catch (err) {
        console.error('[Backtesting] Polling error:', err);
        // Don't stop polling on network errors, only on timeout
        if (attempts >= maxAttempts) {
          clearInterval(poll);
          setError(`Failed to check status: ${err.message}`);
          setLoading(false);
        }
      }
    }, 5000); // Check every 5 seconds
  };

  const runQuickBacktest = async (period) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/backtest/quick/${period}?confidence_threshold=${confidenceThreshold / 100}`,
        { method: 'POST' }
      );

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Backtest failed');
      }

      setBacktestId(data.backtest_id);
      pollForResults(data.backtest_id);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleCalibrate = () => {
    setShowCalibrationModal(true);
  };

  const handleApplyRecommendations = (recommendations) => {
    console.log('Applying recommendations:', recommendations);
    // TODO: Update strategy config with recommendations
    // This will be implemented in Task 3.4
    alert(`Applied ${recommendations.length} recommendations!\n\nThis will update your Strategy Config in Task 3.4.`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">📊 Strategy Backtesting</h1>
          <p className="text-gray-600">Test your strategies against historical data before going live</p>
        </div>

        {/* Quick Backtest Buttons */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">🚀 Quick Backtest</h2>
          <div className="flex gap-4">
            <button
              onClick={() => runQuickBacktest('30d')}
              disabled={loading}
              className="flex-1 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              Last 30 Days
            </button>
            <button
              onClick={() => runQuickBacktest('90d')}
              disabled={loading}
              className="flex-1 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              Last 90 Days
            </button>
            <button
              onClick={() => runQuickBacktest('1y')}
              disabled={loading}
              className="flex-1 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              Last Year
            </button>
          </div>
        </div>

        {/* Custom Backtest Configuration */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">⚙️ Custom Backtest</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Date Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Capital Settings */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Initial Capital ($)</label>
              <input
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Initial Position Size ($)
                <span className="text-xs text-gray-500 block mt-1">
                  {enableCompounding 
                    ? 'Calculated as percentage of portfolio. As portfolio grows, position size increases proportionally.' 
                    : 'Fixed dollar amount per trade. Position size does not change as portfolio grows.'}
                </span>
              </label>
              <input
                type="number"
                value={positionSize}
                onChange={(e) => setPositionSize(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Compounding Toggle */}
            <div className="flex items-center space-x-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <input
                type="checkbox"
                id="enableCompounding"
                checked={enableCompounding}
                onChange={(e) => setEnableCompounding(e.target.checked)}
                className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <label htmlFor="enableCompounding" className="text-sm font-medium text-gray-700 cursor-pointer">
                <div>Enable Compounding <span className="text-green-600 font-semibold">(Recommended)</span></div>
                <span className="text-xs text-gray-600 block mt-1">
                  Position size grows with portfolio. Example: $10k portfolio → $1k position (10%), $20k portfolio → $2k position (10%)
                </span>
              </label>
            </div>

            {/* AI Settings */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                AI Confidence Threshold ({(confidenceThreshold * 100).toFixed(0)}%)
              </label>
              <input
                type="range"
                min="0.5"
                max="0.95"
                step="0.05"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="useAI"
                checked={useAI}
                onChange={(e) => setUseAI(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="useAI" className="ml-2 text-sm text-gray-700">
                Use AI Analysis (if unchecked, uses scanner scores only)
              </label>
            </div>
          </div>

          {/* Strategies */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Strategies to Test</label>
            <div className="flex gap-4">
              {Object.keys(strategies).map(strategy => (
                <label key={strategy} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={strategies[strategy]}
                    onChange={(e) => setStrategies({...strategies, [strategy]: e.target.checked})}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    {strategy.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Run Button */}
          <button
            onClick={runBacktest}
            disabled={loading}
            className="w-full bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium flex items-center justify-center gap-2"
          >
            <PlayCircle className="w-5 h-5" />
            {loading ? 'Running Backtest...' : 'Run Custom Backtest'}
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <div className="flex items-center gap-3">
              <Clock className="w-6 h-6 text-blue-600 animate-spin" />
              <div className="flex-1">
                <p className="text-blue-900 font-semibold">🚀 Backtest Running...</p>
                <p className="text-blue-700 text-sm">Analyzing historical data and simulating trades. This usually takes 1-2 minutes.</p>
                <div className="mt-3 w-full bg-blue-200 rounded-full h-2.5">
                  <div className="bg-blue-600 h-2.5 rounded-full animate-pulse" style={{width: '70%'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <p className="text-red-900 font-medium">❌ Error: {error}</p>
          </div>
        )}

        {/* Results */}
        {results && results.metrics && (
          <div>
            {/* Success Banner */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <div>
                  <p className="text-green-900 font-semibold">✅ Backtest Complete!</p>
                  <p className="text-green-700 text-sm">Analyzed {results.metrics.summary.total_trades} trades with {results.metrics.summary.win_rate.toFixed(1)}% win rate</p>
                </div>
              </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm">Total Return</p>
                    <p className={`text-2xl font-bold ${results.metrics.returns.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {results.metrics.returns.total_return_pct >= 0 ? '+' : ''}
                      {results.metrics.returns.total_return_pct.toFixed(2)}%
                    </p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-500" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm">Win Rate</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {results.metrics.summary.win_rate.toFixed(1)}%
                    </p>
                  </div>
                  <Target className="w-8 h-8 text-blue-500" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm">Net Profit</p>
                    <p className={`text-2xl font-bold ${results.metrics.returns.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${results.metrics.returns.net_profit.toFixed(2)}
                    </p>
                  </div>
                  <DollarSign className="w-8 h-8 text-green-500" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm">Total Trades</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {results.metrics.summary.total_trades}
                    </p>
                  </div>
                  <Calendar className="w-8 h-8 text-gray-500" />
                </div>
              </div>
            </div>

            {/* Calibrate Button */}
            <div className="mb-6 flex justify-center">
              <button
                onClick={() => handleCalibrate()}
                className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-lg transition-all shadow-lg hover:shadow-xl"
              >
                <Target className="w-5 h-5" />
                <span className="font-semibold">Calibrate from Backtest</span>
              </button>
            </div>

            {/* Performance Metrics */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
              <h3 className="text-xl font-semibold mb-4">📈 Performance Metrics</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-gray-500 text-sm">Profit Factor</p>
                  <p className="text-lg font-semibold">{results.metrics.performance.profit_factor.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Average Win</p>
                  <p className="text-lg font-semibold text-green-600">${results.metrics.performance.avg_win.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Average Loss</p>
                  <p className="text-lg font-semibold text-red-600">${results.metrics.performance.avg_loss.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Average Hold Time</p>
                  <p className="text-lg font-semibold">{results.metrics.performance.avg_hold_days.toFixed(1)} days</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Winning Trades</p>
                  <p className="text-lg font-semibold text-green-600">{results.metrics.summary.winning_trades}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Losing Trades</p>
                  <p className="text-lg font-semibold text-red-600">{results.metrics.summary.losing_trades}</p>
                </div>
              </div>
            </div>

            {/* Portfolio Equity Curve Chart */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
              <h3 className="text-xl font-semibold mb-4">💰 Portfolio Equity Curve</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart 
                  data={(() => {
                    // Build cumulative equity data from trades with DATES
                    let equity = results.metrics.returns.initial_capital;
                    const equityData = [
                      { 
                        date: results.config.start_date, 
                        equity: equity, 
                        profit: 0,
                        displayDate: new Date(results.config.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                      }
                    ];
                    
                    results.trades.forEach((trade, idx) => {
                      equity += trade.profit_loss;
                      equityData.push({
                        date: trade.exit_date,
                        equity: Math.round(equity * 100) / 100,
                        profit: Math.round(trade.profit_loss * 100) / 100,
                        displayDate: new Date(trade.exit_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                      });
                    });
                    
                    return equityData;
                  })()}
                  margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="displayDate" 
                    tick={{ fontSize: 11 }}
                    angle={-45}
                    textAnchor="end"
                    height={70}
                    interval={Math.floor(results.trades.length / 8) || 0}
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    domain={['auto', 'auto']}
                    tickFormatter={(value) => `$${value.toLocaleString()}`}
                  />
                  <Tooltip 
                    formatter={(value, name) => {
                      if (name === 'equity') return [`$${value.toLocaleString()}`, 'Portfolio Value'];
                      if (name === 'profit') return [`$${value.toLocaleString()}`, 'Trade P&L'];
                      return [value, name];
                    }}
                    labelFormatter={(label) => `Date: ${label}`}
                    contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #ccc' }}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="equity" 
                    stroke="#10b981" 
                    strokeWidth={3}
                    dot={{ fill: '#10b981', r: 3 }}
                    name="Portfolio Value"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Daily Average Position Size Chart */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
              <h3 className="text-xl font-semibold mb-4">📊 Daily Average Position Size</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart 
                  data={(() => {
                    // Calculate average position size by date
                    const positionsByDate = {};
                    
                    results.trades.forEach((trade) => {
                      const positionCost = trade.shares * trade.entry_price;
                      const entryDate = new Date(trade.entry_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' });
                      
                      if (!positionsByDate[entryDate]) {
                        positionsByDate[entryDate] = { total: 0, count: 0, date: trade.entry_date };
                      }
                      positionsByDate[entryDate].total += positionCost;
                      positionsByDate[entryDate].count += 1;
                    });
                    
                    // Convert to array and calculate averages
                    return Object.entries(positionsByDate)
                      .map(([displayDate, data]) => ({
                        displayDate,
                        date: data.date,
                        avgPositionSize: Math.round((data.total / data.count) * 100) / 100,
                        numTrades: data.count
                      }))
                      .sort((a, b) => new Date(a.date) - new Date(b.date));
                  })()}
                  margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="displayDate" 
                    tick={{ fontSize: 11 }}
                    angle={-45}
                    textAnchor="end"
                    height={70}
                    interval="preserveStartEnd"
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    domain={['auto', 'auto']}
                    tickFormatter={(value) => `$${value.toLocaleString()}`}
                  />
                  <Tooltip 
                    formatter={(value, name) => {
                      if (name === 'avgPositionSize') return [`$${value.toLocaleString()}`, 'Avg Position Size'];
                      if (name === 'numTrades') return [value, 'Trades That Day'];
                      return [value, name];
                    }}
                    labelFormatter={(label) => `Date: ${label}`}
                    contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #ccc' }}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="avgPositionSize" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    dot={{ fill: '#3b82f6', r: 3 }}
                    name="Avg Position Size"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Best & Worst Trades */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {results.metrics.best_trade && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-green-900 mb-3">🏆 Best Trade</h3>
                  <div className="space-y-2">
                    <p className="text-sm"><span className="font-medium">Symbol:</span> {results.metrics.best_trade.symbol}</p>
                    <p className="text-sm"><span className="font-medium">Strategy:</span> {results.metrics.best_trade.strategy}</p>
                    <p className="text-sm"><span className="font-medium">Return:</span> <span className="text-green-600 font-bold">+{results.metrics.best_trade.return_pct.toFixed(2)}%</span></p>
                    <p className="text-sm"><span className="font-medium">Profit:</span> <span className="text-green-600 font-bold">${results.metrics.best_trade.profit_loss.toFixed(2)}</span></p>
                    <p className="text-sm"><span className="font-medium">Hold Time:</span> {results.metrics.best_trade.hold_days} days</p>
                  </div>
                </div>
              )}

              {results.metrics.worst_trade && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-red-900 mb-3">💔 Worst Trade</h3>
                  <div className="space-y-2">
                    <p className="text-sm"><span className="font-medium">Symbol:</span> {results.metrics.worst_trade.symbol}</p>
                    <p className="text-sm"><span className="font-medium">Strategy:</span> {results.metrics.worst_trade.strategy}</p>
                    <p className="text-sm"><span className="font-medium">Return:</span> <span className="text-red-600 font-bold">{results.metrics.worst_trade.return_pct.toFixed(2)}%</span></p>
                    <p className="text-sm"><span className="font-medium">Loss:</span> <span className="text-red-600 font-bold">${results.metrics.worst_trade.profit_loss.toFixed(2)}</span></p>
                    <p className="text-sm"><span className="font-medium">Hold Time:</span> {results.metrics.worst_trade.hold_days} days</p>
                  </div>
                </div>
              )}
            </div>

            {/* Trade List */}
            {results.trades && results.trades.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-xl font-semibold mb-4">📋 All Trades</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left">Symbol</th>
                        <th className="px-4 py-2 text-left">Strategy</th>
                        <th className="px-4 py-2 text-right">Shares</th>
                        <th className="px-4 py-2 text-right">Position $</th>
                        <th className="px-4 py-2 text-right">Portfolio $</th>
                        <th className="px-4 py-2 text-right">Cash Available</th>
                        <th className="px-4 py-2 text-left">Entry</th>
                        <th className="px-4 py-2 text-left">Exit</th>
                        <th className="px-4 py-2 text-right">Return %</th>
                        <th className="px-4 py-2 text-right">P&L</th>
                        <th className="px-4 py-2 text-center">Days</th>
                        <th className="px-4 py-2 text-left">Exit Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.trades.map((trade, idx) => (
                        <tr key={idx} className="border-t border-gray-200 hover:bg-gray-50">
                          <td className="px-4 py-2 font-medium">{trade.symbol}</td>
                          <td className="px-4 py-2 text-gray-600">{trade.strategy.replace('_', ' ')}</td>
                          <td className="px-4 py-2 text-right font-medium text-blue-600">
                            {trade.shares}
                          </td>
                          <td className="px-4 py-2 text-right font-medium text-gray-700">
                            ${(trade.shares * trade.entry_price).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                          </td>
                          <td className="px-4 py-2 text-right font-bold text-purple-600">
                            ${trade.portfolio_value ? trade.portfolio_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) : 'N/A'}
                          </td>
                          <td className="px-4 py-2 text-right font-bold text-green-600">
                            ${trade.cash_available ? trade.cash_available.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) : 'N/A'}
                          </td>
                          <td className="px-4 py-2">
                            <div className="text-xs text-gray-500">{trade.entry_date}</div>
                            <div>${trade.entry_price.toFixed(2)}</div>
                          </td>
                          <td className="px-4 py-2">
                            <div className="text-xs text-gray-500">{trade.exit_date}</div>
                            <div>${trade.exit_price.toFixed(2)}</div>
                          </td>
                          <td className={`px-4 py-2 text-right font-semibold ${trade.return_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {trade.return_pct >= 0 ? '+' : ''}{trade.return_pct.toFixed(2)}%
                          </td>
                          <td className={`px-4 py-2 text-right font-semibold ${trade.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            ${trade.profit_loss.toFixed(2)}
                          </td>
                          <td className="px-4 py-2 text-center">{trade.hold_days}</td>
                          <td className="px-4 py-2 text-xs text-gray-500">{trade.exit_reason.replace('_', ' ')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Calibration Modal */}
      <CalibrationModal
        isOpen={showCalibrationModal}
        onClose={() => setShowCalibrationModal(false)}
        backtestResults={results}
        onApply={handleApplyRecommendations}
      />
    </div>
  );
};

export default Backtesting;
