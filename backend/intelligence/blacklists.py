"""
Blacklist Integration
Person D - Phase 1

Pulls known-malicious address data from external sources and normalizes it
into the same schema used by address_db.py, so it can be merged into the
intelligence DB.

Phase 1 note: network calls are best-effort. If API access isn't available,
use load_local_ofac_dump() with a manually downloaded copy of the data
instead - the pipeline must not crash if a source is unreachable.
"""

import csv
import os
from typing import List

import requests

from address_db import add_address, AddressLabel

CRYPTOSCAMDB_API = "https://api.cryptoscamdb.org/v1/addresses"
OFAC_SDN_LOCAL_PATH = os.path.join(os.path.dirname(__file__), "data", "ofac_sdn_crypto.csv")


def fetch_cryptoscamdb(timeout: int = 10) -> List[AddressLabel]:
    """
    Pull scam addresses from CryptoScamDB. Falls back to an empty list on
    any network/parsing failure rather than crashing the whole pipeline.
    """
    labels: List[AddressLabel] = []
    try:
        resp = requests.get(CRYPTOSCAMDB_API, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        result = data.get("result", {})
        for address, entries in result.items():
            for entry in entries:
                labels.append(
                    AddressLabel(
                        address=address.lower(),
                        entity_name=entry.get("name", "Unknown Scam"),
                        entity_type="SCAM",
                        source="cryptoscamdb",
                        risk_level="CRITICAL",
                    )
                )
    except (requests.RequestException, ValueError) as exc:
        print(f"[blacklists] CryptoScamDB fetch failed, skipping: {exc}")
    return labels


def load_local_ofac_dump(path: str = OFAC_SDN_LOCAL_PATH) -> List[AddressLabel]:
    """
    Load a locally-downloaded OFAC SDN crypto-address CSV
    (expected columns: address, entity_name). Treasury's raw SDN feed isn't
    a clean per-address CSV, so download/extract the relevant rows manually
    and place them here.
    """
    labels: List[AddressLabel] = []
    if not os.path.exists(path):
        print(f"[blacklists] No local OFAC dump found at {path}, skipping.")
        return labels

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels.append(
                AddressLabel(
                    address=row["address"].strip().lower(),
                    entity_name=row.get("entity_name", "OFAC Sanctioned"),
                    entity_type="SANCTIONED",
                    source="ofac",
                    risk_level="CRITICAL",
                )
            )
    return labels


def refresh_blacklists(db: dict) -> int:
    """
    Fetch/load all blacklist sources and merge them into the in-memory DB
    (persisted via address_db.add_address). Returns count of entries merged.
    """
    all_labels = fetch_cryptoscamdb() + load_local_ofac_dump()
    for label in all_labels:
        add_address(
            address=label.address,
            entity_name=label.entity_name,
            entity_type=label.entity_type,
            source=label.source,
            risk_level=label.risk_level,
            db=db,
        )
    return len(all_labels)


if __name__ == "__main__":
    from address_db import load_intelligence_db

    intel_db = load_intelligence_db()
    added = refresh_blacklists(intel_db)
    print(f"Merged {added} blacklist entries. DB now has {len(intel_db)} addresses.")
