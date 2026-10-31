# FairShift — Your Work Has Value. Your Voice Has Power.

> **Theme:** UN SDG 8 – Decent Work and Economic Growth  
> **Event:** Prompt Wars 2026 (Prompt Wars × SRM ACM Student Chapter)  
> **Guidance:** Dr. M. Suchithra, Associate Professor, Department of Computing Technologies, SRMIST Kattankulathur  
> **Repository:** [https://github.com/rohith1246/promptwars.git](https://github.com/rohith1246/promptwars.git)  
> **Live Deployed App:** [https://promptwars-tyoh.onrender.com/](https://promptwars-tyoh.onrender.com/)

---

## 🎙️ The Pitch: Why FairShift Exists

> *"Imagine a worker working 12 hours a day but getting paid for only 8 hours. The employer refuses to pay overtime. The worker knows it's unfair, but stays silent because they are afraid of losing their job.*  
> ***Who will stand up for that worker?***  
> *That is why we created **FairShift**. Our mission is simple: **no worker should have to fight workplace exploitation alone.***"

FairShift is a worker-support platform designed to make workplaces fairer, safer, and more transparent under **United Nations Sustainable Development Goal 8 (Decent Work & Economic Growth)**.

---

## 🚀 How It Works (4-Stage Worker Protection Pipeline)

1. **Report a Problem:** A worker visits the platform and reports workplace exploitation—such as unpaid overtime, withheld salary, workplace harassment, or unsafe conditions.
2. **Submit Supporting Evidence:** The worker can upload or reference supporting evidence (shift logs, salary slips, bank SMS, chat messages, or co-worker witness statements).
3. **Legal Aid & Authority Guidance:** FairShift organizes the complaint dossier, protects the worker's identity, and guides them directly to appropriate statutory authorities (District Labour Commissioners, NALSA free legal aid, EPFO, ESIC, NHRC).
4. **Follow Resolution Progress:** Workers follow real-time progress via their unique tracking code (`FC-XXXXX`) instead of feeling helpless or alone.

---

## 🌟 6 Core Working Features (Built & Verified)

### 1. Shift Attendance & 1.5× Overtime Tracker
- **1-Click QR Check-In / Check-Out:** Instant shift tracking simulating on-site badges.
- **Automated Overtime Math:** Distinguishes normal hours (up to 8.0 hrs) from overtime hours (>8.0 hrs), crediting statutory 1.5× overtime multipliers.
- **48-Hour Fatigue Guardrail (SDG 8.8):** Tracks cumulative weekly shifts and warns workers and site supervisors before exhaustion leads to accidents.

### 2. Transparent Multilingual Payslip & Formula Proof
- **Mathematical Formula:**  
  $$\text{Net Take-Home} = (\text{Regular Hours} \times \text{Rate}) + (\text{Overtime Hours} \times \text{Rate} \times 1.5) - \text{PF/ESI Deductions (5\%)}$$
- **Trilingual Localization:** Instant real-time translations into **English**, **Hindi (हिन्दी)**, **Tamil (தமிழ்)**, and **Telugu (తెలుగు)**.
- **Eliminates Wage Opacity:** Frontline workers see exactly how every rupee was calculated before payday.

### 3. Zero-Knowledge Anonymous Safety Hazard Reporting
- **Total Anonymity Guarantee:** Strips worker identity, names, phone numbers, and IP addresses before database storage.
- **Cryptographic Tracking Code:** Generates unique tracking tickets (e.g. `FS-10492`) to check status updates without revealing identity.
- **Employer Triage Board:** Supervisors investigate incidents and log corrective action notes visible to workers.

### 4. Workplace Complaint & Evidence Organiser (New)
- **Categorized Issue Filing:** Structured reporting for unpaid overtime, withheld salary, harassment, and unsafe conditions.
- **Supporting Evidence Vault:** Organizes salary slips, attendance registers, WhatsApp messages, and witness statements.
- **Multi-Step Progress Timeline:** Tracks status (`Submitted` $\rightarrow$ `Under Review` $\rightarrow$ `Referred to Authority` $\rightarrow$ `Resolved`).

### 5. Legal Aid & Authority Referral Directory (New)
- **Curated Statutory Directory:** Direct links, contacts, and mandates for 8+ statutory bodies:
  - District Labour Commissioner (Factories Act compliance & wage recovery)
  - National Legal Services Authority (NALSA - Free legal aid for workers)
  - Employee Provident Fund Organisation (EPFO) & ESIC
  - National Commission for Safai Karamcharis (Sanitation worker support)
  - Building & Other Construction Workers (BOCW) Welfare Board
  - National Human Rights Commission (NHRC)

### 6. Exploitation Prevention & Compliance Radar (New)
- **Proactive Early Detection:** Stops exploitation *before* it happens.
- **Compliance Score & Grade:** Real-time scoring (Grade A–F) based on excessive hours, critical safety alerts, and open claims.
- **Automated Actionable Recommendations:** Highlights shift rotations and safety inspections needed to prevent labor disputes.

---

## 💼 Business Model & Sustainability

- **B2B Enterprise Subscriptions:** Affordable shift management, fatigue compliance radars, and statutory audit logging for construction firms, universities, hospitals, and factories.
- **Legal & Social Partnerships:** Working alongside legal aid societies, labor unions, and NGOs to provide workers with support without charging vulnerable laborers.
- **The Anti-Retaliation Promise:** Basic complaint filing is always free for workers, and employers cannot buy their way out of accountability.

---

## 🔐 Role-Based Access & Pre-Loaded Demo Accounts

| Role | Username / ID | Password / PIN | Industry / Profile | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Admin / Employer** | `admin` | `admin123` | Multi-Industry | Full management dashboard, compliance radar, attendance logs, and grievance triage |
| **Worker (Construction)** | `CN-101` | `1234` | Skyline Infrastructure | Ramesh Kumar (Master Mason, ₹95/hr, 1.5× OT) |
| **Worker (College)** | `CL-201` | `1234` | SRM University Operations | Lakshmi Narayanan (Sanitation Lead, ₹75/hr, 1.5× OT) |

> 💡 **Evaluator Convenience:** The login screen provides 1-click **"Quick Fill"** buttons for instant demo entry.

---

## 📸 Screenshots Overview

| Screen View | Description |
| :--- | :--- |
| `01_landing_hero.png` | Landing page hero with slogan *"Your Work Has Value. Your Voice Has Power."* |
| `02_six_core_features.png` | Complete 6 core working features grid aligned with UN SDG 8 |
| `03_legal_aid_directory.png` | Curated Legal Aid & Labour Authority Referral Directory |
| `04_login_portal.png` | 1-Click instant demo login & worker self-registration portal |
| `05_worker_portal.png` | Frontline worker dashboard with QR clock-in & 1.5× overtime math |
| `06_worker_complaint_vault.png` | Workplace complaint filing with evidence vault and timeline tracker |
| `07_admin_dashboard.png` | Employer operational KPI dashboard with live attendance records |
| `08_admin_prevention_radar.png` | Proactive prevention radar, Grade A compliance score & recommendations |
| `09_admin_complaints_desk.png` | Admin complaint triage desk with authority referral workflow |
| `10_gemini_ai_advisor.png` | FairShift Gemini AI Labor Rights & Decent Work assistant open |
| `11_mobile_home_view.png` | Mobile-first responsive landing page (iPhone / Android) |
| `12_mobile_worker_view.png` | Mobile worker portal with 1-click touch targets |

---

## 🧪 Automated Test Suite (26/26 Passing)

```bash
pytest tests/test_fairshift.py -v
```

```text
tests/test_fairshift.py::FairShiftTestSuite::test_00_admin_login_and_logout PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_00_invalid_login_rejection PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_00_worker_login_success PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_01_get_workers_by_industry PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_02_worker_check_in_and_duplicate_prevention PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_03_automated_overtime_calculation_on_checkout PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_04_transparent_payslip_mathematical_accuracy PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_05_multilingual_payslip_translations PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_06_fatigue_alert_guardrail_detection PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_07_anonymous_grievance_submission_zero_knowledge PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_08_employer_grievance_triage_update PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_09_security_headers_enforced PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_10_xss_injection_sanitization_in_grievance PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_11_input_validation_worker_code_and_pin_format PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_12_shift_hours_boundary_validation PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_13_ticket_code_tracking_and_invalid_format_rejection PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_14_nonexistent_ticket_returns_404 PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_15_wage_engine_negative_hours_and_zero_rate_guardrails PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_16_health_check_endpoint PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_17_homepage_accessible_rendering PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_18_worker_signup_registration PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_19_ai_chatbot_response PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_20_complaint_submission_and_tracking PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_21_complaint_management_and_referral PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_22_legal_resources_directory PASSED
tests/test_fairshift.py::FairShiftTestSuite::test_23_prevention_dashboard PASSED

======================= 26 passed in 159.50s =======================
```

---

## 💻 Tech Stack & Architectural Rigor

- **Backend:** Python Flask with SQLAlchemy 2.0 ORM.
- **Database:** PostgreSQL (Neon Serverless PostgreSQL support with automatic SQLite fallback).
- **Security:** OWASP Top 10 compliance, CSRF protections, bcrypt-compatible PIN checks, XSS sanitization, Rate-Limiting via Flask-Limiter, strict HTTP security headers.
- **Frontend:** Vanilla JS, Tailwind CSS, Lucide Icons, Mobile-First Responsive Layout.
- **AI Integration:** Google Gemini 1.5 Flash via server-side `.env` configuration with resilient fallback labor knowledge engine.

---

## 🏃‍♂️ How to Run Locally

```bash
# 1. Clone repository
git clone https://github.com/rohith1246/promptwars.git
cd promptwars

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python app.py
```
Open `http://localhost:5000` in your browser.
