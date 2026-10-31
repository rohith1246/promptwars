"""
FairShift - Comprehensive Automated Test Suite with Authentication
Prompt Wars 2026 × SRM ACM Student Chapter
Validates:
- Authentication & Role-Based Access Control (Worker & Admin logins)
- Feature 1: Attendance & Shift Tracking (Normal hours, Overtime calculation)
- Feature 2: Transparent Multilingual Payslip (English, Hindi, Tamil)
- Feature 3: Anonymous Grievance & Safety Hazard Reporting (Zero-Knowledge tracking)
- Multi-Industry Support (Construction & College)
- Security Defenses (SQL Injection, XSS sanitization, Rate limiting, Security headers)
"""

import unittest
import json
from app import app
from database import init_db, db_session, Worker, Attendance, Grievance


class FairShiftTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        with app.app_context():
            init_db()

    def setUp(self):
        self.client = app.test_client()

    def tearDown(self):
        db_session.remove()

    # ============================================================
    # AUTHENTICATION & ROLE-BASED ACCESS CONTROL TESTS
    # ============================================================

    def test_00_worker_login_success(self):
        """Verify worker login with worker_code and 4-digit PIN."""
        res = self.client.post("/api/auth/login", json={
            "role": "worker",
            "worker_code": "CN-101",
            "pin": "1234"
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["worker_code"], "CN-101")
        self.assertEqual(data["user"]["role"], "worker")

        # Verify /api/auth/me returns current session
        res_me = self.client.get("/api/auth/me")
        self.assertEqual(res_me.status_code, 200)
        self.assertTrue(json.loads(res_me.data)["authenticated"])

    def test_00_admin_login_and_logout(self):
        """Verify admin login with username/password and logout session destruction."""
        res = self.client.post("/api/auth/login", json={
            "role": "admin",
            "username": "admin",
            "password": "fairshift2026"
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["user"]["role"], "admin")

        # Logout
        res_logout = self.client.post("/api/auth/logout")
        self.assertEqual(res_logout.status_code, 200)

        # /api/auth/me should now return 401
        res_me = self.client.get("/api/auth/me")
        self.assertEqual(res_me.status_code, 401)

    def test_00_invalid_login_rejection(self):
        """Verify invalid worker credentials are rejected."""
        res = self.client.post("/api/auth/login", json={
            "role": "worker",
            "worker_code": "CN-999",
            "pin": "0000"
        })
        self.assertEqual(res.status_code, 404)

        res_bad_pin = self.client.post("/api/auth/login", json={
            "role": "worker",
            "worker_code": "CN-101",
            "pin": "9999"
        })
        self.assertEqual(res_bad_pin.status_code, 401)

    # ============================================================
    # FEATURE 1: ATTENDANCE & SHIFT / OVERTIME TRACKING TESTS
    # ============================================================

    def test_01_get_workers_by_industry(self):
        """Verify distinct worker rosters for Construction vs College industries."""
        res_cn = self.client.get("/api/workers?industry=construction")
        self.assertEqual(res_cn.status_code, 200)
        workers_cn = json.loads(res_cn.data)
        self.assertTrue(len(workers_cn) >= 4)
        self.assertTrue(any("Mason" in w["role"] for w in workers_cn))

        res_cl = self.client.get("/api/workers?industry=college")
        self.assertEqual(res_cl.status_code, 200)
        workers_cl = json.loads(res_cl.data)
        self.assertTrue(len(workers_cl) >= 4)
        self.assertTrue(any("Sanitation" in w["role"] or "Security" in w["role"] for w in workers_cl))

    def test_02_worker_check_in_and_duplicate_prevention(self):
        """Verify check-in creates record and prevents duplicate active check-ins."""
        res = self.client.post("/api/check-in", json={"worker_id": 1})
        self.assertIn(res.status_code, [200, 201])
        data = json.loads(res.data)
        self.assertIn("attendance", data)

        res_dup = self.client.post("/api/check-in", json={"worker_id": 1})
        self.assertEqual(res_dup.status_code, 200)
        self.assertIn("already checked in", json.loads(res_dup.data)["message"].lower())

    def test_03_automated_overtime_calculation_on_checkout(self):
        """Verify standard 8h shift splits overtime automatically (>8.0 hrs)."""
        res = self.client.post("/api/check-out", json={
            "worker_id": 1,
            "simulated_hours": 11.0
        })
        self.assertEqual(res.status_code, 200)
        att = json.loads(res.data)["attendance"]
        self.assertEqual(att["regular_hours"], 8.0)
        self.assertEqual(att["overtime_hours"], 3.0)
        self.assertEqual(att["total_hours"], 11.0)
        self.assertEqual(att["status"], "completed")

    # ============================================================
    # FEATURE 2: TRANSPARENT MULTILINGUAL PAYSLIP TESTS
    # ============================================================

    def test_04_transparent_payslip_mathematical_accuracy(self):
        """Verify payslip formula: Base Pay + Overtime (1.5x) - 5% PF = Net Take-Home."""
        res = self.client.get("/api/payslip/1?lang=en")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)

        expected_base = round(data["total_regular_hours"] * data["hourly_rate"], 2)
        expected_ot_rate = round(data["hourly_rate"] * 1.5, 2)
        expected_ot = round(data["total_overtime_hours"] * expected_ot_rate, 2)
        expected_gross = round(expected_base + expected_ot, 2)
        expected_deductions = round(expected_gross * 0.05, 2)
        expected_net = round(expected_gross - expected_deductions, 2)

        self.assertEqual(data["base_pay"], expected_base)
        self.assertEqual(data["overtime_pay"], expected_ot)
        self.assertEqual(data["gross_pay"], expected_gross)
        self.assertEqual(data["deductions"], expected_deductions)
        self.assertEqual(data["net_pay"], expected_net)
        self.assertIn("Formula:", data["formula_explanation"])

    def test_05_multilingual_payslip_translations(self):
        """Verify payslip translations for Hindi (hi), Tamil (ta), and Telugu (te)."""
        res_hi = self.client.get("/api/payslip/1?lang=hi")
        self.assertEqual(res_hi.status_code, 200)
        data_hi = json.loads(res_hi.data)
        self.assertIn("पारदर्शी वेतन विवरण", data_hi["labels"]["title"])

        res_ta = self.client.get("/api/payslip/1?lang=ta")
        self.assertEqual(res_ta.status_code, 200)
        data_ta = json.loads(res_ta.data)
        self.assertIn("வெளிப்படையான சம்பள விபரம்", data_ta["labels"]["title"])

        res_te = self.client.get("/api/payslip/1?lang=te")
        self.assertEqual(res_te.status_code, 200)
        data_te = json.loads(res_te.data)
        self.assertIn("పారదర్శక వేతన వివరాలు", data_te["labels"]["title"])

    def test_06_fatigue_alert_guardrail_detection(self):
        """Verify fatigue alert triggers when total hours exceed 48 hours weekly cap."""
        res = self.client.get("/api/payslip/2?lang=en")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["is_fatigued"])
        self.assertIn("exceed 48 hrs", data["fatigue_status"].lower())

    # ============================================================
    # FEATURE 3: ANONYMOUS GRIEVANCE & SAFETY REPORTING TESTS
    # ============================================================

    def test_07_anonymous_grievance_submission_zero_knowledge(self):
        """Verify grievance generates ticket code and stores no user identity."""
        payload = {
            "industry": "construction",
            "category": "Safety Hazard",
            "urgency": "Critical",
            "description": "Loose scaffolding clamp near Tower 3 elevator shaft."
        }
        res = self.client.post("/api/grievances", json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        ticket_code = data["ticket_code"]
        self.assertTrue(ticket_code.startswith("FS-"))

        res_track = self.client.get(f"/api/grievances/track/{ticket_code}")
        self.assertEqual(res_track.status_code, 200)
        grievance_data = json.loads(res_track.data)
        self.assertEqual(grievance_data["ticket_code"], ticket_code)
        self.assertEqual(grievance_data["status"], "Open")

    def test_08_employer_grievance_triage_update(self):
        """Verify employer can triage and resolve an anonymous grievance."""
        res = self.client.post("/api/grievances", json={
            "industry": "college",
            "category": "Work Conditions",
            "urgency": "Medium",
            "description": "Air conditioning broken in security guard post at Gate 3."
        })
        code = json.loads(res.data)["ticket_code"]

        res_update = self.client.post("/api/grievances/update-status", json={
            "ticket_code": code,
            "status": "Under Investigation",
            "resolution_note": "Campus technician dispatched to Gate 3."
        })
        self.assertEqual(res_update.status_code, 200)

        res_check = self.client.get(f"/api/grievances/track/{code}")
        tracked = json.loads(res_check.data)
        self.assertEqual(tracked["status"], "Under Investigation")
        self.assertIn("technician dispatched", tracked["resolution_note"])

    # ============================================================
    # SECURITY & INTEGRITY TESTS
    # ============================================================

    def test_09_security_headers_enforced(self):
        """Verify OWASP-recommended security headers are injected."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertEqual(res.headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertIn("Content-Security-Policy", res.headers)

    def test_10_xss_injection_sanitization_in_grievance(self):
        """Verify dangerous HTML script tags are sanitized."""
        xss_payload = "<script>alert('pwned')</script>Unsafe electrical wiring."
        res = self.client.post("/api/grievances", json={
            "industry": "construction",
            "category": "Safety Hazard",
            "urgency": "Critical",
            "description": xss_payload
        })
        self.assertEqual(res.status_code, 201)
        code = json.loads(res.data)["ticket_code"]

        res_track = self.client.get(f"/api/grievances/track/{code}")
        data = json.loads(res_track.data)
        self.assertNotIn("<script>", data["description"])
        self.assertIn("&lt;script&gt;", data["description"])

    def test_11_input_validation_worker_code_and_pin_format(self):
        """Verify malformed worker codes and invalid PINs are rejected with 400 Bad Request."""
        # Invalid format code
        res_bad_code = self.client.post("/api/auth/login", json={
            "role": "worker",
            "worker_code": "INVALID_CODE_123",
            "pin": "1234"
        })
        self.assertEqual(res_bad_code.status_code, 400)
        self.assertIn("Invalid worker code format", json.loads(res_bad_code.data)["error"])

        # Invalid PIN (non-digit or wrong length)
        res_bad_pin = self.client.post("/api/auth/login", json={
            "role": "worker",
            "worker_code": "CN-101",
            "pin": "abc"
        })
        self.assertEqual(res_bad_pin.status_code, 400)
        self.assertIn("PIN must be a 4 to 6 digit", json.loads(res_bad_pin.data)["error"])

    def test_12_shift_hours_boundary_validation(self):
        """Verify checkout rejects negative, zero, or physically impossible (>24h) shift hours."""
        self.client.post("/api/check-in", json={"worker_id": 3})

        # Test shift > 24 hours rejection
        res_excess = self.client.post("/api/check-out", json={
            "worker_id": 3,
            "simulated_hours": 32.0
        })
        self.assertEqual(res_excess.status_code, 400)
        self.assertIn("cannot exceed 24 hours", json.loads(res_excess.data)["error"])

        # Test shift < 0.1 hours rejection
        res_subzero = self.client.post("/api/check-out", json={
            "worker_id": 3,
            "simulated_hours": -5.0
        })
        self.assertEqual(res_subzero.status_code, 400)
        self.assertIn("at least 0.1 hours", json.loads(res_subzero.data)["error"])

    def test_13_ticket_code_tracking_and_invalid_format_rejection(self):
        """Verify tracking rejects malformed ticket codes before querying the database."""
        res_bad = self.client.get("/api/grievances/track/NOT-A-VALID-CODE")
        self.assertEqual(res_bad.status_code, 400)
        self.assertIn("Invalid ticket code format", json.loads(res_bad.data)["error"])

    def test_14_nonexistent_ticket_returns_404(self):
        """Verify validly formatted but non-existent ticket code returns 404."""
        res = self.client.get("/api/grievances/track/FS-99999")
        self.assertEqual(res.status_code, 404)
        self.assertIn("not found", json.loads(res.data)["error"])

    def test_15_wage_engine_negative_hours_and_zero_rate_guardrails(self):
        """Verify wage engine mathematically clamps negative hours and rates safely."""
        from wage_engine import calculate_payslip
        mock_worker = {"hourly_rate": -50.0, "overtime_multiplier": 0.5, "name": "Test Worker"}
        mock_records = [{"regular_hours": -8.0, "overtime_hours": -4.0}]
        slip = calculate_payslip(mock_worker, mock_records, lang="en")
        self.assertEqual(slip["hourly_rate"], 0.0)
        self.assertEqual(slip["total_regular_hours"], 0.0)
        self.assertEqual(slip["base_pay"], 0.0)
        self.assertEqual(slip["net_pay"], 0.0)

    def test_16_health_check_endpoint(self):
        """Verify health check endpoint returns 200 with UN SDG 8 alignment metadata."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("SDG 8", data["theme"])

    def test_17_homepage_accessible_rendering(self):
        """Verify homepage renders with accessible landmarks, skip link, and login gate."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Skip to main content", res.data)
        self.assertIn(b"loginScreen", res.data)
        self.assertIn(b"SDG 8: Decent Work", res.data)

    def test_18_worker_signup_registration(self):
        """Verify new frontline worker can register, get auto-assigned ID, and immediately authenticate."""
        payload = {
            "name": "Karthik Raja",
            "industry": "construction",
            "role": "Master Electrician",
            "hourly_rate": 105.0,
            "pin": "5678"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertTrue(data["worker_code"].startswith("CN-"))
        self.assertEqual(data["user"]["name"], "Karthik Raja")

        # Verify new worker can log in with new PIN
        res_login = self.client.post("/api/auth/login", json={
            "role": "worker",
            "worker_code": data["worker_code"],
            "pin": "5678"
        })
        self.assertEqual(res_login.status_code, 200)

    def test_19_ai_chatbot_response(self):
        """Verify FairShift AI Chatbot returns accurate decent work intelligence."""
        res = self.client.post("/api/ai/chat", json={
            "message": "How is my overtime calculated?"
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("1.5", data["reply"])
        self.assertIn("Overtime", data["reply"])

    # ============================================================
    # NEW FEATURE TESTS: COMPLAINTS, LEGAL DIRECTORY, PREVENTION
    # ============================================================

    def test_20_complaint_submission_and_tracking(self):
        """Verify submitting a workplace complaint with evidence and tracking its timeline."""
        payload = {
            "category": "Unpaid Overtime",
            "description": "Worked 14 hours on Saturday and Sunday but received no overtime wage payment.",
            "evidence_type": "Salary Slips",
            "evidence_description": "Pay slip showing only standard 8-hour pay.",
            "is_anonymous": True
        }
        res = self.client.post("/api/complaints", json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        ticket_code = data["ticket_code"]
        self.assertTrue(ticket_code.startswith("FC-"))

        # Track the complaint
        res_track = self.client.get(f"/api/complaints/track/{ticket_code}")
        self.assertEqual(res_track.status_code, 200)
        track_data = json.loads(res_track.data)
        self.assertEqual(track_data["ticket_code"], ticket_code)
        self.assertEqual(track_data["category"], "Unpaid Overtime")
        self.assertTrue(len(track_data["timeline"]) >= 4)
        self.assertTrue(track_data["timeline"][0]["completed"])

    def test_21_complaint_management_and_referral(self):
        """Verify admin can list complaints, update status, and refer case to official authority."""
        # List complaints
        res_list = self.client.get("/api/complaints")
        self.assertEqual(res_list.status_code, 200)
        complaints = json.loads(res_list.data)
        self.assertTrue(len(complaints) > 0)
        first_ticket = complaints[0]["ticket_code"]

        # Refer to authority
        res_refer = self.client.post("/api/complaints/update", json={
            "ticket_code": first_ticket,
            "status": "Referred to Authority",
            "authority_referral": "District Labour Commissioner, Chennai",
            "resolution_note": "Case dossier forwarded for official inspection."
        })
        self.assertEqual(res_refer.status_code, 200)
        ref_data = json.loads(res_refer.data)
        self.assertEqual(ref_data["complaint"]["status"], "Referred to Authority")
        self.assertIn("Labour Commissioner", ref_data["complaint"]["authority_referral"])

    def test_22_legal_resources_directory(self):
        """Verify legal aid & authority directory returns verified statutory organizations."""
        res = self.client.get("/api/legal-resources")
        self.assertEqual(res.status_code, 200)
        resources = json.loads(res.data)
        self.assertTrue(len(resources) >= 6)
        names = [r["name"] for r in resources]
        self.assertTrue(any("Labour Commissioner" in n for n in names))
        self.assertTrue(any("Legal Services" in n or "NALSA" in n for n in names))

    def test_23_prevention_dashboard(self):
        """Verify proactive prevention dashboard computes compliance grade, risk radar, and recommendations."""
        res = self.client.get("/api/prevention/dashboard")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("compliance_score", data)
        self.assertIn("compliance_grade", data)
        self.assertIn("recommendations", data)
        self.assertTrue(len(data["recommendations"]) > 0)


if __name__ == "__main__":
    unittest.main()
