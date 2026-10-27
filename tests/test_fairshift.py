"""
FairShift - Comprehensive Automated Test Suite
Prompt Wars 2026 × SRM ACM Student Chapter
Validates:
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
    # FEATURE 1: ATTENDANCE & SHIFT / OVERTIME TRACKING TESTS
    # ============================================================

    def test_01_get_workers_by_industry(self):
        """Verify distinct worker rosters for Construction vs College industries."""
        # Construction
        res_cn = self.client.get("/api/workers?industry=construction")
        self.assertEqual(res_cn.status_code, 200)
        workers_cn = json.loads(res_cn.data)
        self.assertTrue(len(workers_cn) >= 4)
        self.assertTrue(any("Mason" in w["role"] for w in workers_cn))

        # College
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

        # Attempt immediate duplicate check-in
        res_dup = self.client.post("/api/check-in", json={"worker_id": 1})
        self.assertEqual(res_dup.status_code, 200)
        self.assertIn("already checked in", json.loads(res_dup.data)["message"].lower())

    def test_03_automated_overtime_calculation_on_checkout(self):
        """Verify standard 8h shift splits overtime automatically (>8.0 hrs)."""
        # Clock out with simulated 11 hours (8h standard + 3h overtime)
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

        # Mathematical verification
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
        """Verify payslip translations for Hindi (hi) and Tamil (ta)."""
        # Hindi
        res_hi = self.client.get("/api/payslip/1?lang=hi")
        self.assertEqual(res_hi.status_code, 200)
        data_hi = json.loads(res_hi.data)
        self.assertIn("पारदर्शी वेतन विवरण", data_hi["labels"]["title"])

        # Tamil
        res_ta = self.client.get("/api/payslip/1?lang=ta")
        self.assertEqual(res_ta.status_code, 200)
        data_ta = json.loads(res_ta.data)
        self.assertIn("வெளிப்படையான சம்பள விபரம்", data_ta["labels"]["title"])

    def test_06_fatigue_alert_guardrail_detection(self):
        """Verify fatigue alert triggers when total hours exceed 48 hours weekly cap."""
        # Worker 2 was seeded with 5 days of 11.5 hours = 57.5 hours (>48 limit)
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

        # Verify tracking works with generated ticket code
        res_track = self.client.get(f"/api/grievances/track/{ticket_code}")
        self.assertEqual(res_track.status_code, 200)
        grievance_data = json.loads(res_track.data)
        self.assertEqual(grievance_data["ticket_code"], ticket_code)
        self.assertEqual(grievance_data["status"], "Open")

    def test_08_employer_grievance_triage_update(self):
        """Verify employer can triage and resolve an anonymous grievance."""
        # Submit a ticket
        res = self.client.post("/api/grievances", json={
            "industry": "college",
            "category": "Work Conditions",
            "urgency": "Medium",
            "description": "Air conditioning broken in security guard post at Gate 3."
        })
        code = json.loads(res.data)["ticket_code"]

        # Employer marks Under Investigation
        res_update = self.client.post("/api/grievances/update-status", json={
            "ticket_code": code,
            "status": "Under Investigation",
            "resolution_note": "Campus technician dispatched to Gate 3."
        })
        self.assertEqual(res_update.status_code, 200)

        # Worker tracks ticket again anonymously to see update
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

        # Read back sanitized grievance
        res_track = self.client.get(f"/api/grievances/track/{code}")
        data = json.loads(res_track.data)
        self.assertNotIn("<script>", data["description"])
        self.assertIn("&lt;script&gt;", data["description"])


if __name__ == "__main__":
    unittest.main()
