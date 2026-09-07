from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import (
    WalletGraphResponse,
    WalletInfoResponse,
    WalletRiskResponse,
    WalletTransactionsResponse,
)

router = APIRouter(tags=["wallet"])

# Path(pattern=...) makes FastAPI reject a malformed address with a
# standard 422, same as the body validation used in InvestigateRequest.
ADDRESS_PATH = Path(..., pattern=r"^0x[a-fA-F0-9]{40}$")


@router.get("/api/wallet/{address}", response_model=WalletInfoResponse)
def get_wallet(address: str = ADDRESS_PATH):
    """
    Phase 1 placeholder — blockchain ingestion (Person A) is not wired up yet.
    """
    return WalletInfoResponse(
        address=address,
        message="Wallet endpoint ready; blockchain data will be connected in a later phase.",
    )


@router.get("/api/wallet/{address}/risk", response_model=WalletRiskResponse)
def get_wallet_risk(address: str = ADDRESS_PATH, db: Session = Depends(get_db)):
    """
    Return a stored WalletRisk record if one exists, otherwise a
    placeholder. Phase 1 does NOT compute risk — that's Person C/D's
    ML/rule engine.
    """
    risk = (
        db.query(models.WalletRisk)
        .filter(models.WalletRisk.address == address)
        .order_by(models.WalletRisk.id.desc())
        .first()
    )
    if risk is None:
        return WalletRiskResponse(
            address=address,
            risk_score=None,
            risk_level=None,
            message="No risk result available yet.",
        )
    return WalletRiskResponse(
        address=address,
        risk_score=risk.risk_score,
        risk_level=risk.risk_level,
        reasons=risk.reasons,
    )


@router.get("/api/wallet/{address}/graph", response_model=WalletGraphResponse)
def get_wallet_graph(address: str = ADDRESS_PATH):
    """
    Phase 1 placeholder — will eventually expose Person B's TraceResult.
    """
    return WalletGraphResponse(
        address=address,
        paths_found=0,
        paths=[],
        message="Graph data will be connected to Person B in a later phase.",
    )


@router.get("/api/wallet/{address}/transactions", response_model=WalletTransactionsResponse)
def get_wallet_transactions(address: str = ADDRESS_PATH):
    """
    Phase 1 placeholder — will eventually expose Person A's blockchain data.
    """
    return WalletTransactionsResponse(
        address=address,
        transactions=[],
        message="Transaction data will be connected to Person A in a later phase.",
    )
