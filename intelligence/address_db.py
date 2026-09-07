"""
Address Intelligence DB
Person D - Phase 1

Loads a seed list of known blockchain entities (exchanges, mixers, scam
addresses) into memory and a local SQLite table, and exposes lookup helpers
used by rule_engine.py and risk_scorer.py.
"""

import csv
import os
import sqlite3
from dataclasses import dataclass
from typing import Optional

SEED_CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "known_addresses.csv")
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "address_intelligence.db")


@dataclass
class AddressLabel:
    address: str
    entity_name: str
    entity_type: str  # EXCHANGE | MIXER | SCAM | SANCTIONED | UNKNOWN
    source: str
    risk_level: str  # LOW | MEDIUM | HIGH | CRITICAL

    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "source": self.source,
            "risk_level": self.risk_level,
        }


def _normalize(address: str) -> str:
    """Ethereum addresses are case-insensitive at the protocol level."""
    return address.strip().lower()


def _ensure_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS address_labels (
            address TEXT PRIMARY KEY,
            entity_name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            source TEXT NOT NULL,
            risk_level TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def load_intelligence_db(csv_path: str = SEED_CSV_PATH) -> dict:
    """
    Load the seed CSV into memory (dict keyed by lowercased address) and
    persist it into SQLite. Returns the in-memory dict: {address: AddressLabel}
    """
    _ensure_db()
    db: dict = {}

    if not os.path.exists(csv_path):
        return db

    conn = sqlite3.connect(DB_PATH)
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = _normalize(row["address"])
            label = AddressLabel(
                address=addr,
                entity_name=row["entity_name"],
                entity_type=row["entity_type"].upper(),
                source=row["source"],
                risk_level=row["risk_level"].upper(),
            )
            db[addr] = label
            conn.execute(
                """
                INSERT OR REPLACE INTO address_labels
                (address, entity_name, entity_type, source, risk_level)
                VALUES (?, ?, ?, ?, ?)
                """,
                (label.address, label.entity_name, label.entity_type, label.source, label.risk_level),
            )
    conn.commit()
    conn.close()
    return db


def lookup_address(address: str, db: Optional[dict] = None) -> Optional[AddressLabel]:
    """
    Look up an address. If `db` (in-memory dict from load_intelligence_db) is
    provided, use it directly; otherwise fall back to querying SQLite.
    """
    addr = _normalize(address)

    if db is not None:
        return db.get(addr)

    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT address, entity_name, entity_type, source, risk_level FROM address_labels WHERE address = ?",
        (addr,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    return AddressLabel(*row)


def is_exchange(address: str, db: Optional[dict] = None) -> bool:
    label = lookup_address(address, db)
    return label is not None and label.entity_type == "EXCHANGE"


def is_known_malicious(address: str, db: Optional[dict] = None) -> bool:
    label = lookup_address(address, db)
    return label is not None and label.entity_type in ("SCAM", "MIXER", "SANCTIONED")


def add_address(
    address: str,
    entity_name: str,
    entity_type: str,
    source: str,
    risk_level: str = "MEDIUM",
    db: Optional[dict] = None,
) -> AddressLabel:
    """Add or update an address at runtime (e.g. from blacklists.py refresh)."""
    _ensure_db()
    addr = _normalize(address)
    label = AddressLabel(
        address=addr,
        entity_name=entity_name,
        entity_type=entity_type.upper(),
        source=source,
        risk_level=risk_level.upper(),
    )

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT OR REPLACE INTO address_labels
        (address, entity_name, entity_type, source, risk_level)
        VALUES (?, ?, ?, ?, ?)
        """,
        (label.address, label.entity_name, label.entity_type, label.source, label.risk_level),
    )
    conn.commit()
    conn.close()

    if db is not None:
        db[addr] = label

    return label


if __name__ == "__main__":
    intel_db = load_intelligence_db()
    print(f"Loaded {len(intel_db)} known addresses.")
    sample = next(iter(intel_db), None)
    if sample:
        print(lookup_address(sample, intel_db))
