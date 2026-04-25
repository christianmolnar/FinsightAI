# f.insight.AI - Standard Port Configuration

**Port Assignments** (to avoid conflicts):

## Local Development

| Service | Port | URL | Notes |
|---------|------|-----|-------|
| **Backend (FastAPI)** | `8000` | `http://localhost:8000` | Main API server |
| **Frontend (React)** | `3000` | `http://localhost:3000` | Web UI |
| **Slow Hand Studio** | `4000` | `http://localhost:4000` | Separate project (avoid conflict) |

## Production

| Service | URL |
|---------|-----|
| **Backend** | `https://finsightai-production-442e.up.railway.app` |
| **Frontend** | `https://www.f-insight.ai` |

---

## How to Start Services

### Backend (Port 8000)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Or use VS Code task**: `Start Backend`

### Frontend (Port 3000)
```bash
cd frontend
PORT=3000 npm start
```

**Or use VS Code task**: Create task in `.vscode/tasks.json`:
```json
{
  "label": "Start Frontend",
  "type": "shell",
  "command": "cd frontend && PORT=3000 npm start",
  "isBackground": true,
  "problemMatcher": []
}
```

---

## Port Configuration Files

### Backend Port
Set in `backend/app/main.py`:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### Frontend Port
Set via environment variable:
```bash
PORT=3000 npm start
```

Or create `frontend/.env`:
```properties
PORT=3000
```

---

## Frontend API Configuration

The frontend is configured to call backend at:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

Set in `frontend/.env`:
```properties
REACT_APP_API_URL=http://localhost:8000
```

---

## Quick Start (Both Services)

Create a shell script `start-dev.sh`:
```bash
#!/bin/bash

# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../frontend
PORT=3000 npm start &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID (port 8000)"
echo "Frontend PID: $FRONTEND_PID (port 3000)"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait and cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
```

Make executable:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

---

## Current Status

✅ **Backend**: Running on `http://localhost:8000`  
✅ **Frontend**: Running on `http://localhost:3000`  
✅ **Ports Locked**: 8000 (backend), 3000 (frontend), 4000 (Slow Hand Studio)

---

## Troubleshooting

### Port Already in Use

**Backend (8000)**:
```bash
lsof -ti:8000 | xargs kill -9
```

**Frontend (3000)**:
```bash
lsof -ti:3000 | xargs kill -9
```

### Check What's Running
```bash
lsof -i :3000 -i :8000 | grep LISTEN
```
