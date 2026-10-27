"""
FairShift — A Decent Work Platform for Employee-Intensive Organisations
Built for Prompt Wars 2026 (Prompt Wars × SRM ACM Student Chapter)
Theme: UN SDG 8 – Decent Work and Economic Growth

Core Working Features:
1. Attendance & Overtime Shift Tracking (Automated hour calculation & fatigue alert)
2. Transparent Multilingual Payslip Engine (English, Hindi, Tamil)
3. Zero-Knowledge Anonymous Grievance & Safety Hazard Reporting (with Tracking Code)

Two Supported Industries:
- Construction Site ("Skyline Infrastructure")
- College Operations ("SRM University Campus Facilities")
"""

import os
import sys
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from database import (
    init_db, db_session, Worker, Attendance, Grievance, generate_ticket_code
)
from security import (
    sanitize_text, validate_ticket_code, sanitize_grievance_payload, add_security_headers
)
from wage_engine import calculate_payslip


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fairshift-sdg8-decent-work-secret-key-2026")
CORS(app)

# Security: Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["120 per minute"],
    storage_uri="memory://"
)

# Apply Hardened Security Headers to every response
@app.after_request
def apply_security_headers(response):
    return add_security_headers(response)


# Teardown database session per request
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# Initialize database with tables and seed data
with app.app_context():
    init_db()


# ============================================================
# PAGE ROUTES
# ============================================================

@app.route("/")
def index():
    """Serves the primary unified application interface."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check endpoint for Render and uptime monitoring."""
    return jsonify({
        "status": "healthy",
        "app": "FairShift",
        "theme": "SDG 8: Decent Work & Economic Growth",
        "timestamp": datetime.utcnow().isoformat()
    })


# ============================================================
# FEATURE 1: ATTENDANCE & SHIFT / OVERTIME TRACKING API
# ============================================================

@app.route("/api/workers", methods=["GET"])
def get_workers():
    """Fetch workers filtered by industry."""
    industry = request.args.get("industry", "construction").strip().lower()
    session = db_session()
    workers = session.query(Worker).filter_by(industry=industry).all()
    return jsonify([w.to_dict() for w in workers])


@app.route("/api/check-in", methods=["POST"])
@limiter.limit("20 per minute")
def check_in():
    """
    Worker clock-in endpoint.
    Checks if worker already checked in today; if not, records start timestamp.
    """
    data = request.get_json() or {}
    worker_id = data.get("worker_id")
    if not worker_id:
        return jsonify({"error": "Worker ID is required."}), 400

    session = db_session()
    worker = session.query(Worker).filter_by(id=worker_id).first()
    if not worker:
        return jsonify({"error": "Worker not found."}), 404

    today = date.today()
    # Check if existing active check-in exists for today
    existing = session.query(Attendance).filter_by(
        worker_id=worker.id, date=today, status="checked_in"
    ).first()

    if existing:
        return jsonify({
            "message": f"{worker.name} is already checked in for today.",
            "attendance": existing.to_dict()
        }), 200

    new_attendance = Attendance(
        worker_id=worker.id,
        industry=worker.industry,
        date=today,
        check_in=datetime.utcnow(),
        status="checked_in"
    )
    session.add(new_attendance)
    session.commit()

    return jsonify({
        "message": f"Check-in recorded successfully for {worker.name} ({worker.role}).",
        "attendance": new_attendance.to_dict()
    }), 201


@app.route("/api/check-out", methods=["POST"])
@limiter.limit("20 per minute")
def check_out():
    """
    Worker clock-out endpoint.
    Automatically calculates regular hours and overtime (hours > 8.0).
    """
    data = request.get_json() or {}
    worker_id = data.get("worker_id")
    hours_worked = data.get("simulated_hours")  # Option to simulate worked hours for demonstration

    session = db_session()
    today = date.today()
    attendance = session.query(Attendance).filter_by(
        worker_id=worker_id, date=today, status="checked_in"
    ).first()

    if not attendance:
        # Fallback to any latest open attendance
        attendance = session.query(Attendance).filter_by(
            worker_id=worker_id, status="checked_in"
        ).order_by(Attendance.id.desc()).first()

    if not attendance:
        return jsonify({"error": "No active check-in record found for this worker."}), 404

    now = datetime.utcnow()
    attendance.check_out = now

    # Calculate duration
    if hours_worked is not None and float(hours_worked) > 0:
        total_h = float(hours_worked)
    else:
        diff_seconds = (now - attendance.check_in).total_seconds()
        total_h = max(1.0, round(diff_seconds / 3600.0, 2))

    # Standard shift = 8.0 hours; anything above is classified as overtime
    standard_shift = attendance.worker.daily_shift_hours or 8.0
    if total_h > standard_shift:
        attendance.regular_hours = standard_shift
        attendance.overtime_hours = round(total_h - standard_shift, 2)
    else:
        attendance.regular_hours = total_h
        attendance.overtime_hours = 0.0

    attendance.total_hours = total_h
    attendance.status = "completed"
    session.commit()

    return jsonify({
        "message": f"Check-out confirmed for {attendance.worker.name}.",
        "attendance": attendance.to_dict()
    }), 200


@app.route("/api/attendance", methods=["GET"])
def get_attendance():
    """Fetch attendance records filtered by industry."""
    industry = request.args.get("industry", "construction").strip().lower()
    session = db_session()
    records = session.query(Attendance).filter_by(industry=industry).order_by(Attendance.id.desc()).limit(30).all()
    return jsonify([r.to_dict() for r in records])


# ============================================================
# FEATURE 2: TRANSPARENT MULTILINGUAL PAYSLIP API
# ============================================================

@app.route("/api/payslip/<int:worker_id>", methods=["GET"])
def get_payslip(worker_id):
    """
    Computes transparent wage breakdown with mathematical proof and multilingual explanation.
    Languages: 'en' (English), 'hi' (Hindi), 'ta' (Tamil).
    """
    lang = request.args.get("lang", "en").strip().lower()
    session = db_session()
    worker = session.query(Worker).filter_by(id=worker_id).first()
    if not worker:
        return jsonify({"error": "Worker not found."}), 404

    # Fetch last 7 days attendance records for this worker
    attendance_records = session.query(Attendance).filter_by(worker_id=worker.id).all()
    payslip_data = calculate_payslip(
        worker_dict=worker.to_dict(),
        attendance_records=[r.to_dict() for r in attendance_records],
        lang=lang
    )

    return jsonify(payslip_data)


# ============================================================
# FEATURE 3: ANONYMOUS GRIEVANCE & SAFETY REPORTING API
# ============================================================

@app.route("/api/grievances", methods=["POST"])
@limiter.limit("15 per minute")
def submit_grievance():
    """
    Zero-Knowledge Anonymous Grievance Submission.
    Guarantees no worker identity, phone number, or IP address is linked to the ticket.
    Returns a unique alphanumeric Ticket Code for anonymous status tracking.
    """
    raw_payload = request.get_json() or {}
    is_valid, error_msg, clean_data = sanitize_grievance_payload(raw_payload)

    if not is_valid:
        return jsonify({"error": error_msg}), 400

    session = db_session()
    ticket_code = generate_ticket_code()

    # Ensure unique ticket code
    while session.query(Grievance).filter_by(ticket_code=ticket_code).first():
        ticket_code = generate_ticket_code()

    new_grievance = Grievance(
        ticket_code=ticket_code,
        industry=clean_data["industry"],
        category=clean_data["category"],
        urgency=clean_data["urgency"],
        description=clean_data["description"],
        status="Open",
        resolution_note="Report received anonymously. Assigned for triage by compliance safety team."
    )
    session.add(new_grievance)
    session.commit()

    return jsonify({
        "success": True,
        "message": "Anonymous report submitted securely. Save your ticket code to track resolution.",
        "ticket_code": ticket_code
    }), 201


@app.route("/api/grievances/track/<ticket_code>", methods=["GET"])
def track_grievance(ticket_code):
    """
    Allows a worker to track the status of their grievance without revealing who they are.
    """
    clean_code = ticket_code.strip().upper()
    if not validate_ticket_code(clean_code):
        return jsonify({"error": "Invalid ticket code format. Example: FS-10492"}), 400

    session = db_session()
    grievance = session.query(Grievance).filter_by(ticket_code=clean_code).first()
    if not grievance:
        return jsonify({"error": "Ticket code not found. Please verify the code."}), 404

    return jsonify(grievance.to_dict())


@app.route("/api/grievances", methods=["GET"])
def list_grievances():
    """Employer view: List grievances for the selected industry."""
    industry = request.args.get("industry", "construction").strip().lower()
    session = db_session()
    grievances = session.query(Grievance).filter_by(industry=industry).order_by(Grievance.id.desc()).all()
    return jsonify([g.to_dict() for g in grievances])


@app.route("/api/grievances/update-status", methods=["POST"])
def update_grievance_status():
    """Employer action: Update grievance resolution status and corrective action note."""
    data = request.get_json() or {}
    ticket_code = data.get("ticket_code", "").strip().upper()
    new_status = data.get("status", "").strip()
    resolution_note = sanitize_text(data.get("resolution_note", ""), max_length=1000)

    valid_statuses = ["Open", "Under Investigation", "Resolved"]
    if new_status not in valid_statuses:
        return jsonify({"error": "Invalid status."}), 400

    session = db_session()
    grievance = session.query(Grievance).filter_by(ticket_code=ticket_code).first()
    if not grievance:
        return jsonify({"error": "Grievance ticket not found."}), 404

    grievance.status = new_status
    if resolution_note:
        grievance.resolution_note = resolution_note
    if new_status == "Resolved":
        grievance.resolved_at = datetime.utcnow()

    session.commit()
    return jsonify({
        "message": f"Ticket {ticket_code} updated to '{new_status}'.",
        "grievance": grievance.to_dict()
    })


# ============================================================
# OVERVIEW & INDUSTRY METRICS API
# ============================================================

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Provides operational & SDG 8 Decent Work compliance statistics."""
    industry = request.args.get("industry", "construction").strip().lower()
    session = db_session()

    workers = session.query(Worker).filter_by(industry=industry).all()
    worker_ids = [w.id for w in workers]

    attendance_records = session.query(Attendance).filter(Attendance.worker_id.in_(worker_ids)).all()
    grievances = session.query(Grievance).filter_by(industry=industry).all()

    total_hours = sum(r.total_hours for r in attendance_records)
    total_ot_hours = sum(r.overtime_hours for r in attendance_records)

    open_grievances = sum(1 for g in grievances if g.status != "Resolved")
    critical_safety = sum(1 for g in grievances if g.urgency == "Critical" and g.status != "Resolved")

    # Fatigue warning: Any worker with > 48 hours logged in attendance records
    fatigued_count = 0
    for w in workers:
        w_records = [r for r in attendance_records if r.worker_id == w.id]
        if sum(r.total_hours for r in w_records) > 48.0:
            fatigued_count += 1

    return jsonify({
        "industry": industry,
        "total_workforce": len(workers),
        "total_hours_logged": round(total_hours, 1),
        "total_overtime_hours": round(total_ot_hours, 1),
        "open_grievances": open_grievances,
        "critical_safety_alerts": critical_safety,
        "fatigued_workers_count": fatigued_count,
        "sdg_compliance_score": 94 if open_grievances == 0 else max(60, 100 - (open_grievances * 6))
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
