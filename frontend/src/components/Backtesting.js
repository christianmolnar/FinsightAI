import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { PlayCircle, Clock, TrendingUp, TrendingDown, DollarSign, Target, Calendar } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Backtesting = () => {
  const [loading, setLoading] = useState(false);
  const [backtestId, setBacktestId] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Form state
  const [startDate, setStartDate] = useState('2025-01-01');
  const [endDate, setEndDate] = useState('2026-03-01');
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.75);
  const [useAI, setUseAI] = useState(true);
  const [initialCapital, setInitialCapital] = useState(10000);
  const [positionSize, setPositionSize] = useState(1000);
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
          confidence_threshold: confidenceThreshold,
          use_ai: useAI,
          initial_capital: initialCapital,
          position_size: positionSize,
          max_hold_days: 14
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
        const statusData = await statusResponse.json();

        if (statusData.status === 'complete') {
          clearInterval(poll);
          
          // Get full results
          const resultsResponse = await fetch(`${API_BASE_URL}/api/backtest/results/${id}`);
          const resultsData = await resultsResponse.json();

          if (resultsData.success) {
            setResults(resultsData);
          } else {
            setError(resultsData.error || 'Failed to get results');
          }
          setLoading(false);
        } else if (statusData.status === 'failed') {
          clearInterval(poll);
          setError(statusData.error || 'Backtest failed');
          setLoading(false);
        } else if (attempts >= maxAttempts) {
          clearInterval(poll);
          setError('Backtest timed out');
          setLoading(false);
        }
      } catch (err) {
        clearInterval(poll);
        setError('Failed to check status');
        setLoading(false);
      }
    }, 5000); // Check every 5 seconds
  };

  const runQuickBacktest = async (period) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/backtest/quick/${period}?confidence_threshold=${confidenceThreshold}`,
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Position Size ($)</label>
              <input
                type="number"
                value={positionSize}
                onChange={(e) => setPositionSize(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
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
              <div>
                <p className="text-blue-900 font-medium">Backtest Running...</p>
                <p className="text-blue-700 text-sm">This may take 2-5 minutes. Analyzing historical data and simulating trades.</p>
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
    </div>
  );
};

export default Backtesting;
