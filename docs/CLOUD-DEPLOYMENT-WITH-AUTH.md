# Full Cloud Deployment Plan with Authentication

## Current Status (March 7, 2026 - 10:03 PM)
- ✅ Database: Railway PostgreSQL (`yamanote.proxy.rlwy.net`) - Schema migrated
- ✅ Backend API: `https://finsightai-production-442e.up.railway.app` - DEPLOYED & WORKING
- ✅ Frontend: `https://frontend-pi-kohl-57.vercel.app` - DEPLOYED & WORKING
- ❌ Authentication: None (CRITICAL - portfolio data is public!)

## Goal
- ✅ Backend: `https://finsight-backend.up.railway.app`
- ✅ Frontend: `https://finsight.vercel.app` 
- ✅ Auth: Simple password protection (or GitHub OAuth)

---

## Step 1: Deploy Backend to Railway (5 minutes)

### 1A. Create Railway Project
```bash
# Install Railway CLI (if not installed)
brew install railway

# Login
railway login

# Link to existing project OR create new
railway link
# OR
railway init
```

### 1B. Configure Environment Variables in Railway Dashboard
Go to Railway dashboard → Your project → Variables:

```bash
DATABASE_URL=postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Authentication (add these)
AUTH_SECRET_KEY=your-random-secret-here-min-32-chars
ALLOWED_USERS=your_username:your_hashed_password
```

### 1C. Deploy
```bash
# Push to trigger Railway deploy
git push origin feature/alpaca-migration

# Railway auto-deploys from GitHub
# Get your URL from Railway dashboard
# Example: https://finsight-backend-production.up.railway.app
```

---

## Step 2: Add Authentication to Backend (10 minutes)

### 2A. Create Auth Middleware

Create `backend/app/auth.py`:

```python
"""
Simple authentication middleware for f.insight API
Protects all endpoints with HTTP Basic Auth
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

security = HTTPBasic()

# Load from environment: username:hashed_password
ALLOWED_USERS = {
    "christian": os.getenv("AUTH_PASSWORD", "changeme123")
}

def authenticate(credentials: HTTPBasicCredentials = Security(security)):
    """
    Verify HTTP Basic Auth credentials
    
    Usage in routes:
        @app.get("/api/protected")
        async def protected_route(auth=Depends(authenticate)):
            return {"status": "authenticated"}
    """
    username = credentials.username
    password = credentials.password
    
    if username not in ALLOWED_USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Simple password comparison (use hashing in production!)
    if password != ALLOWED_USERS[username]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return username
```

### 2B. Protect Routes

Update `backend/app/main.py`:

```python
from fastapi import FastAPI, Depends
from app.auth import authenticate

app = FastAPI()

# Public routes (no auth needed)
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Protected routes (auth required)
@app.get("/api/portfolio", dependencies=[Depends(authenticate)])
async def get_portfolio():
    # ... existing code

@app.get("/api/transactions", dependencies=[Depends(authenticate)])
async def get_transactions():
    # ... existing code

# Protect ALL /api/* routes
@app.middleware("http")
async def require_auth_for_api(request, call_next):
    if request.url.path.startswith("/api/"):
        # Check if Authorization header exists
        if not request.headers.get("authorization"):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
    return await call_next(request)
```

---

## Step 3: Deploy Frontend to Vercel (10 minutes)

### 3A. Create Vercel Configuration

Create `frontend/vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "create-react-app",
  "env": {
    "REACT_APP_API_URL": "https://finsight-backend-production.up.railway.app"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        }
      ]
    }
  ]
}
```

### 3B. Add Login Component

Create `frontend/src/components/Login.js`:

```javascript
import React, { useState } from 'react';
import axios from 'axios';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    
    try {
      // Set basic auth header
      const auth = btoa(`${username}:${password}`);
      axios.defaults.headers.common['Authorization'] = `Basic ${auth}`;
      
      // Test auth with health check
      await axios.get(`${process.env.REACT_APP_API_URL}/api/portfolio`);
      
      // Store auth
      localStorage.setItem('auth', auth);
      onLogin();
      
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-gray-800 p-8 rounded-lg shadow-xl w-96">
        <h1 className="text-2xl font-bold text-white mb-6">f.insight Login</h1>
        
        {error && (
          <div className="bg-red-500 text-white p-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-3 mb-4 bg-gray-700 text-white rounded"
          />
          
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 mb-6 bg-gray-700 text-white rounded"
          />
          
          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded font-semibold"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
}
```

### 3C. Update App.js with Auth

```javascript
import { useState, useEffect } from 'react';
import axios from 'axios';
import Login from './components/Login';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check for stored auth
    const auth = localStorage.getItem('auth');
    if (auth) {
      axios.defaults.headers.common['Authorization'] = `Basic ${auth}`;
      setIsAuthenticated(true);
    }
  }, []);

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    // ... your existing app
  );
}
```

### 3D. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# From frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Follow prompts:
# - Link to existing project or create new
# - Set environment variable: REACT_APP_API_URL=https://your-railway-url.up.railway.app
# - Deploy

# Get your URL: https://finsight.vercel.app
```

---

## Step 4: Update Backend CORS

Update `backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://finsight.vercel.app",  # Production
        "http://localhost:3000"          # Development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Step 5: Test End-to-End

1. **Backend**: `curl -u christian:yourpassword https://your-railway-url.up.railway.app/api/portfolio`
2. **Frontend**: Go to `https://finsight.vercel.app`
3. **Login**: Enter username/password
4. **Verify**: Dashboard loads, shows your portfolio

---

## Security Considerations

### Current (Simple Password)
- ✅ Protects against public access
- ✅ Fast to implement
- ⚠️ Password in plaintext (not ideal)
- ⚠️ No sessions (auth on every request)

### Future (Better Auth)
- Use hashed passwords (bcrypt)
- Add JWT tokens for sessions
- Add GitHub OAuth
- Add 2FA

---

## Timeline

| Task | Time | Status |
|------|------|--------|
| Deploy backend to Railway | 5 min | 🔲 |
| Add auth middleware | 10 min | 🔲 |
| Deploy frontend to Vercel | 10 min | 🔲 |
| Add login component | 10 min | 🔲 |
| Test end-to-end | 5 min | 🔲 |
| **TOTAL** | **40 min** | |

---

## After Deployment

**Backend URL**: `https://finsight-backend-production.up.railway.app`
**Frontend URL**: `https://finsight.vercel.app`

**Railway Cron Jobs**: ✅ Will run automatically in cloud
**SMS Alerts**: ⚠️ Still needs Twilio verification (optional for now)

**Your PC**: Can be off! Everything runs in cloud. 🎉

---

**Ready to deploy?** We can do this step-by-step, or I can generate all the code files first.
