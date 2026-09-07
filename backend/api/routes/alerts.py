from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import AlertOut

router = APIRouter(tags=["alerts"])


@router.get("/api/alerts", response_model=list[AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    """
    Return stored alerts, newest first. Phase 1 does not generate alerts
    automatically, so this list may simply be empty.
    """
    return (
        db.query(models.Alert).order_by(models.Alert.created_at.desc()).all()
    )
