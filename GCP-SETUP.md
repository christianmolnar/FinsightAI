# FinsightAI Project Setup & Deployment Guide (Google Cloud)

## Overview
FinsightAI is a cloud-native financial forecasting platform. This guide covers setup, development, and deployment using Google Cloud Platform (GCP).

---

## 1. Folder Structure
```
/finsight-ai
├── backend/           # FastAPI backend (Python)
├── frontend/          # React frontend (JavaScript/TypeScript)
├── ml/                # ML microservices, model training, artifacts
├── database/          # DB migrations, seeders, schema
├── mockups/           # UI/UX diagrams, PNGs
├── .env               # Environment variables
├── docker-compose.yml # Multi-service orchestration
├── README.md
├── architecture.md
├── features.md
├── models.md
├── evaluation.md
├── implementation.md
├── journal.md
```

---

## 2. Prerequisites
- Docker Desktop (Windows/Mac/Linux)
- Python 3.10+
- Node.js (v18+ recommended)
- Google Cloud account
- GCP SDK (`gcloud` CLI)

---

## 3. Environment Variables (`.env`)
```
POSTGRES_USER=finsight
POSTGRES_PASSWORD=finsight
POSTGRES_DB=finsight
DATABASE_URL=postgresql://finsight:finsight@db:5432/finsight
SECRET_KEY=your_secret_key_here
ENV=development
REACT_APP_API_URL=http://localhost:8000
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
GCS_BUCKET_NAME=your-bucket-name
```

---

## 4. Running Locally
1. Clone the repo and `cd` into the project root.
2. Ensure `.env` is configured as above.
3. Start all services:
   ```powershell
   docker-compose up --build
   ```
4. Access:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - Database: localhost:5432 (PostgreSQL)

---

## 5. Google Cloud Integration
- **Storage:** Use Google Cloud Storage (GCS) for model artifacts, user uploads, etc.
- **Database:** For production, use Google Cloud SQL (PostgreSQL) and update `DATABASE_URL` accordingly.
- **Credentials:** Download your GCP service account key and mount it as `credentials.json` in your containers.
- **Deployment:** Use Google Cloud Run, GKE, or App Engine for backend/frontend deployment.
- **Monitoring:** Use Google Cloud Monitoring and Logging.

---

## 6. Useful GCP Services
- **GCS:** Object storage for files, models, and assets.
- **Cloud SQL:** Managed PostgreSQL database.
- **Cloud Run:** Serverless container hosting for backend/frontend.
- **Artifact Registry:** Store Docker images.
- **IAM:** Manage service accounts and permissions.

---

## 7. References & Next Steps
- Update all code and docs to use GCP (not OVHCloud).
- Set up GCP billing and enable required APIs.
- Deploy containers to Cloud Run or GKE.
- Set up CI/CD with GitHub Actions and GCP.
- For more, see [Google Cloud Docs](https://cloud.google.com/docs).

---

## 8. Troubleshooting
- Ensure Docker is running.
- Check `.env` for correct credentials.
- Use `gcloud auth login` to authenticate your CLI.
- For GCP errors, check IAM permissions and API enablement.

---

*This guide is tailored for Google Cloud Platform. Update as your architecture evolves!*
