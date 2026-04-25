# Backtest Authentication Issue - Debugging Guide

**Date**: April 25, 2026  
**Issue**: Backtest endpoint returns `401 Unauthorized`

---

## 🔍 Root Cause

The backtest API endpoint `/api/backtest/quick/30d` requires JWT authentication:

```python
# backend/app/main.py
app.include_router(backtest_router, dependencies=[Depends(get_current_user)])
```

**The 401 error means one of these:**
1. User is not logged in (no JWT token sent)
2. JWT token has expired
3. JWT token is invalid
4. JWT token is not being sent in Authorization header

---

## ✅ Enhanced Logging Added

Added detailed authentication logging to `backend/middleware/auth_middleware.py`:

**Now logs:**
- 🔒 `"Authentication failed: No credentials provided"` - No Authorization header
- 🔒 `"Authentication failed: Invalid token"` - Token decode failed
- 🔒 `"Authentication failed: No email in token"` - Token missing email claim
- 🔒 `"Authentication failed: User not found: {email}"` - User doesn't exist in DB
- ✅ `"Authenticated: {email}"` - Success

---

## 🔧 How to Test

### Option 1: Check Frontend (Recommended)

1. **Open frontend**: http://localhost:3000
2. **Check if logged in**: Look for user email in top-right navbar
3. **If not logged in**: Click Login, use your credentials
4. **Try backtest**: Click "Quick Backtest - Technical Breakouts"
5. **Check logs**: `tail -f backend/backend.log`

**Expected logs:**
```
🔍 Checking token: eyJhbGciOiJIUzI1Ni...
🔍 Looking up user: user@example.com
✅ Authenticated: user@example.com
INFO: POST /api/backtest/quick/30d?confidence_threshold=0.75 200 OK
```

### Option 2: Test with cURL

```bash
# 1. Login to get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "yourpassword"}'

# Response will contain: {"access_token": "eyJhbGci...", ...}

# 2. Use token to run backtest
curl -X POST "http://localhost:8000/api/backtest/quick/30d?confidence_threshold=0.75" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🐛 Common Issues & Fixes

### Issue 1: "No credentials provided"
**Cause**: Frontend not sending Authorization header  
**Check**:
1. Is user logged in? (Check localStorage for 'token')
2. Is token being added to API requests? (Check frontend API client)

**Frontend API Client** should have:
```javascript
// frontend/src/utils/apiClient.js
const token = localStorage.getItem('token');
if (token) {
  headers['Authorization'] = `Bearer ${token}`;
}
```

### Issue 2: "Invalid token" or "User not found"
**Cause**: Token expired or user deleted  
**Fix**: Login again to get fresh token

### Issue 3: Token Not Persisting
**Cause**: Frontend not storing token after login  
**Check**: `frontend/src/components/Login.js` stores token:
```javascript
localStorage.setItem('token', data.access_token);
```

---

## 📊 Frontend Token Flow

**Login Process:**
1. User enters email/password
2. POST to `/api/auth/login`
3. Backend returns `{"access_token": "...", "token_type": "bearer"}`
4. Frontend stores in localStorage: `localStorage.setItem('token', access_token)`
5. Frontend adds to all API requests: `Authorization: Bearer ${token}`

**Backtest Request:**
1. User clicks "Quick Backtest"
2. Frontend sends: `POST /api/backtest/quick/30d` with `Authorization: Bearer ${token}`
3. Backend `get_current_user` dependency validates token
4. If valid: Runs backtest
5. If invalid: Returns 401

---

## 🧪 Quick Test Script

Save as `test_auth.py`:

```python
import requests

API_BASE = "http://localhost:8000"

# 1. Login
login_response = requests.post(
    f"{API_BASE}/api/auth/login",
    json={"email": "test@example.com", "password": "password123"}
)
print(f"Login: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"Token: {token[:50]}...")
    
    # 2. Test backtest
    backtest_response = requests.post(
        f"{API_BASE}/api/backtest/quick/30d?confidence_threshold=0.75",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Backtest: {backtest_response.status_code}")
    if backtest_response.status_code == 200:
        print("✅ Backtest working!")
    else:
        print(f"❌ Backtest failed: {backtest_response.text}")
else:
    print(f"❌ Login failed: {login_response.text}")
```

Run: `python3 test_auth.py`

---

## 🎯 Next Steps

1. **Check frontend**: Is user logged in? (Look at navbar)
2. **Check localStorage**: Open browser DevTools → Application → localStorage → Look for 'token'
3. **Try backtest**: Click "Quick Backtest - Technical Breakouts"
4. **Watch logs**: `tail -f backend/backend.log` to see authentication flow
5. **If still failing**: Share the exact log output (🔒 messages)

---

## 📝 Log Locations

- **Backend logs**: `/Users/christian/Repos/f.insight.AI Advanced/backend/backend.log`
- **Frontend console**: Browser DevTools → Console
- **Network requests**: Browser DevTools → Network tab

**Look for:**
- Backend: `🔒` or `✅` authentication messages
- Frontend Console: API request errors
- Network tab: Check if Authorization header is present

---

**Backend is now running with enhanced logging. Try the backtest and check the logs!**
