/**
 * Reports — Strategy Performance History (Phase F.8)
 *
 * Shows:
 * 1. Strategy version timeline — every period a strategy ran (paper or live), its P&L
 * 2. Paper vs Live comparison — did live match paper predictions?
 * 3. Top-line summary stats
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart3, Bot, CheckCircle, ChevronDown, ChevronUp,
  RefreshCw, TrendingDown, TrendingUp, XCircle, ArrowRight
} from 'lucide-react';
import { apiClient } from '../utils/apiClient';

export default function Reports() {
  const [history, setHistory] = useState([]);
  const [comparison, setComparison] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeSection, setActiveSection] = useState('history');
  const [expandedRow, setExpandedRow] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [h, c, s] = await Promise.all([
        apiClient.get('/api/reports/strategy-history'),
        apiClient.get('/api/reports/paper-vs-live'),
        apiClient.get('/api/reports/summary'),
      ]);
      setHistory(h.data || []);
      setComparison(c.data || []);
      setSummary(s.data || null);
    } catch (e) {
      setError('Failed to load reports: ' + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // ── Helpers ────────────────────────────────────────────────────────────────

  const PnlCell = ({ value, suffix = '%', className = '' }) => {
    if (value == null) return <span className="text-gray-400">—</span>;
    const pos = value >= 0;
    return <span className={`font-semibold ${pos ? 'text-green-600' : 'text-red-600'} ${className}`}>{pos ? '+' : ''}{value.toFixed(2)}{suffix}</span>;
  };

  const ModeTag = ({ mode, isActive }) => (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
      mode === 'live' ? 'bg-slate-100 text-slate-700' :
      mode === 'paper' ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-500'
    }`}>
      {mode === 'live' ? '💰 Live' : '📋 Paper'}
      {isActive && ' ●'}
    </span>
  );

  const WinRateBar = ({ rate }) => {
    if (rate == null) return null;
    const pct = Math.round(rate * 100);
    return (
      <div className="flex items-center space-x-2">
        <div className="w-16 bg-gray-200 rounded-full h-1.5">
          <div className={`h-1.5 rounded-full ${pct >= 50 ? 'bg-green-500' : 'bg-red-400'}`} style={{ width: `${pct}%` }} />
        </div>
        <span className={`text-xs font-medium ${pct >= 50 ? 'text-green-600' : 'text-red-600'}`}>{pct}%</span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <RefreshCw className="w-6 h-6 text-indigo-500 animate-spin" />
        <span className="ml-2 text-gray-500">Loading reports...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">

      {/* ── Header ── */}
      <div className="bg-gradient-to-r from-slate-700 to-indigo-800 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <BarChart3 className="w-7 h-7" />
              <h1 className="text-2xl font-bold">Strategy Reports</h1>
            </div>
            <p className="text-slate-300 text-sm">Historical performance across all strategy versions and modes</p>
          </div>
          <button onClick={fetchAll} className="flex items-center space-x-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-sm">
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-2 text-red-700 text-sm">
          <XCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* ── Summary Cards ── */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: 'Total Trades', value: summary.trade_count ?? 0, icon: <Bot className="w-5 h-5 text-indigo-500" /> },
            { label: 'Win Rate', value: summary.win_rate != null ? `${(summary.win_rate * 100).toFixed(1)}%` : '—', icon: <CheckCircle className="w-5 h-5 text-green-500" />, pct: summary.win_rate },
            { label: 'Total P&L', value: summary.total_pnl != null ? `${summary.total_pnl >= 0 ? '+' : ''}$${summary.total_pnl.toFixed(2)}` : '—', icon: summary.total_pnl >= 0 ? <TrendingUp className="w-5 h-5 text-green-500" /> : <TrendingDown className="w-5 h-5 text-red-500" />, color: (summary.total_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600' },
            { label: 'Strategy Periods', value: summary.total_strategy_periods ?? 0, icon: <BarChart3 className="w-5 h-5 text-blue-500" /> },
            { label: 'Open Positions', value: summary.open_positions ?? 0, icon: <Bot className="w-5 h-5 text-purple-500" /> },
          ].map(({ label, value, icon, color }) => (
            <div key={label} className="bg-white rounded-lg border border-gray-200 p-4 flex items-center space-x-3">
              {icon}
              <div>
                <p className="text-xs text-gray-500">{label}</p>
                <p className={`text-lg font-bold ${color || 'text-gray-900'}`}>{value}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Active Strategies ── */}
      {summary && (summary.active_paper_strategy || summary.active_live_strategy) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {summary.active_paper_strategy && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
              <p className="text-xs text-indigo-600 font-medium uppercase tracking-wide mb-1">Active Paper Strategy</p>
              <p className="font-semibold text-indigo-900">{summary.active_paper_strategy}</p>
            </div>
          )}
          {summary.active_live_strategy && (
            <div className="bg-slate-50 border border-slate-300 rounded-lg p-4">
              <p className="text-xs text-slate-600 font-medium uppercase tracking-wide mb-1">Active Live Strategy</p>
              <p className="font-semibold text-slate-900">{summary.active_live_strategy}</p>
            </div>
          )}
        </div>
      )}

      {/* ── Section Switcher ── */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 w-fit">
        {[['history', 'Strategy Timeline'], ['comparison', 'Paper vs Live']].map(([id, label]) => (
          <button key={id} onClick={() => setActiveSection(id)}
            className={`px-5 py-2 rounded-md text-sm font-medium transition-colors ${activeSection === id ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
            {label}
          </button>
        ))}
      </div>

      {/* ── Strategy Timeline ── */}
      {activeSection === 'history' && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-4 border-b border-gray-100">
            <h2 className="font-semibold text-gray-800">Strategy Version Timeline</h2>
            <p className="text-xs text-gray-500 mt-0.5">Every period a strategy ran, its date range, and actual performance</p>
          </div>
          {history.length === 0 ? (
            <div className="p-8 text-center text-gray-400 text-sm">
              No strategy history yet. Activate a variant from Strategy Config to start tracking.
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {history.map(row => (
                <div key={row.id}>
                  <button
                    className="w-full px-4 py-4 hover:bg-gray-50 transition-colors text-left"
                    onClick={() => setExpandedRow(expandedRow === row.id ? null : row.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 min-w-0">
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-semibold text-gray-900 text-sm">{row.name}</span>
                            <span className="text-xs text-gray-400">v{row.version}</span>
                            <ModeTag mode={row.mode} isActive={row.is_active} />
                            {row.is_halted && <span className="text-xs px-1.5 py-0.5 bg-red-100 text-red-700 rounded">halted</span>}
                          </div>
                          <p className="text-xs text-gray-400 mt-0.5">
                            {row.activated_at ? new Date(row.activated_at).toLocaleDateString() : '?'}
                            {' → '}
                            {row.is_active ? 'now' : row.deactivated_at ? new Date(row.deactivated_at).toLocaleDateString() : '?'}
                            {row.days_running != null && ` (${row.days_running}d)`}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-6 flex-shrink-0 ml-4">
                        <div className="text-right hidden sm:block">
                          <p className="text-xs text-gray-400">Trades</p>
                          <p className="font-semibold text-sm">{row.trade_count}</p>
                        </div>
                        <div className="text-right hidden sm:block">
                          <p className="text-xs text-gray-400">Win Rate</p>
                          <WinRateBar rate={row.win_rate} />
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-gray-400">P&L</p>
                          <PnlCell value={row.total_pnl} suffix="$" />
                        </div>
                        {expandedRow === row.id ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                      </div>
                    </div>
                  </button>

                  {/* Expanded detail */}
                  {expandedRow === row.id && (
                    <div className="px-4 pb-4 bg-gray-50 border-t border-gray-100">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-3">
                        {[
                          { label: 'Trades', value: row.trade_count },
                          { label: 'Wins / Losses', value: row.trade_count > 0 ? `${row.win_count} / ${row.loss_count}` : '—' },
                          { label: 'Avg Return', value: row.avg_return_pct != null ? null : '—', pnl: row.avg_return_pct, suffix: '%' },
                          { label: 'Best Trade', value: null, pnl: row.best_trade_pct, suffix: '%' },
                          { label: 'Worst Trade', value: null, pnl: row.worst_trade_pct, suffix: '%' },
                          { label: 'Backtest Return', value: null, pnl: row.backtest_return_pct, suffix: '%' },
                          { label: 'Open Positions', value: row.open_positions },
                          { label: 'Source', value: row.source?.replace(/_/g, ' ') },
                        ].map(({ label, value, pnl, suffix }) => (
                          <div key={label} className="bg-white rounded-lg border border-gray-200 p-3">
                            <p className="text-xs text-gray-400">{label}</p>
                            {value !== undefined && value !== null
                              ? <p className="font-semibold text-sm mt-0.5 capitalize">{value}</p>
                              : pnl != null
                              ? <PnlCell value={pnl} suffix={suffix} className="text-sm" />
                              : <p className="text-gray-400 text-sm">—</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Paper vs Live Comparison ── */}
      {activeSection === 'comparison' && (
        <div className="space-y-4">
          {comparison.length === 0 ? (
            <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400 text-sm">
              No strategy has been promoted to live yet. Once a paper strategy is promoted and runs in live mode, the comparison will appear here.
            </div>
          ) : (
            comparison.map(row => (
              <div key={row.strategy_name} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                <div className="px-4 py-3 bg-gray-50 border-b border-gray-100 flex items-center space-x-2">
                  <span className="font-semibold text-gray-800">{row.strategy_name}</span>
                  {row.has_paper && <ModeTag mode="paper" />}
                  {row.has_live && <ModeTag mode="live" />}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-100">
                  {/* Paper side */}
                  <div className="p-4">
                    <p className="text-xs font-medium text-indigo-600 uppercase tracking-wide mb-3">📋 Paper</p>
                    {row.paper.length === 0 ? (
                      <p className="text-gray-400 text-sm">No paper history</p>
                    ) : row.paper.map(p => (
                      <div key={p.variant_id} className="mb-3 last:mb-0">
                        <p className="text-xs text-gray-400 mb-1">
                          v{p.version} · {p.activated_at ? new Date(p.activated_at).toLocaleDateString() : '?'} → {p.deactivated_at ? new Date(p.deactivated_at).toLocaleDateString() : 'now'}
                        </p>
                        <ComparisonStats stats={p.stats} />
                      </div>
                    ))}
                  </div>

                  {/* Live side */}
                  <div className="p-4">
                    <p className="text-xs font-medium text-slate-600 uppercase tracking-wide mb-3">💰 Live</p>
                    {row.live.length === 0 ? (
                      <div className="text-gray-400 text-sm flex items-center space-x-1">
                        <ArrowRight className="w-3.5 h-3.5" />
                        <span>Not yet promoted to live</span>
                      </div>
                    ) : row.live.map(l => (
                      <div key={l.variant_id} className="mb-3 last:mb-0">
                        <p className="text-xs text-gray-400 mb-1">
                          v{l.version} · {l.activated_at ? new Date(l.activated_at).toLocaleDateString() : '?'} → {l.deactivated_at ? new Date(l.deactivated_at).toLocaleDateString() : 'now'}
                        </p>
                        <ComparisonStats stats={l.stats} />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

function ComparisonStats({ stats }) {
  if (!stats || stats.trade_count === 0) {
    return <p className="text-gray-400 text-xs">No closed trades yet</p>;
  }
  const winPct = stats.win_rate != null ? Math.round(stats.win_rate * 100) : null;
  return (
    <div className="grid grid-cols-3 gap-2 text-xs">
      <div><p className="text-gray-400">Trades</p><p className="font-semibold">{stats.trade_count}</p></div>
      <div>
        <p className="text-gray-400">Win Rate</p>
        <p className={`font-semibold ${winPct >= 50 ? 'text-green-600' : 'text-red-600'}`}>{winPct != null ? `${winPct}%` : '—'}</p>
      </div>
      <div>
        <p className="text-gray-400">Total P&L</p>
        <p className={`font-semibold ${(stats.total_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {stats.total_pnl != null ? `${stats.total_pnl >= 0 ? '+' : ''}$${stats.total_pnl.toFixed(2)}` : '—'}
        </p>
      </div>
      <div><p className="text-gray-400">Avg Return</p><p className={`font-semibold ${(stats.avg_return_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>{stats.avg_return_pct != null ? `${stats.avg_return_pct >= 0 ? '+' : ''}${stats.avg_return_pct.toFixed(2)}%` : '—'}</p></div>
      <div><p className="text-gray-400">Best</p><p className="font-semibold text-green-600">{stats.best_trade_pct != null ? `+${stats.best_trade_pct.toFixed(1)}%` : '—'}</p></div>
      <div><p className="text-gray-400">Worst</p><p className="font-semibold text-red-600">{stats.worst_trade_pct != null ? `${stats.worst_trade_pct.toFixed(1)}%` : '—'}</p></div>
    </div>
  );
}
