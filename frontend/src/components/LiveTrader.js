/**
 * LiveTrader — Autonomous Live Trading Monitor (Phase F.7)
 *
 * Identical layout to PaperTrader but mode='live'.
 * Adds a "Promote Strategy" button to promote the current paper strategy to live.
 *
 * Real money is at risk in this view. All the same operator controls apply.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity, AlertTriangle, BarChart3, Bot, CheckCircle,
  ChevronDown, ChevronUp, Clock, DollarSign, Eye,
  Play, RefreshCw, Shield, Square, Target,
  TrendingDown, TrendingUp, XCircle, Zap, ArrowUpCircle
} from 'lucide-react';
import { apiClient } from '../utils/apiClient';

const MODE = 'live';
const API = `/api/trader/${MODE}`;

export default function LiveTrader() {
  const [status, setStatus] = useState(null);
  const [positions, setPositions] = useState([]);
  const [history, setHistory] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cycleRunning, setCycleRunning] = useState(false);
  const [message, setMessage] = useState(null);
  const [showHistory, setShowHistory] = useState(true);
  const [showPromoteModal, setShowPromoteModal] = useState(false);
  const [paperVariants, setPaperVariants] = useState([]);
  const [promoting, setPromoting] = useState(false);

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
      setMessage({ type: 'error', text: 'Failed to load live trader: ' + (e.response?.data?.detail || e.message) });
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
      setMessage({ type: d.halted ? 'warning' : 'success', text: d.halted ? `Halted: ${d.errors?.[0]}` : `Cycle: ${d.entries_executed} entries, ${d.exits_processed} exits` });
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
      setMessage({ type: 'warning', text: '🛑 Live trader halted.' });
      await fetchAll();
    } catch (e) {
      setMessage({ type: 'error', text: 'Halt failed: ' + (e.response?.data?.detail || e.message) });
    }
  };

  const resumeTrader = async () => {
    try {
      await apiClient.post(`${API}/resume`);
      setMessage({ type: 'success', text: '▶️ Live trader resumed.' });
      await fetchAll();
    } catch (e) {
      setMessage({ type: 'error', text: 'Resume failed: ' + (e.response?.data?.detail || e.message) });
    }
  };

  const openPromoteModal = async () => {
    try {
      const res = await apiClient.get('/api/strategy-variants?mode=paper&is_active=true');
      setPaperVariants(res.data || []);
      setShowPromoteModal(true);
    } catch (e) {
      setMessage({ type: 'error', text: 'Could not load paper variants: ' + e.message });
    }
  };

  const promoteToLive = async (variantId) => {
    setPromoting(true);
    try {
      const res = await apiClient.post(`/api/strategy-variants/${variantId}/promote-to-live`);
      setMessage({ type: 'success', text: `✅ Strategy promoted to live: ${res.data.live_variant?.name}` });
      setShowPromoteModal(false);
      await fetchAll();
    } catch (e) {
      setMessage({ type: 'error', text: 'Promotion failed: ' + (e.response?.data?.detail || e.message) });
    } finally {
      setPromoting(false);
    }
  };

  const isHalted = status?.is_halted;
  const isActive = status?.active;
  const cb = status?.circuit_breakers;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <RefreshCw className="w-6 h-6 text-red-500 animate-spin" />
        <span className="ml-2 text-gray-500">Loading live trader...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">

      {/* ── Real Money Warning Banner ── */}
      <div className="bg-amber-50 border-2 border-amber-400 rounded-lg p-4 flex items-center space-x-3">
        <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0" />
        <div>
          <p className="font-semibold text-amber-900">Real Money</p>
          <p className="text-sm text-amber-700">This trader executes with real Alpaca funds. Only promote a strategy after sufficient paper validation.</p>
        </div>
      </div>

      {/* ── Header ── */}
      <div className={`rounded-lg p-6 text-white ${isHalted ? 'bg-gradient-to-r from-red-700 to-red-900' : 'bg-gradient-to-r from-slate-700 to-slate-900'}`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <Bot className="w-7 h-7" />
              <h1 className="text-2xl font-bold">Live Trader</h1>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${isHalted ? 'bg-red-200 text-red-900' : isActive ? 'bg-green-200 text-green-900' : 'bg-gray-200 text-gray-700'}`}>
                {isHalted ? '🛑 HALTED' : isActive ? '● ACTIVE' : '○ NO STRATEGY'}
              </span>
            </div>
            {isActive && (
              <p className="text-gray-300 text-sm">
                {status.variant_name} v{status.variant_version}
                {status.activated_at && ` · live since ${new Date(status.activated_at).toLocaleDateString()}`}
              </p>
            )}
            {!isActive && (
              <p className="text-gray-400 text-sm">No live strategy active. Promote a validated paper strategy to begin live trading.</p>
            )}
          </div>
          <div className="text-right space-y-2">
            {performance && (
              <div>
                <div className={`text-3xl font-bold ${(performance.total_pnl || 0) >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                  {(performance.total_pnl || 0) >= 0 ? '+' : ''}${(performance.total_pnl || 0).toFixed(2)}
                </div>
                <div className="text-gray-400 text-sm">live P&L this period</div>
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
          <button onClick={haltTrader} disabled={isHalted || !isActive}
            className="flex items-center space-x-2 px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold disabled:opacity-40 transition-colors shadow-sm">
            <Square className="w-4 h-4" /><span>STOP EVERYTHING</span>
          </button>
          <button onClick={resumeTrader} disabled={!isHalted}
            className="flex items-center space-x-2 px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold disabled:opacity-40 transition-colors shadow-sm">
            <Play className="w-4 h-4" /><span>RESUME</span>
          </button>
          <button onClick={runCycle} disabled={cycleRunning || isHalted || !isActive}
            className="flex items-center space-x-2 px-5 py-2.5 bg-slate-700 hover:bg-slate-800 text-white rounded-lg font-medium disabled:opacity-40 transition-colors">
            {cycleRunning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            <span>{cycleRunning ? 'Running...' : 'Run Cycle'}</span>
          </button>
          <button onClick={openPromoteModal}
            className="flex items-center space-x-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-600 text-white rounded-lg font-medium transition-colors">
            <ArrowUpCircle className="w-4 h-4" /><span>Promote Strategy from Paper</span>
          </button>
          <button onClick={fetchAll}
            className="flex items-center space-x-2 px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors">
            <RefreshCw className="w-4 h-4" /><span>Refresh</span>
          </button>
        </div>
      </div>

      {/* ── Circuit Breakers ── */}
      {status && isActive && cb && (
        <div className={`rounded-lg border p-4 ${(cb.daily_breaker_triggered || cb.total_breaker_triggered) ? 'bg-red-50 border-red-300' : 'bg-white border-gray-200'}`}>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3 flex items-center space-x-1">
            <Activity className="w-4 h-4" /><span>Circuit Breakers</span>
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div><p className="text-xs text-gray-500">Daily P&L</p><p className={`text-xl font-bold ${status.daily_pnl_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>{status.daily_pnl_pct >= 0 ? '+' : ''}{status.daily_pnl_pct?.toFixed(2)}%</p><p className="text-xs text-gray-400">limit: -{cb.max_daily_loss_pct}%</p></div>
            <div><p className="text-xs text-gray-500">Total P&L</p><p className={`text-xl font-bold ${status.total_pnl_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>{status.total_pnl_pct >= 0 ? '+' : ''}{status.total_pnl_pct?.toFixed(2)}%</p><p className="text-xs text-gray-400">limit: -{cb.max_total_loss_pct}%</p></div>
            <div><p className="text-xs text-gray-500">Open Positions</p><p className="text-xl font-bold text-gray-900">{status.open_positions}</p></div>
            <div><p className="text-xs text-gray-500">Status</p><p className={`text-sm font-semibold mt-1 ${(cb.daily_breaker_triggered || cb.total_breaker_triggered) ? 'text-red-600' : 'text-green-600'}`}>{(cb.daily_breaker_triggered || cb.total_breaker_triggered) ? '🔴 TRIGGERED' : '🟢 Normal'}</p></div>
          </div>
        </div>
      )}

      {/* ── Open Positions ── */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-4 border-b border-gray-100 flex items-center space-x-2">
          <Eye className="w-5 h-5 text-slate-500" />
          <h3 className="font-semibold text-gray-800">Live Positions ({positions.length})</h3>
        </div>
        {positions.length === 0 ? (
          <div className="p-8 text-center text-gray-400 text-sm">
            {!isActive ? 'Promote a paper strategy to start live trading.' : 'No open live positions.'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                <tr>{['Symbol', 'Strategy', 'Entry $', 'Shares', 'AI Score', 'Target', 'Stop', 'Age', 'Value'].map(h => <th key={h} className="px-4 py-2 text-left font-medium">{h}</th>)}</tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {positions.map(p => {
                  const ageDays = p.entry_time ? Math.floor((Date.now() - new Date(p.entry_time)) / 86400000) : 0;
                  return (
                    <tr key={p.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-semibold">{p.symbol}</td>
                      <td className="px-4 py-3 text-gray-500 text-xs capitalize">{p.strategy}</td>
                      <td className="px-4 py-3">${p.entry_price?.toFixed(2)}</td>
                      <td className="px-4 py-3">{p.shares?.toFixed(2)}</td>
                      <td className="px-4 py-3"><span className={`px-2 py-0.5 rounded-full text-xs font-medium ${p.ai_score >= 75 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>{p.ai_score ?? '—'}</span></td>
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

      {/* ── History ── */}
      <div className="bg-white rounded-lg border border-gray-200">
        <button className="w-full p-4 border-b border-gray-100 flex items-center justify-between" onClick={() => setShowHistory(h => !h)}>
          <div className="flex items-center space-x-2"><Clock className="w-5 h-5 text-gray-400" /><h3 className="font-semibold text-gray-800">Closed Trades ({history.length})</h3></div>
          {showHistory ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
        </button>
        {showHistory && (history.length === 0 ? <div className="p-6 text-center text-gray-400 text-sm">No closed trades yet.</div> : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-xs text-gray-500 uppercase"><tr>{['Symbol', 'Strategy', 'Entry', 'Exit', 'Return', 'P&L', 'Reason', 'Date'].map(h => <th key={h} className="px-4 py-2 text-left font-medium">{h}</th>)}</tr></thead>
              <tbody className="divide-y divide-gray-100">
                {history.map(t => (
                  <tr key={t.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-semibold">{t.symbol}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs capitalize">{t.strategy}</td>
                    <td className="px-4 py-3">${t.entry_price?.toFixed(2)}</td>
                    <td className="px-4 py-3">${t.exit_price?.toFixed(2)}</td>
                    <td className={`px-4 py-3 font-medium ${(t.return_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>{t.return_pct != null ? `${t.return_pct >= 0 ? '+' : ''}${t.return_pct.toFixed(2)}%` : '—'}</td>
                    <td className={`px-4 py-3 font-medium ${(t.profit_loss_usd || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>{t.profit_loss_usd != null ? `${t.profit_loss_usd >= 0 ? '+' : ''}$${t.profit_loss_usd.toFixed(2)}` : '—'}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs capitalize">{t.exit_reason?.replace(/_/g, ' ') || '—'}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{t.exit_time ? new Date(t.exit_time).toLocaleDateString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      {/* ── Promote Modal ── */}
      {showPromoteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center space-x-3">
              <ArrowUpCircle className="w-6 h-6 text-amber-500" />
              <h2 className="text-xl font-bold text-gray-900">Promote Strategy to Live</h2>
            </div>
            <div className="bg-amber-50 border border-amber-300 rounded-lg p-3 text-sm text-amber-800">
              ⚠️ This will start trading with <strong>real money</strong> using the selected strategy. Ensure you have validated it sufficiently on paper first.
            </div>
            {paperVariants.length === 0 ? (
              <p className="text-gray-500 text-sm">No active paper strategy found. Activate a strategy variant from Strategy Config first.</p>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-gray-600">Select the paper strategy to promote:</p>
                {paperVariants.map(v => (
                  <div key={v.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-semibold text-gray-900">{v.name} v{v.version}</p>
                        <p className="text-xs text-gray-500">
                          Active since {v.activated_at ? new Date(v.activated_at).toLocaleDateString() : 'unknown'}
                          {v.backtest_return_pct != null && ` · Backtest: ${v.backtest_return_pct > 0 ? '+' : ''}${v.backtest_return_pct.toFixed(1)}%`}
                        </p>
                      </div>
                      <button
                        onClick={() => promoteToLive(v.id)}
                        disabled={promoting}
                        className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
                      >
                        {promoting ? 'Promoting...' : 'Promote'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="flex justify-end">
              <button onClick={() => setShowPromoteModal(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
