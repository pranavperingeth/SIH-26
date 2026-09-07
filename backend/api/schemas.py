"""
Pydantic schemas for ChainTrace (Person E — Phase 1).
"""

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

ETH_ADDRESS_REGEX = re.compile(r"^0x[a-fA-F0-9]{40}$")


class InvestigateRequest(BaseModel):
    wallet_address: str
    chain: str = "ethereum"
    max_hops: int = Field(default=6, gt=0, le=20)
    description: str | None = None

    @field_validator("wallet_address")
    @classmethod
    def validate_wallet_address(cls, value: str) -> str:
        if not ETH_ADDRESS_REGEX.match(value):
            raise ValueError(
                "wallet_address must be a valid Ethereum address "
                "(0x followed by 40 hex characters)"
            )
        return value


class InvestigateResponse(BaseModel):
    investigation_id: str
    status: str
    message: str


class InvestigationOut(BaseModel):
    id: str
    suspect_wallet: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class InvestigationListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    results: list[InvestigationOut]


class WalletInfoResponse(BaseModel):
    address: str
    message: str


class WalletRiskResponse(BaseModel):
    address: str
    risk_score: int | None = None
    risk_level: str | None = None
    reasons: list | dict | None = None
    message: str | None = None


class WalletGraphResponse(BaseModel):
    address: str
    paths_found: int = 0
    paths: list = []
    message: str


class WalletTransactionsResponse(BaseModel):
    address: str
    transactions: list = []
    message: str


class AlertOut(BaseModel):
    id: str
    investigation_id: str
    wallet_address: str
    alert_type: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
