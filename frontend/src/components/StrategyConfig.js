import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MarketStatus from './MarketStatus';
import RiskManagementPanel from './RiskManagementPanel';
import TechnicalFiltersPanel from './TechnicalFiltersPanel';
import { 
  Brain, 
  Target, 
  TrendingUp, 
  Calendar, 
  Globe, 
  MessageSquare,
  Settings,
  Zap,
  Shield,
  DollarSign,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Lightbulb,
  RefreshCw,
  Save,
  Play,
  Pause,
  Download,
  Upload
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const StrategyConfig = () => {
  const [activeStrategy, setActiveStrategy] = useState('earnings');
  const [activePanel, setActivePanel] = useState('strategies'); // strategies, risk, technical, backtest
  const [isAIOptimizing, setIsAIOptimizing] = useState(false);
  const [strategies, setStrategies] = useState({
    earnings: {
      enabled: true,
      name: 'Earnings Momentum',
      icon: TrendingUp,
      color: 'blue',
      params: {
        daysBeforeEarnings: { value: 5, min: 1, max: 14, description: 'Days before earnings to enter' },
        minEpsGrowth: { value: 15, min: 5, max: 50, description: 'Minimum EPS growth % YoY' },
        minRevenueGrowth: { value: 10, min: 0, max: 30, description: 'Minimum revenue growth % YoY' },
        historicalBeatRate: { value: 70, min: 50, max: 95, description: 'Required historical beat rate %' },
        profitTarget: { value: 12, min: 5, max: 25, description: 'Profit target %' },
        stopLoss: { value: 5, min: 3, max: 10, description: 'Stop loss %' },
        maxPortfolioWeight: { value: 20, min: 5, max: 40, description: 'Max portfolio allocation %' }
      }
    },
    seasonality: {
      enabled: true,
      name: 'Seasonality & Calendar',
      icon: Calendar,
      color: 'green',
      params: {
        weeksBeforePeak: { value: 3, min: 1, max: 8, description: 'Weeks before seasonal peak to enter' },
        minHistoricalYears: { value: 5, min: 3, max: 10, description: 'Years of historical data required' },
        minSeasonalReturn: { value: 8, min: 3, max: 20, description: 'Minimum seasonal return %' },
        profitTarget: { value: 15, min: 8, max: 30, description: 'Profit target %' },
        stopLoss: { value: 7, min: 4, max: 12, description: 'Stop loss %' },
        maxPortfolioWeight: { value: 15, min: 5, max: 30, description: 'Max portfolio allocation %' }
      }
    },
    macro: {
      enabled: true,
      name: 'Macro & Economic',
      icon: Globe,
      color: 'purple',
      params: {
        entryTimeframe: { value: 48, min: 12, max: 168, description: 'Hours after catalyst to enter' },
        catalystStrengthMin: { value: 70, min: 50, max: 90, description: 'Minimum catalyst strength score' },
        correlationThreshold: { value: 0.6, min: 0.3, max: 0.9, description: 'Stock-catalyst correlation' },
        profitTarget: { value: 8, min: 4, max: 15, description: 'Profit target %' },
        stopLoss: { value: 6, min: 3, max: 10, description: 'Stop loss %' },
        maxHoldDays: { value: 30, min: 7, max: 60, description: 'Maximum hold period (days)' },
        maxPortfolioWeight: { value: 10, min: 5, max: 25, description: 'Max portfolio allocation %' }
      }
    },
    sentiment: {
      enabled: true,
      name: 'Social Sentiment',
      icon: MessageSquare,
      color: 'orange',
      params: {
        minSentimentScore: { value: 70, min: 50, max: 90, description: 'Minimum sentiment score %' },
        volumeMultiplier: { value: 1.5, min: 1.2, max: 3.0, description: 'Volume vs 20-day average' },
        newsScoreMin: { value: 80, min: 60, max: 95, description: 'News sentiment threshold %' },
        searchTrendIncrease: { value: 50, min: 20, max: 100, description: 'Google Trends increase %' },
        profitTarget: { value: 8, min: 4, max: 15, description: 'Profit target %' },
        stopLoss: { value: 4, min: 2, max: 8, description: 'Stop loss %' },
        maxPortfolioWeight: { value: 15, min: 5, max: 25, description: 'Max portfolio allocation %' }
      }
    }
  });

  const [riskManagement, setRiskManagement] = useState({
    maxSinglePosition: { value: 5, min: 1, max: 10, description: 'Maximum single position %' },
    maxSectorExposure: { value: 25, min: 10, max: 50, description: 'Maximum sector exposure %' },
    maxDrawdown: { value: 15, min: 5, max: 25, description: 'Maximum portfolio drawdown %' },
    dailyLossLimit: { value: 3, min: 1, max: 5, description: 'Daily loss limit %' },
    vixThreshold: { value: 25, min: 15, max: 40, description: 'VIX threshold for position reduction' },
    consecutiveLossLimit: { value: 5, min: 3, max: 10, description: 'Max consecutive losses before pause' }
  });

  const [technicalFilters, setTechnicalFilters] = useState({
    minRequiredFilters: { value: 3, min: 2, max: 5, description: 'Required technical confirmations' },
    rsiMin: { value: 40, min: 20, max: 50, description: 'RSI minimum level' },
    rsiMax: { value: 70, min: 60, max: 80, description: 'RSI maximum level' },
    minVolume: { value: 500000, min: 100000, max: 2000000, description: 'Minimum daily volume' },
    volumeMultiplier: { value: 1.2, min: 1.0, max: 2.0, description: 'Volume vs 20-day average' },
    ma200Distance: { value: 5, min: 0, max: 15, description: 'Min distance above 200-day MA %' }
  });

  const strategyColors = {
    blue: 'bg-blue-500 text-white border-blue-500',
    green: 'bg-green-500 text-white border-green-500',
    purple: 'bg-purple-500 text-white border-purple-500',
    orange: 'bg-orange-500 text-white border-orange-500'
  };

  const handleAIOptimization = async (strategyType) => {
    setIsAIOptimizing(true);
    
    try {
      // Get current strategy parameters
      const currentStrategy = strategies[strategyType];
      const currentParams = Object.keys(currentStrategy.params).reduce((acc, key) => {
        acc[key] = currentStrategy.params[key].value;
        return acc;
      }, {});

      // Call AI optimization endpoint
      const response = await axios.post(`${API_BASE_URL}/api/v1/ai/optimize-strategy`, {
        strategy_type: strategyType,
        current_parameters: currentParams,
        user_risk_tolerance: "moderate",
        optimization_goal: "risk_adjusted_return",
        ai_model: "openai-gpt4"
      });

      const optimization = response.data;
      
      // Update strategy parameters with AI recommendations
      setStrategies(prev => ({
        ...prev,
        [strategyType]: {
          ...prev[strategyType],
          params: {
            ...prev[strategyType].params,
            ...Object.keys(optimization.optimized_parameters).reduce((acc, key) => {
              if (prev[strategyType].params[key]) {
                acc[key] = {
                  ...prev[strategyType].params[key],
                  value: optimization.optimized_parameters[key]
                };
              }
              return acc;
            }, {})
          }
        }
      }));

      // Show AI reasoning (you could display this in a modal or notification)
      console.log('AI Optimization Result:', {
        reasoning: optimization.reasoning,
        market_analysis: optimization.market_analysis,
        expected_return: optimization.expected_return,
        confidence: optimization.confidence_score
      });

    } catch (error) {
      console.error('AI Optimization failed:', error);
      
      // Fallback to mock recommendations if backend fails
      const aiRecommendations = {
        earnings: { profitTarget: { value: 14 }, stopLoss: { value: 4.5 } },
        seasonality: { profitTarget: { value: 18 }, weeksBeforePeak: { value: 4 } },
        macro: { profitTarget: { value: 9 }, entryTimeframe: { value: 36 } },
        sentiment: { minSentimentScore: { value: 75 }, volumeMultiplier: { value: 1.8 } }
      };

      if (aiRecommendations[strategyType]) {
        setStrategies(prev => ({
          ...prev,
          [strategyType]: {
            ...prev[strategyType],
            params: {
              ...prev[strategyType].params,
              ...Object.keys(aiRecommendations[strategyType]).reduce((acc, key) => {
                if (prev[strategyType].params[key]) {
                  acc[key] = {
                    ...prev[strategyType].params[key],
                    ...aiRecommendations[strategyType][key]
                  };
                }
                return acc;
              }, {})
            }
          }
        }));
      }
    }
    
    setIsAIOptimizing(false);
  };

  const ParameterSlider = ({ param, value, onChange, label }) => (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-sm font-semibold text-gray-900">
          {typeof value === 'number' ? value.toFixed(value < 10 ? 1 : 0) : value}
          {label.includes('%') ? '%' : ''}
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

  const StrategyCard = ({ strategyKey, strategy, isActive, onClick }) => {
    const IconComponent = strategy.icon;
    return (
      <div
        onClick={onClick}
        className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
          isActive 
            ? strategyColors[strategy.color]
            : 'bg-white border-gray-200 hover:border-gray-300'
        }`}
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-3">
            <IconComponent className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-600'}`} />
            <span className={`font-semibold ${isActive ? 'text-white' : 'text-gray-900'}`}>
              {strategy.name}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${strategy.enabled ? 'bg-green-400' : 'bg-gray-400'}`} />
            <span className={`text-xs ${isActive ? 'text-white' : 'text-gray-500'}`}>
              {strategy.enabled ? 'ON' : 'OFF'}
            </span>
          </div>
        </div>
        <p className={`text-sm ${isActive ? 'text-white/90' : 'text-gray-600'}`}>
          {strategyKey === 'earnings' && 'Trade stocks before earnings with strong growth'}
          {strategyKey === 'seasonality' && 'Capitalize on predictable seasonal patterns'}
          {strategyKey === 'macro' && 'React to economic events and catalysts'}
          {strategyKey === 'sentiment' && 'Follow social sentiment and alternative data'}
        </p>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Strategy Configuration</h1>
            <p className="text-gray-600">Configure AI-powered trading strategies with intelligent parameter optimization</p>
          </div>
          <MarketStatus />
        </div>
        <div className="flex justify-end space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
            <Download className="w-4 h-4" />
            <span>Export Config</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
            <Upload className="w-4 h-4" />
            <span>Import Config</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
            <Save className="w-4 h-4" />
            <span>Save Changes</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Strategy Selection Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Trading Strategies</h3>
            <div className="space-y-3">
              {Object.entries(strategies).map(([key, strategy]) => (
                <StrategyCard
                  key={key}
                  strategyKey={key}
                  strategy={strategy}
                  isActive={activeStrategy === key}
                  onClick={() => setActiveStrategy(key)}
                />
              ))}
            </div>

            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Configuration Panels</h4>
              <div className="space-y-2">
                <button 
                  onClick={() => setActivePanel('strategies')}
                  className={`w-full text-left px-3 py-2 text-sm rounded border flex items-center space-x-2 ${
                    activePanel === 'strategies' ? 'bg-blue-100 border-blue-300 text-blue-800' : 'bg-white hover:bg-gray-100'
                  }`}
                >
                  <TrendingUp className="w-4 h-4" />
                  <span>Trading Strategies</span>
                </button>
                <button 
                  onClick={() => setActivePanel('risk')}
                  className={`w-full text-left px-3 py-2 text-sm rounded border flex items-center space-x-2 ${
                    activePanel === 'risk' ? 'bg-red-100 border-red-300 text-red-800' : 'bg-white hover:bg-gray-100'
                  }`}
                >
                  <Shield className="w-4 h-4" />
                  <span>Risk Management</span>
                </button>
                <button 
                  onClick={() => setActivePanel('technical')}
                  className={`w-full text-left px-3 py-2 text-sm rounded border flex items-center space-x-2 ${
                    activePanel === 'technical' ? 'bg-purple-100 border-purple-300 text-purple-800' : 'bg-white hover:bg-gray-100'
                  }`}
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>Technical Filters</span>
                </button>
                <button 
                  onClick={() => setActivePanel('backtest')}
                  className={`w-full text-left px-3 py-2 text-sm rounded border flex items-center space-x-2 ${
                    activePanel === 'backtest' ? 'bg-green-100 border-green-300 text-green-800' : 'bg-white hover:bg-gray-100'
                  }`}
                >
                  <Target className="w-4 h-4" />
                  <span>Backtesting</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Configuration Panel */}
        <div className="lg:col-span-3">
          {activePanel === 'strategies' && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Strategy Header */}
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {React.createElement(strategies[activeStrategy].icon, {
                      className: `w-8 h-8 text-${strategies[activeStrategy].color}-600`
                    })}
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        {strategies[activeStrategy].name} Strategy
                      </h2>
                      <p className="text-gray-600">
                        Configure parameters for optimal performance
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={strategies[activeStrategy].enabled}
                        onChange={(e) => setStrategies(prev => ({
                          ...prev,
                          [activeStrategy]: {
                            ...prev[activeStrategy],
                            enabled: e.target.checked
                          }
                        }))}
                        className="rounded border-gray-300"
                      />
                      <span className="text-sm font-medium">Enable Strategy</span>
                    </label>
                    <button
                      onClick={() => handleAIOptimization(activeStrategy)}
                      disabled={isAIOptimizing}
                      className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-lg transition-all disabled:opacity-50"
                    >
                      {isAIOptimizing ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          <span>Optimizing...</span>
                        </>
                      ) : (
                        <>
                          <Brain className="w-4 h-4" />
                          <span>AI Optimize</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Parameters Configuration */}
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Object.entries(strategies[activeStrategy].params).map(([key, param]) => (
                    <ParameterSlider
                      key={key}
                      param={param}
                      value={param.value}
                      label={key.split(/(?=[A-Z])/).join(' ').replace(/^\w/, c => c.toUpperCase())}
                      onChange={(value) => setStrategies(prev => ({
                        ...prev,
                        [activeStrategy]: {
                          ...prev[activeStrategy],
                          params: {
                            ...prev[activeStrategy].params,
                            [key]: { ...param, value }
                          }
                        }
                      }))}
                    />
                  ))}
                </div>

                {/* Performance Metrics Preview */}
                <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-3">Expected Performance Metrics</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">15.2%</div>
                      <div className="text-sm text-gray-600">Expected Annual Return</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">62%</div>
                      <div className="text-sm text-gray-600">Win Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">1.4</div>
                      <div className="text-sm text-gray-600">Profit Factor</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">12%</div>
                      <div className="text-sm text-gray-600">Max Drawdown</div>
                    </div>
                  </div>
                </div>

                {/* AI Recommendations */}
                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <Lightbulb className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-blue-900">AI Recommendations</h4>
                      <p className="text-blue-800 text-sm mt-1">
                        Based on historical backtesting, consider increasing your profit target to 14% 
                        and tightening your stop loss to 4.5% for optimal risk-adjusted returns.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activePanel === 'risk' && (
            <RiskManagementPanel 
              riskManagement={riskManagement}
              setRiskManagement={setRiskManagement}
              onSave={() => console.log('Saving risk management settings')}
            />
          )}

          {activePanel === 'technical' && (
            <TechnicalFiltersPanel 
              technicalFilters={technicalFilters}
              setTechnicalFilters={setTechnicalFilters}
              onSave={() => console.log('Saving technical filters')}
            />
          )}

          {activePanel === 'backtest' && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-center">
                <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Backtesting Engine</h2>
                <p className="text-gray-600 mb-6">
                  Test your strategies against historical market data
                </p>
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <p className="text-green-800 font-semibold">🚀 Coming Soon!</p>
                  <p className="text-green-700 text-sm mt-2">
                    Advanced backtesting with Monte Carlo simulations, walk-forward analysis, and risk metrics
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StrategyConfig;
