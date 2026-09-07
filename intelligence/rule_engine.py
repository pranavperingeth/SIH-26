"""
Rule Engine
Person D - Phase 1

Each rule takes a WalletProfile (Contract 2 shape from plan.md) and returns a
RuleResult. run_all_rules() executes every rule and returns only the ones
that triggered.
"""

from dataclasses import dataclass
from typing import List, Optional

from address_db import is_known_malicious, lookup_address


@dataclass
class RuleResult:
    rule: str
    triggered: bool
    detail: str

    def to_dict(self) -> dict:
        return {"rule": self.rule, "detail": self.detail}


# --- Thresholds (named constants so they're easy to tune later) ---
HIGH_VELOCITY_SECONDS = 10 * 60  # 10 minutes
PEEL_CHAIN_RATIO = 0.90          # sent > 90% of received
FAN_IN_THRESHOLD = 20            # unique senders
FAN_OUT_THRESHOLD = 20           # unique receivers


def check_high_velocity(wallet_profile: dict) -> RuleResult:
    """Flag if funds were forwarded within HIGH_VELOCITY_SECONDS of receipt."""
    txs = sorted(wallet_profile.get("transactions", []), key=lambda t: t["timestamp"])
    address = wallet_profile["address"].lower()

    incoming = [t for t in txs if t["to_address"].lower() == address]
    outgoing = [t for t in txs if t["from_address"].lower() == address]

    for in_tx in incoming:
        for out_tx in outgoing:
            gap = out_tx["timestamp"] - in_tx["timestamp"]
            if 0 <= gap <= HIGH_VELOCITY_SECONDS:
                return RuleResult(
                    rule="high_velocity",
                    triggered=True,
                    detail=f"Funds forwarded {gap}s after receipt "
                    f"(tx {in_tx['tx_hash'][:10]}... -> {out_tx['tx_hash'][:10]}...).",
                )
    return RuleResult(rule="high_velocity", triggered=False, detail="No rapid forward-on detected.")


def check_peel_chain(wallet_profile: dict) -> RuleResult:
    """Flag if total_sent > PEEL_CHAIN_RATIO * total_received."""
    received = wallet_profile.get("total_received", 0)
    sent = wallet_profile.get("total_sent", 0)

    if received <= 0:
        return RuleResult(rule="peel_chain", triggered=False, detail="No inbound funds to compare.")

    ratio = sent / received
    if ratio > PEEL_CHAIN_RATIO:
        return RuleResult(
            rule="peel_chain",
            triggered=True,
            detail=f"Sent {sent:.4f} of {received:.4f} received ({ratio:.1%}), consistent with peel-chain layering.",
        )
    return RuleResult(rule="peel_chain", triggered=False, detail=f"Sent/received ratio {ratio:.1%}, within normal range.")


def check_fan_in(wallet_profile: dict) -> RuleResult:
    """Flag if unique_senders > FAN_IN_THRESHOLD."""
    in_degree = wallet_profile.get("in_degree", 0)
    if in_degree > FAN_IN_THRESHOLD:
        return RuleResult(
            rule="fan_in",
            triggered=True,
            detail=f"Received from {in_degree} unique senders (threshold: {FAN_IN_THRESHOLD}).",
        )
    return RuleResult(rule="fan_in", triggered=False, detail=f"{in_degree} unique senders, within normal range.")


def check_fan_out(wallet_profile: dict) -> RuleResult:
    """Flag if unique_receivers > FAN_OUT_THRESHOLD."""
    out_degree = wallet_profile.get("out_degree", 0)
    if out_degree > FAN_OUT_THRESHOLD:
        return RuleResult(
            rule="fan_out",
            triggered=True,
            detail=f"Sent to {out_degree} unique receivers (threshold: {FAN_OUT_THRESHOLD}).",
        )
    return RuleResult(rule="fan_out", triggered=False, detail=f"{out_degree} unique receivers, within normal range.")


def check_known_malicious(wallet_profile: dict, address_db: dict) -> RuleResult:
    """Flag if the wallet itself is in the blacklist/address DB as malicious."""
    address = wallet_profile["address"]
    if is_known_malicious(address, address_db):
        label = lookup_address(address, address_db)
        return RuleResult(
            rule="known_malicious",
            triggered=True,
            detail=f"Address is listed as {label.entity_type} ({label.entity_name}, source: {label.source}).",
        )
    return RuleResult(rule="known_malicious", triggered=False, detail="Address not found in blacklist/intelligence DB.")


def check_mixer_interaction(wallet_profile: dict, address_db: dict) -> RuleResult:
    """Flag if any counterparty in the wallet's transactions is a known mixer."""
    for tx in wallet_profile.get("transactions", []):
        for counterparty in (tx["from_address"], tx["to_address"]):
            label = lookup_address(counterparty, address_db)
            if label and label.entity_type == "MIXER":
                return RuleResult(
                    rule="mixer_interaction",
                    triggered=True,
                    detail=f"Interacted with known mixer {label.entity_name} (tx {tx['tx_hash'][:10]}...).",
                )
    return RuleResult(rule="mixer_interaction", triggered=False, detail="No known mixer interactions found.")


def check_round_tripping(wallet_profile: dict, graph_client: Optional[object] = None) -> RuleResult:
    """
    Flag if funds cycle back to a previously-seen counterparty.
    Phase 1: graph_client is not yet available (Person B builds the real
    tracer in later phases), so this checks only within the wallet's own
    transaction list as an approximation.
    """
    txs = wallet_profile.get("transactions", [])
    seen_counterparties = set()
    address = wallet_profile["address"].lower()

    for tx in sorted(txs, key=lambda t: t["timestamp"]):
        other = tx["to_address"].lower() if tx["from_address"].lower() == address else tx["from_address"].lower()
        if other in seen_counterparties:
            return RuleResult(
                rule="round_tripping",
                triggered=True,
                detail=f"Funds cycled back through a previously-seen counterparty ({other[:10]}...).",
            )
        seen_counterparties.add(other)

    return RuleResult(
        rule="round_tripping",
        triggered=False,
        detail="No round-tripping detected in available transaction data "
        "(full graph-level check pending Person B's tracer).",
    )


def run_all_rules(wallet_profile: dict, address_db: dict, graph_client: Optional[object] = None) -> List[RuleResult]:
    """Run every rule and return only the ones that triggered."""
    all_results = [
        check_high_velocity(wallet_profile),
        check_peel_chain(wallet_profile),
        check_fan_in(wallet_profile),
        check_fan_out(wallet_profile),
        check_known_malicious(wallet_profile, address_db),
        check_mixer_interaction(wallet_profile, address_db),
        check_round_tripping(wallet_profile, graph_client),
    ]
    return [r for r in all_results if r.triggered]
