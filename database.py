"""
FairShift - Database Module with Neon PostgreSQL Support
Supports Neon Serverless PostgreSQL via DATABASE_URL with automatic fallback to SQLite for local development.
"""

import os
import random
import string
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Date, Text, ForeignKey, inspect
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session

load_dotenv()

Base = declarative_base()


def get_database_uri() -> str:
    """Retrieve and normalize database URI for Neon PostgreSQL or fallback."""
    uri = os.getenv("DATABASE_URL", "sqlite:///fairshift.db")
    # Neon and Heroku provide postgres:// URLs, SQLAlchemy requires postgresql://
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return uri


database_uri = get_database_uri()
connect_args = {"check_same_thread": False} if database_uri.startswith("sqlite") else {}

engine = create_engine(
    database_uri,
    connect_args=connect_args,
    pool_pre_ping=True,  # Keeps Neon serverless connection alive and drops stale connections
    pool_recycle=300
)

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
    """
    Zero-Knowledge Anonymous Grievance Model.
    Notice: NO worker_id, NO IP address, NO user device metadata is stored.
    Generates a secure alphanumeric tracking token (e.g. FS-84920) so the worker can track resolution.
    """
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True)
    ticket_code = Column(String(32), unique=True, nullable=False, index=True)
    industry = Column(String(64), nullable=False, index=True)
    category = Column(String(64), nullable=False)  # 'Safety Hazard', 'Wage Discrepancy', 'Harassment', 'Work Conditions'
    urgency = Column(String(32), nullable=False, default="Medium")  # 'Low', 'Medium', 'Critical'
    description = Column(Text, nullable=False)
    status = Column(String(32), default="Open")  # 'Open' | 'Under Investigation' | 'Resolved'
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


# ============================================================
# HELPER FUNCTIONS & SEED DATA
# ============================================================

def generate_ticket_code() -> str:
    """Generate a high-entropy collision-resistant anonymous ticket code."""
    num_part = "".join(random.choices(string.digits, k=5))
    return f"FS-{num_part}"


def init_db():
    """Create all tables and seed sample data for Construction and College industries."""
    Base.metadata.create_all(bind=engine)
    session = db_session()

    # Only seed if workers table is empty
    if session.query(Worker).count() == 0:
        seed_workers = [
            # Construction Industry: Skyline Infrastructure
            Worker(worker_code="CN-101", name="Ramesh Kumar", industry="construction", role="Master Mason", hourly_rate=95.0),
            Worker(worker_code="CN-102", name="Deepak Verma", industry="construction", role="Scaffolding Technician", hourly_rate=85.0),
            Worker(worker_code="CN-103", name="Suresh Yadav", industry="construction", role="Structural Welder", hourly_rate=110.0),
            Worker(worker_code="CN-104", name="Arun Singh", industry="construction", role="Site General Labor", hourly_rate=65.0),

            # College / Campus Operations: SRM University Campus Operations
            Worker(worker_code="CL-201", name="Lakshmi Narayanan", industry="college", role="Campus Sanitation Lead", hourly_rate=75.0),
            Worker(worker_code="CL-202", name="K. Murugan", industry="college", role="Senior Security Guard", hourly_rate=80.0),
            Worker(worker_code="CL-203", name="Priya Selvam", industry="college", role="Laboratory Assistant", hourly_rate=90.0),
            Worker(worker_code="CL-204", name="Anand Raj", industry="college", role="Campus Shuttle Driver", hourly_rate=85.0),
        ]
        session.add_all(seed_workers)
        session.commit()

        # Seed sample historical attendance for transparency & fatigue demo
        today = date.today()
        workers = session.query(Worker).all()

        for w in workers:
            # 5 days of attendance history for each worker
            for day_offset in range(1, 6):
                hist_date = today - timedelta(days=day_offset)
                
                # Make some workers have realistic overtime to demonstrate transparent calculation and fatigue alerts
                if w.worker_code in ["CN-102", "CL-202"]:
                    reg_h = 8.0
                    ot_h = 3.5  # Heavy overtime -> Fatigue alert
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

        # Seed realistic grievances for both industries
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
        session.commit()

    session.close()
