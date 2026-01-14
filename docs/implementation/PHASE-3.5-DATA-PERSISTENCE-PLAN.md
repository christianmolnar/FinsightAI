# Phase 3.5: Data Persistence & Advanced Table Controls
**Post-Testing Enhancement Phase**

**Date Created:** January 13, 2026  
**Status:** Planning - Awaiting user testing completion  
**Estimated Time:** 8-12 hours  
**Priority:** HIGH - Blocks cross-device functionality

---

## 📋 Overview

After successful live trading testing, implement comprehensive data persistence and advanced table controls to enable cross-device access and professional data management.

---

## 🎯 Requirements Summary

### 1. Data Persistence (Database Migration)
- **Requirement:** All user data must sync across devices (desktop, mobile, tablet)
- **Current State:** Data stored in browser localStorage (device-specific)
- **Target State:** All data stored in PostgreSQL with user account linking

### 2. Watchlist Synchronization
- **Paper & Live Sync:** Both portfolios share same watchlist
- **Alpaca Integration:** 
  - One-way sync: f.insight.AI → Alpaca (minimum requirement)
  - Two-way sync: Bidirectional sync preferred (if time permits)
- **Current State:** Separate localStorage keys (`paperWatchlist`, `liveWatchlist`)

### 3. Reusable Table Component
- **Requirement:** Single shared component for all data tables
- **Features Required:**
  - Pagination (10, 20, 50 rows per page, default 10)
  - Search across all columns
  - Column sorting (ascending/descending)
  - Column filtering
- **Tables to Convert:**
  - Holdings (Live Portfolio)
  - Holdings (Paper Portfolio)
  - Pending Orders (Live Portfolio)
  - Pending Orders (Paper Portfolio)
  - Watchlist (Shared)
  - Transaction History (Paper Portfolio)

### 4. Auto-Refresh Configuration
- **Requirement:** Real-time data updates during market hours
- **Target Intervals:**
  - Watchlist: 15 seconds
  - Portfolio/Holdings: 30 seconds
  - Pending Orders: 20 seconds
  - Market Status: 60 seconds (already implemented)
- **Smart Behavior:**
  - Auto-enable during market hours
  - Auto-disable when market closed
  - User toggle for manual control
  - Always-available manual refresh button

---

## 🗄️ Database Schema Changes

### New Tables Required

#### 1. `user_watchlists`
```sql
CREATE TABLE user_watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    price DECIMAL(10, 2),
    change DECIMAL(10, 2),
    change_percent DECIMAL(5, 2),
    last_updated TIMESTAMP,
    alpaca_synced BOOLEAN DEFAULT FALSE,
    alpaca_watchlist_id VARCHAR(50),
    UNIQUE(user_id, symbol)
);

CREATE INDEX idx_watchlist_user ON user_watchlists(user_id);
CREATE INDEX idx_watchlist_symbol ON user_watchlists(symbol);
```

#### 2. `user_preferences`
```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    auto_refresh_enabled BOOLEAN DEFAULT TRUE,
    refresh_interval_watchlist INTEGER DEFAULT 15000,
    refresh_interval_portfolio INTEGER DEFAULT 30000,
    refresh_interval_orders INTEGER DEFAULT 20000,
    default_rows_per_page INTEGER DEFAULT 10,
    theme VARCHAR(20) DEFAULT 'light',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. `user_strategies` (for future Phase 4+)
```sql
CREATE TABLE user_strategies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    strategy_name VARCHAR(100) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,
    parameters JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. Existing `users` table (verify/update)
```sql
-- Ensure users table exists with authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    alpaca_paper_key_encrypted TEXT,
    alpaca_live_key_encrypted TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

---

## 🔧 Backend Implementation

### 1. New API Endpoints

#### Watchlist Endpoints
```python
# /backend/api/watchlist.py (NEW FILE)

GET    /api/v1/watchlist                    # Get user's watchlist
POST   /api/v1/watchlist                    # Add symbol to watchlist
DELETE /api/v1/watchlist/{symbol}           # Remove symbol
PUT    /api/v1/watchlist/refresh            # Refresh all quotes
POST   /api/v1/watchlist/sync-alpaca        # Sync with Alpaca
GET    /api/v1/watchlist/alpaca             # Get Alpaca watchlist
```

#### User Preferences Endpoints
```python
# /backend/api/preferences.py (NEW FILE)

GET    /api/v1/preferences                  # Get user preferences
PUT    /api/v1/preferences                  # Update preferences
POST   /api/v1/preferences/reset            # Reset to defaults
```

#### Enhanced Portfolio Endpoints
```python
# /backend/api/portfolio.py (UPDATES)

# Add pagination, search, filter, sort parameters
GET    /api/v1/alpaca/paper/holdings?page=1&per_page=10&search=AAPL&sort=symbol&order=asc
GET    /api/v1/alpaca/live/holdings?page=1&per_page=10&search=AAPL&sort=symbol&order=asc
GET    /api/v1/alpaca/paper/orders?page=1&per_page=10&status=pending&sort=date&order=desc
GET    /api/v1/alpaca/live/orders?page=1&per_page=10&status=pending&sort=date&order=desc
```

### 2. Alpaca Watchlist Integration

#### Research Alpaca API
```python
# From alpaca-py documentation:
# Watchlists API endpoints:
# - GET /v2/watchlists
# - POST /v2/watchlists
# - GET /v2/watchlists/{watchlist_id}
# - PUT /v2/watchlists/{watchlist_id}
# - DELETE /v2/watchlists/{watchlist_id}
# - POST /v2/watchlists/{watchlist_id}  (add symbol)
# - DELETE /v2/watchlists/{watchlist_id}/{symbol}

# Implementation in alpaca_service.py:
class AlpacaService:
    def get_watchlists(self) -> List[dict]:
        """Get all watchlists from Alpaca"""
        
    def create_watchlist(self, name: str, symbols: List[str]) -> dict:
        """Create new watchlist in Alpaca"""
        
    def add_to_watchlist(self, watchlist_id: str, symbol: str) -> dict:
        """Add symbol to existing watchlist"""
        
    def remove_from_watchlist(self, watchlist_id: str, symbol: str) -> bool:
        """Remove symbol from watchlist"""
        
    def sync_watchlist(self, symbols: List[str]) -> dict:
        """Sync f.insight.AI watchlist to Alpaca"""
```

### 3. Service Layer Updates

#### WatchlistService (NEW)
```python
# /backend/services/watchlist_service.py

class WatchlistService:
    def __init__(self, db_session, alpaca_service):
        self.db = db_session
        self.alpaca = alpaca_service
    
    async def get_user_watchlist(self, user_id: int) -> List[dict]:
        """Get watchlist with fresh quotes"""
        
    async def add_symbol(self, user_id: int, symbol: str) -> dict:
        """Add symbol to DB watchlist and sync to Alpaca"""
        
    async def remove_symbol(self, user_id: int, symbol: str) -> bool:
        """Remove from DB and Alpaca"""
        
    async def refresh_quotes(self, user_id: int) -> List[dict]:
        """Refresh all watchlist quotes"""
        
    async def sync_with_alpaca(self, user_id: int, direction: str = "push") -> dict:
        """
        Sync watchlist with Alpaca
        direction: "push" (f.insight → Alpaca), "pull" (Alpaca → f.insight), "both"
        """
```

### 4. Database Models

```python
# /backend/models/watchlist.py (NEW FILE)

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class UserWatchlist(Base):
    __tablename__ = "user_watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    symbol = Column(String(10), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    price = Column(Numeric(10, 2))
    change = Column(Numeric(10, 2))
    change_percent = Column(Numeric(5, 2))
    last_updated = Column(DateTime)
    alpaca_synced = Column(Boolean, default=False)
    alpaca_watchlist_id = Column(String(50))
    
    # Relationship
    user = relationship("User", back_populates="watchlist")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    auto_refresh_enabled = Column(Boolean, default=True)
    refresh_interval_watchlist = Column(Integer, default=15000)
    refresh_interval_portfolio = Column(Integer, default=30000)
    refresh_interval_orders = Column(Integer, default=20000)
    default_rows_per_page = Column(Integer, default=10)
    theme = Column(String(20), default="light")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="preferences", uselist=False)
```

---

## 🎨 Frontend Implementation

### 1. Reusable DataTable Component

#### File: `/frontend/src/components/DataTable.js`

**Features:**
```javascript
// Props interface:
{
  data: Array<Object>,           // Table data
  columns: Array<ColumnDef>,     // Column definitions
  loading: Boolean,              // Loading state
  onRefresh: Function,           // Refresh callback
  searchable: Boolean,           // Enable search
  sortable: Boolean,             // Enable sorting
  filterable: Boolean,           // Enable filtering
  paginated: Boolean,            // Enable pagination
  defaultRowsPerPage: Number,    // Default 10
  rowsPerPageOptions: Array,     // [10, 20, 50]
  emptyState: ReactNode,         // Custom empty state
  actions: Array<ActionDef>,     // Row actions (Trade, Remove, etc.)
}

// Column definition:
{
  key: string,                   // Data key
  label: string,                 // Display label
  sortable: boolean,             // Can sort this column
  filterable: boolean,           // Can filter this column
  searchable: boolean,           // Include in search
  render: Function,              // Custom render function
  width: string,                 // Column width
  align: 'left'|'center'|'right' // Text alignment
}
```

**Component Structure:**
```javascript
import React, { useState, useMemo } from 'react';
import { Search, SortAsc, SortDesc, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';

const DataTable = ({
  data,
  columns,
  loading = false,
  onRefresh,
  searchable = true,
  sortable = true,
  filterable = true,
  paginated = true,
  defaultRowsPerPage = 10,
  rowsPerPageOptions = [10, 20, 50],
  emptyState,
  actions = []
}) => {
  // State management
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(defaultRowsPerPage);
  const [filters, setFilters] = useState({});
  
  // Data processing pipeline
  const processedData = useMemo(() => {
    let result = [...data];
    
    // 1. Search
    if (searchable && searchTerm) {
      result = result.filter(row => 
        columns
          .filter(col => col.searchable !== false)
          .some(col => 
            String(row[col.key])
              .toLowerCase()
              .includes(searchTerm.toLowerCase())
          )
      );
    }
    
    // 2. Filter
    if (filterable && Object.keys(filters).length > 0) {
      result = result.filter(row => {
        return Object.entries(filters).every(([key, value]) => {
          if (!value) return true;
          return String(row[key]).toLowerCase().includes(value.toLowerCase());
        });
      });
    }
    
    // 3. Sort
    if (sortable && sortColumn) {
      result.sort((a, b) => {
        const aVal = a[sortColumn];
        const bVal = b[sortColumn];
        const modifier = sortDirection === 'asc' ? 1 : -1;
        
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return (aVal - bVal) * modifier;
        }
        return String(aVal).localeCompare(String(bVal)) * modifier;
      });
    }
    
    return result;
  }, [data, searchTerm, sortColumn, sortDirection, filters, columns]);
  
  // Pagination
  const totalPages = Math.ceil(processedData.length / rowsPerPage);
  const paginatedData = paginated
    ? processedData.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage)
    : processedData;
  
  // Handlers
  const handleSort = (columnKey) => {
    if (sortColumn === columnKey) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };
  
  // Render component
  return (
    <div className="w-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        {/* Search */}
        {searchable && (
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full"
            />
          </div>
        )}
        
        {/* Refresh Button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={loading}
            className="ml-4 p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="Refresh data"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        )}
      </div>
      
      {/* Table */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  onClick={() => column.sortable !== false && handleSort(column.key)}
                  className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${
                    column.sortable !== false ? 'cursor-pointer hover:bg-gray-100' : ''
                  }`}
                  style={{ width: column.width }}
                >
                  <div className="flex items-center space-x-1">
                    <span>{column.label}</span>
                    {column.sortable !== false && sortColumn === column.key && (
                      sortDirection === 'asc' 
                        ? <SortAsc className="w-4 h-4" />
                        : <SortDesc className="w-4 h-4" />
                    )}
                  </div>
                </th>
              ))}
              {actions.length > 0 && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedData.length > 0 ? (
              paginatedData.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  {columns.map((column) => (
                    <td key={column.key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {column.render ? column.render(row[column.key], row) : row[column.key]}
                    </td>
                  ))}
                  {actions.length > 0 && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm space-x-3">
                      {actions.map((action, actionIdx) => (
                        <button
                          key={actionIdx}
                          onClick={() => action.onClick(row)}
                          className={action.className || "text-blue-600 hover:text-blue-800"}
                        >
                          {action.label}
                        </button>
                      ))}
                    </td>
                  )}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length + (actions.length > 0 ? 1 : 0)} className="px-6 py-12 text-center">
                  {emptyState || <p className="text-gray-500">No data available</p>}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      {/* Pagination */}
      {paginated && totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Rows per page:</span>
            <select
              value={rowsPerPage}
              onChange={(e) => {
                setRowsPerPage(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              {rowsPerPageOptions.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1 text-gray-600 hover:text-blue-600 disabled:opacity-50"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1 text-gray-600 hover:text-blue-600 disabled:opacity-50"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable;
```

### 2. Convert Existing Tables to DataTable

#### Example: Holdings Table
```javascript
// In RealPortfolio.js

import DataTable from './components/DataTable';

// Define columns
const holdingsColumns = [
  {
    key: 'symbol',
    label: 'Symbol',
    sortable: true,
    searchable: true,
    width: '15%'
  },
  {
    key: 'quantity',
    label: 'Quantity',
    sortable: true,
    align: 'right',
    width: '12%'
  },
  {
    key: 'avg_entry_price',
    label: 'Avg Price',
    sortable: true,
    align: 'right',
    width: '12%',
    render: (value) => `$${value?.toFixed(2) || '0.00'}`
  },
  {
    key: 'current_price',
    label: 'Current Price',
    sortable: true,
    align: 'right',
    width: '12%',
    render: (value) => `$${value?.toFixed(2) || '0.00'}`
  },
  {
    key: 'market_value',
    label: 'Market Value',
    sortable: true,
    align: 'right',
    width: '15%',
    render: (value) => `$${value?.toLocaleString() || '0'}`
  },
  {
    key: 'unrealized_pl',
    label: 'Profit/Loss',
    sortable: true,
    align: 'right',
    width: '15%',
    render: (value, row) => (
      <span className={value >= 0 ? 'text-green-600' : 'text-red-600'}>
        {value >= 0 ? '+' : ''}${value?.toFixed(2) || '0.00'}
        ({row.unrealized_plpc >= 0 ? '+' : ''}{row.unrealized_plpc?.toFixed(2)}%)
      </span>
    )
  }
];

// Define actions
const holdingsActions = [
  {
    label: 'Trade',
    onClick: (row) => {
      setTradeForm({ ...tradeForm, symbol: row.symbol, action: 'SELL' });
      setShowTradeModal(true);
    },
    className: 'text-blue-600 hover:text-blue-800'
  }
];

// Use DataTable
<DataTable
  data={portfolioData?.positions || []}
  columns={holdingsColumns}
  loading={loading}
  onRefresh={fetchPortfolioData}
  searchable={true}
  sortable={true}
  paginated={true}
  defaultRowsPerPage={10}
  rowsPerPageOptions={[10, 20, 50]}
  actions={holdingsActions}
  emptyState={
    <div>
      <Eye className="w-12 h-12 text-gray-300 mx-auto mb-3" />
      <p className="text-gray-500 font-medium">No positions yet</p>
      <p className="text-gray-400 text-sm mt-1">Execute your first trade to get started!</p>
    </div>
  }
/>
```

### 3. Auto-Refresh Implementation

#### RefreshManager Hook
```javascript
// /frontend/src/hooks/useAutoRefresh.js

import { useEffect, useRef } from 'react';

/**
 * Custom hook for managing auto-refresh intervals
 * Automatically adjusts based on market status
 */
const useAutoRefresh = (callback, interval, enabled = true, marketOpen = true) => {
  const savedCallback = useRef();
  const intervalRef = useRef();
  
  // Save latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);
  
  // Set up interval
  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      return;
    }
    
    // Adjust interval based on market status
    const actualInterval = marketOpen ? interval : interval * 4; // Slow down when market closed
    
    const tick = () => {
      savedCallback.current?.();
    };
    
    intervalRef.current = setInterval(tick, actualInterval);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [interval, enabled, marketOpen]);
  
  // Manual trigger
  const trigger = () => {
    savedCallback.current?.();
  };
  
  return { trigger };
};

export default useAutoRefresh;
```

#### Usage in Portfolio Components
```javascript
// In RealPortfolio.js

import useAutoRefresh from '../hooks/useAutoRefresh';

const RealPortfolio = () => {
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [marketStatus, setMarketStatus] = useState(null);
  
  // Auto-refresh portfolio
  useAutoRefresh(
    fetchPortfolioData,
    30000, // 30 seconds
    autoRefreshEnabled,
    marketStatus?.is_open
  );
  
  // Auto-refresh pending orders
  useAutoRefresh(
    fetchPendingOrders,
    20000, // 20 seconds
    autoRefreshEnabled,
    marketStatus?.is_open
  );
  
  // Auto-refresh watchlist
  useAutoRefresh(
    refreshWatchlist,
    15000, // 15 seconds
    autoRefreshEnabled,
    marketStatus?.is_open
  );
  
  // Render toggle
  return (
    <div>
      <button
        onClick={() => setAutoRefreshEnabled(!autoRefreshEnabled)}
        className={`px-3 py-1 rounded ${autoRefreshEnabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}
      >
        Auto-refresh: {autoRefreshEnabled ? 'ON' : 'OFF'}
      </button>
      {/* Rest of component */}
    </div>
  );
};
```

### 4. Unified Watchlist Component

```javascript
// /frontend/src/components/UnifiedWatchlist.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DataTable from './DataTable';
import { Eye, TrendingUp, TrendingDown } from 'lucide-react';
import useAutoRefresh from '../hooks/useAutoRefresh';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Unified Watchlist Component
 * Shared between Paper and Live portfolios
 * Syncs with database and Alpaca
 */
const UnifiedWatchlist = ({ onTrade, autoRefreshEnabled = true, marketOpen = true }) => {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newSymbol, setNewSymbol] = useState('');
  
  // Fetch watchlist from API
  const fetchWatchlist = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/v1/watchlist`);
      if (response.data.success) {
        setWatchlist(response.data.watchlist);
      }
    } catch (error) {
      console.error('Error fetching watchlist:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Add symbol
  const addSymbol = async () => {
    const symbol = newSymbol.trim().toUpperCase();
    if (!symbol) return;
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/watchlist`, { symbol });
      if (response.data.success) {
        setWatchlist(response.data.watchlist);
        setNewSymbol('');
      }
    } catch (error) {
      console.error('Error adding symbol:', error);
      alert(error.response?.data?.detail || 'Failed to add symbol');
    }
  };
  
  // Remove symbol
  const removeSymbol = async (symbol) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/api/v1/watchlist/${symbol}`);
      if (response.data.success) {
        setWatchlist(response.data.watchlist);
      }
    } catch (error) {
      console.error('Error removing symbol:', error);
    }
  };
  
  // Auto-refresh
  useAutoRefresh(fetchWatchlist, 15000, autoRefreshEnabled, marketOpen);
  
  // Initial load
  useEffect(() => {
    fetchWatchlist();
  }, []);
  
  // Column definitions
  const columns = [
    {
      key: 'symbol',
      label: 'Symbol',
      sortable: true,
      searchable: true,
      width: '25%',
      render: (value) => <span className="font-medium">{value}</span>
    },
    {
      key: 'price',
      label: 'Price',
      sortable: true,
      width: '25%',
      align: 'right',
      render: (value) => `$${value?.toFixed(2) || '0.00'}`
    },
    {
      key: 'change_percent',
      label: 'Change',
      sortable: true,
      width: '25%',
      align: 'right',
      render: (value, row) => (
        <span className={`flex items-center justify-end ${value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {value >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
          {value >= 0 ? '+' : ''}{value?.toFixed(2)}%
        </span>
      )
    },
    {
      key: 'last_updated',
      label: 'Updated',
      sortable: true,
      width: '25%',
      render: (value) => value ? new Date(value).toLocaleTimeString() : 'Never'
    }
  ];
  
  // Actions
  const actions = [
    {
      label: 'Trade',
      onClick: (row) => onTrade(row.symbol),
      className: 'text-blue-600 hover:text-blue-800'
    },
    {
      label: 'Remove',
      onClick: (row) => removeSymbol(row.symbol),
      className: 'text-red-600 hover:text-red-800'
    }
  ];
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Watchlist</h2>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-32"
              placeholder="AAPL"
            />
            <button
              onClick={addSymbol}
              disabled={!newSymbol}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors disabled:opacity-50"
            >
              Add
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-6">
        <DataTable
          data={watchlist}
          columns={columns}
          loading={loading}
          onRefresh={fetchWatchlist}
          searchable={true}
          sortable={true}
          paginated={true}
          defaultRowsPerPage={10}
          rowsPerPageOptions={[10, 20, 50]}
          actions={actions}
          emptyState={
            <div>
              <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No symbols in watchlist</p>
              <p className="text-gray-400">Add symbols to monitor their prices</p>
            </div>
          }
        />
      </div>
    </div>
  );
};

export default UnifiedWatchlist;
```

---

## 📝 Implementation Checklist

### Phase 1: Database Setup (2 hours)
- [ ] Create migration script for new tables
- [ ] Add `user_watchlists` table
- [ ] Add `user_preferences` table
- [ ] Add `user_strategies` table (placeholder)
- [ ] Verify `users` table structure
- [ ] Test database migrations
- [ ] Create indexes for performance

### Phase 2: Backend - Watchlist API (3 hours)
- [ ] Research Alpaca watchlist API endpoints
- [ ] Create `/backend/models/watchlist.py`
- [ ] Create `/backend/services/watchlist_service.py`
- [ ] Implement one-way sync (f.insight → Alpaca)
- [ ] Implement two-way sync (optional, if time permits)
- [ ] Create `/backend/api/watchlist.py` endpoints
- [ ] Add authentication/authorization
- [ ] Test all watchlist endpoints

### Phase 3: Backend - Preferences API (1 hour)
- [ ] Create `/backend/models/preferences.py`
- [ ] Create `/backend/api/preferences.py` endpoints
- [ ] Implement get/update/reset preferences
- [ ] Test preferences endpoints

### Phase 4: Backend - Enhanced Portfolio Endpoints (2 hours)
- [ ] Add pagination to holdings endpoints
- [ ] Add search/filter/sort to holdings endpoints
- [ ] Add pagination to orders endpoints
- [ ] Add search/filter/sort to orders endpoints
- [ ] Update response schemas
- [ ] Test all enhanced endpoints

### Phase 5: Frontend - DataTable Component (3 hours)
- [ ] Create `/frontend/src/components/DataTable.js`
- [ ] Implement search functionality
- [ ] Implement column sorting
- [ ] Implement column filtering
- [ ] Implement pagination (10/20/50 rows)
- [ ] Add loading states
- [ ] Add empty states
- [ ] Test with sample data

### Phase 6: Frontend - Convert Existing Tables (2 hours)
- [ ] Convert Live Portfolio Holdings to DataTable
- [ ] Convert Paper Portfolio Holdings to DataTable
- [ ] Convert Live Pending Orders to DataTable
- [ ] Convert Paper Pending Orders to DataTable
- [ ] Convert Paper Transaction History to DataTable
- [ ] Remove old table code
- [ ] Test all tables

### Phase 7: Frontend - Unified Watchlist (2 hours)
- [ ] Create `/frontend/src/components/UnifiedWatchlist.js`
- [ ] Connect to API watchlist endpoints
- [ ] Replace localStorage watchlist in both portfolios
- [ ] Test add/remove/refresh operations
- [ ] Test Alpaca sync
- [ ] Verify cross-device persistence

### Phase 8: Frontend - Auto-Refresh (1.5 hours)
- [ ] Create `/frontend/src/hooks/useAutoRefresh.js`
- [ ] Implement smart market-aware refresh
- [ ] Add auto-refresh to Live Portfolio (watchlist, holdings, orders)
- [ ] Add auto-refresh to Paper Portfolio (watchlist, holdings, orders)
- [ ] Add user toggle for auto-refresh
- [ ] Test performance with multiple intervals
- [ ] Verify rate limiting compliance

### Phase 9: Testing & Polish (1.5 hours)
- [ ] Test watchlist persistence across devices
- [ ] Test Alpaca sync (add symbol in app → shows in Alpaca)
- [ ] Test Alpaca sync (add symbol in Alpaca → shows in app)
- [ ] Test all table operations (search, sort, filter, paginate)
- [ ] Test auto-refresh during market hours
- [ ] Test auto-refresh when market closed (slower)
- [ ] Load test with large datasets (100+ holdings)
- [ ] Cross-browser testing
- [ ] Mobile responsive testing

### Phase 10: Documentation (1 hour)
- [ ] Update API documentation
- [ ] Document DataTable component usage
- [ ] Document watchlist sync behavior
- [ ] Update deployment guide
- [ ] Create user guide for new features

---

## ⏱️ Time Estimates

| Phase | Task | Estimated Time |
|-------|------|----------------|
| 1 | Database Setup | 2 hours |
| 2 | Backend - Watchlist API | 3 hours |
| 3 | Backend - Preferences API | 1 hour |
| 4 | Backend - Enhanced Endpoints | 2 hours |
| 5 | Frontend - DataTable Component | 3 hours |
| 6 | Frontend - Convert Tables | 2 hours |
| 7 | Frontend - Unified Watchlist | 2 hours |
| 8 | Frontend - Auto-Refresh | 1.5 hours |
| 9 | Testing & Polish | 1.5 hours |
| 10 | Documentation | 1 hour |
| **TOTAL** | | **19 hours** |

**Estimated Delivery:** 2-3 working days

---

## 🎯 Success Criteria

### Must Have (MVP)
- ✅ All watchlist data persists in database
- ✅ Watchlist syncs to Alpaca (one-way minimum)
- ✅ Single unified watchlist shared between Paper and Live
- ✅ DataTable component used for all tables
- ✅ Pagination working (10/20/50 rows)
- ✅ Search working across all tables
- ✅ Column sorting working
- ✅ Auto-refresh enabled during market hours
- ✅ User can toggle auto-refresh on/off
- ✅ Works on desktop and mobile

### Nice to Have (Stretch Goals)
- ⭐ Two-way Alpaca sync (pull changes from Alpaca)
- ⭐ Column filtering (in addition to search)
- ⭐ User preferences persist (rows per page, refresh intervals)
- ⭐ Refresh rate configuration in settings
- ⭐ Export table data to CSV
- ⭐ Keyboard shortcuts for table navigation

---

## 🔄 Migration Path

### Phase 1: Backend First
1. Deploy database migrations
2. Deploy backend API changes
3. Test endpoints with Postman
4. Verify Alpaca sync working

### Phase 2: Frontend Gradual Rollout
1. Deploy DataTable component
2. Convert one table at a time (test each)
3. Deploy unified watchlist
4. Enable auto-refresh
5. Monitor performance

### Phase 3: Data Migration
1. Script to migrate localStorage data to database (one-time)
2. User notification about improved cross-device support
3. Clear localStorage after successful migration

---

## 📊 Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Alpaca API rate limits exceeded | HIGH | Implement intelligent batching, cache quotes, respect 200/min limit |
| Large datasets slow table rendering | MEDIUM | Virtual scrolling for 100+ rows, optimize React re-renders |
| Database migration fails | HIGH | Test migrations thoroughly, have rollback plan, backup data |
| Alpaca sync conflicts | MEDIUM | Implement conflict resolution (last-write-wins), log all sync operations |
| Auto-refresh performance impact | LOW | Use efficient polling, disable when tab not visible, optimize queries |

---

## 📚 References

### Alpaca API Documentation
- Watchlists: https://alpaca.markets/docs/api-references/trading-api/watchlist/
- Rate Limits: https://alpaca.markets/docs/api-references/trading-api/#rate-limit
- Best Practices: https://alpaca.markets/docs/trading/best-practices/

### React Patterns
- Compound Components: https://kentcdodds.com/blog/compound-components-with-react-hooks
- Custom Hooks: https://react.dev/learn/reusing-logic-with-custom-hooks
- Performance: https://react.dev/learn/render-and-commit

### Database Design
- PostgreSQL Indexes: https://www.postgresql.org/docs/current/indexes.html
- SQLAlchemy Best Practices: https://docs.sqlalchemy.org/en/20/orm/

---

## 🚀 Next Steps After Completion

1. **User Testing:** Have user test all features across devices
2. **Performance Monitoring:** Track API response times, database query performance
3. **Phase 4 Preparation:** With persistence complete, ready for Opportunity Scanner
4. **Mobile App:** Consider React Native app using same backend APIs

---

**Status:** ⏸️ READY TO IMPLEMENT - Awaiting user testing completion

**Last Updated:** January 13, 2026
