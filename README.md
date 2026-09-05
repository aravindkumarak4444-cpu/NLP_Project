# SIH26165 – AI/NLP Engine to Detect SIF Precursors in Oil India Limited (OIL) Safety Reports

**Problem Statement ID:** SIH26165  
**Project:** AI/NLP Engine to Detect Serious Injury & Fatality (SIF) Precursors in OIL Unsafe-Act, Unsafe-Condition and Near-Miss Reports  
**Organization:** Oil India Limited (OIL) / Smart India Hackathon  

---

## 1. Project Overview

This repository contains the complete, production-ready backend integration layer, AI adapters, risk evaluation engines, Life-Saving Rule mappers, and analytical pattern detection services for Project SIH26165.

The backend acts as the central orchestrator connecting:
- Safety Officers & Field Workers $\rightarrow$ React HSE Dashboard (`dashboard/`)
- Natural Language Input $\rightarrow$ FastAPI Backend (`backend/`)
- Raw Description $\rightarrow$ SIF Precursor Detection AI Model (`ai_model/`)
- Detected Hazards $\rightarrow$ Life-Saving Rules Engine (`rule_mapping/`)
- Severity & Likelihood $\rightarrow$ 5x5 Risk Matrix Assessment Engine
- Incident Data $\rightarrow$ Pattern & Trend Analysis Engine (`pattern_analysis/`)
- Database Persistence $\rightarrow$ MongoDB Atlas (`oil_sif` database)

---

## 2. Repository Structure

```text
SIH26165-SIF-Precursor-AI/
├── backend/                        # FastAPI Backend & Integration Layer
│   ├── app/
│   │   ├── main.py                 # FastAPI Application & Lifespan Handler
│   │   ├── config.py               # Pydantic Settings & Environment Loader
│   │   ├── api/                    # API v1 Routers (auth, reports, analysis, dashboard, rules, patterns, health)
│   │   ├── auth/                   # JWT Auth, Password Hashing & RBAC
│   │   ├── database/               # Motor MongoDB Async Connection & Repositories
│   │   ├── integrations/           # Teammate Adapters (ai_adapter, rule_adapter, pattern_adapter)
│   │   ├── middleware/             # Error Handlers & Rate Limiter
│   │   ├── models/                 # PyMongo & Domain Pydantic Models
│   │   ├── schemas/                # OpenAPI Request/Response Schemas
│   │   ├── services/               # Core Business Services (risk, recommendations, report, etc.)
│   │   └── utils/                  # UUID Generator & Timestamp Helpers
│   ├── ml/models/                  # AI Model Binaries (.pkl)
│   ├── tests/                      # Pytest Test Suite
│   ├── Dockerfile                  # Production Docker Build Setup
│   ├── docker-compose.yml          # Container Orchestration with MongoDB
│   ├── .env.example                # Backend Environment Variable Template
│   └── requirements.txt            # Python Dependencies
├── ai_model/                       # Member 1 AI/NLP Model Development Workspace
│   ├── notebooks/                  # Training Notebooks
│   └── src/                        # Model Training & Prediction Scripts
├── rule_mapping/                   # Member 2 Life-Saving Rules Workspace
├── pattern_analysis/               # Member 3 Pattern Detection & Data Pipeline Workspace
├── dashboard/                      # Member 5 React HSE Dashboard Workspace
├── data/                           # Sample Datasets & Reports
├── docs/                           # Architecture Diagrams & Documentation
├── .env.example                    # Root Environment Template
├── requirements.txt                # Root Python Dependencies
└── README.md                       # Main Project Documentation
```

---

## 3. Quick Start Instructions

### Prerequisites
- Python 3.12+
- MongoDB Atlas cluster or local MongoDB instance (Port 27017)
- Docker Desktop (Optional)

### Installation

1. **Clone & Setup Environment:**
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Set `MONGODB_URI` to your MongoDB Atlas connection string:
   ```env
   MONGODB_URI=mongodb+srv://<username>:<password>@<cluster_host>/oil_sif?retryWrites=true&w=majority
   DATABASE_NAME=oil_sif
   JWT_SECRET=super_secret_sif_precursor_key_change_in_production_2026
   ```

4. **Launch Backend Service:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access Interactive API Documentation:**
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc UI: [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

## 4. Team Integration Guide

| Team Role | Responsibility | Integration Point |
| :--- | :--- | :--- |
| **Member 1 (AI/NLP Lead)** | SIF Precursor Detection Model | Place trained model binary at `backend/ml/models/model.pkl` or populate `ai_model/src/predict.py`. `AIAdapter` will automatically load it. |
| **Member 2 (NLP Specialist)** | Life-Saving Rule Mapping | Populate `rule_mapping/` or update `RuleAdapter` in `backend/app/integrations/rule_adapter.py`. |
| **Member 3 (Data Engineer)** | Pattern Detection & Data Pipeline | Populate `pattern_analysis/` or update `PatternAdapter` in `backend/app/integrations/pattern_adapter.py`. |
| **Member 4 (Backend Lead)** | APIs, Auth & Integration Layer | Implemented core FastAPI backend, MongoDB Atlas integration, Pytest suite, and Security layer. |
| **Member 5 (Frontend Lead)** | React HSE Dashboard | Connect to REST endpoints under `http://localhost:8000/api/v1` using JWT bearer tokens. |
| **Member 6 (QA & Deployment)** | Testing & Documentation | Run `pytest backend/tests` and deploy via `docker-compose up --build`. |

---

## 5. Automated Testing

Run the automated Pytest test suite:
```bash
pytest backend/tests -v
```
All 9 core integration test suites covering Authentication, Safety Report Lifecycle, AI/NLP Analysis Pipeline, and HSE Dashboard Aggregations pass cleanly.
