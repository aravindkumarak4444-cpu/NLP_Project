# SIH26165 — Mobile Application Reusable Backend API Specification

This document defines the unified REST API contract exposed by the FastAPI backend (`http://127.0.0.1:8000/api/v1`) for future mobile client integration (React Native / Flutter / Android).

The backend endpoints, JWT authentication tokens, role-based access control (RBAC), and MongoDB persistence are identical for both the Web Portal and Mobile clients.

---

## 1. Authentication & Session Management

### POST `/api/v1/auth/register`
- **Description**: Registers a new mobile user account (Worker / Safety Officer / Manager).
- **Request Body**:
  ```json
  {
    "username": "worker_rajesh",
    "email": "rajesh@oil.in",
    "password": "Password123!",
    "full_name": "Rajesh Kumar",
    "role": "WORKER",
    "department": "Operations"
  }
  ```
- **Response** (`201 Created`): Returns user object.

### POST `/api/v1/auth/login`
- **Description**: Authenticates user and issues OAuth2 JWT Bearer Token.
- **Request Body**:
  ```json
  {
    "email": "rajesh@oil.in",
    "password": "Password123!"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  }
  ```

### GET `/api/v1/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Description**: Fetches current authenticated user profile and permissions.

---

## 2. Safety Report Lifecycle Endpoints

### POST `/api/v1/reports`
- **Description**: Submits a new Unsafe-Act, Unsafe-Condition, or Near-Miss report.
- **Request Body**:
  ```json
  {
    "report_type": "UNSAFE_ACT",
    "description": "Worker entered vessel V-101 without gas testing prior to entry.",
    "location": "Processing Plant A",
    "department": "Operations"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "report_id": "REP-894102",
    "status": "SUBMITTED",
    "created_at": "2026-09-15T22:00:00Z"
  }
  ```

### GET `/api/v1/reports`
- **Query Parameters**: `page=1&limit=20&status=SUBMITTED&department=Operations`
- **Description**: Returns paginated list of safety reports.

### GET `/api/v1/reports/{report_id}`
- **Description**: Fetches complete report details including AI analysis, risk score, Life-Saving Rules, and corrective actions.

---

## 3. AI/NLP SIF Precursor Analysis

### POST `/api/v1/analysis/{report_id}`
- **Description**: Triggers automated AI/NLP inference pipeline (SIF precursor detection, safety context classification, risk assessment, Life-Saving Rule mapping, recommendations, pattern analysis).
- **Response** (`200 OK`):
  ```json
  {
    "report_id": "REP-894102",
    "analysis": {
      "sif_precursor": true,
      "confidence": 0.88,
      "hazard_category": "CONFINED_SPACE",
      "unsafe_act": "ENTRY_WITHOUT_GAS_TEST",
      "raw_prediction": true,
      "raw_confidence": 0.68,
      "context_type": "UNSAFE_BEHAVIOR",
      "context_adjustment_reason": "Unsafe behavior or violation confirmed by safety context analysis.",
      "evidence": ["Context evidence: 'without gas testing'"]
    },
    "risk": {
      "score": 20,
      "level": "CRITICAL",
      "likelihood": 4,
      "severity": 5
    },
    "life_saving_rule": {
      "rule_id": "LSR-01",
      "rule_name": "Confined Space Entry",
      "description": "Obtain authorization before entering a confined space and verify atmospheric gas testing."
    }
  }
  ```

---

## 4. Human-in-the-Loop Reviews & Corrective Actions

### GET `/api/v1/reviews`
- **Description**: Retrieves reports requiring safety officer review (`status=REVIEW_REQUIRED`).

### POST `/api/v1/reviews/{report_id}/override`
- **Request Body**: `{"decision": "ACCEPT", "notes": "Verified by Safety Officer"}`

### POST `/api/v1/actions`
- **Description**: Assigns a new corrective action item.
- **Request Body**:
  ```json
  {
    "report_id": "REP-894102",
    "description": "Calibrate portable gas detectors and inspect vessel isolation valves.",
    "assigned_to": "engineer@oil.in",
    "due_date": "2026-09-22T00:00:00Z"
  }
  ```

### PATCH `/api/v1/actions/{action_id}/status`
- **Request Body**: `{"status": "COMPLETED"}`

---

## 5. Offline & Push Notification Sync

Mobile clients can cache token credentials locally in secure encrypted storage (e.g. `AsyncStorage` / `Keychain`) and poll or connect via websockets/push notifications for active SIF Precursor Alerts (`GET /api/v1/notifications`).
