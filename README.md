# FairShift — A Decent Work Platform for Employee-Intensive Organisations

> **Theme:** UN SDG 8 – Decent Work and Economic Growth  
> **Event:** Prompt Wars 2026 (Prompt Wars × SRM ACM Student Chapter)  
> **Repository:** [https://github.com/rohith1246/LegalLens-AI.git](https://github.com/rohith1246/LegalLens-AI.git)

---

## 📌 Executive Summary & Problem Statement

Millions of frontline, deskless workers across employee-intensive sectors—such as construction sites, factories, hospitals, and college campus operations—are managed through paper registers, fragile Excel spreadsheets, and informal WhatsApp groups.

### Problems for Workers:
1. **Wage Opackness:** Workers do not understand how their pay was calculated or whether their overtime hours were properly credited.
2. **Fear of Retaliation:** Legitimate grievances (harassment, unpaid overtime, safety hazards) go unreported because workers fear being identified and terminated.
3. **Safety Hazards:** Severe site risks remain unaddressed until someone gets injured.
4. **Language & Literacy Barriers:** Workers speak regional languages (Hindi, Tamil, Telugu) and use basic smartphones, making standard enterprise HR tools unusable.

### Problems for Employers:
1. **Blind Spots:** Management has no visibility into who is overworked, fatigued, or close to quitting.
2. **Audit & Compliance Risk:** Missing statutory registers create crippling fines during labor inspections.

---

## 🌟 The Solution: FairShift

FairShift replaces fragmented manual registers with a **secure, transparent, multilingual decent work platform**.

### Two Supported Real-World Industries:
1. **🏗️ Construction Site Operations (*Skyline Infrastructure*):** Focuses on high-risk site shifts, automated overtime multipliers, scaffolding hazard reporting, and daily wage calculations for masons, welders, and site laborers.
2. **🎓 College / Campus Operations (*SRM University Campus Facilities*):** Focuses on campus sanitation shifts, security guard rosters, chemical storage hazard reports, and transparent hourly wages.

---

## 🚀 3 Core Working Features (Built & Tested)

### 1. Shift Attendance & Overtime Tracker
- **1-Click Clock-In / Clock-Out:** Instant check-in simulation with dynamic QR badge.
- **Automated Overtime Classification:** System automatically logs normal shift hours (up to 8.0 hrs) and overtime hours (>8.0 hrs) at a 1.5x pay multiplier.
- **Fatigue Guardrail (SDG 8.8):** Tracks cumulative weekly hours. Flags workers exceeding the 48-hour legal limit to prevent exhaustion and accidents.

### 2. Transparent Multilingual Payslip & Formula Proof
- **Transparent Formula:**  
  $$\text{Net Pay} = (\text{Regular Hours} \times \text{Rate}) + (\text{Overtime Hours} \times \text{Rate} \times 1.5) - \text{PF/ESI Deductions (5\%)}$$
- **Multilingual Support:** One-click translation of pay items and mathematical explanations into **English**, **Hindi (हिन्दी)**, and **Tamil (தமிழ்)**.
- **Visual Proof:** Eliminates wage disputes before pay day by providing workers with live visual calculations.

### 3. Zero-Knowledge Anonymous Grievance & Safety Reporting
- **Zero Retaliation Guarantee:** Submissions strictly strip worker identity, name, phone number, and IP address.
- **Unique Tracking Code:** Workers receive an anonymous alphanumeric ticket code (e.g., `FS-10492`) to check status updates without revealing who they are.
- **Employer Triage Board:** Employers review incidents, mark tickets (*Open* $\rightarrow$ *Under Investigation* $\rightarrow$ *Resolved*), and attach corrective action notes visible to the worker.

---

## 👥 Dual-Interface Design

| Interface | Target Audience | Key Capabilities |
| :--- | :--- | :--- |
| **Worker Portal (Mobile-First)** | Deskless workers, masons, sanitation staff | 1-Click QR check-in, transparent payslip in regional languages, anonymous safety hazard reporting, ticket status tracker. |
| **Employer Admin Dashboard** | Site supervisors, campus managers, HR | Real-time workforce KPIs, 48h fatigue alert radar, live attendance log table, anonymous grievance triage queue. |

---

## 🔒 Security & Architectural Rigor

- **Database:** PostgreSQL (supports **Neon Serverless PostgreSQL** via `DATABASE_URL` with automatic SQLite local fallback).
- **SQL Injection Defense:** All database interactions are governed through parameterized SQLAlchemy ORM queries.
- **XSS Sanitization:** User descriptions and notes are strictly sanitized and HTML-escaped.
- **Zero-Knowledge Privacy:** Grievance endpoints drop all client identifiers before database writes.
- **Rate Limiting:** `Flask-Limiter` protects endpoints against brute-force flooding (120 req/min).
- **Hardened HTTP Headers:** Enforces CSP, X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, X-XSS-Protection.

---

## 🧪 Automated Test Suite (10/10 Passing)

Run test suite:
```bash
pytest tests/test_fairshift.py -v
```

Tests cover:
- Worker roster segregation for Construction and College industries
- Duplicate check-in prevention
- Overtime calculation accuracy
- Mathematical payslip formula and 1.5x multiplier verification
- Multilingual translations (Hindi and Tamil)
- 48-hour fatigue limit detection
- Anonymous ticket generation and zero-knowledge status tracking
- Employer status triage workflow
- XSS injection sanitization and OWASP security headers

---

## 💻 Local Setup & Neon PostgreSQL

### 1. Run with SQLite (Default Out-of-the-Box)
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000)

### 2. Run with Neon PostgreSQL
Add your Neon connection string to `.env`:
```env
DATABASE_URL=postgresql://user:password@ep-cool-sample.us-east-2.aws.neon.tech/fairshift?sslmode=require
```
Run:
```bash
python app.py
```

---

## ☁️ Deployment on Render

This repository is pre-configured with `Procfile`, `wsgi.py` (with `ProxyFix`), and `render.yaml`.
Simply push to GitHub and Render will automatically deploy with Gunicorn WSGI.
