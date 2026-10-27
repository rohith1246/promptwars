"""
FairShift - Wage & Transparent Payslip Calculation Engine
Calculates wages mathematically and provides transparent explanations in English, Hindi, Tamil, and Telugu.
Monitors fatigue guardrails (UN SDG 8.8: >48 hours weekly threshold).
"""

from typing import Dict, Any, List


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "title": "Transparent Wage Breakdown",
        "base_pay": "Regular Shift Pay",
        "overtime_pay": "Overtime Pay (1.5x Rate)",
        "gross_pay": "Gross Earnings",
        "deductions": "Statutory Social Security (PF/ESI 5%)",
        "net_pay": "Net Take-Home Pay",
        "formula": "Formula: (Regular Hours × Rate) + (Overtime Hours × Rate × 1.5) - Deductions",
        "fatigue_safe": "Fatigue Status: Normal Work Hours",
        "fatigue_warning": "Warning: Weekly hours exceed 48 hrs limit. Worker needs rest to prevent fatigue accidents."
    },
    "hi": {
        "title": "पारदर्शी वेतन विवरण (Transparent Payslip)",
        "base_pay": "नियमित कार्य वेतन (Base Shift Pay)",
        "overtime_pay": "अतिरिक्त समय वेतन (Overtime 1.5x दर)",
        "gross_pay": "कुल अर्जित वेतन (Gross Earnings)",
        "deductions": "वैधानिक कटौती (PF / बीमा 5%)",
        "net_pay": "खाते में मिलने वाली शुद्ध राशि (Take-Home)",
        "formula": "सूत्र: (नियमित घंटे × दर) + (ओवरटाइम घंटे × दर × 1.5) - कटौती",
        "fatigue_safe": "थकान स्तर: सामान्य कार्य घंटे (सुरक्षित)",
        "fatigue_warning": "सावधानी: इस सप्ताह काम के घंटे 48 से अधिक हो चुके हैं। दुर्घटना से बचाव हेतु विश्राम आवश्यक है।"
    },
    "ta": {
        "title": "வெளிப்படையான சம்பள விபரம் (Transparent Payslip)",
        "base_pay": "வழக்கமான ஷிப்ட் சம்பளம் (Base Pay)",
        "overtime_pay": "கூடுதல் நேர ஊதியம் (Overtime 1.5x)",
        "gross_pay": "மொத்த வருவாய் (Gross Earnings)",
        "deductions": "சட்டப்பூர்வ பிடித்தங்கள் (PF / ESI 5%)",
        "net_pay": "கைக்கு வரும் நிகர சம்பளம் (Take-Home)",
        "formula": "சூத்திரம்: (வழக்கமான மணிநேரம் × வீதம்) + (ஓவர் டைம் × 1.5) - பிடித்தம்",
        "fatigue_safe": "சோர்வு நிலை: சாதாரண வேலை நேரம் (பாதுகாப்பானது)",
        "fatigue_warning": "எச்சரிக்கை: வாராந்திர வேலை நேரம் 48 மணிநேரத்தை தாண்டியுள்ளது. ஓய்வு தேவை."
    },
    "te": {
        "title": "పారదర్శక వేతన వివరాలు (Transparent Payslip)",
        "base_pay": "సాధారణ షిఫ్ట్ వేతనం (Base Pay)",
        "overtime_pay": "ఓవర్‌టైమ్ వేతనం (1.5x రేటు)",
        "gross_pay": "మొత్తం సంపాదన (Gross Earnings)",
        "deductions": "చట్టబద్ధమైన తగ్గింపులు (PF / ESI 5%)",
        "net_pay": "చేతికి అందే నికర వేతనం (Take-Home)",
        "formula": "సూత్రం: (సాధారణ గంటలు × రేటు) + (ఓవర్‌టైమ్ గంటలు × రేటు × 1.5) - తగ్గింపులు",
        "fatigue_safe": "అలసట స్థితి: సాధారణ పని గంటలు (సురక్షితం)",
        "fatigue_warning": "హెచ్చరిక: వారపు పని గంటలు 48 దాటాయి. ప్రమాద నివారణకు విశ్రాంతి అవసరం."
    }
}


def calculate_payslip(worker_dict: Dict[str, Any], attendance_records: List[Dict[str, Any]], lang: str = "en") -> Dict[str, Any]:
    """
    Computes mathematical transparent payslip with plain-language explanation.
    
    Parameters:
        worker_dict: Dictionary containing worker's metadata (hourly_rate, overtime_multiplier, etc.)
        attendance_records: List of shift attendance records for the billing cycle
        lang: Selected language code ('en', 'hi', 'ta', 'te')
        
    Returns:
        Structured dictionary with mathematical breakdown, statutory deductions, fatigue analysis, and localized labels.
    """
    if lang not in TRANSLATIONS:
        lang = "en"
    text = TRANSLATIONS[lang]

    # Defensive parsing with non-negative bounds
    hourly_rate = max(0.0, float(worker_dict.get("hourly_rate", 75.0) or 75.0))
    ot_multiplier = max(1.0, float(worker_dict.get("overtime_multiplier", 1.5) or 1.5))

    # Single-pass high-efficiency accumulation
    total_reg_hours = 0.0
    total_ot_hours = 0.0
    for r in attendance_records:
        total_reg_hours += float(r.get("regular_hours", 0.0) or 0.0)
        total_ot_hours += float(r.get("overtime_hours", 0.0) or 0.0)

    total_reg_hours = max(0.0, total_reg_hours)
    total_ot_hours = max(0.0, total_ot_hours)
    total_work_hours = total_reg_hours + total_ot_hours

    base_pay = round(total_reg_hours * hourly_rate, 2)
    overtime_rate = round(hourly_rate * ot_multiplier, 2)
    overtime_pay = round(total_ot_hours * overtime_rate, 2)
    gross_pay = round(base_pay + overtime_pay, 2)

    # 5% statutory deduction for PF/ESI social security
    deductions = round(gross_pay * 0.05, 2)
    net_pay = round(gross_pay - deductions, 2)

    # Fatigue Alert: ILO / Labor Law standard 48 hours / week (UN SDG 8.8)
    is_fatigued = total_work_hours > 48.0
    fatigue_status = text["fatigue_warning"] if is_fatigued else text["fatigue_safe"]

    return {
        "language": lang,
        "worker_name": worker_dict.get("name", "Unknown Worker"),
        "worker_code": worker_dict.get("worker_code", "UNKNOWN"),
        "role": worker_dict.get("role", "Worker"),
        "hourly_rate": hourly_rate,
        "overtime_rate": overtime_rate,
        "total_regular_hours": round(total_reg_hours, 1),
        "total_overtime_hours": round(total_ot_hours, 1),
        "total_work_hours": round(total_work_hours, 1),
        "base_pay": base_pay,
        "overtime_pay": overtime_pay,
        "gross_pay": gross_pay,
        "deductions": deductions,
        "net_pay": net_pay,
        "is_fatigued": is_fatigued,
        "fatigue_status": fatigue_status,
        "formula_explanation": text["formula"],
        "labels": text
    }
