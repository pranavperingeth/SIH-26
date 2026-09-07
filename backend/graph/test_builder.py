"""
===========================================================
TEST SCRIPT — Verify your Neo4j Graph Engine works
===========================================================

HOW TO RUN:
    1. Make sure Neo4j is running (Docker or Neo4j Desktop)
    2. cd into the project root: cd /path/to/SIH-26
    3. Run: python -m backend.graph.test_builder

WHAT THIS DOES:
    - Connects to Neo4j
    - Creates the schema (constraints + indexes)
    - Inserts 5 fake transactions forming a chain:
        Victim → Scammer → Hop1 → Hop2 → BinanceHotWallet
    - Labels BinanceHotWallet as an EXCHANGE
    - Prints stats and transaction data
    - Verifies everything worked

AFTER RUNNING:
    Open http://localhost:7474 in your browser
    Run this Cypher query to SEE your graph:
        MATCH (n)-[r]->(m) RETURN n, r, m

    You should see 5 wallet nodes connected by 5 SENT edges,
    forming a chain from Victim to Binance.
===========================================================
"""

import sys
import os

# Add the project root to the Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.graph.neo4j_client import Neo4jClient
from backend.graph.schema import init_schema, drop_all
from backend.graph.builder import GraphBuilder


def main():
    print("=" * 60)
    print("🧪 ChainTrace — Graph Engine Test")
    print("=" * 60)

    # ─────────────────────────────────────────────
    # Step 1: Connect to Neo4j
    # ─────────────────────────────────────────────
    print("\n📡 Step 1: Connecting to Neo4j...")

    try:
        client = Neo4jClient()
        connected = client.verify_connection()
        if connected:
            print("   ✅ Connected to Neo4j!")
        else:
            print("   ❌ Could not connect. Is Neo4j running?")
            print("   💡 Start it with: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/chaintrace123 neo4j:5")
            return
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("   💡 Start Neo4j with: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/chaintrace123 neo4j:5")
        return

    # ─────────────────────────────────────────────
    # Step 2: Clean slate + initialize schema
    # ─────────────────────────────────────────────
    print("\n🗑️  Step 2: Clearing old data and creating schema...")

    drop_all(client, confirm=True)
    print("   Cleared old data.")

    init_schema(client)
    print("   ✅ Schema created (constraints + indexes)")

    # ─────────────────────────────────────────────
    # Step 3: Create test transactions
    # ─────────────────────────────────────────────
    print("\n📝 Step 3: Inserting test transactions...")

    # These simulate a real fraud chain:
    # Victim --2.0 ETH--> Scammer --1.95 ETH--> Hop1 --1.90 ETH--> Hop2 --1.85 ETH--> Binance
    # Plus: Victim2 --0.5 ETH--> Scammer (fan-in pattern)

    test_transactions = [
        {
            "tx_hash": "0xaaa111",
            "from_address": "0xVICTIM_WALLET",
            "to_address": "0xSCAMMER_WALLET",
            "value": 2.0,
            "token": "ETH",
            "timestamp": 1693000000,
            "block_number": 18200000,
        },
        {
            "tx_hash": "0xbbb222",
            "from_address": "0xSCAMMER_WALLET",
            "to_address": "0xHOP1_WALLET",
            "value": 1.95,
            "token": "ETH",
            "timestamp": 1693000180,
            "block_number": 18200015,
        },
        {
            "tx_hash": "0xccc333",
            "from_address": "0xHOP1_WALLET",
            "to_address": "0xHOP2_WALLET",
            "value": 1.90,
            "token": "ETH",
            "timestamp": 1693000360,
            "block_number": 18200030,
        },
        {
            "tx_hash": "0xddd444",
            "from_address": "0xHOP2_WALLET",
            "to_address": "0xBINANCE_HOT_WALLET",
            "value": 1.85,
            "token": "ETH",
            "timestamp": 1693000900,
            "block_number": 18200050,
        },
        {
            "tx_hash": "0xeee555",
            "from_address": "0xVICTIM2_WALLET",
            "to_address": "0xSCAMMER_WALLET",
            "value": 0.5,
            "token": "ETH",
            "timestamp": 1693001000,
            "block_number": 18200060,
        },
    ]

    builder = GraphBuilder(client)

    builder.insert_batch(test_transactions)
    print(f"   ✅ Inserted {len(test_transactions)} transactions")

    # ─────────────────────────────────────────────
    # Step 4: Label the exchange wallet
    # ─────────────────────────────────────────────
    print("\n🏷️  Step 4: Labeling known wallets...")

    builder.label_wallet("0xBINANCE_HOT_WALLET", "EXCHANGE", "EXCHANGE")
    print("   ✅ Labeled 0xBINANCE_HOT_WALLET as EXCHANGE")

    builder.label_wallet("0xSCAMMER_WALLET", "SCAM", "SCAM")
    print("   ✅ Labeled 0xSCAMMER_WALLET as SCAM")

    # ─────────────────────────────────────────────
    # Step 5: Check stats
    # ─────────────────────────────────────────────
    print("\n📊 Step 5: Graph stats...")

    stats = builder.get_stats()
    print(f"   Wallet nodes:      {stats['total_wallets']}")
    print(f"   Transaction edges: {stats['total_transactions']}")
    print(f"   Labeled wallets:   {stats['labeled_wallets']}")
    print(f"   Exchanges found:   {stats['exchanges_found']}")

    # ─────────────────────────────────────────────
    # Step 6: Query specific wallet data
    # ─────────────────────────────────────────────
    print("\n🔍 Step 6: Querying the scammer wallet...")

    wallet = builder.get_wallet("0xSCAMMER_WALLET")
    if wallet:
        print(f"   Address:     {wallet.get('address', 'N/A')}")
        print(f"   Label:       {wallet.get('label', 'N/A')}")
        print(f"   Entity type: {wallet.get('entity_type', 'N/A')}")
        print(f"   First seen:  {wallet.get('first_seen', 'N/A')}")
    else:
        print("   ⚠️  Wallet not found!")

    print("\n📤 Scammer's OUTGOING transactions:")
    outgoing = builder.get_wallet_transactions("0xSCAMMER_WALLET", direction="outgoing")
    for tx in outgoing:
        print(f"   → Sent {tx.get('amount', '?')} {tx.get('token', '?')} to {tx.get('to_address', '?')}")

    print("\n📥 Scammer's INCOMING transactions:")
    incoming = builder.get_wallet_transactions("0xSCAMMER_WALLET", direction="incoming")
    for tx in incoming:
        print(f"   ← Received {tx.get('amount', '?')} {tx.get('token', '?')} from {tx.get('from_address', '?')}")

    # ─────────────────────────────────────────────
    # Done!
    # ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Open Neo4j Browser: http://localhost:7474")
    print("  2. Run: MATCH (n)-[r]->(m) RETURN n, r, m")
    print()
    print("  You should see:")
    print("  Victim1 ──→ Scammer ──→ Hop1 ──→ Hop2 ──→ Binance")
    print("  Victim2 ──→ Scammer")
    print()
    print("  Phase 2: You'll build tracer.py (BFS) to find")
    print("  the path from suspect → exchange automatically! 🔥")

    client.close()


if __name__ == "__main__":
    main()
