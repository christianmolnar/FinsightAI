# FInsightAI - Autonomous Trading Agent

**Intelligent, autonomous trading agent that executes real-time trades using Charles Schwab API, social sentiment analysis, and advanced market intelligence.**

*Productivity Multiplier: 1 AI Agent Hour = 80 Human Hours*

## 🚀 Quick Start

### Local Development
```bash
# 1. Install PostgreSQL locally
brew install postgresql
brew services start postgresql

# 2. Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set up frontend  
cd frontend
npm install

# 4. Configure environment
cp .env.example .env
# Edit .env with your Schwab API credentials

# 5. Run services
# Terminal 1: Backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
npm start
```

### Production Deployment (Railway)
- See [Implementation Plan](docs/implementation-plan.md) Phase 5
- Deploy to Railway for production trading

## 🧠 Core Capabilities

### Autonomous Trading
- **Real-time Market Analysis**: Technical & fundamental analysis
- **AI Decision Engine**: Multi-factor signal processing
- **Risk Management**: Automated position sizing and stop-losses
- **Trade Execution**: Direct integration with Charles Schwab API

### Market Intelligence
- **Live Data Feeds**: Real-time market data and economic indicators  
- **Sentiment Analysis**: Social media and news sentiment tracking
- **Pattern Recognition**: Advanced market pattern detection
- **Performance Analytics**: Real-time P&L and risk metrics

### User Experience
- **Beautiful Dashboard**: Modern React interface with real-time charts
- **Portfolio Visualization**: Interactive portfolio and performance charts
- **Trade Management**: Intuitive trade history and analytics
- **Mobile Responsive**: Optimized for all devices

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │  FastAPI        │    │  PostgreSQL     │
│   :3000         │◄──►│  Trading Engine │◄──►│  Market Data    │
│                 │    │  :8000          │    │  :5432          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Charles Schwab │
                    │  Trading API    │
                    └─────────────────┘
```

## 🎯 Development Progress

**Current Phase**: Foundation Setup (Phase 1)
**Next Milestone**: Market Data Integration (Phase 2)

- [ ] ✅ Docker removed, local development ready
- [ ] 🔄 PostgreSQL setup and database models
- [ ] 📋 FastAPI backend with authentication  
- [ ] 🎨 React frontend with modern UI
- [ ] 🔌 Charles Schwab API integration

See [Implementation Plan](docs/implementation-plan.md) for complete roadmap.

## 📁 Repository Structure

- `backend/` – FastAPI trading engine and API
- `frontend/` – React dashboard and user interface
- `ml/` – Machine learning models and analysis
- `CNS/` – Central Nervous System (AI brain, memory, reflexes)
- `docs/` – Complete project documentation
- `database/` – Database migrations and setup

## 📚 Documentation

- **[Implementation Plan](docs/implementation-plan.md)** - Complete development roadmap
- **[Agent Guidelines](docs/AGENTS.md)** - AI development standards
- **[Architecture](docs/architecture.md)** - System design and components  
- **[Capabilities](CNS/brain/capabilities.md)** - Core trading capabilities
- **[Features](docs/features.md)** - Detailed feature specifications

## 🔒 Security & Risk

- **Secure API Integration**: OAuth2 with Charles Schwab
- **Risk Management**: Automated position limits and stop-losses
- **Audit Trail**: Complete logging of all trading decisions
- **Environment Security**: Encrypted credentials and secure deployment

## 🚀 Next Steps

1. **Complete Phase 1**: Foundation setup with local PostgreSQL
2. **Integrate Schwab API**: Real-time market data and trading
3. **Build Trading Engine**: Autonomous decision making
4. **Deploy to Railway**: Production-ready deployment

---

*Building the future of autonomous trading, one intelligent decision at a time.*
- Ready for cloud or on-prem deployment

---

## Quick Start

1. **Start all services:**
   ```powershell
   docker-compose up --build
   ```
2. **Backend (local dev):**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
3. **Frontend:**
   - Visit http://localhost:3000
4. **Backend API Docs:**
   - Visit http://localhost:8000/docs

---

## Repository Structure
- `backend/` – FastAPI backend
- `frontend/` – React frontend
- `database/` – Database config and migrations
- `ml/` – Machine learning models and scripts
- `mockups/` – UI/UX diagrams and design assets
- `implementation.md` – Detailed project history, progress log, and tracking

---

## Contributing & Tracking Progress
- For detailed progress, history, and next steps, see `implementation.md`.
- Use `journal.md` for daily logs or brainstorming.
- Update this README if the solution’s purpose or architecture changes.

---

*For detailed implementation steps and ongoing progress, see `implementation.md`.*
