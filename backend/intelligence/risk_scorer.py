"""
Risk Scorer (Phase 1 - partial)
Person D

Combines rule engine results and known-entity overrides into a preliminary
RiskReport. ML probability and graph hop distance are wired in during Phase 3
(see plan.md Contract 3) - those fields are placeholders here.
"""

from typing import List, Optional

from rule_engine import RuleResult, run_all_rules
from address_db import lookup_address, is_exchange, is_known_malicious

RULE_POINTS_PER_RULE = 8
MAX_RULE_POINTS = 40
MAX_RULES_COUNTED = 5

# Checked in order; first threshold the score meets or exceeds wins.
RISK_LEVEL_BANDS = [
    (80, "CRITICAL"),
    (60, "HIGH"),
    (30, "MEDIUM"),
    (0, "LOW"),
]


def _risk_level_for_score(score: int) -> str:
    for threshold, level in RISK_LEVEL_BANDS:
        if score >= threshold:
            return level
    return "LOW"


def compute_risk_score(
    wallet_profile: dict,
    address_db: dict,
    graph_client: Optional[object] = None,
) -> dict:
    """
    Phase 1 scoring: rules + known-entity overrides only.
    ml_confidence and shap_features are left as placeholders for Phase 3.

    Scoring:
      - Rule score: len(triggered_rules) * 8, capped at 40 (max 5 rules counted)
      - Known-entity override: known exchange -> 0 (LOW);
        known scam/mixer/sanctioned -> 100 (CRITICAL)
    """
    address = wallet_profile["address"]

    triggered_rules: List[RuleResult] = run_all_rules(wallet_profile, address_db, graph_client)
    rules_triggered_payload = [r.to_dict() for r in triggered_rules]

    rule_score = min(len(triggered_rules), MAX_RULES_COUNTED) * RULE_POINTS_PER_RULE
    rule_score = min(rule_score, MAX_RULE_POINTS)

    entity_label = "UNKNOWN"
    entity_name = None
    label = lookup_address(address, address_db)
    if label:
        entity_label = label.entity_type
        entity_name = label.entity_name

    # Known-entity overrides take priority over the computed rule score.
    if is_exchange(address, address_db):
        risk_score = 0
    elif is_known_malicious(address, address_db):
        risk_score = 100
    else:
        risk_score = rule_score

    risk_level = _risk_level_for_score(risk_score)

    return {
        "address": address,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "ml_confidence": None,   # filled in Phase 3 by Person C's model
        "rules_triggered": rules_triggered_payload,
        "shap_features": [],     # filled in Phase 3
        "entity_label": entity_label,
        "entity_name": entity_name,
    }


if __name__ == "__main__":
    from address_db import load_intelligence_db

    intel_db = load_intelligence_db()
    mock_profile = {
        "address": "0xSuspectWalletExample000000000000000001",
        "transactions": [],
        "in_degree": 25,
        "out_degree": 2,
        "total_received": 10.0,
        "total_sent": 9.5,
        "first_seen": 1690000000,
        "last_seen": 1693000000,
        "hop_distance_from_suspect": 0,
    }
    report = compute_risk_score(mock_profile, intel_db)
    print(report)
