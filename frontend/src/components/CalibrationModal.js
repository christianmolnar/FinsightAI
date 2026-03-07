import React, { useState, useEffect } from 'react';
import { X, Target, TrendingUp, CheckCircle, XCircle, Loader, Lightbulb, AlertCircle } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const CalibrationModal = ({ isOpen, onClose, backtestResults, onApply }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedRecommendations, setSelectedRecommendations] = useState(new Set());

  useEffect(() => {
    if (isOpen && backtestResults) {
      fetchRecommendations();
    }
  }, [isOpen, backtestResults]);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Extract current config from backtest results
      const currentConfig = {
        strategy: 'earnings', // TODO: Get from backtest config
        profitTarget: 12,
        stopLoss: 5,
        positionSize: 1000,
        // Add more parameters as needed
      };

      // Prepare trades data
      const trades = backtestResults.trades || [];
      
      const response = await fetch(`${API_BASE_URL}/api/calibration/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          metrics: backtestResults.metrics,
          current_config: currentConfig,
          trades: trades.map(t => ({
            symbol: t.symbol,
            entry_date: t.entry_date,
            exit_date: t.exit_date,
            entry_price: t.entry_price,
            exit_price: t.exit_price,
            pnl: t.pnl,
            pnl_percent: t.pnl_percent,
            exit_reason: t.exit_reason,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch recommendations: ${response.statusText}`);
      }

      const data = await response.json();
      setRecommendations(data.recommendations || []);
      
      // Select all recommendations by default
      setSelectedRecommendations(new Set(data.recommendations.map((_, idx) => idx)));
    } catch (err) {
      console.error('Calibration error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleRecommendation = (index) => {
    const newSelected = new Set(selectedRecommendations);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedRecommendations(newSelected);
  };

  const handleApplySelected = () => {
    const selected = recommendations.filter((_, idx) => selectedRecommendations.has(idx));
    onApply(selected);
    onClose();
  };

  const handleApplyAll = () => {
    onApply(recommendations);
    onClose();
  };

  const handleRejectAll = () => {
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Target className="w-6 h-6 text-indigo-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">AI Calibration Results</h2>
              <p className="text-sm text-gray-600">
                Analyzed {backtestResults?.metrics?.summary?.total_trades || 0} trades • {backtestResults?.metrics?.summary?.win_rate?.toFixed(1) || 0}% win rate
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading && (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
              <p className="text-gray-600">Analyzing backtest results...</p>
              <p className="text-sm text-gray-500 mt-2">AI is evaluating optimal parameter adjustments</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900">Error Loading Recommendations</h3>
                <p className="text-red-800 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && recommendations.length === 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
              <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-3" />
              <h3 className="font-semibold text-green-900 text-lg">No Adjustments Needed</h3>
              <p className="text-green-800 text-sm mt-2">
                Your current configuration is already well-optimized for this backtest period.
              </p>
            </div>
          )}

          {!loading && !error && recommendations.length > 0 && (
            <div className="space-y-4">
              {/* Summary */}
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6">
                <div className="flex items-start space-x-3">
                  <Lightbulb className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-indigo-900">
                      {recommendations.length} Recommendation{recommendations.length !== 1 ? 's' : ''} Found
                    </h3>
                    <p className="text-indigo-800 text-sm mt-1">
                      Select the recommendations you want to apply to your strategy configuration.
                    </p>
                  </div>
                </div>
              </div>

              {/* Recommendations List */}
              {recommendations.map((rec, index) => (
                <div
                  key={index}
                  className={`border-2 rounded-lg p-4 transition-all cursor-pointer ${
                    selectedRecommendations.has(index)
                      ? 'border-indigo-300 bg-indigo-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                  onClick={() => toggleRecommendation(index)}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {selectedRecommendations.has(index) ? (
                        <CheckCircle className="w-5 h-5 text-indigo-600" />
                      ) : (
                        <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-gray-900">{rec.parameter}</h4>
                        <span className="text-xs font-medium px-2 py-1 bg-green-100 text-green-800 rounded">
                          {rec.confidence}% confidence
                        </span>
                      </div>
                      <div className="flex items-center space-x-2 text-sm mb-2">
                        <span className="text-gray-600">Current:</span>
                        <span className="font-semibold text-gray-900">{rec.current_value}</span>
                        <TrendingUp className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-600">Suggested:</span>
                        <span className="font-semibold text-indigo-600">{rec.suggested_value}</span>
                      </div>
                      <p className="text-sm text-gray-700">{rec.reasoning}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {!loading && !error && recommendations.length > 0 && (
          <div className="p-6 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {selectedRecommendations.size} of {recommendations.length} selected
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleRejectAll}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Reject All
              </button>
              <button
                onClick={handleApplySelected}
                disabled={selectedRecommendations.size === 0}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Apply Selected ({selectedRecommendations.size})
              </button>
              <button
                onClick={handleApplyAll}
                className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-colors"
              >
                Apply All
              </button>
            </div>
          </div>
        )}

        {!loading && !error && recommendations.length === 0 && (
          <div className="p-6 border-t border-gray-200 bg-gray-50 flex justify-end">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CalibrationModal;
