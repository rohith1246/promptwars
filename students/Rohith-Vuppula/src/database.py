"""
FairShift - Database Module with Neon PostgreSQL Support
Supports Neon Serverless PostgreSQL via DATABASE_URL with automatic fallback to SQLite for local development.
"""

import os
import random
import string
import logging
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Date, Text, ForeignKey, Index, text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session

load_dotenv()
logger = logging.getLogger("fairshift.database")

Base = declarative_base()


def get_database_uri() -> str:
    """
    Retrieve and normalize database URI for Neon PostgreSQL or fallback.
    Supports both psycopg (v3) and psycopg2 drivers automatically.
    """
    uri = os.getenv("DATABASE_URL", "sqlite:///fairshift.db")
    
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    if uri.startswith("postgresql://") and not uri.startswith("postgresql+"):
        try:
            import psycopg  # noqa: F401
        except ImportError:
            uri = uri.replace("postgresql://", "postgresql+psycopg2://", 1)

    return uri


def create_resilient_engine():
    """
    Creates an optimized engine for Neon Serverless PostgreSQL with automatic
    fallback to SQLite if network DNS or external database is unreachable.
    """
    uri = get_database_uri()
    if uri.startswith("postgresql"):
        try:
            eng = create_engine(
                uri,
                pool_size=10,
                max_overflow=20,
                pool_timeout=10,
                pool_recycle=1800,
                pool_pre_ping=True
            )
            with eng.connect() as conn:
                conn.execute(text("SELECT 1;"))
            logger.info("Connected to Neon Serverless PostgreSQL.")
            return eng
        except Exception as err:
            logger.warning(f"Neon PostgreSQL offline or DNS unreachable ({err}). Falling back to SQLite.")
            return create_engine(
                "sqlite:///fairshift.db",
                connect_args={"check_same_thread": False},
                pool_pre_ping=True
            )
    return create_engine(
        uri,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )


engine = create_resilient_engine()
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


# ============================================================
# DATABASE MODELS
# ============================================================

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)
    worker_code = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    industry = Column(String(64), nullable=False, index=True)  # 'construction' | 'college'
    role = Column(String(120), nullable=False)
    hourly_rate = Column(Float, nullable=False, default=75.0)  # in INR
    daily_shift_hours = Column(Float, nullable=False, default=8.0)
    overtime_multiplier = Column(Float, nullable=False, default=1.5)  # 1.5x for OT
    pin = Column(String(32), nullable=False, default="1234")  # 4-digit PIN for deskless worker login
    created_at = Column(DateTime, default=datetime.utcnow)

    attendance_records = relationship("Attendance", back_populates="worker", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "worker_code": self.worker_code,
            "name": self.name,
            "industry": self.industry,
            "role": self.role,
            "hourly_rate": self.hourly_rate,
            "daily_shift_hours": self.daily_shift_hours,
            "overtime_multiplier": self.overtime_multiplier
        }


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        Index("ix_attendance_worker_date", "worker_id", "date"),
        Index("ix_attendance_industry_status", "industry", "status"),
    )

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    industry = Column(String(64), nullable=False, index=True)
    date = Column(Date, nullable=False, default=date.today, index=True)
    check_in = Column(DateTime, nullable=False, default=datetime.utcnow)
    check_out = Column(DateTime, nullable=True)
    regular_hours = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    total_hours = Column(Float, default=0.0)
    status = Column(String(32), default="checked_in")  # 'checked_in' | 'completed'

    worker = relationship("Worker", back_populates="attendance_records")

    def to_dict(self):
        return {
            "id": self.id,
            "worker_id": self.worker_id,
            "worker_name": self.worker.name if self.worker else "Unknown",
            "worker_code": self.worker.worker_code if self.worker else "",
            "role": self.worker.role if self.worker else "",
            "industry": self.industry,
            "date": self.date.isoformat(),
            "check_in": self.check_in.strftime("%H:%M:%S") if self.check_in else None,
            "check_out": self.check_out.strftime("%H:%M:%S") if self.check_out else None,
            "regular_hours": round(self.regular_hours, 2),
            "overtime_hours": round(self.overtime_hours, 2),
            "total_hours": round(self.total_hours, 2),
            "status": self.status
        }


class Grievance(Base):
    __tablename__ = "grievances"
    __table_args__ = (
        Index("ix_grievance_industry_status", "industry", "status"),
        Index("ix_grievance_urgency_status", "urgency", "status"),
    )

    id = Column(Integer, primary_key=True)
    ticket_code = Column(String(32), unique=True, nullable=False, index=True)
    industry = Column(String(64), nullable=False, index=True)
    category = Column(String(64), nullable=False)
    urgency = Column(String(32), nullable=False, default="Medium")
    description = Column(Text, nullable=False)
    status = Column(String(32), default="Open")
    resolution_note = Column(Text, default="Your report has been logged and queued for administrative review.")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "ticket_code": self.ticket_code,
            "industry": self.industry,
            "category": self.category,
            "urgency": self.urgency,
            "description": self.description,
            "status": self.status,
            "resolution_note": self.resolution_note,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "resolved_at": self.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if self.resolved_at else None
        }


class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = (
        Index("ix_complaint_status", "status"),
        Index("ix_complaint_category", "category"),
    )

    id = Column(Integer, primary_key=True)
    ticket_code = Column(String(32), unique=True, nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)  # nullable for anonymous
    category = Column(String(64), nullable=False)  # 'Unpaid Overtime', 'Withheld Salary', 'Workplace Harassment', 'Unsafe Conditions', 'Discrimination', 'Other'
    description = Column(Text, nullable=False)
    evidence_type = Column(String(64), nullable=True)  # 'Attendance Records', 'Salary Slips', 'Messages/Screenshots', 'Witness Statement', 'Other'
    evidence_description = Column(Text, nullable=True)
    status = Column(String(32), default="Submitted")  # 'Submitted' -> 'Under Review' -> 'Referred to Authority' -> 'Resolved'
    authority_referral = Column(String(120), nullable=True)  # Which authority/service it was referred to
    resolution_note = Column(Text, default="Your complaint has been received and is being processed.")
    is_anonymous = Column(Integer, default=1)  # 1 = anonymous, 0 = identified
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    worker = relationship("Worker", backref="complaints", foreign_keys=[worker_id])

    def to_dict(self):
        return {
            "id": self.id,
            "ticket_code": self.ticket_code,
            "category": self.category,
            "description": self.description,
            "evidence_type": self.evidence_type,
            "evidence_description": self.evidence_description,
            "status": self.status,
            "authority_referral": self.authority_referral,
            "resolution_note": self.resolution_note,
            "is_anonymous": bool(self.is_anonymous),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            "worker_name": self.worker.name if self.worker and not self.is_anonymous else "Anonymous",
        }


def generate_ticket_code() -> str:
    num_part = "".join(random.choices(string.digits, k=5))
    return f"FS-{num_part}"


def generate_complaint_code() -> str:
    num_part = "".join(random.choices(string.digits, k=5))
    return f"FC-{num_part}"


def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Auto-migrate schema updates for Neon PostgreSQL
    try:
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            if "postgresql" in str(engine.url):
                conn.execute(text("ALTER TABLE workers ADD COLUMN IF NOT EXISTS pin VARCHAR(64) DEFAULT '1234';"))
                conn.execute(text("UPDATE workers SET pin = '1234' WHERE pin IS NULL;"))
    except Exception as e:
        logger.info(f"Schema check complete: {e}")

    session = db_session()

    if session.query(Worker).count() == 0:
        seed_workers = [
            Worker(worker_code="CN-101", name="Ramesh Kumar", industry="construction", role="Master Mason", hourly_rate=95.0, pin="1234"),
            Worker(worker_code="CN-102", name="Deepak Verma", industry="construction", role="Scaffolding Technician", hourly_rate=85.0, pin="1234"),
            Worker(worker_code="CN-103", name="Suresh Yadav", industry="construction", role="Structural Welder", hourly_rate=110.0, pin="1234"),
            Worker(worker_code="CN-104", name="Arun Singh", industry="construction", role="Site General Labor", hourly_rate=65.0, pin="1234"),

            Worker(worker_code="CL-201", name="Lakshmi Narayanan", industry="college", role="Campus Sanitation Lead", hourly_rate=75.0, pin="1234"),
            Worker(worker_code="CL-202", name="K. Murugan", industry="college", role="Senior Security Guard", hourly_rate=80.0, pin="1234"),
            Worker(worker_code="CL-203", name="Priya Selvam", industry="college", role="Laboratory Assistant", hourly_rate=90.0, pin="1234"),
            Worker(worker_code="CL-204", name="Anand Raj", industry="college", role="Campus Shuttle Driver", hourly_rate=85.0, pin="1234"),
        ]
        session.add_all(seed_workers)
        session.commit()

        today = date.today()
        workers = session.query(Worker).all()

        for w in workers:
            for day_offset in range(1, 6):
                hist_date = today - timedelta(days=day_offset)
                if w.worker_code in ["CN-102", "CL-202"]:
                    reg_h = 8.0
                    ot_h = 3.5
                else:
                    reg_h = 8.0
                    ot_h = 1.0 if day_offset % 2 == 0 else 0.0

                att = Attendance(
                    worker_id=w.id,
                    industry=w.industry,
                    date=hist_date,
                    check_in=datetime.combine(hist_date, datetime.min.time()) + timedelta(hours=8),
                    check_out=datetime.combine(hist_date, datetime.min.time()) + timedelta(hours=8, minutes=int((reg_h + ot_h) * 60)),
                    regular_hours=reg_h,
                    overtime_hours=ot_h,
                    total_hours=reg_h + ot_h,
                    status="completed"
                )
                session.add(att)

        seed_grievances = [
            Grievance(
                ticket_code="FS-10492",
                industry="construction",
                category="Safety Hazard",
                urgency="Critical",
                description="Damaged toe-boards on scaffolding at Sector B, 4th floor. High risk of falling bricks.",
                status="Under Investigation",
                resolution_note="Safety inspector assigned. Work at Sector B scaffold temporarily halted for harness check.",
                created_at=datetime.utcnow() - timedelta(hours=14)
            ),
            Grievance(
                ticket_code="FS-39201",
                industry="construction",
                category="Wage Discrepancy",
                urgency="Medium",
                description="Night concrete pouring overtime for 3 hours on Tuesday was marked as regular hours on the paper sheet.",
                status="Resolved",
                resolution_note="Supervisor verified logbook. 3 hours overtime credited at 1.5x multiplier in current pay cycle.",
                created_at=datetime.utcnow() - timedelta(days=2),
                resolved_at=datetime.utcnow() - timedelta(hours=6)
            ),
            Grievance(
                ticket_code="FS-58193",
                industry="college",
                category="Work Conditions",
                urgency="Medium",
                description="Sanitation chemical storage room in Science Block has no exhaust fan. Causes eye irritation during mixing.",
                status="Open",
                resolution_note="Ticket received. Forwarded to Campus Estate & Maintenance department.",
                created_at=datetime.utcnow() - timedelta(hours=4)
            ),
            Grievance(
                ticket_code="FS-71044",
                industry="college",
                category="Safety Hazard",
                urgency="Critical",
                description="Main Gate 2 barrier arm wire is frayed and sparking during morning bus rush.",
                status="Under Investigation",
                resolution_note="Electrical crew notified. Gate power rerouted to backup line.",
                created_at=datetime.utcnow() - timedelta(hours=8)
            )
        ]
        session.add_all(seed_grievances)

        # Seed sample complaints for the enhanced complaint system
        seed_complaints = [
            Complaint(
                ticket_code="FC-20001",
                worker_id=None,
                category="Unpaid Overtime",
                description="Worked 12 hours daily for the past 2 weeks but salary slip shows payment for only 8 hours each day. No overtime compensation received.",
                evidence_type="Salary Slips",
                evidence_description="Salary slip for October 2026 showing only 8-hour payment despite 12-hour shifts.",
                status="Under Review",
                resolution_note="Complaint escalated to payroll audit team. Comparing attendance logs with salary records.",
                is_anonymous=1,
                created_at=datetime.utcnow() - timedelta(days=3)
            ),
            Complaint(
                ticket_code="FC-20002",
                worker_id=None,
                category="Unsafe Conditions",
                description="Construction site Block C lacks proper safety nets on floors 6-8. Workers forced to work at height without harness equipment.",
                evidence_type="Witness Statement",
                evidence_description="Multiple workers witnessed the absence of safety nets during morning shift on 25 Oct.",
                status="Referred to Authority",
                authority_referral="District Labour Commissioner, Chennai",
                resolution_note="Referred to District Labour Commissioner. Site inspection scheduled.",
                is_anonymous=1,
                created_at=datetime.utcnow() - timedelta(days=5)
            ),
            Complaint(
                ticket_code="FC-20003",
                worker_id=None,
                category="Withheld Salary",
                description="September salary not paid to 15 campus cleaning staff. Management says 'budget delay' but no written communication.",
                evidence_type="Attendance Records",
                evidence_description="Attendance register showing all 15 staff present throughout September.",
                status="Submitted",
                resolution_note="Your complaint has been received and is being processed.",
                is_anonymous=0,
                created_at=datetime.utcnow() - timedelta(hours=18)
            ),
        ]
        session.add_all(seed_complaints)
        session.commit()

    session.close()
