# Schwab API Connection Fix Guide
**Updated:** December 23, 2024  
**Based on:** Schwab Support Feedback

---

## 🎯 The Issue

Schwab support confirmed:
> "Your callback URL in the developer portal is set to `https://127.0.0.1` so that is what you would want to use as the `redirect_uri` in your URL."

**Key Point:** The `redirect_uri` parameter in OAuth requests **MUST EXACTLY MATCH** what's configured in your Schwab Developer Portal.

---

## ✅ Corrected Setup

### 1. Verify Developer Portal Settings

Go to https://beta-developer.schwab.com/ and check your app:

```
App Name: [Your App Name]
Status: Ready for Use ✅ (must be this, not "Approved - Pending")
Callback URL: https://127.0.0.1 ✅
```

**Important:** The callback URL should be **exactly** `https://127.0.0.1` (no port, no path)

### 2. Update .env File

Your `.env` should have:
```bash
APP_KEY=your_32_character_app_key_here
APP_SECRET=your_16_character_app_secret_here
CALLBACK_URL=https://127.0.0.1
```

### 3. Test Connection

Run the test script:
```bash
cd /Users/christian/Repos/f.insight.AI\ Advanced
python backend/test_schwab_connection.py
```

The script will:
1. ✅ Validate your credentials
2. ✅ Generate correct authorization URL with `redirect_uri=https://127.0.0.1`
3. ✅ Guide you through OAuth flow
4. ✅ Save tokens to `tokens.json`

---

## 📋 Step-by-Step OAuth Flow

### Step 1: Authorization URL

The script generates:
```
https://api.schwabapi.com/v1/oauth/authorize?
  client_id=YOUR_APP_KEY&
  redirect_uri=https://127.0.0.1&
  response_type=code
```

**Note:** `redirect_uri` is now `https://127.0.0.1` (no localhost, no port)

### Step 2: User Authorization

1. Open the URL in your browser
2. Log in with your Schwab credentials
3. Authorize the app
4. You'll be redirected to: `https://127.0.0.1/?code=XXXXXXXX`

**Expected Behavior:**
- Browser shows "Connection refused" or "Can't reach this page" ✅ **THIS IS NORMAL**
- The URL bar contains the authorization code ✅
- Copy the ENTIRE URL from address bar

### Step 3: Exchange Code for Tokens

The script sends:
```http
POST https://api.schwabapi.com/v1/oauth/token
Authorization: Basic <base64(app_key:app_secret)>
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=XXXXXXXX&
redirect_uri=https://127.0.0.1
```

**Critical:** The `redirect_uri` in token request **MUST MATCH** the one used in authorization URL

### Step 4: Tokens Saved

Success response:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 1800,
  "token_type": "Bearer",
  "scope": "api"
}
```

Tokens saved to: `tokens.json`

---

## 🐛 Common Issues & Fixes

### Issue 1: "redirect_uri_mismatch"

**Cause:** Mismatch between developer portal and OAuth request

**Fix:**
```bash
# Check developer portal setting
Portal Callback URL: https://127.0.0.1

# Verify .env file
CALLBACK_URL=https://127.0.0.1

# Both must match exactly
```

### Issue 2: "invalid_grant" (Authorization code)

**Cause:** Authorization code already used or expired

**Fix:**
1. Get a NEW authorization code (start from Step 1)
2. Complete the flow within 5 minutes
3. Each code can only be used ONCE

### Issue 3: "unauthorized_client"

**Cause:** App not approved or credentials wrong

**Fix:**
1. Check app status: **Must be "Ready for Use"**
2. "Approved - Pending" won't work - wait for full approval
3. Verify APP_KEY and APP_SECRET in developer portal

### Issue 4: Connection refused when redirected

**Status:** ✅ **THIS IS EXPECTED BEHAVIOR**

**Why:** The browser tries to connect to `https://127.0.0.1` (which isn't running)

**What to do:**
1. Don't worry about the error page
2. Just copy the URL from browser address bar
3. URL contains the code: `https://127.0.0.1/?code=XXXXX`

---

## 🔧 Manual Testing

If the automated script fails, try manually:

### 1. Generate Authorization URL
```python
app_key = "YOUR_APP_KEY"
redirect_uri = "https://127.0.0.1"  # Must match portal

auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri={redirect_uri}&response_type=code"
print(auth_url)
```

### 2. Get Authorization Code
- Open URL in browser
- Log in and authorize
- Copy entire redirect URL
- Extract code parameter

### 3. Exchange for Tokens
```python
import requests
import base64

app_key = "YOUR_APP_KEY"
app_secret = "YOUR_APP_SECRET"
auth_code = "CODE_FROM_STEP_2"
redirect_uri = "https://127.0.0.1"  # Must match authorization URL

headers = {
    'Authorization': f'Basic {base64.b64encode(f"{app_key}:{app_secret}".encode()).decode()}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': redirect_uri  # CRITICAL: Must match
}

response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)
print(response.status_code)
print(response.json())
```

---

## ✅ Verification Checklist

Before running the test:

- [ ] Schwab Developer account created
- [ ] App status is "Ready for Use" (not "Approved - Pending")
- [ ] Callback URL in portal is: `https://127.0.0.1`
- [ ] APP_KEY is 32 characters
- [ ] APP_SECRET is 16 characters
- [ ] Both credentials in `.env` file
- [ ] CALLBACK_URL in `.env` is: `https://127.0.0.1`
- [ ] Thinkorswim (TOS) enabled on Schwab account

---

## 🚀 Next Steps After Success

Once you have `tokens.json`:

### 1. Test Market Data
```bash
python backend/app/schwab_api.py
```

### 2. Verify Token Refresh
Tokens expire in 30 minutes. The system should auto-refresh using the refresh token.

### 3. Integrate with Backend
The API service will automatically use `tokens.json` for all requests.

---

## 📊 What Changed?

### Before (Incorrect)
```python
callback_url = "https://localhost:8000/api/auth/schwab/callback"
redirect_uri = callback_url  # ❌ Doesn't match portal
```

### After (Correct - Based on Schwab Support)
```python
callback_url = "https://127.0.0.1"  # ✅ Matches portal exactly
redirect_uri = callback_url  # ✅ Correct
```

**Why:** OAuth 2.0 requires exact match between:
1. Redirect URI in developer portal
2. Redirect URI in authorization request
3. Redirect URI in token exchange request

---

## 🆘 Still Having Issues?

### Check These:

1. **App Status**
   ```
   Go to: https://beta-developer.schwab.com/dashboard
   Status must be: "Ready for Use"
   ```

2. **Credentials Length**
   ```bash
   echo $APP_KEY | wc -c  # Should be 32
   echo $APP_SECRET | wc -c  # Should be 16
   ```

3. **Callback URL Exact Match**
   ```
   Portal: https://127.0.0.1
   .env:   https://127.0.0.1
   Code:   https://127.0.0.1
   
   All three MUST be identical
   ```

4. **Time Sensitivity**
   - Authorization code expires in ~5 minutes
   - Complete OAuth flow quickly
   - If it expires, get a new code

---

## 📝 Summary

**The Fix:** Use `redirect_uri=https://127.0.0.1` everywhere, matching your developer portal setting exactly.

**Test Command:**
```bash
python backend/test_schwab_connection.py
```

**Success Indicators:**
- ✅ Tokens saved to `tokens.json`
- ✅ Access token present
- ✅ Refresh token present
- ✅ Can fetch market data

---

**Last Updated:** December 23, 2024  
**Based On:** Schwab Developer Support feedback about redirect_uri matching
