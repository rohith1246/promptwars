# FairShift — Key Prompts Used (Prompt Wars 2026)

> **Event:** Prompt Wars × ACM SRM Student Chapter 2026  
> **Guidance:** Dr. M. Suchithra, Associate Professor, Department of Computing Technologies, SRMIST  
> **Student:** rohith1246  
> **Problem Statement:** FairShift — A Decent Work Platform for Employee-Intensive Organisations (UN SDG 8)

---

## 🎯 Prompt 1: Initial Architecture & UN SDG 8 Problem Statement Alignment
```text
Build FairShift: A Decent Work Platform for Employee-Intensive Organisations addressing UN SDG 8 (Decent Work & Economic Growth).
Focus on deskless frontline workers across two sectors:
1. Construction Site Operations (Skyline Infrastructure): masons, welders, scaffolders.
2. College Operations (SRM University Campus Facilities): sanitation staff, security guards, lab attendants.

Implement:
- Shift attendance & overtime calculation with 1.5x pay multiplier for hours beyond 8 hours.
- 48-hour cumulative weekly fatigue safety guardrail.
- Transparent multilingual payslips with explicit math formula proof in English, Hindi, and Tamil.
- Zero-knowledge anonymous safety hazard reporting with tracking code.
- Role-based authentication with 1-click test accounts for workers and employers.
```

---

## 🎯 Prompt 2: Enterprise Database & Multi-Tenant Industry Separation
```text
Design SQLAlchemy 2.0 models for PostgreSQL (Neon Serverless PostgreSQL via DATABASE_URL) with resilient SQLite fallback:
- Worker model with worker_code (CN-101, CL-201), industry, role, hourly_rate, 4-digit PIN.
- Attendance model with check_in, check_out, regular_hours, overtime_hours, total_hours.
- Grievance model with anonymous ticket_code (FS-XXXXX), industry, category, urgency, status, and resolution_note.
Seed with realistic frontline worker data across Skyline Infrastructure and SRM University Operations.
```

---

## 🎯 Prompt 3: Zero-Knowledge Privacy & Security Hardening (OWASP Compliance)
```text
Harden the application against security vulnerabilities:
- Enforce parameterized SQLAlchemy ORM queries to prevent SQL injection.
- Implement XSS input sanitization and HTML escaping on all text inputs.
- Strip worker identifiers and IP addresses on anonymous grievance submissions before saving.
- Add Flask-Limiter for brute-force protection (120 req/min).
- Inject comprehensive HTTP security headers: CSP, HSTS, X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN.
```

---

## 🎯 Prompt 4: Multilingual Engine & Mathematical Formula Verification
```text
Implement wage_engine.py:
- Compute Net Pay = (Regular Hours * Rate) + (Overtime Hours * Rate * 1.5) - (5% statutory PF/ESI deduction).
- Provide localized JSON payslip translations for English, Hindi (हिन्दी), Tamil (தமிழ்), and Telugu (తెలుగు).
- Return dynamic fatigue alert flags when weekly hours exceed 48.0 hours under SDG 8.8.
```

---

## 🎯 Prompt 5: Performance Optimization & Eliminating N+1 Queries
```text
Optimize backend queries and frontend rendering:
- Use joinedload(Attendance.worker) to eliminate N+1 database queries.
- Add compound B-Tree indexes: ix_attendance_worker_date, ix_attendance_industry_status, ix_grievance_industry_status.
- Optimize /api/stats to O(N) single-pass hash aggregation.
- Add HTTP static asset caching (Cache-Control: public, max-age=31536000, immutable).
```

---

## 🎯 Prompt 6: Server-Secured Gemini AI Labor Advisor & Home Landing Page
```text
Add a comprehensive landing page explaining all features, 1-click worker signup self-registration, and a built-in FairShift Gemini AI chatbot:
- Gemini API key must be strictly read from server-side .env (never exposed to browser or client).
- Chatbot assists workers in plain language regarding 1.5x overtime math, 48h fatigue caps, and labor rights under Indian labor standards.
- Fallback seamlessly to built-in Decent Work knowledge engine if external API key is absent.
```

---

## 🎯 Prompt 7: Enhanced Complaint System, Evidence Vault & Legal Aid Directory
```text
Expand FairShift into a complete worker-support platform:
"Your Work Has Value. Your Voice Has Power."
- Add Complaint model and endpoints for reporting unpaid overtime, withheld salary, harassment, and unsafe conditions.
- Support evidence submission: salary slips, attendance records, messages, witness statements.
- Build interactive Complaint Progress Tracker with multi-step timeline (Submitted -> Under Review -> Referred to Authority -> Resolved).
- Add Legal Aid & Authority Referral Directory connecting workers directly to District Labour Commissioner, NALSA free legal aid, EPFO, ESIC, NHRC, and BOCW Board.
- Add Proactive Exploitation Prevention & Compliance Radar to monitor excessive shifts (>48h/wk) and score site compliance.
- Capture full desktop and mobile screenshots for presentation and submission.
```
