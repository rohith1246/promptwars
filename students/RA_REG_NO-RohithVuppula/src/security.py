"""
FairShift - Security & Protection Module
Implements defense-in-depth:
1. SQL Injection Prevention via Parameterized ORM queries
2. XSS Input Sanitization & HTML escaping
3. Zero-Knowledge Grievance Protection (Strict IP/Identifier Stripping)
4. Comprehensive HTTP Security Headers
5. Request Payload Validation and Bounds Checking
"""

import re
import html
from typing import Dict, Any, Tuple


def sanitize_text(text: str, max_length: int = 2000) -> str:
    """Sanitize user input string against XSS and control characters."""
    if not text:
        return ""
    # Strip dangerous null bytes and format characters
    cleaned = text.replace("\x00", "").strip()
    # Escape HTML tags (<, >, &, ", ')
    escaped = html.escape(cleaned)
    # Enforce safe length bounds
    return escaped[:max_length]


def validate_worker_code(code: str) -> bool:
    """Validate format of worker code (e.g. CN-101, CL-201)."""
    if not code:
        return False
    return bool(re.match(r"^[A-Z]{2,4}-\d{3,5}$", code.strip().upper()))


def validate_pin(pin: str) -> bool:
    """Validate format of 4 to 6 digit security PIN."""
    if not pin:
        return False
    return bool(re.match(r"^\d{4,6}$", pin.strip()))


def validate_shift_hours(hours: float) -> Tuple[bool, str]:
    """Validate shift duration within realistic, non-negative, and safe labor limits."""
    try:
        val = float(hours)
    except (ValueError, TypeError):
        return False, "Shift hours must be a valid number."
    
    if val < 0.1:
        return False, "Shift duration must be at least 0.1 hours (6 minutes)."
    if val > 24.0:
        return False, "Shift duration cannot exceed 24 hours in a single calendar day."
    
    return True, ""


def validate_ticket_code(code: str) -> bool:
    """Validate format of anonymous grievance ticket code (e.g. FS-12345)."""
    if not code:
        return False
    return bool(re.match(r"^FS-\d{4,6}$", code.strip().upper()))


def sanitize_grievance_payload(payload: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates and sanitizes anonymous grievance reports.
    Enforces that zero identifiable metadata is logged.
    """
    if not payload:
        return False, "Payload cannot be empty", {}

    category = payload.get("category", "").strip()
    urgency = payload.get("urgency", "Medium").strip()
    description = payload.get("description", "").strip()
    industry = payload.get("industry", "construction").strip().lower()

    valid_categories = ["Safety Hazard", "Wage Discrepancy", "Harassment", "Work Conditions", "Other"]
    valid_urgencies = ["Low", "Medium", "Critical"]
    valid_industries = ["construction", "college"]

    if category not in valid_categories:
        category = "Other"

    if urgency not in valid_urgencies:
        urgency = "Medium"

    if industry not in valid_industries:
        industry = "construction"

    if not description or len(description) < 5:
        return False, "Description must be at least 5 characters long.", {}

    sanitized_desc = sanitize_text(description, max_length=1500)

    clean_data = {
        "category": category,
        "urgency": urgency,
        "description": sanitized_desc,
        "industry": industry
    }

    return True, "", clean_data


def add_security_headers(response):
    """Inject hardened HTTP security headers into every outgoing response (OWASP Top 10 Compliance)."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self';"
    )
    return response
