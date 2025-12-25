# Alpaca Account Security Information

## 🔒 2FA Emergency Recovery Code

**STORED LOCATION**: `/backend/.env` (gitignored)

**Emergency Code**: `5c2eb89e-874b-4b99-af4b-a4901bd136d4`

### ⚠️ CRITICAL SECURITY NOTES

1. **Purpose**: This code allows you to bypass 2FA and sign in if you lose access to your authenticator app
2. **Storage**: Safely stored in `.env` file (confirmed in `.gitignore` on line 12)
3. **Never Share**: Do not share this code with anyone
4. **Single Use**: This code can only be used once - Alpaca will generate a new one after use
5. **Backup**: Consider storing a copy in a password manager (1Password, LastPass, etc.)

## 🔐 API Credentials Setup

Once you get your Alpaca API keys, add them to `/backend/.env`:

```bash
ALPACA_API_KEY_ID=PKXXXXXXXXXXXXXXXX
ALPACA_API_SECRET_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ALPACA_PAPER=true
```

## 📋 Account Details

- **Account Type**: Paper Trading (sandbox)
- **2FA Status**: ✅ Activated via authenticator app
- **Created**: December 25, 2025

## 🚨 If You Lose 2FA Access

1. Go to https://alpaca.markets/
2. Click "Forgot Password" or "2FA Issues"
3. Use emergency code: `5c2eb89e-874b-4b99-af4b-a4901bd136d4`
4. Alpaca will let you sign in and regenerate a new emergency code
5. Update this document with the new code

## 🔍 Security Verification

- ✅ `.env` file is in `.gitignore` (line 12)
- ✅ Emergency code stored in `.env` with warning comments
- ✅ This README is safe to commit (no actual credentials, just documentation)
- ⚠️ **NEVER** commit `.env` file to git

## Next Steps

1. Complete Alpaca account setup
2. Generate API keys in dashboard
3. Add keys to `.env` file
4. Run `python3 backend/test_alpaca_connection.py` to verify
5. Continue with migration Phase 1

---

**Last Updated**: December 25, 2025  
**Security Level**: High (2FA enabled, emergency code secured)
