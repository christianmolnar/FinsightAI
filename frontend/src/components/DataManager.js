/**
 * DataManager — Historical Data Status + Update Trigger
 *
 * Shows DB freshness (symbol count, date range, gap in days)
 * and lets the operator trigger an incremental update.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Database, RefreshCw, CheckCircle, AlertTriangle,
  Calendar, BarChart3, Clock, Play, Plus
} from 'lucide-react';
import { apiClient } from '../utils/apiClient';

export default function DataManager() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [triggering, setTriggering] = useState(false);
  const [expanding, setExpanding] = useState(false);
  const [expandStatus, setExpandStatus] = useState(null);
  const [pollInterval, setPollInterval] = useState(null);

  const fetchStatus = useCallback(async () => {
    try {
      const resp = await apiClient.get('/api/data/status');
      setStatus(resp.data);
      setError(null);
    } catch (e) {
      setError('Failed to load data status: ' + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Poll every 5 seconds while an update or expansion is running
  useEffect(() => {
    if (status?.update?.running || expandStatus?.running) {
      const id = setInterval(() => {
        fetchStatus();
        if (expandStatus?.running) {
          apiClient.get('/api/data/expand-universe/status')
            .then(r => setExpandStatus(r.data))
            .catch(() => {});
        }
      }, 5000);
      setPollInterval(id);
    } else if (pollInterval) {
      clearInterval(pollInterval);
      setPollInterval(null);
    }
    return () => { if (pollInterval) clearInterval(pollInterval); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status?.update?.running, expandStatus?.running]);

  const triggerUpdate = async () => {
    setTriggering(true);
    try {
      await apiClient.post('/api/data/update');
      await fetchStatus();
    } catch (e) {
      setError('Failed to start update: ' + (e.response?.data?.detail || e.message));
    } finally {
      setTriggering(false);
    }
  };

  const triggerExpand = async () => {
    setExpanding(true);
    try {
      const resp = await apiClient.post('/api/data/expand-universe');
      setExpandStatus(resp.data.state || { running: true, message: resp.data.message, done: 0, total: 221 });
    } catch (e) {
      setError('Failed to start expansion: ' + (e.response?.data?.detail || e.message));
    } finally {
      setExpanding(false);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center min-h-64">
      <RefreshCw className="w-6 h-6 text-indigo-500 animate-spin" />
      <span className="ml-2 text-gray-500">Loading data status...</span>
    </div>
  );

  const s = status || {};
  const update = s.update || {};
  const gapDays = s.gap_days ?? null;
  const isFresh = s.is_fresh;
  const isRunning = update.running;

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">

      {/* Header */}
      <div className="bg-gradient-to-r from-gray-700 to-gray-900 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <Database className="w-7 h-7" />
              <h1 className="text-2xl font-bold">Historical Data</h1>
            </div>
            <p className="text-gray-400 text-sm">Manage market data used by the backtester and live scanner</p>
          </div>
          <button onClick={fetchStatus} className="flex items-center space-x-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-sm">
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Symbols', value: s.symbol_count ?? '—', icon: <BarChart3 className="w-5 h-5 text-indigo-500" /> },
          { label: 'Total Bars', value: s.total_bars != null ? s.total_bars.toLocaleString() : '—', icon: <Database className="w-5 h-5 text-blue-500" /> },
          { label: 'Earliest Date', value: s.earliest_date ?? '—', icon: <Calendar className="w-5 h-5 text-gray-500" /> },
          { label: 'Latest Date', value: s.latest_date ?? '—', icon: <Calendar className="w-5 h-5 text-gray-500" /> },
        ].map(({ label, value, icon }) => (
          <div key={label} className="bg-white rounded-lg border border-gray-200 p-4 flex items-center space-x-3">
            {icon}
            <div>
              <p className="text-xs text-gray-500">{label}</p>
              <p className="font-bold text-gray-900 text-sm">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Freshness banner */}
      <div className={`rounded-lg p-4 flex items-center justify-between ${
        isFresh ? 'bg-green-50 border border-green-200' : 'bg-amber-50 border border-amber-200'
      }`}>
        <div className="flex items-center space-x-3">
          {isFresh
            ? <CheckCircle className="w-5 h-5 text-green-600" />
            : <AlertTriangle className="w-5 h-5 text-amber-600" />}
          <div>
            <p className={`font-medium ${isFresh ? 'text-green-800' : 'text-amber-800'}`}>
              {isFresh
                ? 'Data is fresh'
                : `Data is ${gapDays ?? '?'} calendar days behind — last bar: ${s.latest_date}`}
            </p>
            <p className={`text-xs mt-0.5 ${isFresh ? 'text-green-600' : 'text-amber-600'}`}>
              {isFresh
                ? 'Backtests will use up-to-date market data.'
                : 'Run an update to bring data current. Backtests may miss recent price action.'}
            </p>
          </div>
        </div>
        {!isFresh && !isRunning && (
          <button
            onClick={triggerUpdate}
            disabled={triggering}
            className="flex items-center space-x-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
          >
            {triggering ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            <span>Update Now</span>
          </button>
        )}
      </div>

      {/* Update progress */}
      {isRunning && (
        <div className="bg-white rounded-lg border border-indigo-200 p-5">
          <div className="flex items-center space-x-3 mb-4">
            <RefreshCw className="w-5 h-5 text-indigo-600 animate-spin" />
            <h2 className="font-semibold text-gray-800">Update in progress…</h2>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>{update.symbols_done} / {update.symbols_total} symbols</span>
              <span>{update.progress_pct ?? 0}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${update.progress_pct ?? 0}%` }}
              />
            </div>
            <p className="text-xs text-gray-500">
              {update.new_bars?.toLocaleString() ?? 0} new bars added · {update.errors ?? 0} errors
            </p>
          </div>
        </div>
      )}

      {/* Last update result */}
      {!isRunning && update.last_result && !update.last_result.error && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="w-4 h-4 text-gray-400" />
            <h3 className="font-medium text-gray-700 text-sm">Last Update</h3>
          </div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div><p className="text-gray-400 text-xs">Symbols updated</p><p className="font-semibold">{update.last_result.symbols_updated}</p></div>
            <div><p className="text-gray-400 text-xs">New bars</p><p className="font-semibold">{update.last_result.new_bars?.toLocaleString()}</p></div>
            <div><p className="text-gray-400 text-xs">Completed</p><p className="font-semibold text-xs">{update.last_result.completed_at ? new Date(update.last_result.completed_at).toLocaleString() : '—'}</p></div>
          </div>
        </div>
      )}

      {/* Expand Universe */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="font-semibold text-gray-800">Expand Universe</h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Add 221 missing symbols: full S&P 500 + 11 sector ETFs (XLK, XLF…) + 11 commodity ETFs (GLD, SLV, USO…)
            </p>
          </div>
          <button
            onClick={triggerExpand}
            disabled={expanding || expandStatus?.running}
            className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 ml-4 flex-shrink-0"
          >
            {expanding || expandStatus?.running
              ? <RefreshCw className="w-4 h-4 animate-spin" />
              : <Plus className="w-4 h-4" />}
            <span>{expandStatus?.running ? 'Running…' : 'Add 221 Symbols'}</span>
          </button>
        </div>

        {expandStatus && (
          <div className="mt-3 space-y-2">
            {expandStatus.running && (
              <>
                <div className="flex justify-between text-sm text-gray-600">
                  <span>{expandStatus.done ?? 0} / {expandStatus.total ?? 221} symbols</span>
                  <span>{expandStatus.progress_pct ?? 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${expandStatus.progress_pct ?? 0}%` }} />
                </div>
              </>
            )}
            <p className={`text-xs ${expandStatus.running ? 'text-gray-500' : 'text-green-700 font-medium'}`}>
              {expandStatus.message}
            </p>
            {!expandStatus.running && expandStatus.bars > 0 && (
              <p className="text-xs text-gray-500">{(expandStatus.bars).toLocaleString()} bars added · {expandStatus.errors} errors</p>
            )}
          </div>
        )}
      </div>

      {/* Info box */}
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-5">
        <h3 className="font-medium text-gray-700 mb-3">What's in the database</h3>
        <div className="space-y-2 text-sm text-gray-600">
          <p>📈 <strong>409–630 US equities</strong> — S&P 500 + NASDAQ 100. Use "Add 221 Symbols" above to expand to full S&P 500.</p>
          <p>📊 <strong>Sector ETFs</strong> — XLK, XLF, XLE, XLV, XLI, XLY, XLP, XLU, XLB, XLRE, XLC (after expansion)</p>
          <p>🪙 <strong>Commodity ETFs</strong> — GLD, SLV, USO, GDX, CORN, WEAT and more (after expansion)</p>
          <p>📅 <strong>10 years of daily OHLCV</strong> — sourced from Yahoo Finance (free)</p>
          <p>🔄 <strong>Auto-updates daily</strong> — Mon–Fri at 6:30 PM ET via the built-in scheduler</p>
        </div>
      </div>
    </div>
  );
}
