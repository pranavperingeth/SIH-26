"""
SQLAlchemy models for ChainTrace (Person E — Phase 1).

Only Phase 1 fields are implemented. Do not add Phase 2+ columns
(e.g. the full status workflow, ML fields beyond what's listed) here —
extend later without a rewrite by keeping these models minimal now.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String

from .database import Base


def generate_id() -> str:
    return str(uuid.uuid4())


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String, primary_key=True, default=generate_id)
    suspect_wallet = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class WalletRisk(Base):
    __tablename__ = "wallet_risks"

    id = Column(String, primary_key=True, default=generate_id)
    investigation_id = Column(String, ForeignKey("investigations.id"), nullable=False)
    address = Column(String, nullable=False)
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String, nullable=True)
    # JSON so Person C/D can eventually store SHAP features / rule triggers
    # here without a schema migration.
    reasons = Column(JSON, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=generate_id)
    investigation_id = Column(String, ForeignKey("investigations.id"), nullable=False)
    wallet_address = Column(String, nullable=False)
    alert_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
