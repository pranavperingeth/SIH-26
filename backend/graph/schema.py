"""
================================================================================
CHAINTRACE - NEO4J GRAPH DATABASE SCHEMA DEFINITIONS
================================================================================
Smart India Hackathon 2026 | Problem ID: 26183
Organization: Ministry of Home Affairs | Department: I4C, CIS Division
Theme: Blockchain & Cybersecurity

Project: ChainTrace - Real-Time Identification of Fraud-Linked Crypto Exchanges
Module:  backend/graph/schema.py
Purpose: Defines the complete Neo4j Property Graph schema, including:
         - Node labels and property specifications
         - Relationship types and edge attributes
         - Cypher DDL queries for uniqueness constraints & performance indexes
         - Utility functions for schema lifecycle (init, drop, inspect)

================================================================================
GRAPH DATA MODELING CONCEPTS (A BEGINNER'S GUIDE)
================================================================================

1. WHAT IS A GRAPH DATABASE (NEO4J)?
   ---------------------------------
   In traditional relational databases (SQL), data lives in tables with rows and
   columns. To connect two entities, you use foreign keys and JOIN operations.
   As queries span multiple "hops" (e.g., Wallet A -> Wallet B -> Wallet C),
   relational JOINs become exponentially slow and computationally prohibitive.

   Neo4j is a "Labeled Property Graph" database. Here:
   - NODES (Vertices) represent entities (e.g., a Wallet, an Exchange).
   - LABELS categorize nodes (e.g., :Wallet, :Exchange, :SmartContract).
   - RELATIONSHIPS (Edges) represent directed connections between nodes
     (e.g., :SENT, :DEPOSITED_TO).
   - PROPERTIES are key-value pairs stored directly on nodes or relationships
     (e.g., amount: 1.5, timestamp: 1698765432).

   Graph databases excel at "index-free adjacency", meaning traversing from one
   wallet to the next takes constant O(1) time per step, making 6-hop money
   laundering path-tracing blisteringly fast.

2. WHAT IS A CONSTRAINT AND WHY DO WE NEED IT?
   -------------------------------------------
   A CONSTRAINT is a database-level integrity rule that enforces data validity.
   In ChainTrace, the most critical constraint is the UNIQUENESS CONSTRAINT:

       CREATE CONSTRAINT wallet_address_unique
       FOR (w:Wallet) REQUIRE w.address IS UNIQUE

   * WHY WE NEED IT (PREVENTING DUPLICATE WALLETS):
     Suppose an investigator traces funds through wallet "0xabc...123". Later,
     another transaction arrives that also involves "0xabc...123".
     Without a uniqueness constraint, a naive insertion query might create a
     brand-new second node for "0xabc...123".
     If duplicate nodes exist for the same physical blockchain address:
     a) The money trail is fragmented into disconnected graph islands.
     b) Breadth-First Search (BFS) tracing algorithms will fail to find the
        path to the cash-out exchange because the incoming and outgoing edges
        attach to different node instances.
     c) Risk scores and transaction volumes become inaccurate.

   * AUTOMATIC INDEXING BENEFIT:
     In Neo4j, creating a uniqueness constraint automatically creates a backing
     index. You get duplicate prevention AND instant O(1)/O(log N) address
     lookups in a single command.

3. WHAT IS AN INDEX AND WHY DO WE NEED IT?
   ---------------------------------------
   An INDEX is a specialized lookup data structure (such as a B-tree) maintained
   by the database engine alongside the raw graph data.

   * WHY WE NEED IT (SPEEDING UP QUERIES):
     Without an index, finding a node with a specific property value requires a
     "Full Node Scan" (examining every single node in the entire database one by
     one - an O(N) operation). In a production database with millions of wallets,
     this would take several seconds or minutes per query.

     With an index on `risk_score`:
     - Neo4j traverses a balanced tree in O(log N) time to immediately locate
       high-risk nodes (e.g., `WHERE w.risk_score >= 80`).
     - Queries used in emergency freeze requests execute in milliseconds.

   * RELATIONSHIP INDEXES (NEO4J 5+):
     ChainTrace also indexes properties on relationships (like `tx_hash` and
     `timestamp` on `:SENT` edges). This allows instant lookup of specific
     transactions and rapid time-range filtering during peel-chain velocity
     detection.

4. NODE TYPES EXPLAINED:
   ---------------------
   a) Wallet (:Wallet):
      Represents an on-chain account, typically an Externally Owned Account (EOA)
      controlled by a private key. In ChainTrace investigations, a Wallet node
      can be a victim wallet, a scammer's primary collection wallet, an
      intermediate laundering hop (mule/peel chain), or an aggregator wallet.

   b) Exchange (:Exchange):
      Represents a cryptocurrency exchange entity (e.g., Binance, WazirX,
      Coinbase) or an exchange-operated deposit gateway/hot wallet.
      This is the primary TARGET for law enforcement: once stolen funds enter
      an exchange that enforces KYC (Know Your Customer), police can serve a
      legal freeze notice to seize the illicit funds before fiat withdrawal.

   c) SmartContract (:SmartContract):
      Represents autonomous executable code deployed on the blockchain. Examples
      include decentralized exchange (DEX) liquidity pools (Uniswap), cross-chain
      bridges (Hop, Multichain), or privacy mixers (Tornado Cash). Criminals
      frequently interact with smart contracts to swap stolen assets or obscure
      the transaction audit trail.

5. RELATIONSHIP TYPES EXPLAINED:
   -----------------------------
   a) SENT (:SENT):
      Directed edge from (:Wallet)-[:SENT]->(:Wallet).
      Represents an on-chain value transfer. Holds critical transaction evidence:
      amount, token symbol, transaction hash, and block timestamp.

   b) DEPOSITED_TO (:DEPOSITED_TO):
      Directed edge from (:Wallet)-[:DEPOSITED_TO]->(:Exchange).
      Represents a deposit into an exchange account. This edge marks the final
      cash-out hop of an investigation where an alert/freeze notice is triggered.

   c) INTERACTED_WITH (:INTERACTED_WITH):
      Directed edge from (:Wallet)-[:INTERACTED_WITH]->(:SmartContract).
      Represents a contract call (e.g., depositing into Tornado Cash or swapping
      ERC-20 tokens). Crucial for flagging mixer usage and obfuscation tactics.
================================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

# Set up module logger
logger = logging.getLogger("chaintrace.graph.schema")
if not logger.handlers:
    # Default to a console stream handler if none configured
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    _handler.setFormatter(_formatter)
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


# ==============================================================================
# SCHEMA CONSTANTS: CYPHERS, NODE LABELS & RELATIONSHIP TYPES
# ==============================================================================

# Cypher DDL queries to create all database constraints and performance indexes.
# Using 'IF NOT EXISTS' guarantees idempotent execution (safe to run repeatedly).
SCHEMA_QUERIES: List[str] = [
    # -------------------------------------------------------------------------
    # 1. Uniqueness Constraints (Data Integrity + Automatic Unique Indexes)
    # -------------------------------------------------------------------------
    # Enforces that each on-chain address exists as a single unique Wallet node.
    # Prevents duplicate wallet creation during high-concurrency trace ingestion.
    (
        "CREATE CONSTRAINT wallet_address_unique IF NOT EXISTS "
        "FOR (w:Wallet) REQUIRE w.address IS UNIQUE"
    ),

    # Enforces that each Exchange entity (e.g. 'Binance', 'WazirX') is unique.
    # Prevents multiple conflicting entries for the same exchange brand.
    (
        "CREATE CONSTRAINT exchange_name_unique IF NOT EXISTS "
        "FOR (e:Exchange) REQUIRE e.name IS UNIQUE"
    ),

    # Enforces that each SmartContract deployment address is globally unique.
    (
        "CREATE CONSTRAINT smart_contract_address_unique IF NOT EXISTS "
        "FOR (c:SmartContract) REQUIRE c.address IS UNIQUE"
    ),

    # -------------------------------------------------------------------------
    # 2. Node Property Indexes (Fast Lookups & Range Filtering)
    # -------------------------------------------------------------------------
    # Index on Wallet.risk_score:
    # Used when filtering suspects by threat tier (e.g., WHERE w.risk_score > 70.0).
    (
        "CREATE INDEX wallet_risk_score_idx IF NOT EXISTS "
        "FOR (w:Wallet) ON (w.risk_score)"
    ),

    # Index on Wallet.label:
    # Used when querying by investigative tag (e.g., WHERE w.label = 'EXCHANGE').
    (
        "CREATE INDEX wallet_label_idx IF NOT EXISTS "
        "FOR (w:Wallet) ON (w.label)"
    ),

    # Index on Wallet.entity_type:
    # Used for grouping by entity category (e.g., 'SCAM', 'MIXER', 'SANCTIONED').
    (
        "CREATE INDEX wallet_entity_type_idx IF NOT EXISTS "
        "FOR (w:Wallet) ON (w.entity_type)"
    ),

    # Index on Exchange.address:
    # Facilitates instant lookup when a known exchange deposit address is matched.
    (
        "CREATE INDEX exchange_address_idx IF NOT EXISTS "
        "FOR (e:Exchange) ON (e.address)"
    ),

    # Index on SmartContract.protocol:
    # Used to locate all contracts belonging to a specific DeFi/mixer protocol.
    (
        "CREATE INDEX smart_contract_protocol_idx IF NOT EXISTS "
        "FOR (c:SmartContract) ON (c.protocol)"
    ),

    # -------------------------------------------------------------------------
    # 3. Relationship Property Indexes (Neo4j 5+ Edge Attribute Lookups)
    # -------------------------------------------------------------------------
    # Index on (:SENT).tx_hash:
    # Enables instant O(1) retrieval of transfer edges by blockchain transaction hash.
    (
        "CREATE INDEX sent_tx_hash_idx IF NOT EXISTS "
        "FOR ()-[r:SENT]-() ON (r.tx_hash)"
    ),

    # Index on (:SENT).timestamp:
    # Accelerates time-window filtering during rapid-hop velocity analysis.
    (
        "CREATE INDEX sent_timestamp_idx IF NOT EXISTS "
        "FOR ()-[r:SENT]-() ON (r.timestamp)"
    ),

    # Index on (:SENT).amount:
    # Accelerates queries filtering out micro-dust transactions (e.g., r.amount > 0.01).
    (
        "CREATE INDEX sent_amount_idx IF NOT EXISTS "
        "FOR ()-[r:SENT]-() ON (r.amount)"
    ),

    # Index on (:DEPOSITED_TO).timestamp:
    # Speeds up timeline sequencing for exchange cash-out events.
    (
        "CREATE INDEX deposited_to_timestamp_idx IF NOT EXISTS "
        "FOR ()-[r:DEPOSITED_TO]-() ON (r.timestamp)"
    ),
]


# Comprehensive schema documentation dictionary for all Node types.
# Explains the role of each node and the exact schema/type of its properties.
NODE_LABELS: Dict[str, Dict[str, Any]] = {
    "Wallet": {
        "description": (
            "Represents a cryptocurrency address on the blockchain (typically an "
            "Externally Owned Account or unspecified wallet). It serves as the primary "
            "building block for transaction graph traversal."
        ),
        "properties": {
            "address": {
                "type": "STRING",
                "description": "Unique 0x-prefixed hexadecimal blockchain address (normalized to lowercase).",
                "required": True,
                "is_unique": True,
                "indexed": True,
                "example": "0x71c67d8e1234567890abcdef1234567890abcdef",
            },
            "label": {
                "type": "STRING",
                "description": (
                    "High-level role or tag assigned during investigation. "
                    "Allowed values: 'SUSPECT', 'VICTIM', 'AGGREGATOR', 'MULE', 'EXCHANGE', 'UNKNOWN'."
                ),
                "required": False,
                "is_unique": False,
                "indexed": True,
                "example": "SUSPECT",
            },
            "risk_score": {
                "type": "FLOAT",
                "description": (
                    "Composite risk score between 0.0 (clean) and 100.0 (high fraud risk) "
                    "computed by combining XGBoost model predictions, heuristic rules, and graph centrality."
                ),
                "required": False,
                "is_unique": False,
                "indexed": True,
                "example": 87.5,
            },
            "entity_type": {
                "type": "STRING",
                "description": (
                    "Specific intelligence classification from threat intelligence feeds. "
                    "Examples: 'INVESTMENT_SCAM', 'TASK_FRAUD', 'RANSOMWARE', 'TORNADO_CASH_USER', 'EXCHANGE_HOT_WALLET'."
                ),
                "required": False,
                "is_unique": False,
                "indexed": True,
                "example": "INVESTMENT_SCAM",
            },
            "first_seen": {
                "type": "INTEGER",
                "description": "Unix epoch timestamp (seconds) of the earliest transaction recorded for this address.",
                "required": False,
                "is_unique": False,
                "indexed": False,
                "example": 1698700000,
            },
            "last_seen": {
                "type": "INTEGER",
                "description": "Unix epoch timestamp (seconds) of the most recent transaction recorded for this address.",
                "required": False,
                "is_unique": False,
                "indexed": False,
                "example": 1698800000,
            },
        },
    },

    "Exchange": {
        "description": (
            "Represents a Centralized (CEX) or Decentralized (DEX) cryptocurrency exchange entity. "
            "In ChainTrace, this node is the critical destination point where stolen funds are identified "
            "for law-enforcement freeze requests."
        ),
        "properties": {
            "name": {
                "type": "STRING",
                "description": "Canonical legal or commercial name of the exchange.",
                "required": True,
                "is_unique": True,
                "indexed": True,
                "example": "Binance",
            },
            "address": {
                "type": "STRING",
                "description": "Primary hot-wallet or deposit gateway contract address associated with the exchange.",
                "required": False,
                "is_unique": False,
                "indexed": True,
                "example": "0x28c6c06298d514db089934071355e5743bf21d60",
            },
            "kyc_required": {
                "type": "BOOLEAN",
                "description": (
                    "True if the exchange enforces Know Your Customer identification. "
                    "Vital for investigators because KYC-compliant exchanges allow freezing user accounts and subpoenaing IDs."
                ),
                "required": True,
                "is_unique": False,
                "indexed": False,
                "example": True,
            },
        },
    },

    "SmartContract": {
        "description": (
            "Represents an on-chain immutable smart contract program. Criminals often route stolen "
            "funds through decentralized finance (DeFi) protocols, automated market makers (AMMs), "
            "or mixer contracts (e.g., Tornado Cash) to obfuscate the transaction trail."
        ),
        "properties": {
            "address": {
                "type": "STRING",
                "description": "On-chain deployed hex address of the smart contract bytecode.",
                "required": True,
                "is_unique": True,
                "indexed": True,
                "example": "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b",
            },
            "protocol": {
                "type": "STRING",
                "description": "The human-readable project or protocol name (e.g., 'Uniswap V3', 'Tornado Cash', 'Hop Exchange').",
                "required": False,
                "is_unique": False,
                "indexed": True,
                "example": "Tornado Cash",
            },
            "verified": {
                "type": "BOOLEAN",
                "description": "Indicates whether the smart contract source code has been verified and published on Etherscan.",
                "required": False,
                "is_unique": False,
                "indexed": False,
                "example": True,
            },
        },
    },
}


# Comprehensive schema documentation dictionary for all Relationship types (Edges).
# Details edge semantics, connecting node types, and edge attributes.
RELATIONSHIP_TYPES: Dict[str, Dict[str, Any]] = {
    "SENT": {
        "description": (
            "Represents a direct transfer of cryptocurrency or digital tokens from one "
            "Wallet node to another Wallet node. Forms the primary traversal pathway for "
            "money laundering path tracing."
        ),
        "start_node": "Wallet",
        "end_node": "Wallet",
        "properties": {
            "amount": {
                "type": "FLOAT",
                "description": "The quantity of cryptocurrency transferred (in decimal ether or token units).",
                "required": True,
                "indexed": True,
                "example": 2.45,
            },
            "token": {
                "type": "STRING",
                "description": "Symbol of the transferred currency (e.g., 'ETH', 'USDT', 'USDC', 'DAI').",
                "required": True,
                "indexed": False,
                "example": "ETH",
            },
            "tx_hash": {
                "type": "STRING",
                "description": "The immutable 66-character 0x-prefixed blockchain transaction hash.",
                "required": True,
                "indexed": True,
                "example": "0x5a1d7f6e0b2a3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d",
            },
            "timestamp": {
                "type": "INTEGER",
                "description": "Unix epoch timestamp (seconds) when the block containing this transfer was confirmed.",
                "required": True,
                "indexed": True,
                "example": 1698765432,
            },
        },
    },

    "DEPOSITED_TO": {
        "description": (
            "Directed edge indicating a transfer from a Wallet directly into an Exchange deposit account. "
            "This relationship marks the end of the laundering trail and triggers police freeze warnings."
        ),
        "start_node": "Wallet",
        "end_node": "Exchange",
        "properties": {
            "amount": {
                "type": "FLOAT",
                "description": "Quantity of cryptocurrency deposited into the exchange.",
                "required": False,
                "indexed": False,
                "example": 1.85,
            },
            "timestamp": {
                "type": "INTEGER",
                "description": "Unix epoch timestamp (seconds) when the deposit occurred.",
                "required": False,
                "indexed": True,
                "example": 1698769999,
            },
        },
    },

    "INTERACTED_WITH": {
        "description": (
            "Directed edge from a Wallet to a SmartContract. Represents an invocation of a contract method "
            "(e.g., token swap, liquidity provision, or mixer deposit). Used by the fraud engine to compute "
            "anonymization and obfuscation penalty scores."
        ),
        "start_node": "Wallet",
        "end_node": "SmartContract",
        "properties": {
            "method": {
                "type": "STRING",
                "description": "Name or 4-byte signature of the contract function invoked (e.g., 'deposit', 'swap').",
                "required": False,
                "indexed": False,
                "example": "deposit",
            },
            "timestamp": {
                "type": "INTEGER",
                "description": "Unix epoch timestamp (seconds) when the contract call occurred.",
                "required": False,
                "indexed": False,
                "example": 1698767777,
            },
            "tx_hash": {
                "type": "STRING",
                "description": "Transaction hash of the contract interaction.",
                "required": False,
                "indexed": False,
                "example": "0x9b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c",
            },
        },
    },
}


# ==============================================================================
# INTERNAL CLIENT QUERY EXECUTION ADAPTER
# ==============================================================================

def _execute_cypher(client: Any, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Internal helper to execute a Cypher query across diverse client implementations.

    This function provides seamless compatibility whether the caller passes:
    1. A custom `Neo4jClient` wrapper class with a `.run(query, params)` method.
    2. A custom `Neo4jClient` wrapper with a `.query(query, params)` method.
    3. An official `neo4j.Driver` object with `.execute_query()` (Neo4j Python Driver 5.x+).
    4. An official `neo4j.Driver` object supporting `.session()`.

    Parameters
    ----------
    client : Any
        An active Neo4j database client or driver instance.
    query : str
        The raw Cypher query string to execute.
    parameters : Optional[Dict[str, Any]], default None
        Dictionary of parameters to bind into the Cypher query (prevents Cypher injection).

    Returns
    -------
    List[Dict[str, Any]]
        A list of dictionaries representing the query output records.

    Raises
    ------
    TypeError
        If the provided client object does not support any recognized query execution interface.
    Exception
        Any underlying database or network driver exception during query execution.
    """
    params = parameters or {}

    # Case 1: Client provides a .run_query() method (e.g. ChainTrace's Neo4jClient)
    if hasattr(client, "run_query") and callable(client.run_query):
        try:
            return client.run_query(query, params=params)
        except TypeError:
            # Fall back if run_query has a different signature (e.g. parameters instead of params)
            return client.run_query(query, params)

    # Case 2: Client provides a .run() method (e.g. Neo4j Session or custom wrapper)
    if hasattr(client, "run") and callable(client.run):
        try:
            result = client.run(query, params)
        except TypeError:
            result = client.run(query, parameters=params)
        # Handle cases where .run() returns a generator, list, or neo4j.Result
        if hasattr(result, "data") and callable(result.data):
            return result.data()
        elif hasattr(result, "__iter__") and not isinstance(result, (dict, str)):
            records = []
            for item in result:
                if hasattr(item, "data") and callable(item.data):
                    records.append(item.data())
                elif isinstance(item, dict):
                    records.append(item)
                else:
                    try:
                        records.append(dict(item))
                    except Exception:
                        records.append({"value": item})
            return records
        return []

    # Case 3: Client provides a .query() method
    if hasattr(client, "query") and callable(client.query):
        result = client.query(query, params)
        if isinstance(result, list):
            return result
        elif hasattr(result, "data") and callable(result.data):
            return result.data()
        return []

    # Case 4: Official neo4j.Driver 5.x execute_query method
    if hasattr(client, "execute_query") and callable(client.execute_query):
        records, summary, keys = client.execute_query(query, parameters_=params)
        return [r.data() if hasattr(r, "data") else dict(r) for r in records]

    # Case 4: Neo4j driver with session context manager
    if hasattr(client, "session") and callable(client.session):
        with client.session() as session:
            result = session.run(query, params)
            return [r.data() if hasattr(r, "data") else dict(r) for r in result]

    raise TypeError(
        f"Unsupported Neo4j client type '{type(client).__name__}'. "
        "Expected an object implementing .run(), .query(), .execute_query(), or .session()."
    )


# ==============================================================================
# SCHEMA LIFECYCLE FUNCTIONS
# ==============================================================================

def init_schema(client: Any) -> Dict[str, Any]:
    """
    Initialize the Neo4j graph database schema by executing all constraint
    and index creation queries defined in `SCHEMA_QUERIES`.

    Each query is executed individually. The function logs and prints the
    success or failure status of each operation, ensuring that an error in one
    statement does not prevent subsequent statements from executing.

    Design Rationale:
    - Running queries sequentially with error handling ensures partial success
      and full transparency into which specific constraint or index failed.
    - Uses 'IF NOT EXISTS' in all Cypher statements to allow repeated, idempotent
      invocations (e.g. during application startup or CI/CD test runs).

    Parameters
    ----------
    client : Any
        An active Neo4jClient or neo4j.Driver instance connected to the database.

    Returns
    -------
    Dict[str, Any]
        A summary dictionary containing:
        - "total": Total number of schema queries attempted.
        - "successful": Number of queries successfully executed.
        - "failed": Number of queries that raised an error.
        - "errors": List of dicts describing any errors encountered (query + error message).

    Example
    -------
    >>> from backend.graph.client import Neo4jClient
    >>> client = Neo4jClient()
    >>> status = init_schema(client)
    >>> print(f"Initialized {status['successful']} of {status['total']} schema items.")
    """
    total = len(SCHEMA_QUERIES)
    successful = 0
    failed = 0
    errors: List[Dict[str, str]] = []

    print("\n" + "=" * 70)
    print("CHAINTRACE: INITIALIZING NEO4J GRAPH SCHEMA")
    print("=" * 70)
    print(f"Total schema queries to execute: {total}\n")

    for index, query in enumerate(SCHEMA_QUERIES, start=1):
        # Extract a short friendly name from the query for logging
        short_name = query.replace("CREATE CONSTRAINT ", "").replace("CREATE INDEX ", "")
        short_name = short_name.split(" IF NOT EXISTS")[0].strip()

        try:
            _execute_cypher(client, query)
            successful += 1
            print(f"[{index:02d}/{total:02d}] ✓ SUCCESS: {short_name}")
            logger.info("Successfully executed schema query: %s", short_name)
        except Exception as exc:
            failed += 1
            err_msg = str(exc)
            errors.append({"query": query, "error": err_msg})
            print(f"[{index:02d}/{total:02d}] ✗ FAILED:  {short_name}")
            print(f"          Reason: {err_msg}")
            logger.error("Failed to execute schema query: %s. Error: %s", query, err_msg)

    print("\n" + "-" * 70)
    print(f"SCHEMA INITIALIZATION COMPLETE: {successful}/{total} succeeded ({failed} failed).")
    print("=" * 70 + "\n")

    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "errors": errors,
    }


def drop_all(client: Any, confirm: bool = False) -> Dict[str, Any]:
    """
    Deletes all nodes and relationships from the connected Neo4j database.

    WARNING: THIS DELETES ALL GRAPH DATA IN THE DATABASE!
    This utility is intended strictly for:
    - Unit, integration, and end-to-end testing
    - Local development environment resets
    - Clearing mock graph fixtures before test runs

    How it works:
    - Executes `MATCH (n) DETACH DELETE n`
    - 'DETACH' instructs Neo4j to first delete all attached relationships
      before deleting each node, preventing constraint/referential integrity errors.
    - Note: This operation removes graph data (nodes and edges), but preserves
      the schema constraints and indexes so new data can immediately be ingested.

    Parameters
    ----------
    client : Any
        An active Neo4jClient or neo4j.Driver instance.
    confirm : bool, default False
        Safety flag. When set to False, a warning is printed before proceeding.

    Returns
    -------
    Dict[str, Any]
        Dictionary with deletion summary, e.g.:
        {
            "success": True,
            "message": "All nodes and relationships successfully deleted.",
            "nodes_deleted": <int>,
            "relationships_deleted": <int>
        }

    Example
    -------
    >>> drop_all(client, confirm=True)
    """
    print("\n" + "!" * 70)
    print("CHAINTRACE: WIPING ALL GRAPH DATA (DROP ALL)")
    print("!" * 70)

    try:
        # First, count existing nodes and relationships for reporting
        count_query = (
            "MATCH (n) "
            "OPTIONAL MATCH (n)-[r]->() "
            "RETURN count(DISTINCT n) AS node_count, count(DISTINCT r) AS rel_count"
        )
        counts = _execute_cypher(client, count_query)
        node_count = counts[0].get("node_count", 0) if counts else 0
        rel_count = counts[0].get("rel_count", 0) if counts else 0

        logger.warning(
            "Wiping database. Found %d nodes and %d relationships to delete.",
            node_count,
            rel_count,
        )

        # Execute DETACH DELETE to wipe all nodes and edges
        wipe_query = "MATCH (n) DETACH DELETE n"
        _execute_cypher(client, wipe_query)

        print(f"✓ Successfully deleted {node_count} nodes and {rel_count} relationships.")
        print("!" * 70 + "\n")
        logger.info("Database wiped successfully.")

        return {
            "success": True,
            "message": "All nodes and relationships successfully deleted.",
            "nodes_deleted": node_count,
            "relationships_deleted": rel_count,
        }

    except Exception as exc:
        err_msg = str(exc)
        print(f"✗ Failed to drop graph data: {err_msg}")
        print("!" * 70 + "\n")
        logger.error("Failed to execute drop_all query: %s", err_msg)
        return {
            "success": False,
            "message": f"Error deleting graph data: {err_msg}",
            "nodes_deleted": 0,
            "relationships_deleted": 0,
        }


def get_schema_info(client: Any) -> Dict[str, Any]:
    """
    Retrieve live schema information from the running Neo4j database,
    including all active uniqueness constraints and property indexes.

    Implementation Details:
    - Modern Neo4j (v5.x and v4.4+) supports the standard SQL-like administrative
      commands: `SHOW CONSTRAINTS` and `SHOW INDEXES`.
    - If running against older database versions, this function gracefully falls
      back to legacy procedures `CALL db.constraints()` and `CALL db.indexes()`.

    Parameters
    ----------
    client : Any
        An active Neo4jClient or neo4j.Driver instance.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing two lists:
        - "constraints": List of constraint metadata records (name, type, entity, properties).
        - "indexes": List of index metadata records (name, state, type, entity, properties).

    Example
    -------
    >>> info = get_schema_info(client)
    >>> print(f"Found {len(info['constraints'])} constraints and {len(info['indexes'])} indexes.")
    """
    schema_info: Dict[str, List[Dict[str, Any]]] = {
        "constraints": [],
        "indexes": [],
    }

    # 1. Fetch active constraints
    try:
        # Standard Neo4j 5.x Cypher
        constraints_records = _execute_cypher(client, "SHOW CONSTRAINTS")
        schema_info["constraints"] = constraints_records
        logger.info("Retrieved %d constraints via SHOW CONSTRAINTS.", len(constraints_records))
    except Exception as primary_exc:
        # Fallback for legacy Neo4j versions
        logger.debug("SHOW CONSTRAINTS failed (%s), falling back to CALL db.constraints().", primary_exc)
        try:
            legacy_records = _execute_cypher(client, "CALL db.constraints()")
            schema_info["constraints"] = legacy_records
            logger.info("Retrieved %d constraints via legacy CALL db.constraints().", len(legacy_records))
        except Exception as fallback_exc:
            logger.error("Failed to fetch constraints from database: %s", fallback_exc)

    # 2. Fetch active indexes
    try:
        # Standard Neo4j 5.x Cypher
        indexes_records = _execute_cypher(client, "SHOW INDEXES")
        schema_info["indexes"] = indexes_records
        logger.info("Retrieved %d indexes via SHOW INDEXES.", len(indexes_records))
    except Exception as primary_exc:
        # Fallback for legacy Neo4j versions
        logger.debug("SHOW INDEXES failed (%s), falling back to CALL db.indexes().", primary_exc)
        try:
            legacy_records = _execute_cypher(client, "CALL db.indexes()")
            schema_info["indexes"] = legacy_records
            logger.info("Retrieved %d indexes via legacy CALL db.indexes().", len(legacy_records))
        except Exception as fallback_exc:
            logger.error("Failed to fetch indexes from database: %s", fallback_exc)

    return schema_info


# ==============================================================================
# SCRIPT SELF-TEST / DEMO (WHEN RUN DIRECTLY)
# ==============================================================================

if __name__ == "__main__":
    """
    Self-test demonstration: Prints the schema documentation so developers
    can inspect all nodes, relationships, constraints, and indexes without
    needing a live Neo4j connection.
    """
    print("=" * 80)
    print("CHAINTRACE NEO4J SCHEMA DEFINITIONS - OVERVIEW")
    print("=" * 80)

    print("\n[+] NODE LABELS CONFIGURED:")
    for label, info in NODE_LABELS.items():
        print(f"  • :{label}")
        print(f"    Description: {info['description']}")
        print("    Properties:")
        for prop, p_info in info["properties"].items():
            req = "REQUIRED" if p_info["required"] else "OPTIONAL"
            uniq = " [UNIQUE]" if p_info.get("is_unique") else ""
            idx = " [INDEXED]" if p_info.get("indexed") else ""
            print(f"      - {prop} ({p_info['type']}) [{req}]{uniq}{idx}: {p_info['description']}")

    print("\n[+] RELATIONSHIP TYPES CONFIGURED:")
    for rel_type, info in RELATIONSHIP_TYPES.items():
        print(f"  • (:{info['start_node']})-[:{rel_type}]->(:{info['end_node']})")
        print(f"    Description: {info['description']}")
        print("    Properties:")
        for prop, p_info in info["properties"].items():
            req = "REQUIRED" if p_info["required"] else "OPTIONAL"
            idx = " [INDEXED]" if p_info.get("indexed") else ""
            print(f"      - {prop} ({p_info['type']}) [{req}]{idx}: {p_info['description']}")

    print(f"\n[+] TOTAL SCHEMA DDL QUERIES: {len(SCHEMA_QUERIES)}")
    for i, q in enumerate(SCHEMA_QUERIES, 1):
        print(f"  {i:02d}. {q}")

    print("\n" + "=" * 80)
    print("Schema documentation successfully displayed.")
    print("=" * 80)
