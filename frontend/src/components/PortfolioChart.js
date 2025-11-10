import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const PortfolioChart = ({ portfolioData }) => {
  // Placeholder data for the chart - this will be replaced with real time-series data
  const mockData = [
    { time: '09:30', value: 98500, pnl: -1500 },
    { time: '10:00', value: 99200, pnl: -800 },
    { time: '10:30', value: 99800, pnl: -200 },
    { time: '11:00', value: 100500, pnl: 500 },
    { time: '11:30', value: 100200, pnl: 200 },
    { time: '12:00', value: 100800, pnl: 800 },
    { time: '12:30', value: 101200, pnl: 1200 },
    { time: '13:00', value: 100900, pnl: 900 },
    { time: '13:30', value: 101500, pnl: 1500 },
    { time: '14:00', value: 101800, pnl: 1800 },
    { time: '14:30', value: 101600, pnl: 1600 },
    { time: '15:00', value: 102200, pnl: 2200 },
  ];

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatTooltipCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const currentValue = portfolioData?.total_value || 100000;
  const dailyPnl = portfolioData?.performance?.daily_pnl || 1500;

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="card-title">Portfolio Performance</h3>
            <p className="text-sm text-gray-500 mt-1">Intraday portfolio value and P&L</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(currentValue)}</p>
            <p className={`text-sm font-medium ${dailyPnl >= 0 ? 'positive' : 'negative'}`}>
              {dailyPnl >= 0 ? '+' : ''}{formatCurrency(dailyPnl)} today
            </p>
          </div>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={mockData}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis 
              dataKey="time" 
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: '#64748b' }}
            />
            <YAxis 
              domain={['dataMin - 1000', 'dataMax + 1000']}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: '#64748b' }}
              tickFormatter={formatCurrency}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              }}
              formatter={(value, name) => [
                formatTooltipCurrency(value),
                name === 'value' ? 'Portfolio Value' : 'P&L'
              ]}
              labelStyle={{ color: '#374151' }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#3b82f6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorValue)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex justify-between items-center text-sm text-gray-500">
        <span>Market Hours: 9:30 AM - 4:00 PM EST</span>
        <span>Last Update: {new Date().toLocaleTimeString()}</span>
      </div>
    </div>
  );
};

export default PortfolioChart;
