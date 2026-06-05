/**
 * PaperTrader — Autonomous Paper Trading Monitor (Phase F.6)
 *
 * This view is for monitoring and controlling the autonomous paper trader.
 * There is NO manual trade execution here — all positions come from the trader.
 *
 * Controls:
 *   🔴 STOP EVERYTHING  — halt trader immediately, no new entries
 *   🟡 PAUSE            — no new entries, existing run to natural exit
 *   ▶️ RESUME           — clear halt, resume normal cycles
 *   🔄 Run Cycle        — manually trigger one scan/execute/exit cycle
 *
 * The active StrategyVariant must be set from Strategy Config before the
 * trader can execute. If none is set, a prompt is shown.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity, AlertTriangle, BarChart3, Bot, CheckCircle,
  ChevronDown, ChevronUp, Clock, DollarSign, Eye,
  Pause, Play, RefreshCw, Shield, Square, Target,
  TrendingDown, TrendingUp, XCircle, Zap
} from 'lucide-react';
import { apiClient } from '../utils/apiClient';

const MODE = 'paper';
const API = `/api/trader/${MODE}`;

export default function PaperTrader() {
  const [status, setStatus] = useState(null);
  const [positions, setPositions] = useState([]);
  const [history, setHistory] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cycleRunning, setCycleRunning] = useState(false);
  const [message, setMessage] = useState(null);
  const [showHistory, setShowHistory] = useState(true);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [s, p, h, perf] = await Promise.all([
        apiClient.get(`${API}/status`),
        apiClient.get(`${API}/positions`),
        apiClient.get(`${API}/history`),
        apiClient.get(`${API}/performance`),
      ]);
      setStatus(s.data);
      setPositions(p.data || []);
      setHistory(h.data || []);
      setPerformance(perf.data || null);
    } catch (e) {
      setMessage({ type: 'error', text: 'Failed to load trader data: ' + (e.response?.data?.detail || e.message) });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const runCycle = async () => {
    setCycleRunning(true);
    setMessage(null);
    try {
      const res = await apiClient.post(`${API}/cycle`);
      const d = res.data;
      if (d.halted) {
        setMessage({ type: 'warning', text: `Cycle skipped — trader is halted: ${d.errors?.[0] || ''}` });
      } else {
        setMessage({
          type: 'success',
          text: `Cycle complete — ${d.entries_executed} entries, ${d.exits_processed} exits, ${d.portfolio_exposure_pct?.toFixed(1)}% exposure`
        });
      }
      await fetchAll();
    } catch (e) {
      setMessage({ type: 'error', text: 'Cycle failed: ' + (e.response?.data?.detail || e.message) });
    } finally {
      setCycleRunning(false);
    }
  };

  const haltTrader = async () => {
    try {
      await apiClient.post(`${API}/halt`, { reason: 'manual — operator stop' });
      setMessage({ type: 'warning', text: '🛑 Trader halted. Open positions will run to natural exit.' });
      await fetchAll();
    } catch (e) {
      setMessage({ type: 'error', text: 'Halt failed: ' + (e.response?.data?.detail || e.message) });
    }
  };

  const resumeTrader = async () => {
    try {
      await apiClient.post(`${API}/resume`);
      setMessage({ type: 'success', text: '▶️ Trader resumed.' });
      await fetchAll();
    } catch (e) {
      setMessage({ type: 'error', text: 'Resume failed: ' + (e.response?.data?.detail || e.message) });
    }
  };

  // ── Derived state ──────────────────────────────────────────────────────────

  const isHalted = status?.is_halted;
  const isActive = status?.active;
  const cb = status?.circuit_breakers;
  const dailyWarning = cb && Math.abs(status.daily_pnl_pct) >= cb.max_daily_loss_pct * 0.7;
  const totalWarning = cb && Math.abs(status.total_pnl_pct) >= cb.max_total_loss_pct * 0.7;

  // ── Render helpers ─────────────────────────────────────────────────────────

  const PnlBadge = ({ value, suffix = '%' }) => {
    const pos = value >= 0;
    return (
      <span className={`font-semibold ${pos ? 'text-green-600' : 'text-red-600'}`}>
        {pos ? '+' : ''}{value?.toFixed(2)}{suffix}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <RefreshCw className="w-6 h-6 text-indigo-500 animate-spin" />
        <span className="ml-2 text-gray-500">Loading trader...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">

      {/* ── Header ── */}
      <div className={`rounded-lg p-6 text-white ${isHalted ? 'bg-gradient-to-r from-red-600 to-red-800' : 'bg-gradient-to-r from-indigo-600 to-purple-700'}`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <Bot className="w-7 h-7" />
              <h1 className="text-2xl font-bold">Paper Trader</h1>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${isHalted ? 'bg-red-200 text-red-900' : isActive ? 'bg-green-200 text-green-900' : 'bg-gray-200 text-gray-700'}`}>
                {isHalted ? '🛑 HALTED' : isActive ? '● ACTIVE' : '○ NO STRATEGY'}
              </span>
            </div>
            {isActive && (
              <p className="text-indigo-200 text-sm">
                {status.variant_name} v{status.variant_version}
                {status.activated_at && ` · running since ${new Date(status.activated_at).toLocaleDateString()}`}
              </p>
            )}
            {isHalted && status.halted_reason && (
              <p className="text-red-200 text-sm mt-1">Reason: {status.halted_reason}</p>
            )}
            {!isActive && !isHalted && (
              <p className="text-gray-300 text-sm">No active strategy. Go to Strategy Config → activate a variant as Paper.</p>
            )}
          </div>
          <div className="text-right">
            {performance && (
              <div>
                <div className={`text-3xl font-bold ${(performance.total_pnl || 0) >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                  {(performance.total_pnl || 0) >= 0 ? '+' : ''}${(performance.total_pnl || 0).toFixed(2)}
                </div>
                <div className="text-indigo-200 text-sm">total P&L this period</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Message Banner ── */}
      {message && (
        <div className={`p-4 rounded-lg flex items-center space-x-3 border ${
          message.type === 'success' ? 'bg-green-50 border-green-200 text-green-800' :
          message.type === 'warning' ? 'bg-yellow-50 border-yellow-200 text-yellow-800' :
          'bg-red-50 border-red-200 text-red-800'
        }`}>
          {message.type === 'success' ? <CheckCircle className="w-5 h-5 flex-shrink-0" /> :
           message.type === 'warning' ? <AlertTriangle className="w-5 h-5 flex-shrink-0" /> :
           <XCircle className="w-5 h-5 flex-shrink-0" />}
          <span className="text-sm">{message.text}</span>
          <button onClick={() => setMessage(null)} className="ml-auto text-gray-400 hover:text-gray-600">✕</button>
        </div>
      )}

      {/* ── Operator Controls ── */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3 flex items-center space-x-1">
          <Shield className="w-4 h-4" />
          <span>Operator Controls</span>
        </h2>
        <div className="flex flex-wrap gap-3">
          {/* STOP */}
          <button
            onClick={haltTrader}
            disabled={isHalted || !isActive}
            className="flex items-center space-x-2 px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            <Square className="w-4 h-4" />
            <span>STOP EVERYTHING</span>
          </button>

          {/* RESUME */}
          <button
            onClick={resumeTrader}
            disabled={!isHalted}
            className="flex items-center space-x-2 px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            <Play className="w-4 h-4" />
            <span>RESUME</span>
          </button>

          {/* RUN CYCLE */}
          <button
            onClick={runCycle}
            disabled={cycleRunning || isHalted || !isActive}
            className="flex items-center space-x-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {cycleRunning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            <span>{cycleRunning ? 'Running...' : 'Run Cycle'}</span>
          </button>

          {/* REFRESH */}
          <button
            onClick={fetchAll}
            className="flex items-center space-x-2 px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* ── Circuit Breakers ── */}
      {status && isActive && cb && (
        <div className={`rounded-lg border p-4 ${(cb.daily_breaker_triggered || cb.total_breaker_triggered) ? 'bg-red-50 border-red-300' : dailyWarning || totalWarning ? 'bg-yellow-50 border-yellow-300' : 'bg-white border-gray-200'}`}>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3 flex items-center space-x-1">
            <Activity className="w-4 h-4" />
            <span>Circuit Breakers</span>
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-gray-500">Daily P&L</p>
              <p className={`text-xl font-bold ${status.daily_pnl_pct >= 0 ? 'text-green-600' : dailyWarning ? 'text-red-600' : 'text-orange-600'}`}>
                <PnlBadge value={status.daily_pnl_pct} />
              </p>
              <p className="text-xs text-gray-400">limit: -{cb.max_daily_loss_pct}%</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Total P&L</p>
              <p className="text-xl font-bold">
                <PnlBadge value={status.total_pnl_pct} />
              </p>
              <p className="text-xs text-gray-400">limit: -{cb.max_total_loss_pct}%</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Open Positions</p>
              <p className="text-xl font-bold text-gray-900">{status.open_positions}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Breaker Status</p>
              <p className={`text-sm font-semibold mt-1 ${(cb.daily_breaker_triggered || cb.total_breaker_triggered) ? 'text-red-600' : 'text-green-600'}`}>
                {(cb.daily_breaker_triggered || cb.total_breaker_triggered) ? '🔴 TRIGGERED' : '🟢 Normal'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ── Performance Summary ── */}
      {performance && performance.total_trades > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Total Trades', value: performance.total_trades, icon: <BarChart3 className="w-6 h-6 text-blue-500" /> },
            { label: 'Win Rate', value: `${((performance.win_rate || 0) * 100).toFixed(1)}%`, icon: <Target className="w-6 h-6 text-purple-500" /> },
            { label: 'Total P&L', value: `${(performance.total_pnl || 0) >= 0 ? '+' : ''}$${(performance.total_pnl || 0).toFixed(2)}`, icon: (performance.total_pnl || 0) >= 0 ? <TrendingUp className="w-6 h-6 text-green-500" /> : <TrendingDown className="w-6 h-6 text-red-500" />, color: (performance.total_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600' },
            { label: 'Return %', value: `${(performance.total_return_pct || 0) >= 0 ? '+' : ''}${(performance.total_return_pct || 0).toFixed(2)}%`, icon: <DollarSign className="w-6 h-6 text-indigo-500" />, color: (performance.total_return_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600' },
          ].map(({ label, value, icon, color }) => (
            <div key={label} className="bg-white rounded-lg border border-gray-200 p-4 flex items-center space-x-3">
              {icon}
              <div>
                <p className="text-xs text-gray-500">{label}</p>
                <p className={`text-xl font-bold ${color || 'text-gray-900'}`}>{value}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Open Positions ── */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-4 border-b border-gray-100 flex items-center space-x-2">
          <Eye className="w-5 h-5 text-indigo-500" />
          <h3 className="font-semibold text-gray-800">Open Positions ({positions.length})</h3>
        </div>
        {positions.length === 0 ? (
          <div className="p-8 text-center text-gray-400 text-sm">
            {!isActive ? 'Activate a strategy variant from Strategy Config to start trading.' :
             isHalted ? 'Trader is halted. Resume to allow new entries.' :
             'No open positions. Run a cycle to scan for signals.'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                <tr>
                  {['Symbol', 'Strategy', 'Entry $', 'Shares', 'AI Score', 'Target', 'Stop', 'Age', 'Value'].map(h => (
                    <th key={h} className="px-4 py-2 text-left font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {positions.map(p => {
                  const ageMs = p.entry_time ? Date.now() - new Date(p.entry_time).getTime() : 0;
                  const ageDays = Math.floor(ageMs / 86400000);
                  return (
                    <tr key={p.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-semibold text-gray-900">{p.symbol}</td>
                      <td className="px-4 py-3 text-gray-500 capitalize text-xs">{p.strategy}</td>
                      <td className="px-4 py-3">${p.entry_price?.toFixed(2)}</td>
                      <td className="px-4 py-3">{p.shares?.toFixed(2)}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${p.ai_score >= 75 ? 'bg-green-100 text-green-700' : p.ai_score >= 60 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                          {p.ai_score ?? '—'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-green-600 text-xs">+{p.profit_target_pct?.toFixed(1)}%</td>
                      <td className="px-4 py-3 text-red-600 text-xs">-{p.stop_loss_pct?.toFixed(1)}%</td>
                      <td className="px-4 py-3 text-gray-400 text-xs">{ageDays}d</td>
                      <td className="px-4 py-3 font-medium">${p.position_usd?.toFixed(0)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Closed Trade History ── */}
      <div className="bg-white rounded-lg border border-gray-200">
        <button
          className="w-full p-4 border-b border-gray-100 flex items-center justify-between"
          onClick={() => setShowHistory(h => !h)}
        >
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-gray-400" />
            <h3 className="font-semibold text-gray-800">Closed Trades ({history.length})</h3>
          </div>
          {showHistory ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
        </button>
        {showHistory && (
          history.length === 0 ? (
            <div className="p-6 text-center text-gray-400 text-sm">No closed trades yet for this strategy period.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                  <tr>
                    {['Symbol', 'Strategy', 'Entry', 'Exit', 'Return', 'P&L', 'Exit Reason', 'Date'].map(h => (
                      <th key={h} className="px-4 py-2 text-left font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {history.map(t => (
                    <tr key={t.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-semibold text-gray-900">{t.symbol}</td>
                      <td className="px-4 py-3 text-gray-500 text-xs capitalize">{t.strategy}</td>
                      <td className="px-4 py-3">${t.entry_price?.toFixed(2)}</td>
                      <td className="px-4 py-3">${t.exit_price?.toFixed(2)}</td>
                      <td className={`px-4 py-3 font-medium ${(t.return_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {t.return_pct != null ? `${t.return_pct >= 0 ? '+' : ''}${t.return_pct.toFixed(2)}%` : '—'}
                      </td>
                      <td className={`px-4 py-3 font-medium ${(t.profit_loss_usd || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {t.profit_loss_usd != null ? `${t.profit_loss_usd >= 0 ? '+' : ''}$${t.profit_loss_usd.toFixed(2)}` : '—'}
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs capitalize">{t.exit_reason?.replace(/_/g, ' ') || '—'}</td>
                      <td className="px-4 py-3 text-gray-400 text-xs">{t.exit_time ? new Date(t.exit_time).toLocaleDateString() : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>
    </div>
  );
}
