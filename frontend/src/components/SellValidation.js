import React, { useState } from 'react';
import './SellValidation.css';

const SellValidation = ({ position, onClose, onConfirmSell }) => {
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const [validation, setValidation] = useState(null);
  const [error, setError] = useState(null);
  const [selectedReason, setSelectedReason] = useState('');
  const [customReason, setCustomReason] = useState('');

  const sellReasons = [
    { value: 'profit_target', label: 'Hit Profit Target' },
    { value: 'overvalued', label: 'Stock Overvalued' },
    { value: 'bad_news', label: 'Bad News/Fundamentals Changed' },
    { value: 'stop_loss', label: 'Stop Loss Triggered' },
    { value: 'rebalance', label: 'Portfolio Rebalancing' },
    { value: 'need_cash', label: 'Need Cash' },
    { value: 'better_opportunity', label: 'Better Opportunity Elsewhere' },
    { value: 'other', label: 'Other (Specify)' }
  ];

  const handleValidate = async () => {
    if (!selectedReason) {
      setError('Please select a reason for selling');
      return;
    }

    if (selectedReason === 'other' && !customReason.trim()) {
      setError('Please specify your reason');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/research/sell-validation/${position.symbol}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            position: {
              quantity: position.quantity,
              avg_price: position.avg_price,
              current_price: position.current_price,
              purchase_date: position.purchase_date || new Date().toISOString(),
            },
            reason: selectedReason,
            custom_reason: selectedReason === 'other' ? customReason : null,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Validation failed');
      }

      const data = await response.json();
      setValidation(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getValidationColor = (validationType) => {
    switch (validationType) {
      case 'AGREE':
        return '#10b981'; // Green
      case 'WAIT':
        return '#f59e0b'; // Orange
      case 'DISAGREE':
        return '#ef4444'; // Red
      default:
        return '#6b7280'; // Gray
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const calculateGainLoss = () => {
    const cost = position.quantity * position.avg_price;
    const value = position.quantity * position.current_price;
    const gain = value - cost;
    const gainPercent = (gain / cost) * 100;
    return { gain, gainPercent };
  };

  const { gain, gainPercent } = calculateGainLoss();

  return (
    <div className="sell-validation-overlay">
      <div className="sell-validation-modal">
        <div className="sell-validation-header">
          <h2>Sell Decision Validation</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="position-summary">
          <h3>{position.symbol}</h3>
          <div className="position-details">
            <div className="detail-item">
              <span className="label">Quantity:</span>
              <span className="value">{position.quantity} shares</span>
            </div>
            <div className="detail-item">
              <span className="label">Avg Price:</span>
              <span className="value">{formatCurrency(position.avg_price)}</span>
            </div>
            <div className="detail-item">
              <span className="label">Current Price:</span>
              <span className="value">{formatCurrency(position.current_price)}</span>
            </div>
            <div className="detail-item">
              <span className="label">Total Value:</span>
              <span className="value">
                {formatCurrency(position.quantity * position.current_price)}
              </span>
            </div>
            <div className="detail-item">
              <span className="label">Gain/Loss:</span>
              <span className={`value ${gain >= 0 ? 'positive' : 'negative'}`}>
                {formatCurrency(gain)} ({gainPercent >= 0 ? '+' : ''}
                {gainPercent.toFixed(2)}%)
              </span>
            </div>
          </div>
        </div>

        {!validation ? (
          <div className="validation-input">
            <div className="form-group">
              <label>Why are you selling?</label>
              <select
                value={selectedReason}
                onChange={(e) => setSelectedReason(e.target.value)}
                className="reason-select"
              >
                <option value="">Select a reason...</option>
                {sellReasons.map((reason) => (
                  <option key={reason.value} value={reason.value}>
                    {reason.label}
                  </option>
                ))}
              </select>
            </div>

            {selectedReason === 'other' && (
              <div className="form-group">
                <label>Please specify:</label>
                <textarea
                  value={customReason}
                  onChange={(e) => setCustomReason(e.target.value)}
                  placeholder="Enter your reason for selling..."
                  className="custom-reason-input"
                  rows="3"
                />
              </div>
            )}

            {error && <div className="error-message">{error}</div>}

            <button
              onClick={handleValidate}
              disabled={loading || !selectedReason}
              className="validate-button"
            >
              {loading ? 'Analyzing...' : 'Get AI Validation'}
            </button>
          </div>
        ) : (
          <div className="validation-results">
            <div
              className="validation-verdict"
              style={{ borderColor: getValidationColor(validation.validation) }}
            >
              <div className="verdict-badge" style={{ backgroundColor: getValidationColor(validation.validation) }}>
                {validation.validation}
              </div>
              <p className="verdict-message">{validation.reasoning}</p>
              <div className="confidence-bar">
                <span className="confidence-label">
                  AI Confidence: {formatPercent(validation.confidence)}
                </span>
                <div className="confidence-track">
                  <div
                    className="confidence-fill"
                    style={{
                      width: `${validation.confidence * 100}%`,
                      backgroundColor: getValidationColor(validation.validation),
                    }}
                  />
                </div>
              </div>
            </div>

            <div className="ai-recommendations">
              <h4>AI Model Recommendations</h4>
              <div className="model-recommendations">
                <div className="model-rec">
                  <span className="model-name">🤖 OpenAI GPT-4:</span>
                  <span className="model-verdict">{validation.openai_recommendation}</span>
                </div>
                <div className="model-rec">
                  <span className="model-name">🧠 Anthropic Claude:</span>
                  <span className="model-verdict">{validation.claude_recommendation}</span>
                </div>
              </div>
            </div>

            <div className="tax-implications">
              <h4>Tax Implications</h4>
              <div className="tax-details">
                <div className="tax-item">
                  <span className="label">Holding Period:</span>
                  <span className="value">
                    {validation.tax_implications.holding_period_days} days
                    {validation.tax_implications.is_long_term ? (
                      <span className="badge long-term"> Long-term</span>
                    ) : (
                      <span className="badge short-term"> Short-term</span>
                    )}
                  </span>
                </div>
                <div className="tax-item">
                  <span className="label">Tax Type:</span>
                  <span className="value">{validation.tax_implications.tax_type}</span>
                </div>
                <div className="tax-item">
                  <span className="label">Tax Rate:</span>
                  <span className="value">
                    {formatPercent(validation.tax_implications.tax_rate)}
                  </span>
                </div>
                <div className="tax-item">
                  <span className="label">Estimated Tax:</span>
                  <span className="value warning">
                    {formatCurrency(validation.tax_implications.estimated_tax)}
                  </span>
                </div>
                <div className="tax-item">
                  <span className="label">Proceeds After Tax:</span>
                  <span className="value highlight">
                    {formatCurrency(validation.tax_implications.proceeds_after_tax)}
                  </span>
                </div>
                {!validation.tax_implications.is_long_term && (
                  <div className="tax-item">
                    <span className="label">Days Until Long-term:</span>
                    <span className="value">
                      {validation.tax_implications.days_until_long_term} days
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="alternatives">
              <h4>Alternative Recommendations</h4>
              <ul className="alternatives-list">
                {validation.alternatives.map((alt, index) => (
                  <li key={index}>{alt}</li>
                ))}
              </ul>
            </div>

            <div className="action-buttons">
              {validation.validation === 'AGREE' && (
                <button
                  onClick={() => onConfirmSell(position)}
                  className="action-button sell-now"
                >
                  Proceed with Sale
                </button>
              )}
              {validation.validation === 'WAIT' && (
                <>
                  <button onClick={onClose} className="action-button wait">
                    Wait (Consider Alternatives)
                  </button>
                  <button
                    onClick={() => onConfirmSell(position)}
                    className="action-button sell-anyway"
                  >
                    Sell Anyway
                  </button>
                </>
              )}
              {validation.validation === 'DISAGREE' && (
                <>
                  <button onClick={onClose} className="action-button keep">
                    Keep Position
                  </button>
                  <button
                    onClick={() => onConfirmSell(position)}
                    className="action-button sell-anyway"
                  >
                    Sell Anyway
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SellValidation;
