# FinSight AI Documentation

Welcome to the FinSight AI documentation hub. This directory contains all project documentation organized by topic and component.

## 📚 Core Documentation

### Project Overview
- **[Main README](../README.md)** - Project overview and quick start guide
- **[Architecture](architecture.md)** - System architecture and infrastructure components
- **[Features](features.md)** - Feature specifications and requirements
- **[Models](models.md)** - ML models and algorithms documentation

### Implementation & Development  
- **[Implementation Guide](implementation.md)** - Detailed implementation guide and project history
- **[Development Journal](journal.md)** - Development progress and notes
- **[Evaluation Criteria](evaluation.md)** - Model evaluation and testing criteria

### Deployment & Operations
- **[GCP Setup](GCP-SETUP.md)** - Google Cloud Platform deployment guide

## 🏗️ Component Documentation

### Backend (FastAPI)
- **[Backend Guide](backend.md)** - Backend setup, API endpoints, and development
- **[Database Guide](database.md)** - Database schema, migrations, and setup

### Frontend (React)
- **[Frontend Guide](frontend.md)** - Frontend setup, components, and development

### Machine Learning
- **[ML Components](ml.md)** - Machine learning models, training, and deployment

### Design & Mockups
- **[Mockups](mockups.md)** - UI/UX designs and wireframes

## � AI Agent Configuration (CNS)

The **CNS (Cognitive Neural System)** directory contains AI agent configuration files that define the behavior, capabilities, and learning systems for the FInsightAI agent. These are **not user documentation** but rather **AI system configuration**:

- **[`../CNS/brain/`](../CNS/brain/)** - AI persona, capabilities, and behavioral definitions
- **[`../CNS/memory/`](../CNS/memory/)** - Memory architecture and private system links  
- **[`../CNS/reflexes/`](../CNS/reflexes/)** - Learning triggers and automated improvements

*Note: CNS files configure AI behavior and are separate from project documentation.*

## 📖 Documentation Guidelines

### For Developers
1. **Update documentation** as you implement new features
2. **Keep implementation.md** updated with progress logs
3. **Document API changes** in the backend guide
4. **Update architecture.md** when adding new components

### File Organization
```
docs/
├── README.md              # This index file
├── architecture.md        # System architecture
├── features.md           # Feature specifications  
├── models.md            # ML model documentation
├── implementation.md     # Implementation guide & history
├── journal.md           # Development journal
├── evaluation.md        # Evaluation criteria
├── GCP-SETUP.md         # Cloud deployment guide
├── backend.md           # Backend documentation
├── frontend.md          # Frontend documentation
├── database.md          # Database documentation
├── ml.md               # ML documentation
└── mockups.md          # Design documentation

CNS/                      # AI Agent Configuration (separate)
├── brain/               # AI capabilities & persona
├── memory/              # Memory management
└── reflexes/            # Learning & checks
```

## 🔗 Quick Links

- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Frontend App**: http://localhost:3000 (when frontend is running)
- **GitHub Repository**: [FinsightAI](https://github.com/christianmolnar/FinsightAI)

---

*Last updated: November 9, 2025*
