"""
Tests for Person D's Phase 1 module: address_db, rule_engine, risk_scorer.
Run with: pytest backend/tests/test_rules.py -v
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "intelligence"))

import pytest

from address_db import load_intelligence_db, lookup_address
from rule_engine import (
    check_high_velocity,
    check_peel_chain,
    check_fan_in,
    check_fan_out,
    check_known_malicious,
    check_mixer_interaction,
    check_round_tripping,
    run_all_rules,
)
from risk_scorer import compute_risk_score


# ---------- Fixtures / helpers ----------

@pytest.fixture(scope="module")
def address_db():
    return load_intelligence_db()


def make_tx(from_addr, to_addr, ts, value=1.0, tx_hash="0xabc"):
    return {
        "tx_hash": tx_hash,
        "from_address": from_addr,
        "to_address": to_addr,
        "value": value,
        "value_usd": None,
        "token": "ETH",
        "token_contract": None,
        "block_number": 18200000,
        "timestamp": ts,
        "gas_used": 21000,
        "gas_price_gwei": 25.0,
        "is_erc20": False,
        "tx_status": "success",
    }


def make_profile(address, transactions=None, **overrides):
    base = {
        "address": address,
        "transactions": transactions or [],
        "in_degree": 2,
        "out_degree": 2,
        "total_received": 5.0,
        "total_sent": 1.0,
        "first_seen": 1690000000,
        "last_seen": 1693000000,
        "hop_distance_from_suspect": 1,
    }
    base.update(overrides)
    return base


# ---------- high velocity ----------

def test_high_velocity_triggers():
    addr = "0xSuspect1"
    txs = [
        make_tx("0xVictim", addr, ts=1000, tx_hash="0xin"),
        make_tx(addr, "0xHop1", ts=1300, tx_hash="0xout"),  # 5 min later
    ]
    assert check_high_velocity(make_profile(addr, txs)).triggered is True


def test_high_velocity_does_not_trigger_when_slow():
    addr = "0xSuspect2"
    txs = [
        make_tx("0xVictim", addr, ts=1000, tx_hash="0xin"),
        make_tx(addr, "0xHop1", ts=100000, tx_hash="0xout"),
    ]
    assert check_high_velocity(make_profile(addr, txs)).triggered is False


# ---------- peel chain ----------

def test_peel_chain_triggers():
    profile = make_profile("0xSuspect3", total_received=10.0, total_sent=9.5)
    assert check_peel_chain(profile).triggered is True


def test_peel_chain_does_not_trigger():
    profile = make_profile("0xSuspect4", total_received=10.0, total_sent=2.0)
    assert check_peel_chain(profile).triggered is False


def test_peel_chain_handles_zero_received():
    profile = make_profile("0xSuspect13", total_received=0, total_sent=0)
    assert check_peel_chain(profile).triggered is False


# ---------- fan-in / fan-out ----------

def test_fan_in_triggers():
    assert check_fan_in(make_profile("0xSuspect5", in_degree=25)).triggered is True


def test_fan_in_does_not_trigger():
    assert check_fan_in(make_profile("0xSuspect6", in_degree=5)).triggered is False


def test_fan_out_triggers():
    assert check_fan_out(make_profile("0xSuspect7", out_degree=30)).triggered is True


def test_fan_out_does_not_trigger():
    assert check_fan_out(make_profile("0xSuspect8", out_degree=1)).triggered is False


# ---------- known malicious / mixer ----------

def test_known_malicious_triggers_for_blacklisted_address(address_db):
    scam_addr = next(
        (a for a, label in address_db.items() if label.entity_type in ("SCAM", "SANCTIONED")),
        None,
    )
    assert scam_addr is not None, "Seed DB needs at least one SCAM/SANCTIONED address."
    assert check_known_malicious(make_profile(scam_addr), address_db).triggered is True


def test_known_malicious_does_not_trigger_for_clean_address(address_db):
    profile = make_profile("0xNotInDatabaseWhatsoever")
    assert check_known_malicious(profile, address_db).triggered is False


def test_mixer_interaction_triggers(address_db):
    mixer_addr = next((a for a, label in address_db.items() if label.entity_type == "MIXER"), None)
    assert mixer_addr is not None, "Seed DB needs at least one MIXER address."
    txs = [make_tx("0xSuspect9", mixer_addr, ts=1000)]
    assert check_mixer_interaction(make_profile("0xSuspect9", txs), address_db).triggered is True


def test_mixer_interaction_does_not_trigger(address_db):
    txs = [make_tx("0xSuspect10", "0xSomeRandomAddress", ts=1000)]
    assert check_mixer_interaction(make_profile("0xSuspect10", txs), address_db).triggered is False


# ---------- round tripping ----------

def test_round_tripping_triggers():
    addr = "0xSuspect11"
    txs = [
        make_tx(addr, "0xHopA", ts=1000, tx_hash="0x1"),
        make_tx("0xHopB", addr, ts=1100, tx_hash="0x2"),
        make_tx(addr, "0xHopA", ts=1200, tx_hash="0x3"),  # HopA seen again
    ]
    assert check_round_tripping(make_profile(addr, txs)).triggered is True


def test_round_tripping_does_not_trigger():
    addr = "0xSuspect12"
    txs = [
        make_tx(addr, "0xHopA", ts=1000, tx_hash="0x1"),
        make_tx(addr, "0xHopB", ts=1100, tx_hash="0x2"),
    ]
    assert check_round_tripping(make_profile(addr, txs)).triggered is False


# ---------- address lookup edge case ----------

def test_address_lookup_is_case_insensitive(address_db):
    some_addr = next(iter(address_db))
    upper = "0x" + some_addr[2:].upper()
    assert lookup_address(upper, address_db) is not None


# ---------- run_all_rules ----------

def test_run_all_rules_returns_only_triggered():
    addr = "0xSuspect14"
    profile = make_profile(addr, in_degree=50, out_degree=1)  # fan_in should trigger
    results = run_all_rules(profile, {})
    assert all(r.triggered for r in results)
    assert any(r.rule == "fan_in" for r in results)


# ---------- risk_scorer ----------

def test_risk_scorer_overrides_for_known_exchange(address_db):
    exchange_addr = next((a for a, label in address_db.items() if label.entity_type == "EXCHANGE"), None)
    assert exchange_addr is not None, "Seed DB needs at least one EXCHANGE address."
    profile = make_profile(exchange_addr, in_degree=100, out_degree=100)  # would otherwise score high
    report = compute_risk_score(profile, address_db)
    assert report["risk_score"] == 0
    assert report["risk_level"] == "LOW"
    assert report["entity_label"] == "EXCHANGE"


def test_risk_scorer_overrides_for_known_scam(address_db):
    scam_addr = next((a for a, label in address_db.items() if label.entity_type in ("SCAM", "SANCTIONED")), None)
    assert scam_addr is not None
    report = compute_risk_score(make_profile(scam_addr), address_db)
    assert report["risk_score"] == 100
    assert report["risk_level"] == "CRITICAL"


def test_risk_scorer_uses_rule_score_for_unknown_address(address_db):
    profile = make_profile("0xTotallyUnknownAddress", in_degree=25)  # triggers fan_in only
    report = compute_risk_score(profile, address_db)
    assert report["entity_label"] == "UNKNOWN"
    assert report["risk_score"] == 8  # 1 rule * 8 points
    assert report["ml_confidence"] is None
    assert report["shap_features"] == []


def test_risk_scorer_output_matches_contract_3_shape(address_db):
    report = compute_risk_score(make_profile("0xShapeCheckAddress"), address_db)
    expected_keys = {
        "address", "risk_score", "risk_level", "ml_confidence",
        "rules_triggered", "shap_features", "entity_label", "entity_name",
    }
    assert set(report.keys()) == expected_keys
