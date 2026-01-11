# Pending Orders Feature Implementation

**Date:** January 10, 2026  
**Status:** ✅ COMPLETE  
**Version:** 1.1.0  

## Overview

Added pending/queued orders visibility to both Paper and Live trading portfolios, allowing users to see all orders that haven't executed yet (queued when markets are closed or pending execution).

---

## 🎯 Objectives

1. **Visibility**: Show all pending orders in a dedicated table
2. **Real-time Updates**: Refresh pending orders with portfolio data
3. **Collapsible UI**: Allow users to expand/collapse sections
4. **Status Tracking**: Color-coded badges for order status and side (BUY/SELL)
5. **Empty State Handling**: Clear messaging when no pending orders

---

## 📦 Components Added

### Pending Orders Table

**Location:**
- `/frontend/src/RealPortfolio.js` (Live Trading)
- `/frontend/src/components/PaperPortfolio.js` (Paper Trading)

**Features:**
- **Collapsible Header**: Clock icon with order count badge
- **7-Column Table Layout**:
  1. Symbol (e.g., "AAPL")
  2. Side (BUY/SELL with color-coded badges)
  3. Quantity
  4. Order Type (market, limit, stop, etc.)
  5. Limit Price (if applicable)
  6. Status (new, accepted, pending_new, partially_filled)
  7. Submitted Time (formatted date/time)
- **Empty State**: Clock icon with "No pending orders" message
- **Default State**: Expanded by default (per user requirement)

---

## 🔧 Backend Endpoints

### Created New API Endpoints

#### 1. GET `/api/v1/alpaca/paper/orders`
**Purpose:** Fetch pending orders from paper trading account

**Response Format:**
```json
{
  "success": true,
  "orders": [
    {
      "id": "order-id-123",
      "symbol": "AAPL",
      "qty": 10,
      "side": "buy",
      "type": "market",
      "limit_price": null,
      "status": "new",
      "submitted_at": "2026-01-10T14:30:00Z"
    }
  ]
}
```

**Implementation:**
```python
@router.get("/alpaca/paper/orders")
async def get_alpaca_paper_orders():
    alpaca = get_alpaca_service(paper=True)
    orders = alpaca.get_orders(status="open")
    return {"success": True, "orders": orders}
```

---

#### 2. GET `/api/v1/alpaca/live/orders`
**Purpose:** Fetch pending orders from live trading account

**Response Format:** Same as paper orders endpoint

**Implementation:**
```python
@router.get("/alpaca/live/orders")
async def get_alpaca_live_orders():
    alpaca = get_alpaca_service(paper=False)
    orders = alpaca.get_orders(status="open")
    return {"success": True, "orders": orders}
```

---

## 💾 Service Layer

### Alpaca Service (`alpaca_service.py`)

**Existing Method Used:**
```python
def get_orders(self, status: str = "open") -> List[Dict]:
    """
    Get orders
    
    Args:
        status: Order status filter ('open', 'closed', 'all')
        
    Returns:
        List of order dicts with formatted fields
    """
    if status == "open":
        orders = self.trading_client.get_orders()
    else:
        orders = self.trading_client.get_orders(status="all")
        
    return [self._format_order(order) for order in orders]
```

**Formatted Order Object:**
```python
{
    "id": str,
    "symbol": str,
    "qty": float,
    "side": str,  # 'buy' or 'sell'
    "type": str,  # 'market', 'limit', 'stop', etc.
    "limit_price": float | None,
    "stop_price": float | None,
    "status": str,  # 'new', 'accepted', 'pending_new', 'partially_filled'
    "submitted_at": str,  # ISO format timestamp
    "filled_avg_price": float | None,
    "filled_qty": float
}
```

---

## 🎨 Frontend Implementation

### State Management

**Added to Both Portfolios:**
```javascript
const [pendingOrders, setPendingOrders] = useState([]);
const [showPendingOrders, setShowPendingOrders] = useState(true);
const [showHoldings, setShowHoldings] = useState(true);
```

---

### Fetch Function

**Paper Portfolio:**
```javascript
const fetchPendingOrders = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/alpaca/paper/orders`);
    if (response.ok) {
      const data = await response.json();
      const pending = (data.orders || []).filter(order => 
        ['new', 'accepted', 'pending_new', 'partially_filled'].includes(order.status)
      );
      setPendingOrders(pending);
    }
  } catch (err) {
    console.error('Failed to fetch pending orders:', err);
  }
};
```

**Live Portfolio:**
```javascript
const fetchPendingOrders = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/alpaca/live/orders`);
    if (response.ok) {
      const data = await response.json();
      const pending = (data.orders || []).filter(order => 
        ['new', 'accepted', 'pending_new', 'partially_filled'].includes(order.status)
      );
      setPendingOrders(pending);
    }
  } catch (err) {
    console.error('Failed to fetch pending orders:', err);
  }
};
```

---

### UI Component Structure

```jsx
{/* Pending Orders Table */}
<div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
  {/* Collapsible Header */}
  <div 
    className="p-6 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors flex items-center justify-between"
    onClick={() => setShowPendingOrders(!showPendingOrders)}
  >
    <div className="flex items-center gap-3">
      <Clock className="w-5 h-5 text-yellow-500" />
      <h2 className="text-xl font-semibold text-gray-900">Pending Orders</h2>
      {pendingOrders.length > 0 && (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          {pendingOrders.length}
        </span>
      )}
    </div>
    {showPendingOrders ? <ChevronUp /> : <ChevronDown />}
  </div>
  
  {/* Table Content */}
  {showPendingOrders && (
    <div className="overflow-x-auto">
      {pendingOrders.length > 0 ? (
        <table className="w-full">
          {/* Table headers and rows */}
        </table>
      ) : (
        <div className="p-12 text-center">
          <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No pending orders</p>
        </div>
      )}
    </div>
  )}
</div>
```

---

## 🎨 Visual Design

### Color Coding

**Side Badges:**
- **BUY**: Green badge (`bg-green-100 text-green-800`)
- **SELL**: Red badge (`bg-red-100 text-red-800`)

**Status Badges:**
- **All Pending Statuses**: Yellow badge (`bg-yellow-100 text-yellow-800`)
  - `new`
  - `accepted`
  - `pending_new`
  - `partially_filled`

**Icons:**
- **Clock Icon**: Yellow (`text-yellow-500`) - Represents pending/waiting state
- **Count Badge**: Yellow background with dark yellow text

---

### Responsive Layout

**Desktop:**
- Full 7-column table
- Collapsible header with hover effect
- Clear spacing between sections

**Mobile:**
- Horizontal scroll for table
- Maintains all columns
- Touch-friendly collapsible header

---

## 📊 Order Status Filtering

### Pending Order Statuses

The frontend filters for these statuses only:
1. **`new`**: Order submitted but not yet accepted by exchange
2. **`accepted`**: Order accepted by exchange but not filled
3. **`pending_new`**: Order is being submitted
4. **`partially_filled`**: Order partially executed, remainder pending

### Excluded Statuses

Orders with these statuses are NOT shown in pending table:
- **`filled`**: Order completely executed
- **`canceled`**: Order canceled by user or system
- **`expired`**: Order expired (e.g., day order after market close)
- **`rejected`**: Order rejected by exchange
- **`replaced`**: Order replaced by another order

---

## 🔄 Integration with Existing Features

### 1. Component Mount
```javascript
useEffect(() => {
  fetchPortfolio();
  fetchPendingOrders();  // ← Added
  // ... other fetches
}, []);
```

### 2. Manual Refresh
```javascript
const handleRefresh = async () => {
  setRefreshing(true);
  await Promise.all([
    fetchPortfolioData(),
    fetchPendingOrders()  // ← Added
  ]);
  setRefreshing(false);
};
```

### 3. After Trade Execution
```javascript
if (response.ok) {
  // ... success notification
  await fetchPortfolioData();
  await fetchPendingOrders();  // ← Added - Show newly queued order
}
```

---

## 🧪 Testing Scenarios

### Test Case 1: Market Closed Order
1. ✅ Open Live or Paper Portfolio
2. ✅ Place order when markets are closed
3. ✅ Confirm "Markets Closed" modal
4. ✅ Order appears in Pending Orders table
5. ✅ Status shows "new" or "accepted"
6. ✅ Order count badge updates

### Test Case 2: Order Cancellation
1. ✅ Have pending order in Alpaca dashboard
2. ✅ Cancel order in Alpaca dashboard
3. ✅ Refresh f.insight.AI portfolio
4. ✅ Order no longer appears in Pending Orders table

### Test Case 3: Order Execution
1. ✅ Have pending order queued
2. ✅ Markets open
3. ✅ Order executes automatically
4. ✅ Refresh portfolio
5. ✅ Order removed from Pending Orders
6. ✅ Position appears in Holdings table

### Test Case 4: Empty State
1. ✅ Portfolio with no pending orders
2. ✅ Table shows clock icon and "No pending orders"
3. ✅ Count badge not displayed
4. ✅ Section remains collapsible

### Test Case 5: Collapsible Behavior
1. ✅ Click Pending Orders header
2. ✅ Table collapses (ChevronDown icon appears)
3. ✅ Click again
4. ✅ Table expands (ChevronUp icon appears)
5. ✅ State persists during session

---

## 📋 Files Modified

### Backend
- ✅ `/backend/app/api/portfolio.py` - Added orders endpoints
- ✅ `/backend/app/services/alpaca_service.py` - Uses existing `get_orders()` method

### Frontend
- ✅ `/frontend/src/RealPortfolio.js` - Live portfolio pending orders
- ✅ `/frontend/src/components/PaperPortfolio.js` - Paper portfolio pending orders

### Documentation
- ✅ `/docs/features/PENDING-ORDERS-FEATURE.md` - This file

---

## 🚀 Future Enhancements

### Potential Improvements
1. **Cancel Order Button**: Add ability to cancel pending orders from UI
2. **Edit Order**: Modify pending order quantity or limit price
3. **Order Details Modal**: Click order for full details (time in force, extended hours, etc.)
4. **Filter by Status**: Filter pending orders by specific status
5. **Sort Options**: Sort by symbol, time submitted, quantity
6. **Notifications**: Alert when pending order executes
7. **Order History**: Separate table for filled/canceled orders

---

## ✅ Completion Criteria

- [x] Backend endpoints created for paper and live orders
- [x] Frontend state management added
- [x] Pending Orders table implemented in Live Portfolio
- [x] Pending Orders table implemented in Paper Portfolio
- [x] Collapsible headers with icons and count badges
- [x] Color-coded side and status badges
- [x] Empty state UI with clear messaging
- [x] Tables expanded by default
- [x] Holdings tables also made collapsible
- [x] Integration with refresh functionality
- [x] Integration with trade execution
- [x] No TypeScript/linting errors
- [x] Documentation complete

---

## 📊 Impact

### User Benefits
- ✅ Visibility into queued orders (especially market-closed trades)
- ✅ Confidence that orders are properly submitted
- ✅ Easy tracking of order status
- ✅ Clear understanding of pending positions
- ✅ Better portfolio management

### Technical Benefits
- ✅ Reuses existing `alpaca_service.get_orders()` method
- ✅ Consistent endpoint pattern (`/alpaca/{paper|live}/orders`)
- ✅ Clean separation between pending and executed orders
- ✅ Scalable architecture for future order management features

---

**Status**: ✅ COMPLETE  
**Next**: Continue with UI polish and documentation updates
