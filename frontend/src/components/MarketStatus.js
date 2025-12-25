import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Reusable Market Status Indicator Component
 * Shows a badge with market open/closed status and pulsing indicator
 */
const MarketStatus = ({ className = '' }) => {
  const [marketStatus, setMarketStatus] = useState(null);

  useEffect(() => {
    fetchMarketStatus();
    
    // Refresh market status every 60 seconds
    const interval = setInterval(() => {
      fetchMarketStatus();
    }, 60000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchMarketStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/market/status`);
      if (response.data.success) {
        setMarketStatus(response.data);
      }
    } catch (err) {
      console.error('Error fetching market status:', err);
    }
  };

  if (!marketStatus) return null;

  return (
    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700 ${className}`}>
      <div className={`w-2 h-2 rounded-full ${
        marketStatus.is_open ? 'bg-green-500 animate-pulse' : 'bg-red-500'
      }`}></div>
      <span>Markets {marketStatus.status}</span>
    </div>
  );
};

export default MarketStatus;
