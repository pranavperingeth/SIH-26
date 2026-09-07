from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import (
    InvestigateRequest,
    InvestigateResponse,
    InvestigationListResponse,
    InvestigationOut,
)

router = APIRouter(tags=["investigations"])


@router.post(
    "/api/investigate",
    response_model=InvestigateResponse,
    status_code=201,
)
def create_investigation(payload: InvestigateRequest, db: Session = Depends(get_db)):
    """
    Create a new investigation record.

    Phase 1 only persists the request — it does NOT trigger blockchain
    ingestion, Neo4j tracing, ML scoring, or Celery. That wiring belongs
    to Phase 3 (F integration).
    """
    investigation = models.Investigation(
        suspect_wallet=payload.wallet_address,
        status="PENDING",
    )
    db.add(investigation)
    db.commit()
    db.refresh(investigation)

    return InvestigateResponse(
        investigation_id=investigation.id,
        status=investigation.status,
        message="Investigation created",
    )


@router.get("/api/investigations", response_model=InvestigationListResponse)
def list_investigations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List investigations, newest first, with simple pagination."""
    query = db.query(models.Investigation).order_by(
        models.Investigation.created_at.desc()
    )
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()

    return InvestigationListResponse(
        page=page,
        page_size=page_size,
        total=total,
        results=results,
    )


@router.get("/api/investigations/{investigation_id}", response_model=InvestigationOut)
def get_investigation(investigation_id: str, db: Session = Depends(get_db)):
    investigation = (
        db.query(models.Investigation)
        .filter(models.Investigation.id == investigation_id)
        .first()
    )
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return investigation
