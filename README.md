# SIH26165 – AI/NLP Engine to Detect SIF Precursors in Oil India Limited (OIL) Safety Reports

**Problem Statement ID:** SIH26165  
**Project:** AI/NLP Engine to Detect Serious Injury & Fatality (SIF) Precursors in OIL Unsafe-Act, Unsafe-Condition and Near-Miss Reports  
**Organization:** Oil India Limited (OIL) / Smart India Hackathon  

---

> [!NOTE]
> **System Scope & Disclaimer**: The system identifies operational safety indicators, hazard categories, and potential Serious Injury & Fatality (SIF) precursors in industrial safety reports. It does not medically diagnose physical injury, burnout, or mental health conditions.

---

## 1. Project Overview

This repository contains the complete, production-ready full-stack web application, backend API integration layer, AI adapters, 5x5 risk evaluation matrix engines, Life-Saving Rule mappers, and analytical pattern detection services for Project SIH26165.

The system connects:
- **React HSE Dashboard (`dashboard/`)** $\rightarrow$ Frontend portal built with React 19, TypeScript, Vite, Tailwind CSS, and Recharts.
- **FastAPI Backend (`backend/`)** $\rightarrow$ Async REST API with Motor MongoDB connection, JWT auth, and role-based permissions (`WORKER`, `SAFETY_OFFICER`, `MANAGER`, `ADMIN`).
- **SIF Precursor AI Model (`ai_model/`)** $\rightarrow$ Member 1 ML model & text prediction pipeline.
- **Life-Saving Rules Engine (`rule_mapping/`)** $\rightarrow$ Member 2 keyword & rule mapping engine (`rules.json` / `mapper.py`).
- **Pattern & Trend Analysis (`pattern_analysis/`)** $\rightarrow$ Member 3 pattern analyzer (`analyzer.py` & SQLite persistence).
- **Database Persistence** $\rightarrow$ MongoDB Atlas (`oil_sif` database).

---

## 2. Repository Structure

```text
SIH26165-SIF-Precursor-AI/
├── backend/                        # FastAPI Backend & Integration Layer
│   ├── app/
│   │   ├── main.py                 # FastAPI Application & Lifespan Handler
│   │   ├── config.py               # Settings & Environment Loader
│   │   ├── api/                    # Routers (auth, reports, analysis, dashboard, rules, patterns, health)
│   │   ├── auth/                   # JWT Auth, Password Hashing & RBAC
│   │   ├── database/               # MongoDB Async Connection & Repositories
│   │   ├── integrations/           # Teammate Adapters (ai_adapter, rule_adapter, pattern_adapter)
│   │   ├── middleware/             # Error Handlers & Rate Limiter
│   │   ├── models/                 # PyMongo & Domain Pydantic Models
│   │   ├── schemas/                # Request/Response Schemas
│   │   ├── services/               # Services (risk, recommendations, report, etc.)
│   │   └── utils/                  # UUID Generator & Timestamp Helpers
│   ├── ml/models/                  # AI Model Binaries (.pkl)
│   ├── tests/                      # Pytest Test Suite
│   ├── Dockerfile                  # Docker Build Setup
│   ├── docker-compose.yml          # Container Orchestration with MongoDB
│   └── requirements.txt            # Python Dependencies
├── dashboard/                      # Member 5 React HSE Dashboard Workspace
│   ├── src/
│   │   ├── api/                    # Centralized Axios API Client
│   │   ├── components/             # Reusable UI Components
│   │   ├── context/                # AuthContext
│   │   ├── pages/                  # Pages (Dashboard, Reports, Analysis, Rules, Patterns, Actions, Users, Profile, Settings)
│   │   └── types/                  # TypeScript Interfaces
│   └── package.json
├── ai_model/                       # Member 1 AI/NLP Model Development Workspace
├── rule_mapping/                   # Member 2 Life-Saving Rules Workspace
├── pattern_analysis/               # Member 3 Pattern Detection & Data Pipeline Workspace
├── .env.example                    # Environment Template
└── README.md                       # Main Documentation
```

---

## 3. Quick Start Instructions

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- MongoDB instance (Local or MongoDB Atlas)

---

### Step A: Launch Backend Service (FastAPI)

```bash
cd backend

# 1. Activate environment and install dependencies
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Run FastAPI Backend Server
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### Step B: Launch Frontend Web Portal (React + Vite)

```bash
cd dashboard

# 1. Install dependencies
npm install

# 2. Start Vite Development Server
npm run dev
```

- **Web Application Portal**: [http://localhost:5173](http://localhost:5173)

---

## 4. Default Demo Accounts

| Role | Username / Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Safety Officer** | `testuser` / `test@example.com` | `Test@12345` | Review & analyze reports, assign corrective actions, manage status lifecycles |
| **Administrator** | `admin` / `admin@oil.in` | `password123` | Full admin privileges, user directory management, report deletion |

---

## 5. Automated Testing

### Run Backend Tests (`pytest`)
```bash
cd backend
.\venv\Scripts\python.exe -m pytest -v
```

### Run Pattern Analysis Tests (`unittest`)
```bash
cd pattern_analysis
..\backend\venv\Scripts\python.exe test_analyzer.py
```

### Run Frontend Production Build (`tsc -b && vite build`)
```bash
cd dashboard
npm run build
```

---

## 6. Web Application Portal Routes

- `/login` — User authentication portal
- `/register` — HSE personnel registration portal
- `/dashboard` — Real-time OIL HSE intelligence dashboard & trends
- `/reports` — Filterable safety reports directory with pagination
- `/reports/new` — Report submission form for Unsafe Act, Unsafe Condition, or Near Miss
- `/reports/:id` — Report detail view with status lifecycle controls & corrective actions
- `/analysis/:id` — AI/NLP model diagnostics, evidence extraction & confidence scores
- `/rules` — Official Life-Saving Rules directory (Member 2 mapping)
- `/patterns` — Incident pattern analysis & SIF trend insights (Member 3 mapping)
- `/actions` — Corrective action item tracker across all sites
- `/users` — Registered HSE personnel directory
- `/profile` — User profile & role privileges checklist
- `/settings` — AI engine mode status & system health diagnostics
