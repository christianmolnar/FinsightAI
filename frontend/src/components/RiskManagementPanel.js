import React, { useState } from 'react';
import { Shield, AlertTriangle, TrendingDown, DollarSign, Target, BarChart3 } from 'lucide-react';

const RiskManagementPanel = ({ riskManagement, setRiskManagement, onSave }) => {
  const ParameterSlider = ({ param, value, onChange, label, suffix = '%' }) => (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-sm font-semibold text-gray-900">
          {typeof value === 'number' ? value.toFixed(value < 10 ? 1 : 0) : value}{suffix}
        </span>
      </div>
      <input
        type="range"
        min={param.min}
        max={param.max}
        step={param.max > 10 ? 1 : 0.1}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
      />
      <p className="text-xs text-gray-500 mt-1">{param.description}</p>
    </div>
  );

  const riskLevels = [
    { key: 'maxSinglePosition', icon: Target, color: 'blue' },
    { key: 'maxSectorExposure', icon: BarChart3, color: 'green' },
    { key: 'maxDrawdown', icon: TrendingDown, color: 'red' },
    { key: 'dailyLossLimit', icon: AlertTriangle, color: 'orange' },
    { key: 'vixThreshold', icon: Shield, color: 'purple' },
    { key: 'consecutiveLossLimit', icon: DollarSign, color: 'indigo' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Shield className="w-8 h-8 text-red-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Risk Management</h2>
              <p className="text-gray-600">Configure portfolio risk controls and safety limits</p>
            </div>
          </div>
          <button
            onClick={onSave}
            className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            <Shield className="w-4 h-4" />
            <span>Save Risk Settings</span>
          </button>
        </div>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {riskLevels.map(({ key, icon: Icon, color }) => (
            <div key={key} className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-4">
                <Icon className={`w-5 h-5 text-${color}-600`} />
                <h3 className="font-semibold text-gray-900">
                  {key.split(/(?=[A-Z])/).join(' ').replace(/^\w/, c => c.toUpperCase())}
                </h3>
              </div>
              <ParameterSlider
                param={riskManagement[key]}
                value={riskManagement[key].value}
                label=""
                suffix={key.includes('Limit') && !key.includes('Loss') ? '' : '%'}
                onChange={(value) => setRiskManagement(prev => ({
                  ...prev,
                  [key]: { ...prev[key], value }
                }))}
              />
            </div>
          ))}
        </div>

        <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
            <div>
              <h4 className="font-semibold text-red-900">Risk Assessment</h4>
              <p className="text-red-800 text-sm mt-1">
                Current settings provide <strong>Conservative</strong> risk management. 
                Maximum portfolio risk: <strong>{riskManagement.maxDrawdown.value}%</strong>. 
                Recommended for stable, long-term growth with capital preservation.
              </p>
              <div className="mt-3 flex space-x-4 text-sm">
                <span className="text-red-700">
                  <strong>Portfolio Risk Score:</strong> {Math.round((riskManagement.maxDrawdown.value / 25) * 100)}%
                </span>
                <span className="text-red-700">
                  <strong>Daily Risk:</strong> {riskManagement.dailyLossLimit.value}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskManagementPanel;
