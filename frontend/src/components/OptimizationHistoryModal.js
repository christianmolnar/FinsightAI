import React, { useState, useEffect } from 'react';
import { X, Star, Check, TrendingUp, Clock, Target, Zap, Calendar } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const OptimizationHistoryModal = ({ isOpen, onClose, token }) => {
  const [optimizations, setOptimizations] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadOptimizations();
    }
  }, [isOpen]);

  const loadOptimizations = async () => {
    setLoading(true);
    try {
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/optimization/runs`, { headers });
      const data = await response.json();

      setOptimizations(data);
    } catch (err) {
      console.error('Failed to load optimizations:', err);
    } finally {
      setLoading(false);
    }
  };

  const viewDetails = async (runId) => {
    try {
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/optimization/runs/${runId}`, { headers });
      const data = await response.json();

      if (data.success) {
        setSelectedRun(data.run);
      }
    } catch (err) {
      console.error('Failed to load run details:', err);
    }
  };

  const applyOptimization = async (runId) => {
    if (!window.confirm('Apply this optimization to your Strategy Config? This will update your live trading parameters.')) {
      return;
    }

    setApplying(true);
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/optimization/apply`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          optimization_run_id: runId
        })
      });

      const data = await response.json();

      if (data.success) {
        alert(`✅ Applied ${data.changes.length} optimized parameters!\n\n${data.changes.map(c => `• ${c.parameter}: ${c.old_value} → ${c.new_value}`).join('\n')}`);
        loadOptimizations(); // Refresh list
      } else {
        alert('Failed to apply optimization: ' + data.error);
      }
    } catch (err) {
      alert('Failed to apply optimization: ' + err.message);
    } finally {
      setApplying(false);
    }
  };

  const toggleFavorite = async (runId) => {
    try {
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/optimization/runs/${runId}/favorite`, {
        method: 'POST',
        headers
      });

      const data = await response.json();

      if (data.success) {
        loadOptimizations(); // Refresh list
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-purple-50 to-pink-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Zap className="w-6 h-6 text-purple-600" />
              Optimization History
            </h2>
            <p className="text-sm text-gray-600 mt-1">View and apply saved optimization runs</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            </div>
          ) : optimizations.length === 0 ? (
            <div className="text-center py-12">
              <Zap className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600">No optimization runs yet</p>
              <p className="text-sm text-gray-500 mt-2">Run an AI optimization to see results here</p>
            </div>
          ) : selectedRun ? (
            /* Detail View */
            <div>
              <button
                onClick={() => setSelectedRun(null)}
                className="text-purple-600 hover:text-purple-700 mb-4 flex items-center gap-2"
              >
                ← Back to list
              </button>

              {/* Run Details */}
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6 mb-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{selectedRun.name || 'Optimization Run'}</h3>
                    <p className="text-sm text-gray-600">
                      {new Date(selectedRun.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {selectedRun.is_applied && (
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium flex items-center gap-1">
                        <Check className="w-4 h-4" />
                        Applied
                      </span>
                    )}
                    <button
                      onClick={() => toggleFavorite(selectedRun.id)}
                      className={`p-2 rounded-lg ${selectedRun.is_favorite ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'}`}
                    >
                      <Star className="w-5 h-5" fill={selectedRun.is_favorite ? 'currentColor' : 'none'} />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Initial Return</p>
                    <p className="text-2xl font-bold text-gray-900">{selectedRun.initial_return_pct.toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Best Return</p>
                    <p className="text-2xl font-bold text-purple-600">{selectedRun.best_return_pct.toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Improvement</p>
                    <p className="text-2xl font-bold text-green-600">+{selectedRun.total_improvement.toFixed(2)}%</p>
                  </div>
                </div>
              </div>

              {/* Iterations */}
              <div className="mb-6">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Optimization Journey ({selectedRun.total_iterations} iterations)
                </h4>
                <div className="space-y-3">
                  {selectedRun.iterations.map((iter, idx) => (
                    <div key={idx} className={`border rounded-lg p-4 ${iter.is_best ? 'bg-green-50 border-green-300' : 'bg-gray-50 border-gray-200'}`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold">
                          Iteration {iter.iteration} {iter.is_best && '🏆'}
                        </span>
                        <span className={`font-bold ${iter.is_best ? 'text-green-600' : 'text-gray-600'}`}>
                          {iter.return_pct.toFixed(2)}%
                        </span>
                      </div>
                      {iter.applied_recommendation && (
                        <p className="text-sm text-gray-600">
                          Applied: {iter.applied_recommendation.parameter} → {iter.applied_recommendation.suggested_value}
                        </p>
                      )}
                      {iter.converged && (
                        <p className="text-sm text-green-600 font-medium mt-2">✅ Converged</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Best Configuration */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Best Configuration
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                  <div>
                    <span className="text-gray-600">Position Size:</span>
                    <span className="ml-2 font-medium">${selectedRun.best_config.position_size}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Confidence:</span>
                    <span className="ml-2 font-medium">{(selectedRun.best_config.confidence_threshold * 100).toFixed(0)}%</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Max Hold Days:</span>
                    <span className="ml-2 font-medium">{selectedRun.best_config.max_hold_days}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Compounding:</span>
                    <span className="ml-2 font-medium">{selectedRun.best_config.enable_compounding ? 'Yes' : 'No'}</span>
                  </div>
                </div>
              </div>

              {/* Apply Button */}
              {!selectedRun.is_applied && (
                <button
                  onClick={() => applyOptimization(selectedRun.id)}
                  disabled={applying}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 font-medium flex items-center justify-center gap-2"
                >
                  {applying ? (
                    <>
                      <Clock className="w-5 h-5 animate-spin" />
                      Applying...
                    </>
                  ) : (
                    <>
                      <Check className="w-5 h-5" />
                      Apply to Strategy Config
                    </>
                  )}
                </button>
              )}
            </div>
          ) : (
            /* List View */
            <div className="space-y-4">
              {optimizations.map((run) => (
                <div
                  key={run.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => viewDetails(run.id)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-900">{run.name}</h3>
                        {run.is_favorite && (
                          <Star className="w-4 h-4 text-yellow-500" fill="currentColor" />
                        )}
                        {run.is_applied && (
                          <span className="px-2 py-0.5 bg-green-100 text-green-800 rounded text-xs font-medium">
                            Applied
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {new Date(run.created_at).toLocaleDateString()} • {run.start_date} to {run.end_date}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-purple-600">{run.best_return_pct.toFixed(2)}%</p>
                      <p className="text-xs text-green-600">+{run.total_improvement.toFixed(2)}%</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Initial</p>
                      <p className="font-medium">{run.initial_return_pct.toFixed(2)}%</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Iterations</p>
                      <p className="font-medium">{run.total_iterations}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Status</p>
                      <p className="font-medium">{run.converged ? '✅ Converged' : '🔄 Completed'}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default OptimizationHistoryModal;
