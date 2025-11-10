# FinSight AI

A cloud-native financial forecast## Repository Structure
- `backend/` – FastAPI backend
- `frontend/` – React frontend
- `database/` – Database config and migrations
- `ml/` – Machine learning models and scripts
- `mockups/` – UI/UX diagrams and design assets
- `docs/` – **📚 All project documentation** (moved from root)

---

## 📚 Documentation

All project documentation has been organized in the [`docs/`](docs/) directory:

- **[Documentation Index](docs/README.md)** - Complete documentation overview
- **[Implementation Guide](docs/implementation.md)** - Detailed project history and progress tracking
- **[Architecture](docs/architecture.md)** - System architecture and components
- **[Features](docs/features.md)** - Feature specifications
- **[GCP Setup](docs/GCP-SETUP.md)** - Cloud deployment guide

## Contributing & Tracking Progress
- For detailed progress, history, and next steps, see [`docs/implementation.md`](docs/implementation.md)
- Use [`docs/journal.md`](docs/journal.md) for daily logs or brainstorming
- Update documentation in the `docs/` directory as you develop

---

*For comprehensive documentation, see the [`docs/`](docs/) directory.*helps users track their portfolios and receive intelligent, model-based recommendations.

## Goals
- Predict stock and bond performance
- Visualize profit/loss metrics and recommendations
- Continuously evaluate and improve models

---

## Solution Overview

**FinSight AI** is a full-stack, cloud-native platform for financial forecasting and portfolio analytics. It provides:
- A FastAPI backend for serving data, analytics, and ML-powered recommendations
- A React frontend for interactive dashboards and user experience
- A Postgres database for persistent storage
- Docker-based orchestration for easy local development and deployment

### Key Features
- REST API for financial data and model results
- Interactive dashboards and visualizations
- Modular architecture for easy extension (ML, analytics, etc.)
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
