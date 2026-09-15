# SIH26165 — 5-Minute Live Presentation & Demo Script

**Project**: AI/NLP Engine to Detect Serious Injury & Fatality (SIF) Precursors for Oil India Limited (OIL) HSE Safety Portal  
**Target Duration**: 5 to 7 minutes  

---

## Pre-Demo Checklist & Startup Commands

1. **Verify Backend**:
   ```bash
   cd D:\SIH26165\SIH26165-SIF-Precursor-AI\backend
   .\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *Health Check*: `http://127.0.0.1:8000/health` → `{"status": "healthy", "database": "connected"}`

2. **Verify Frontend**:
   ```bash
   cd D:\SIH26165\SIH26165-SIF-Precursor-AI\dashboard
   npm run dev
   ```
   *Portal URL*: `http://127.0.0.1:5173/`

---

## Live Demonstration Sequence

### Step 1: Landing Page & Authenticated Sign In (0:00 - 0:45)
- Open `http://127.0.0.1:5173/`.
- Show the public **OIL HSE Intelligence Platform Landing Page**.
- Click **Sign In**.
- Enter credentials: `officer@oil.in` / `password123`.
- Highlight Role-Based Access Control (RBAC): User is authenticated as `SAFETY_OFFICER`.

### Step 2: Live HSE Safety Dashboard (0:45 - 1:30)
- Navigate to **Dashboard**.
- Demonstrate real-time analytics powered directly by MongoDB:
  - Total Reports, SIF Precursor Count, Risk Breakdown (Low, Medium, High, Critical).
  - Department distribution, Location distribution, and Risk trend charts.
- Point out the active AI Model Status Badge (`REAL_MODEL` / `TF-IDF + Logistic Regression`).

### Step 3: Submitting a High-Risk Safety Report (Scenario A - Confined Space) (1:30 - 2:15)
- Click **New Report**.
- Fill out the form:
  - **Report Type**: `UNSAFE_ACT`
  - **Department**: `Operations`
  - **Location**: `Processing Plant A`
  - **Description**: `"Worker entered confined space vessel without gas testing prior to entry."`
- Click **Submit Report**.

### Step 4: AI/NLP Precursor Pipeline Execution (2:15 - 3:30)
- Open the newly generated report detail page and click **Run AI Engine**.
- Highlight the 5 integrated analysis outputs:
  1. **SIF Precursor Status**: `SIF PRECURSOR DETECTED` (Red Alert Banner).
  2. **Explainable Safety Context**: Displays `Context Type: UNSAFE_BEHAVIOR` and extracted phrase `"without gas testing"`.
  3. **Risk Matrix**: Score `20 / 25` → `CRITICAL` risk level.
  4. **Life-Saving Rule Mapping**: Automatically mapped to `LSR-01` (*Confined Space Entry*).
  5. **Pattern Analysis**: Identifies activity and barrier failure indicators.
  6. **Preventive Recommendations**: Displays immediate and long-term action items.

### Step 5: Demonstrating Safety Context Correctness (Scenario C - Safe Compliance) (3:30 - 4:15)
- Submit a second report:
  - **Description**: `"Worker completed gas testing before entering confined space and used required PPE."`
- Run AI Analysis:
  - Show how the raw ML prediction (`SIF = True` due to "confined space" keywords) is preserved for auditability, but the **Safety Context Layer** adjusts the final assessment:
  - **Context Type**: `SAFE_COMPLIANCE`
  - **Final Assessment**: `NO SIF PRECURSOR` (Green Banner)
  - **Risk Level**: `LOW` (Score: 2 / 25)
  - **Reason Banner**: Explains transparently that safe procedures were completed.

### Step 6: Corrective Action Assignment & Workflow (4:15 - 5:00)
- Assign a corrective action:
  - **Description**: *"Inspect vessel V-101 isolation valves and re-calibrate gas detectors."*
  - **Assigned To**: `engineer@oil.in`
- Update action status from `PENDING` → `IN_PROGRESS` → `COMPLETED`.
- Return to **Dashboard** to show live updates in open action counters and audit logs.
- Click **Logout** to return safely to the public Home landing page.

---

## Key Talking Points for Judges & Evaluators

1. **Zero Fabrication**: Every AI inference, risk calculation, rule mapping, and chart is generated live from real code and real MongoDB data.
2. **Explainable AI**: AI model confidence is decoupled from risk severity. Raw ML model predictions are preserved alongside domain context adjustments.
3. **No Teammate Modules Overwritten**: Member 1 (ML Model), Member 2 (Life-Saving Rules), and Member 3 (Pattern Analysis) work harmoniously through a unified API facade.
