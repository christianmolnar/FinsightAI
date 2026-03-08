import React, { useState } from 'react';
import './Research.css';

const Research = () => {
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const [loading, setLoading] = useState(false);
  const [research, setResearch] = useState(null);
  const [error, setError] = useState(null);

  const handleResearch = async (e) => {
    e.preventDefault();
    
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);
    setResearch(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/research/stock/${symbol.toUpperCase()}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Research failed');
      }

      const data = await response.json();
      setResearch(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'BUY':
        return '#10b981'; // Green
      case 'WAIT':
        return '#f59e0b'; // Orange
      case 'AVOID':
        return '#ef4444'; // Red
      default:
        return '#6b7280'; // Gray
    }
  };

  const getConfidenceBar = (confidence) => {
    const percentage = Math.round(confidence * 100);
    return (
      <div className="confidence-container">
        <div className="confidence-bar-bg">
          <div
            className="confidence-bar-fill"
            style={{
              width: `${percentage}%`,
              backgroundColor: percentage >= 75 ? '#10b981' : percentage >= 50 ? '#f59e0b' : '#ef4444'
            }}
          />
        </div>
        <span className="confidence-text">{percentage}%</span>
      </div>
    );
  };

  return (
    <div className="research-container">
      <div className="research-header">
        <h1>🔍 AI Stock Research</h1>
        <p>Get dual AI analysis with OpenAI GPT-4 + Anthropic Claude</p>
      </div>

      <form onSubmit={handleResearch} className="research-form">
        <div className="search-input-group">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Enter stock symbol (e.g., AAPL, MSFT, NVDA)"
            className="symbol-input"
            disabled={loading}
          />
          <button type="submit" className="research-button" disabled={loading}>
            {loading ? '🔄 Researching...' : '🚀 Analyze'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Gathering market data and consulting AI models...</p>
          <p className="loading-subtext">This usually takes 3-5 seconds</p>
        </div>
      )}

      {research && (
        <div className="research-results">
          {/* Consensus Recommendation */}
          <div
            className="consensus-card"
            style={{ borderColor: getRecommendationColor(research.consensus) }}
          >
            <div className="consensus-badge" style={{ backgroundColor: getRecommendationColor(research.consensus) }}>
              {research.consensus}
            </div>
            <h2>{research.symbol}</h2>
            <p className="consensus-subtitle">
              {research.agreement ? '✅ Both AI models agree' : '⚠️ AI models disagree - proceed with caution'}
            </p>
            <div className="confidence-section">
              <label>Overall Confidence:</label>
              {getConfidenceBar(research.confidence)}
            </div>
          </div>

          {/* AI Model Reasoning */}
          <div className="ai-models-section">
            <h3>🤖 AI Model Analysis</h3>
            <div className="models-grid">
              {research.models.map((model, index) => (
                <div key={index} className="model-card">
                  <div className="model-header">
                    <h4>{model.model_name}</h4>
                    <span
                      className="model-recommendation"
                      style={{ backgroundColor: getRecommendationColor(model.recommendation) }}
                    >
                      {model.recommendation}
                    </span>
                  </div>
                  <p className="model-reasoning">{model.reasoning}</p>
                  <div className="model-confidence">
                    <label>Confidence:</label>
                    {getConfidenceBar(model.confidence)}
                  </div>
                  {model.entry_price && (
                    <div className="model-prices">
                      <div className="price-item">
                        <label>Entry:</label>
                        <span>${model.entry_price.toFixed(2)}</span>
                      </div>
                      <div className="price-item">
                        <label>Stop:</label>
                        <span className="stop-loss">${model.stop_loss.toFixed(2)}</span>
                      </div>
                      <div className="price-item">
                        <label>Target:</label>
                        <span className="target-price">${model.target_price.toFixed(2)}</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Market Data */}
          <div className="market-data-section">
            <div className="data-grid">
              <div className="data-card">
                <h4>📊 Fundamental Analysis</h4>
                <div className="data-items">
                  {research.fundamental.pe_ratio && (
                    <div className="data-row">
                      <span>P/E Ratio:</span>
                      <strong>{research.fundamental.pe_ratio.toFixed(2)}</strong>
                    </div>
                  )}
                  {research.fundamental.eps && (
                    <div className="data-row">
                      <span>EPS:</span>
                      <strong>${research.fundamental.eps.toFixed(2)}</strong>
                    </div>
                  )}
                  {research.fundamental.profit_margin && (
                    <div className="data-row">
                      <span>Profit Margin:</span>
                      <strong>{research.fundamental.profit_margin.toFixed(2)}%</strong>
                    </div>
                  )}
                  {research.fundamental.sector && (
                    <div className="data-row">
                      <span>Sector:</span>
                      <strong>{research.fundamental.sector}</strong>
                    </div>
                  )}
                </div>
              </div>

              <div className="data-card">
                <h4>📈 Technical Analysis</h4>
                <div className="data-items">
                  {research.technical.current_price && (
                    <div className="data-row">
                      <span>Current Price:</span>
                      <strong>${research.technical.current_price.toFixed(2)}</strong>
                    </div>
                  )}
                  {research.technical.rsi && (
                    <div className="data-row">
                      <span>RSI (14):</span>
                      <strong style={{
                        color: research.technical.rsi > 70 ? '#ef4444' : research.technical.rsi < 30 ? '#10b981' : 'inherit'
                      }}>
                        {research.technical.rsi.toFixed(2)}
                      </strong>
                    </div>
                  )}
                  {research.technical.ma_50 && (
                    <div className="data-row">
                      <span>50-Day MA:</span>
                      <strong>${research.technical.ma_50.toFixed(2)}</strong>
                    </div>
                  )}
                  {research.technical.ma_200 && (
                    <div className="data-row">
                      <span>200-Day MA:</span>
                      <strong>${research.technical.ma_200.toFixed(2)}</strong>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Recent News */}
          {research.news && research.news.length > 0 && (
            <div className="news-section">
              <h4>📰 Recent News</h4>
              <div className="news-list">
                {research.news.slice(0, 5).map((item, index) => (
                  <div key={index} className="news-item">
                    <span
                      className="sentiment-badge"
                      style={{
                        backgroundColor:
                          item.sentiment === 'positive' ? '#10b981' :
                          item.sentiment === 'negative' ? '#ef4444' :
                          '#6b7280'
                      }}
                    >
                      {item.sentiment}
                    </span>
                    <span className="news-title">{item.title}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Button */}
          {research.consensus === 'BUY' && (
            <div className="action-section">
              <button className="create-trade-button">
                💰 Create Trade Proposal
              </button>
              <p className="action-note">
                This will create a trade proposal based on the AI recommendations
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Research;
