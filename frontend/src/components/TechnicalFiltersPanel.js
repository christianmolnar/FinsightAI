import React, { useState } from 'react';
import { BarChart3, TrendingUp, Activity, Volume2, Target, Zap } from 'lucide-react';

const TechnicalFiltersPanel = ({ technicalFilters, setTechnicalFilters, onSave }) => {
  const ParameterSlider = ({ param, value, onChange, label, suffix = '' }) => (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-sm font-semibold text-gray-900">
          {typeof value === 'number' ? 
            (value >= 1000 ? (value / 1000).toFixed(0) + 'K' : value.toFixed(value < 10 ? 1 : 0)) 
            : value}{suffix}
        </span>
      </div>
      <input
        type="range"
        min={param.min}
        max={param.max}
        step={param.max > 1000 ? 50000 : param.max > 10 ? 1 : 0.1}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
      />
      <p className="text-xs text-gray-500 mt-1">{param.description}</p>
    </div>
  );

  const filterCategories = [
    {
      title: "Signal Strength",
      icon: Zap,
      color: "yellow",
      filters: ['minRequiredFilters']
    },
    {
      title: "Momentum Indicators", 
      icon: TrendingUp,
      color: "green",
      filters: ['rsiMin', 'rsiMax']
    },
    {
      title: "Volume Analysis",
      icon: Volume2, 
      color: "blue",
      filters: ['minVolume', 'volumeMultiplier']
    },
    {
      title: "Trend Confirmation",
      icon: Activity,
      color: "purple", 
      filters: ['ma200Distance']
    }
  ];

  const getFilterSuffix = (key) => {
    if (key.includes('Percent') || key.includes('Distance') || key.includes('rsi')) return '%';
    if (key.includes('Volume') && !key.includes('Multiplier')) return '';
    if (key.includes('Multiplier')) return 'x';
    return '';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Technical Filters</h2>
              <p className="text-gray-600">Configure technical analysis confirmations for trade entry</p>
            </div>
          </div>
          <button
            onClick={onSave}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <Target className="w-4 h-4" />
            <span>Save Filters</span>
          </button>
        </div>
      </div>

      <div className="p-6">
        {filterCategories.map(({ title, icon: Icon, color, filters }) => (
          <div key={title} className="mb-8">
            <div className="flex items-center space-x-2 mb-4">
              <Icon className={`w-6 h-6 text-${color}-600`} />
              <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filters.map((key) => (
                <div key={key} className="bg-gray-50 rounded-lg p-4">
                  <ParameterSlider
                    param={technicalFilters[key]}
                    value={technicalFilters[key].value}
                    label={key.split(/(?=[A-Z])/).join(' ').replace(/^\w/, c => c.toUpperCase())}
                    suffix={getFilterSuffix(key)}
                    onChange={(value) => setTechnicalFilters(prev => ({
                      ...prev,
                      [key]: { ...prev[key], value }
                    }))}
                  />
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* Technical Analysis Summary */}
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <BarChart3 className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-900">Technical Analysis Summary</h4>
              <p className="text-blue-800 text-sm mt-1">
                Requiring <strong>{technicalFilters.minRequiredFilters.value}</strong> out of 5 technical confirmations. 
                RSI range: <strong>{technicalFilters.rsiMin.value} - {technicalFilters.rsiMax.value}</strong>. 
                Minimum volume: <strong>{(technicalFilters.minVolume.value / 1000).toFixed(0)}K shares</strong>.
              </p>
              <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="font-medium text-blue-900">Signal Strength:</span>
                  <div className="text-blue-700">
                    {technicalFilters.minRequiredFilters.value >= 4 ? 'Very High' : 
                     technicalFilters.minRequiredFilters.value >= 3 ? 'High' : 
                     technicalFilters.minRequiredFilters.value >= 2 ? 'Medium' : 'Low'}
                  </div>
                </div>
                <div>
                  <span className="font-medium text-blue-900">Volume Threshold:</span>
                  <div className="text-blue-700">{technicalFilters.volumeMultiplier.value}x Average</div>
                </div>
                <div>
                  <span className="font-medium text-blue-900">Trend Filter:</span>
                  <div className="text-blue-700">{technicalFilters.ma200Distance.value}% above MA200</div>
                </div>
                <div>
                  <span className="font-medium text-blue-900">RSI Range:</span>
                  <div className="text-blue-700">
                    {technicalFilters.rsiMax.value - technicalFilters.rsiMin.value} point range
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Filter Quality Assessment */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {Math.round(((technicalFilters.minRequiredFilters.value / 5) + 
                          (technicalFilters.volumeMultiplier.value / 3) + 
                          (technicalFilters.ma200Distance.value / 15)) * 33)}%
            </div>
            <div className="text-sm text-green-700">Filter Strength</div>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {Math.round(100 - (technicalFilters.minRequiredFilters.value / 5) * 60)}%
            </div>
            <div className="text-sm text-blue-700">Trade Frequency</div>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {Math.round(40 + (technicalFilters.minRequiredFilters.value / 5) * 30)}%
            </div>
            <div className="text-sm text-purple-700">Expected Win Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TechnicalFiltersPanel;
