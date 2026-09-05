# OIL SIF Precursor Detection API - FastAPI Backend & Integration Layer

**Problem Statement ID:** SIH26165  
**Project:** AI/NLP Engine to Detect Serious Injury & Fatality (SIF) Precursors in OIL Unsafe-Act, Unsafe-Condition and Near-Miss Reports  
**Organization:** Oil India Limited (OIL) / Smart India Hackathon  

---

## 1. Project Overview

This repository contains the production-ready FastAPI backend and central integration engine for SIH26165. The backend acts as the orchestrator connecting safety officers, the React HSE dashboard, NLP/AI models, Oil India Limited Life-Saving Rules, pattern analysis engines, and MongoDB storage.

Key Capabilities:
- **Natural Language Safety Report Ingestion** (Near-Miss, Unsafe Act, Unsafe Condition).
- **Decoupled AI/NLP Integration Adapter** for SIF Precursor classification & high-energy hazard extraction.
- **Explainable 5x5 SIF Risk Engine** (Severity $\times$ Likelihood) separating risk matrix score from AI confidence.
- **Life-Saving Rules Mapping** (IOGP / OIL standards).
- **Hazard-Specific Action Recommendation Generator**.
- **Incident Pattern Detection & Trend Analytics**.
- **Role-Based JWT Authorization** (WORKER, SAFETY_OFFICER, MANAGER, ADMIN).
- **Report Lifecycle State Machine** (SUBMITTED $\rightarrow$ AI_ANALYZED $\rightarrow$ REVIEW_REQUIRED $\rightarrow$ ACTION_ASSIGNED $\rightarrow$ IN_PROGRESS $\rightarrow$ RESOLVED $\rightarrow$ VERIFIED $\rightarrow$ CLOSED).

---

## 2. System Architecture

```text
User / Safety Officer
        ↓
React HSE Frontend (Port 5173)
        ↓
FastAPI Backend Integration Layer (Port 8000)
        ↓
Input Validation & Security Headers / CORS / Rate Limiter
        ↓
MongoDB Persistence (`oil_sif` database)
        ↓
AI / NLP Pipeline Orchestration Engine
  ├── AIAdapter → Member 1 Model / NLP Baseline Engine
  ├── RuleAdapter → Member 2 Life-Saving Rules Mapping
  ├── RiskEngine → 5x5 Matrix SIF Risk Evaluator
  └── PatternAdapter → Member 3 Pattern & Trend Engine
        ↓
Interactive HSE Dashboard / Alerts / Action Tracking
```

---

## 3. Technology Stack

- **Language:** Python 3.12+
- **Framework:** FastAPI, Uvicorn
- **Validation:** Pydantic v2, Pydantic Settings
- **Database:** MongoDB (Motor async driver & PyMongo)
- **Security:** PyJWT, Passlib (Bcrypt), CORS, Rate Limiting
- **Testing:** Pytest, pytest-asyncio, HTTPX
- **Containerization:** Docker, Docker Compose

---

## 4. Folder Structure

```text
backend/
├── app/
│   ├── main.py                     # FastAPI application setup, lifecycle & middlewares
│   ├── config.py                   # Environment settings loader
│   ├── api/
│   │   ├── router.py               # Central API Router (/api/v1)
│   │   └── routes/                 # Route controllers (auth, reports, analysis, dashboard, rules, patterns, health)
│   ├── schemas/                    # Pydantic v2 schemas
│   ├── models/                     # Domain models
│   ├── services/                   # Business logic services (risk, recommendations, report, auth, etc.)
│   ├── integrations/               # Adapter interfaces (AIAdapter, RuleAdapter, PatternAdapter)
│   ├── database/                   # MongoDB motor connection & repositories
│   ├── auth/                       # JWT, password hashing & RBAC dependencies
│   ├── middleware/                 # Exception handler & rate limiting
│   └── utils/                      # ID generators & UTC timestamp helpers
├── ml/
│   └── models/                     # ML binary model storage (.pkl)
├── tests/                          # Pytest suite
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 5. Installation & Setup

### Prerequisites
- Python 3.12+
- MongoDB 7.0+ (Local or Docker)
- Docker Desktop (Optional)

### Local Environment Setup

1. **Clone & Navigate:**
   ```bash
   cd backend
   ```

2. **Create Virtual Environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

---

## 6. Running the Application

### Running Locally with Uvicorn
Ensure MongoDB is running locally at `mongodb://localhost:27017`:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger API Docs: `http://localhost:8000/docs`
- ReDoc API Documentation: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

### Running with Docker Compose
```bash
docker-compose up --build -d
```

---

## 7. API Endpoint Overview

| Method | Endpoint | Description | Role Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service & DB Health Status | Public |
| `POST` | `/api/v1/auth/register` | Register new user | Public |
| `POST` | `/api/v1/auth/login` | Login & receive JWT token | Public |
| `GET` | `/api/v1/auth/me` | Fetch active user profile | Authenticated |
| `POST` | `/api/v1/reports` | Submit safety report | Authenticated |
| `GET` | `/api/v1/reports` | List & filter safety reports | Authenticated |
| `GET` | `/api/v1/reports/{id}` | Get report detail | Authenticated |
| `PUT` | `/api/v1/reports/{id}` | Update report detail | Authenticated |
| `PATCH` | `/api/v1/reports/{id}/status` | Transition report status | Safety Officer / Admin |
| `POST` | `/api/v1/reports/{id}/actions` | Assign corrective action item | Safety Officer / Admin |
| `POST` | `/api/v1/analysis/{id}` | Execute AI/NLP Analysis Pipeline | Authenticated |
| `GET` | `/api/v1/dashboard/summary` | Aggregate HSE Dashboard Summary | Authenticated |
| `GET` | `/api/v1/dashboard/trends` | SIF Precursor Trend Analytics | Authenticated |
| `GET` | `/api/v1/dashboard/patterns` | Incident Pattern Analytics | Authenticated |
| `GET` | `/api/v1/rules` | List Life-Saving Rules | Authenticated |

---

## 8. Team Member Integration Instructions

### Member 1 (AI / NLP Model)
Place trained model binaries under `ml/models/model.pkl` or update `AIAdapter` in `app/integrations/ai_adapter.py`. The adapter expects:
```python
def analyze(text: str) -> AIAnalysisModel
```

### Member 2 (Life-Saving Rules Mapping)
Update `RuleAdapter` in `app/integrations/rule_adapter.py` to extend rules database or plug in custom mapping logic:
```python
def map_rule(hazard_category, unsafe_act, unsafe_condition) -> LifeSavingRuleModel
```

### Member 3 (Data Pipeline & Pattern Detection)
Update `PatternAdapter` in `app/integrations/pattern_adapter.py` to integrate advanced spark/pandas pipeline aggregations:
```python
def detect_patterns(reports) -> PatternAnalysisResult
```

### Member 5 (Frontend Integration)
Point your React API base URL to `http://localhost:8000/api/v1`. All endpoints return standard JSON responses and require `Authorization: Bearer <jwt_token>` header for protected routes.

---

## 9. Testing Suite

Run full automated pytest test suite:
```bash
pytest -v
```

---

## 10. Deployment & Production Readiness

- Set `DEBUG=false` in `.env`.
- Replace `JWT_SECRET` with a secure 256-bit secret string.
- Restrict `FRONTEND_URL` in `.env` to trusted domains (e.g. `https://hse.oilindia.in`).
- Use Docker Compose or Kubernetes for production container orchestration.