import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  GitBranch,
  Star,
  StarOff,
  CheckCircle,
  Archive,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Cpu,
  User,
  Zap,
  AlertCircle,
  Clock
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const SOURCE_LABELS = {
  optimization: { label: 'AI Optimizer', icon: Cpu, color: 'text-purple-600 bg-purple-50 border-purple-200' },
  manual: { label: 'Manual', icon: User, color: 'text-blue-600 bg-blue-50 border-blue-200' },
  ai_discovery: { label: 'AI Discovery', icon: Zap, color: 'text-yellow-600 bg-yellow-50 border-yellow-200' },
};

const StrategyVariantLibrary = ({ onApplyVariant }) => {
  const [variants, setVariants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [promoting, setPromoting] = useState(null);
  const [showArchived, setShowArchived] = useState(false);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('auth_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const fetchVariants = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE_URL}/api/strategy-variants`, {
        params: { include_archived: showArchived },
        headers: getAuthHeaders(),
      });
      setVariants(res.data.variants || []);
    } catch (err) {
      setError('Failed to load strategy variants.');
    } finally {
      setLoading(false);
    }
  }, [showArchived]);

  useEffect(() => {
    fetchVariants();
  }, [fetchVariants]);

  const handlePromote = async (variant) => {
    setPromoting(variant.id);
    try {
      const res = await axios.post(
        `${API_BASE_URL}/api/strategy-variants/${variant.id}/promote`,
        {},
        { headers: getAuthHeaders() }
      );
      await fetchVariants();
      if (onApplyVariant && res.data.active_variant?.config) {
        onApplyVariant(res.data.active_variant.config);
      }
    } catch (err) {
      setError('Failed to promote variant.');
    } finally {
      setPromoting(null);
    }
  };

  const handleToggleFavorite = async (variant) => {
    try {
      await axios.patch(
        `${API_BASE_URL}/api/strategy-variants/${variant.id}`,
        { is_favorite: !variant.is_favorite },
        { headers: getAuthHeaders() }
      );
      await fetchVariants();
    } catch {
      setError('Failed to update favorite.');
    }
  };

  const handleArchive = async (variant) => {
    if (!window.confirm(`Archive "${variant.name}"? It will be hidden from the library.`)) return;
    try {
      await axios.delete(
        `${API_BASE_URL}/api/strategy-variants/${variant.id}`,
        { headers: getAuthHeaders() }
      );
      await fetchVariants();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to archive variant.');
    }
  };

  const formatDate = (iso) => {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const ReturnBadge = ({ value }) => {
    if (value == null) return <span className="text-gray-400 text-sm">No backtest</span>;
    const positive = value >= 0;
    return (
      <span className={`flex items-center space-x-1 text-sm font-semibold ${positive ? 'text-green-600' : 'text-red-600'}`}>
        {positive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
        <span>{positive ? '+' : ''}{value.toFixed(1)}%</span>
      </span>
    );
  };

  const VariantCard = ({ variant }) => {
    const isExpanded = expandedId === variant.id;
    const src = SOURCE_LABELS[variant.source] || SOURCE_LABELS.manual;
    const SrcIcon = src.icon;

    return (
      <div className={`border rounded-lg transition-all duration-200 ${
        variant.is_active
          ? 'border-green-400 bg-green-50'
          : 'border-gray-200 bg-white hover:border-gray-300'
      }`}>
        {/* Card Header */}
        <div className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                <span className="font-semibold text-gray-900 truncate">{variant.name}</span>
                <span className="text-xs text-gray-400">v{variant.version}</span>
                {variant.is_active && (
                  <span className="flex items-center space-x-1 text-xs font-medium text-green-700 bg-green-100 border border-green-300 px-2 py-0.5 rounded-full">
                    <CheckCircle className="w-3 h-3" />
                    <span>Active</span>
                  </span>
                )}
                <span className={`flex items-center space-x-1 text-xs border px-2 py-0.5 rounded-full ${src.color}`}>
                  <SrcIcon className="w-3 h-3" />
                  <span>{src.label}</span>
                </span>
              </div>
              <div className="flex items-center space-x-4 mt-2">
                <ReturnBadge value={variant.backtest_return_pct} />
                {variant.backtest_win_rate != null && (
                  <span className="text-sm text-gray-500">
                    {(variant.backtest_win_rate * 100).toFixed(0)}% win rate
                  </span>
                )}
                {variant.backtest_total_trades != null && (
                  <span className="text-sm text-gray-500">
                    {variant.backtest_total_trades} trades
                  </span>
                )}
                <span className="flex items-center space-x-1 text-xs text-gray-400">
                  <Clock className="w-3 h-3" />
                  <span>{formatDate(variant.created_at)}</span>
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-1 ml-3 flex-shrink-0">
              <button
                onClick={() => handleToggleFavorite(variant)}
                className="p-1.5 rounded hover:bg-gray-100 transition-colors"
                title={variant.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
              >
                {variant.is_favorite
                  ? <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                  : <StarOff className="w-4 h-4 text-gray-400" />}
              </button>

              {!variant.is_active && (
                <button
                  onClick={() => handlePromote(variant)}
                  disabled={promoting === variant.id}
                  className="flex items-center space-x-1 px-3 py-1.5 text-xs font-medium bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:opacity-50"
                  title="Set as active config"
                >
                  {promoting === variant.id
                    ? <RefreshCw className="w-3 h-3 animate-spin" />
                    : <CheckCircle className="w-3 h-3" />}
                  <span>Promote</span>
                </button>
              )}

              {!variant.is_active && (
                <button
                  onClick={() => handleArchive(variant)}
                  className="p-1.5 rounded hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                  title="Archive variant"
                >
                  <Archive className="w-4 h-4" />
                </button>
              )}

              <button
                onClick={() => setExpandedId(isExpanded ? null : variant.id)}
                className="p-1.5 rounded hover:bg-gray-100 transition-colors text-gray-400"
              >
                {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>

        {/* Expanded Detail */}
        {isExpanded && (
          <div className="border-t border-gray-200 px-4 pb-4 pt-3 space-y-3">
            {variant.ai_summary && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs font-semibold text-blue-800 mb-1">AI Summary</p>
                <p className="text-sm text-blue-900">{variant.ai_summary}</p>
              </div>
            )}

            {variant.ai_proposed_changes && Object.keys(variant.ai_proposed_changes).length > 0 && (
              <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                <p className="text-xs font-semibold text-purple-800 mb-2">AI Proposed Changes</p>
                <div className="space-y-1">
                  {Object.entries(variant.ai_proposed_changes).map(([key, val]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-purple-700 font-medium">{key}</span>
                      <span className="text-purple-900">{JSON.stringify(val)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Config snapshot */}
            {variant.config && (
              <div>
                <p className="text-xs font-semibold text-gray-600 mb-2">Strategy Parameters</p>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(variant.config).filter(([k]) => k !== 'strategies').map(([key, val]) => (
                    <div key={key} className="flex justify-between text-xs bg-gray-50 rounded px-2 py-1">
                      <span className="text-gray-500">{key}</span>
                      <span className="font-medium text-gray-800">
                        {typeof val === 'object' ? '...' : String(val)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {variant.backtest_date_range && (
              <p className="text-xs text-gray-400">
                Backtest period: {variant.backtest_date_range}
              </p>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <GitBranch className="w-6 h-6 text-purple-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">Strategy Variant Library</h2>
              <p className="text-sm text-gray-500">
                {variants.length} variant{variants.length !== 1 ? 's' : ''} — promote any to become the active live config
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <label className="flex items-center space-x-2 text-sm text-gray-600 cursor-pointer">
              <input
                type="checkbox"
                checked={showArchived}
                onChange={(e) => setShowArchived(e.target.checked)}
                className="rounded border-gray-300"
              />
              <span>Show archived</span>
            </label>
            <button
              onClick={fetchVariants}
              className="p-2 rounded hover:bg-gray-100 transition-colors text-gray-500"
              title="Refresh"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {error && (
          <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg mb-4 text-red-700 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {loading && variants.length === 0 ? (
          <div className="flex items-center justify-center py-12 text-gray-400">
            <RefreshCw className="w-5 h-5 animate-spin mr-2" />
            <span>Loading variants...</span>
          </div>
        ) : variants.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <GitBranch className="w-10 h-10 mx-auto mb-3 opacity-40" />
            <p className="font-medium">No variants yet</p>
            <p className="text-sm mt-1">
              Run an optimization from the Backtesting tab — each improvement auto-saves a variant here.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {/* Favorites first */}
            {variants.filter(v => v.is_favorite).length > 0 && (
              <div>
                <p className="text-xs font-semibold text-yellow-600 uppercase tracking-wide mb-2">
                  ★ Favorites
                </p>
                {variants.filter(v => v.is_favorite).map(v => (
                  <VariantCard key={v.id} variant={v} />
                ))}
              </div>
            )}

            {/* Rest */}
            {variants.filter(v => !v.is_favorite).length > 0 && (
              <div>
                {variants.filter(v => v.is_favorite).length > 0 && (
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2 mt-4">
                    All Variants
                  </p>
                )}
                {variants.filter(v => !v.is_favorite).map(v => (
                  <VariantCard key={v.id} variant={v} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategyVariantLibrary;
