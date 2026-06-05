import React, { useState, useEffect, useCallback } from 'react';
import {
  Brain, Play, RefreshCw, TrendingUp, TrendingDown, DollarSign,
  Target, Clock, CheckCircle, XCircle, AlertTriangle, BarChart3,
  ChevronDown, ChevronUp, Shield, Zap
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const fmt = (n, decimals = 2) =>
  n == null ? '—' : Number(n).toFixed(decimals);

const fmtUsd = (n) =>
  n == null ? '—' : `$${Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

const signColor = (n) => (n >= 0 ? 'text-green-600' : 'text-red-600');

const StatusBadge = ({ status }) => {
  const map = {
    open:   'bg-blue-100 text-blue-700',
    closed: 'bg-gray-100 text-gray-600',
    profit: 'bg-green-100 text-green-700',
    stop:   'bg-red-100 text-red-700',
    expired:'bg-yellow-100 text-yellow-700',
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${map[status] || 'bg-gray-100 text-gray-600'}`}>
      {status}
    </span>
  );
};

export default function PaperLoop() {
  const { token } = useAuth();
  const [positions, setPositions] = useState([]);
  const [history, setHistory] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [guardrails, setGuardrails] = useState(null);
  const [cycleRunning, setCycleRunning] = useState(false);
  const [cycleResult, setCycleResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showGuardrails, setShowGuardrails] = useState(false);
  const [closingId, setClosingId] = useState(null);

  const authHeaders = useCallback(() => {
    const h = { 'Content-Type': 'application/json' };
    if (token) h['Authorization'] = `Bearer ${token}`;
    return h;
  }, [token]);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [posRes, histRes, perfRes, grRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/paper-loop/positions`, { headers: authHeaders() }),
        fetch(`${API_BASE_URL}/api/paper-loop/history`, { headers: authHeaders() }),
        fetch(`${API_BASE_URL}/api/paper-loop/performance`, { headers: authHeaders() }),
        fetch(`${API_BASE_URL}/api/paper-loop/guardrails`, { headers: authHeaders() }),
      ]);
      const [pos, hist, perf, gr] = await Promise.all([
        posRes.json(), histRes.json(), perfRes.json(), grRes.json()
      ]);
      setPositions(pos.positions || []);
      setHistory(hist.trades || []);
      setPerformance(perf);
      setGuardrails(gr.guardrails || gr);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [authHeaders]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const runCycle = async () => {
    setCycleRunning(true);
    setCycleResult(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/paper-loop/cycle`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ user_id: 'current' })
      });
      const data = await res.json();
      setCycleResult(data);
      await fetchAll();
    } catch (e) {
      setCycleResult({ error: e.message });
    } finally {
      setCycleRunning(false);
    }
  };

  const closePosition = async (id) => {
    setClosingId(id);
    try {
      await fetch(`${API_BASE_URL}/api/paper-loop/close/${id}`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ reason: 'manual' })
      });
      await fetchAll();
    } finally {
      setClosingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin mr-3" />
        <span className="text-gray-500">Loading AI Paper Loop…</span>
      </div>
    );
  }

  const totalPnL = performance?.total_profit_loss_usd ?? 0;
  const winRate = performance?.win_rate_pct ?? 0;
  const totalTrades = performance?.total_trades ?? 0;
  const avgReturn = performance?.avg_return_pct ?? 0;
  const byStrategy = performance?.by_strategy ?? {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="w-7 h-7 text-indigo-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Paper Trading Loop</h1>
            <p className="text-sm text-gray-500">Autonomous scan → score → execute → learn cycle</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowGuardrails(!showGuardrails)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors"
          >
            <Shield className="w-4 h-4" />
            Guardrails
            {showGuardrails ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          <button
            onClick={fetchAll}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={runCycle}
            disabled={cycleRunning}
            className="flex items-center gap-2 px-5 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white rounded-lg text-sm font-semibold transition-colors"
          >
            <Zap className={`w-4 h-4 ${cycleRunning ? 'animate-pulse' : ''}`} />
            {cycleRunning ? 'Running Cycle…' : 'Run Cycle'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {/* Cycle Result */}
      {cycleResult && !cycleResult.error && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="font-semibold text-green-800">Cycle Complete</span>
          </div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div><span className="text-gray-500">Entries executed:</span> <span className="font-medium">{cycleResult.entries_executed ?? 0}</span></div>
            <div><span className="text-gray-500">Exits processed:</span> <span className="font-medium">{cycleResult.exits_processed ?? 0}</span></div>
            <div><span className="text-gray-500">Skipped (guardrails):</span> <span className="font-medium">{cycleResult.skipped ?? 0}</span></div>
          </div>
        </div>
      )}
      {cycleResult?.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
          Cycle error: {cycleResult.error}
        </div>
      )}

      {/* Guardrails Panel */}
      {showGuardrails && guardrails && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-amber-600" />
            <h2 className="font-semibold text-amber-900">Active Guardrails</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            {Object.entries(guardrails).map(([k, v]) => (
              <div key={k} className="bg-white rounded-lg p-3 border border-amber-100">
                <p className="text-gray-500 text-xs mb-1">{k.replace(/_/g, ' ')}</p>
                <p className="font-semibold text-gray-900">
                  {typeof v === 'number' ? (k.includes('pct') ? `${v}%` : v) : String(v)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-xs text-gray-500 mb-1">Total P&amp;L</p>
          <p className={`text-2xl font-bold ${signColor(totalPnL)}`}>
            {totalPnL >= 0 ? '+' : '-'}{fmtUsd(totalPnL)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-xs text-gray-500 mb-1">Win Rate</p>
          <p className="text-2xl font-bold text-blue-600">{fmt(winRate)}%</p>
          <p className="text-xs text-gray-400">{totalTrades} closed trades</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-xs text-gray-500 mb-1">Avg Return / Trade</p>
          <p className={`text-2xl font-bold ${signColor(avgReturn)}`}>
            {avgReturn >= 0 ? '+' : ''}{fmt(avgReturn)}%
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-xs text-gray-500 mb-1">Open Positions</p>
          <p className="text-2xl font-bold text-indigo-600">{positions.length}</p>
        </div>
      </div>

      {/* Strategy Breakdown */}
      {Object.keys(byStrategy).length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-indigo-500" />
            Performance by Strategy
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(byStrategy).map(([strat, stats]) => (
              <div key={strat} className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                <p className="font-medium text-gray-800 text-sm capitalize mb-2">{strat.replace(/_/g, ' ')}</p>
                <div className="grid grid-cols-3 gap-1 text-xs">
                  <div>
                    <p className="text-gray-400">Trades</p>
                    <p className="font-semibold">{stats.trades ?? 0}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Win %</p>
                    <p className="font-semibold">{fmt(stats.win_rate_pct ?? 0)}%</p>
                  </div>
                  <div>
                    <p className="text-gray-400">P&L</p>
                    <p className={`font-semibold ${signColor(stats.total_pnl ?? 0)}`}>
                      {(stats.total_pnl ?? 0) >= 0 ? '+' : ''}{fmtUsd(stats.total_pnl)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Open Positions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-semibold text-gray-800 flex items-center gap-2">
            <Target className="w-4 h-4 text-green-500" />
            Open Positions ({positions.length})
          </h2>
        </div>
        {positions.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-8">No open positions. Run a cycle to check for new signals.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                <tr>
                  {['Symbol', 'Strategy', 'Entry', 'Shares', 'AI Score', 'Target', 'Stop', 'Expires', ''].map(h => (
                    <th key={h} className="px-4 py-3 text-left">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {positions.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-semibold text-gray-900">{p.symbol}</td>
                    <td className="px-4 py-3 text-gray-500 capitalize">{(p.strategy || '').replace(/_/g, ' ')}</td>
                    <td className="px-4 py-3">${fmt(p.entry_price)}</td>
                    <td className="px-4 py-3">{p.shares}</td>
                    <td className="px-4 py-3">
                      <span className={`font-semibold ${p.ai_score >= 70 ? 'text-green-600' : p.ai_score >= 55 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {fmt(p.ai_score, 0)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-green-600">+{fmt(p.profit_target_pct)}%</td>
                    <td className="px-4 py-3 text-red-600">-{fmt(p.stop_loss_pct)}%</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">
                      {p.max_hold_until ? new Date(p.max_hold_until).toLocaleDateString() : '—'}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => closePosition(p.id)}
                        disabled={closingId === p.id}
                        className="text-xs px-3 py-1 bg-red-50 hover:bg-red-100 text-red-600 rounded font-medium transition-colors disabled:opacity-50"
                      >
                        {closingId === p.id ? '…' : 'Close'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Trade History */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-800 flex items-center gap-2">
            <Clock className="w-4 h-4 text-gray-400" />
            Closed Trade History ({history.length})
          </h2>
        </div>
        {history.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-8">No closed trades yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                <tr>
                  {['Symbol', 'Strategy', 'Entry', 'Exit', 'Return', 'P&L', 'Exit Reason', 'Closed'].map(h => (
                    <th key={h} className="px-4 py-3 text-left">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {history.slice(0, 50).map(t => (
                  <tr key={t.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-semibold text-gray-900">{t.symbol}</td>
                    <td className="px-4 py-3 text-gray-500 capitalize">{(t.strategy || '').replace(/_/g, ' ')}</td>
                    <td className="px-4 py-3">${fmt(t.entry_price)}</td>
                    <td className="px-4 py-3">${fmt(t.exit_price)}</td>
                    <td className={`px-4 py-3 font-semibold ${signColor(t.return_pct ?? 0)}`}>
                      {(t.return_pct ?? 0) >= 0 ? '+' : ''}{fmt(t.return_pct)}%
                    </td>
                    <td className={`px-4 py-3 font-semibold ${signColor(t.profit_loss_usd ?? 0)}`}>
                      {(t.profit_loss_usd ?? 0) >= 0 ? '+' : '-'}{fmtUsd(t.profit_loss_usd)}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={t.exit_reason || t.status} />
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs">
                      {t.exit_time ? new Date(t.exit_time).toLocaleDateString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
