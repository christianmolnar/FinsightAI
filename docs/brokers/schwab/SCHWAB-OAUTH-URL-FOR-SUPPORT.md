# 📧 Response to Schwab Support

**Date:** December 22, 2025

---

## Full OAuth Request URL

### The Complete Authorization URL:
```
https://api.schwabapi.com/v1/oauth/authorize?client_id=5NJ1UhKllGkAMB4XL9JrddqiCXiLysoR&redirect_uri=https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback&response_type=code
```

---

## URL Breakdown

### Base URL:
```
https://api.schwabapi.com/v1/oauth/authorize
```

### Parameters:

| Parameter | Value |
|-----------|-------|
| `client_id` | `5NJ1UhKllGkAMB4XL9JrddqiCXiLysoR` |
| `redirect_uri` | `https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback` |
| `response_type` | `code` |

---

## Application Details

### App Key (Client ID):
```
5NJ1UhKllGkAMB4XL9JrddqiCXiLysoR
```

### Registered Callback URL in Schwab Developer Portal:
```
https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback
```

**Note:** This should match exactly what was registered in the Schwab Developer Portal when the app was created.

---

## Possible Issues

### 1. Callback URL Mismatch
The `redirect_uri` in the authorization request **must exactly match** the callback URL registered in your Schwab Developer Portal.

**Check:**
- Go to https://developer.schwab.com/dashboard
- View your app settings
- Verify the "Callback URL" or "Redirect URI" field matches:
  ```
  https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback
  ```

### 2. URL Encoding
The redirect_uri might need to be URL-encoded:
```
https%3A%2F%2Ffinsightai-production-442e.up.railway.app%2Fapi%2Fauth%2Fschwab%2Fcallback
```

**Full URL with encoded redirect_uri:**
```
https://api.schwabapi.com/v1/oauth/authorize?client_id=5NJ1UhKllGkAMB4XL9JrddqiCXiLysoR&redirect_uri=https%3A%2F%2Ffinsightai-production-442e.up.railway.app%2Fapi%2Fauth%2Fschwab%2Fcallback&response_type=code
```

### 3. Protocol Mismatch
- Registered URL uses `https://` (correct)
- Request URL uses `https://` (correct)
- ✅ No protocol mismatch

### 4. Trailing Slash
Some OAuth providers are strict about trailing slashes.

**Current (no trailing slash):**
```
https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback
```

**Alternative (with trailing slash):**
```
https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback/
```

---

## Alternative: Use Localhost for Initial Testing

If you haven't deployed to production yet, use localhost callback:

### Callback URL for Local Development:
```
https://127.0.0.1:8000/api/auth/schwab/callback
```

### Full Authorization URL (Local):
```
https://api.schwabapi.com/v1/oauth/authorize?client_id=5NJ1UhKllGkAMB4XL9JrddqiCXiLysoR&redirect_uri=https://127.0.0.1:8000/api/auth/schwab/callback&response_type=code
```

**Note:** You'll need to register `https://127.0.0.1:8000/api/auth/schwab/callback` in your Schwab app settings.

---

## Questions for Schwab Support

### 1. What callback URL is registered for my app?
**My App Key:** `5NJ1UhKllGkAMB4XL9JrddqiCXiLysoR`

Can you confirm what redirect_uri/callback URL is currently registered in my application settings?

### 2. Does the redirect_uri need to be URL-encoded?
Should the `redirect_uri` parameter be URL-encoded in the authorization request?

Example:
- Unencoded: `redirect_uri=https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback`
- Encoded: `redirect_uri=https%3A%2F%2Ffinsightai-production-442e.up.railway.app%2Fapi%2Fauth%2Fschwab%2Fcallback`

### 3. Are multiple callback URLs supported?
Can I register both:
- `https://127.0.0.1:8000/api/auth/schwab/callback` (for local testing)
- `https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback` (for production)

### 4. Trailing slash sensitivity?
Does the redirect_uri need to match exactly including/excluding trailing slashes?

---

## How to Test the Authorization Flow

### Step 1: Click This Link
```
https://api.schwabapi.com/v1/oauth/authorize?client_id=5NJ1UhKllGkAMB4XL9JrddqiCXiLysoR&redirect_uri=https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback&response_type=code
```

### Step 2: Expected Behavior
1. You're redirected to Schwab login page
2. You log in with your Schwab credentials
3. You authorize the app
4. Schwab redirects to: `https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback?code=XXXXX`

### Step 3: Current Error
"Invalid redirect_uri parameter" error appears before or after login.

---

## Developer Portal Settings to Check

Go to: https://developer.schwab.com/dashboard

### Check These Settings:

1. **App Status:** Should be "Approved" or "Active"
2. **App Key:** `5NJ1UhKllGkAMB4XL9JrddqiCXiLysoR`
3. **Callback URL/Redirect URI:** Should exactly match what you're using
4. **API Access:** Make sure "Accounts and Trading Production" and/or "Market Data" is enabled

---

## Copy & Paste for Schwab Support

Dear Schwab Support,

I'm experiencing an "invalid redirect_uri parameter" error when trying to authenticate my application.

**My App Key (Client ID):**
```
5NJ1UhKllGkAMB4XL9JrddqiCXiLysoR
```

**Full Authorization Request URL:**
```
https://api.schwabapi.com/v1/oauth/authorize?client_id=5NJ1UhKllGkAMB4XL9JrddqiCXiLysoR&redirect_uri=https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback&response_type=code
```

**redirect_uri parameter value:**
```
https://finsightai-production-442e.up.railway.app/api/auth/schwab/callback
```

**Questions:**
1. Can you confirm what callback URL is registered for this app key in your system?
2. Does the redirect_uri parameter need to be URL-encoded?
3. Are there any other issues with this authorization request URL?

Thank you for your help!

---

## Temporary Solution: Use Localhost

While waiting for Schwab support response, you can test locally:

### 1. Update Schwab Developer Portal
Register this callback URL:
```
https://127.0.0.1:8000/api/auth/schwab/callback
```

### 2. Start Local Backend with HTTPS
```bash
cd backend
python run_https.py  # or python generate_ssl.sh first if needed
```

### 3. Visit Local Auth URL
```
https://127.0.0.1:8000/api/auth/schwab/login
```

This will work immediately if the localhost URL is registered.

---

## Summary

**Send to Schwab Support:**
The complete authorization URL above and ask them to:
1. Verify the registered callback URL for your app
2. Confirm if there's a mismatch
3. Update it if needed

**Meanwhile:**
Register `https://127.0.0.1:8000/api/auth/schwab/callback` in your Schwab app settings to test locally while the production URL issue is resolved.

---

**Status:** Waiting for Schwab support to verify registered callback URL
