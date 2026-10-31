# FairShift — Your Work Has Value. Your Voice Has Power.

> **Hackathon Event:** Prompt Wars × ACM SRM Student Chapter 2026  
> **Guidance:** Dr. M. Suchithra, Associate Professor, Department of Computing Technologies, SRMIST Kattankulathur  
> **Student:** Rohith Vuppula  
> **Theme:** UN SDG 8 – Decent Work and Economic Growth  

---

## 📌 Problem Statement (as given)
**FairShift: A Decent Work Platform for Employee-Intensive Organisations (UN SDG 8).**  
Millions of frontline, deskless workers across employee-intensive sectors—such as construction sites, factories, hospitals, and educational institutions—face paper register tampering, wage opacity, unpaid overtime, severe safety hazards, and fear of retaliation when reporting exploitation. Workers stay silent because they fear losing their livelihood, leaving them without voice or defense.

---

## 💡 Your Solution (What it does, in 3–5 lines)
FairShift is an enterprise-grade worker-support platform that guarantees every hour worked has value and every worker has a voice. It mathematically calculates statutory 1.5× overtime pay beyond 8 hours, enforces an automated 48-hour weekly fatigue guardrail, and delivers itemized payslips in English, Hindi, Tamil, and Telugu. Workers can submit structured complaints with supporting evidence (salary slips, registers, chat messages) and track their resolution progress or referral to official labour authorities and free legal-aid services.

---

## 🛠️ Tools Used
- **AI & Vibe Coding:** Google Antigravity, Google Gemini 1.5 Flash
- **Backend Framework:** Python 3.11, Flask, Flask-CORS, Flask-Limiter
- **Database & ORM:** SQLAlchemy 2.0, PostgreSQL (Neon Serverless PostgreSQL with auto-failover SQLite local resilience)
- **Frontend & UI:** HTML5, Tailwind CSS, Lucide Icons, Mobile-First Responsive Design
- **Testing & Verification:** Pytest (26/26 automated unit and integration tests passing)

---

## 🏃 How to Run It

```bash
# 1. Navigate to src directory
cd src

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python app.py
```
Access the application at `http://localhost:5000` in your browser.  
Use the 1-Click preset demo buttons on the login screen for instant evaluation as Construction Worker (`CN-101`), Campus Worker (`CL-201`), or Employer Admin (`admin`).

To execute the automated test suite:
```bash
pytest tests/test_fairshift.py -v
```

---

## 🌐 Demo Link
- **Live Deployed App:** [https://fairshift-app.onrender.com](https://fairshift-app.onrender.com)
- **Public GitHub Repository:** [https://github.com/rohith1246/promptwars](https://github.com/rohith1246/promptwars)

---

## 🎯 Key Prompts
Refer to the enclosed [`prompts.md`](./prompts.md) for the complete prompt engineering trajectory that designed the architecture, wage calculation math, multi-industry support, zero-knowledge privacy defenses, evidence vault, and legal authority directory.
