"""Graph Builder Module — Ingestion & Graph Construction Pipeline (Phase 1)
========================================================================

ChainTrace: Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges
Smart India Hackathon 2026 | Problem ID: 26183
Ministry of Home Affairs | I4C, CIS Division

Author: Team Blockies 🧱
Domain: Graph Engine (Phase 1 Deliverable)

-------------------------------------------------------------------------------
EDUCATIONAL GUIDE & DESIGN PRINCIPLES: NEO4J IN BLOCKCHAIN INVESTIGATIONS
-------------------------------------------------------------------------------

1. WHAT MERGE DOES VS CREATE:
   -------------------------
   - `CREATE`: Unconditionally creates a new node or relationship every time
     it is executed. If you run:
         CREATE (w:Wallet {address: '0x123'})
     ten times, Neo4j will create 10 distinct nodes in the database, each
     having address '0x123'. This leads to data duplication and graph fragmentation.
   - `MERGE`: Acts as an "upsert" (find-or-create). It first checks whether a
     node or relationship matching the specified pattern and properties already
     exists in the graph:
       * IF IT EXISTS: Neo4j binds to the existing node/relationship.
       * IF IT DOES NOT EXIST: Neo4j creates a brand-new node/relationship.
     This guarantees idempotency: running `MERGE` repeatedly with the same
     address will never produce duplicate wallet nodes.

2. WHY WE USE MERGE FOR WALLETS BUT CREATE FOR TRANSACTIONS:
   ---------------------------------------------------------
   - Wallets represent real-world blockchain entities (accounts/contracts).
     Even if an address participates in 100,000 transactions, there MUST
     ONLY EVER BE ONE (:Wallet) node in the graph for that unique address.
     Therefore, we use `MERGE` on wallets to reuse the same node across all
     incoming and outgoing transactions.
   - Transactions, by contrast, represent discrete financial transfer events.
     Two wallets (e.g., Alice and Bob) can send money to each other multiple
     times at different timestamps, amounts, and block heights.
     If we used `MERGE` on the `[:SENT]` relationship without indexing every
     transaction property, Neo4j would risk collapsing distinct transfer events
     into a single relationship!
     Furthermore, `CREATE` on relationships avoids the expensive overhead of
     searching through all existing edges between two high-volume nodes.
     Hence: MERGE for Wallets, CREATE for SENT edges.

3. WHAT UNWIND DOES:
   -----------------
   - `UNWIND` is Cypher's native looping mechanism. It takes a list (array) of
     items passed as a query parameter (e.g., `$batch = [tx1, tx2, tx3, ...]`)
     and transforms ("explodes") that single list into individual rows.
   - Subsequent Cypher clauses (`MERGE`, `CREATE`, `SET`) are then executed
     once for every element in the exploded stream.
   - Analogy: `UNWIND` is equivalent to Python's `for item in batch:` or
     SQL's `CROSS JOIN UNNEST(batch)`.

4. WHAT ON CREATE SET (AND ON MATCH SET) DOES:
   -------------------------------------------
   - When using `MERGE`, Neo4j allows conditional property assignment:
       * `ON CREATE SET`: Executes ONLY when the node is brand new (just created).
         We use this to record immutable initialization metadata such as
         `first_seen = tx.timestamp` and `created_at = timestamp()`.
       * `ON MATCH SET`: Executes ONLY when the node already existed in the database.
         We use this to update dynamic state, such as bumping `last_seen` when
         newer transactions are ingested.

5. WHY BATCH INSERT IS FASTER THAN ONE-BY-ONE:
   -------------------------------------------
   - Network Round-Trips: Inserting 1,000 transactions one-by-one requires
     1,000 separate network round-trips between your Python application and
     Neo4j. With `UNWIND $batch`, all 1,000 transactions travel across the
     wire in ONE single HTTP/Bolt network payload.
   - Transaction Overhead: Running 1,000 individual queries forces the database
     to allocate 1,000 ACID transactions, write to the Write-Ahead Log (WAL),
     and flush to disk 1,000 times. A batch insert executes in ONE atomic
     database transaction with a single commit.
   - Query Plan Caching: Neo4j parses and compiles the Cypher query plan ONCE,
     then executes that plan in an optimized C++ memory loop over all items.
   - Performance Gain: Batching typically improves throughput from ~100 tx/sec
     to over 10,000+ tx/sec (a 50x-100x speedup).

-------------------------------------------------------------------------------
GRAPH SCHEMA SPECIFICATION:
-------------------------------------------------------------------------------
(:Wallet {
    address: STRING (lowercase, unique identifier),
    label: STRING (e.g., 'Binance 14', 'Tornado Cash', optional),
    entity_type: STRING (e.g., 'EXCHANGE', 'MIXER', 'SCAM', optional),
    first_seen: INTEGER (Unix timestamp of earliest transaction),
    last_seen: INTEGER (Unix timestamp of latest transaction),
    created_at: INTEGER (Neo4j epoch millisecond timestamp)
})

-[:SENT {
    tx_hash: STRING (blockchain transaction hash),
    amount: FLOAT (token amount transferred - used by BFS tracer),
    value: FLOAT (alias for amount, matches ingestion schema),
    token: STRING (e.g., 'ETH', 'USDT', 'BTC'),
    timestamp: INTEGER (Unix block timestamp),
    block_number: INTEGER (block height)
}]->
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

# Graceful import handling for Neo4jClient:
# In development or testing environments, client may reside in backend.graph.neo4j_client.
# If neo4j_client.py is not yet instantiated, we fall back to Any for type hints.
if TYPE_CHECKING:
    try:
        from backend.graph.neo4j_client import Neo4jClient
    except ImportError:
        try:
            from .neo4j_client import Neo4jClient
        except ImportError:
            Neo4jClient = Any  # type: ignore[misc, assignment]
else:
    try:
        from .neo4j_client import Neo4jClient
    except ImportError:
        try:
            from backend.graph.neo4j_client import Neo4jClient
        except ImportError:
            Neo4jClient = Any  # type: ignore[misc, assignment]


logger = logging.getLogger(__name__)


class GraphBuilder:
    """Graph construction and mutation engine for ChainTrace.

    This class takes normalized blockchain transaction dictionaries (produced by
    the ingestion pipeline) and models them into a Neo4j property graph. Wallets
    are stored as nodes (:Wallet), and transactions are stored as directed edges
    (:Wallet)-[:SENT]->(:Wallet).

    Attributes:
        client (Neo4jClient): Active Neo4j connection client wrapper used to
            execute parameterized Cypher statements.
    """

    def __init__(self, client: Neo4jClient) -> None:
        """Initialize GraphBuilder with a Neo4j client connection.

        Args:
            client (Neo4jClient): The initialized Neo4j database client wrapper
                responsible for executing Cypher queries against the cluster.

        Returns:
            None

        Example:
            >>> from backend.graph.neo4j_client import Neo4jClient
            >>> from backend.graph.builder import GraphBuilder
            >>> client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="password")
            >>> builder = GraphBuilder(client)
        """
        self.client: Neo4jClient = client
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("GraphBuilder initialized successfully.")

    def _execute(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Internal helper to execute Cypher queries across various client wrappers.

        Supports client wrappers implementing:
        1. `execute_query(query, parameters=...)` (Neo4j Driver 5+ standard)
        2. `query(query, parameters)` (Custom application wrapper)
        3. `run(query, parameters)` (Neo4j Session standard)

        Args:
            query (str): Cypher query string to execute.
            parameters (dict, optional): Query parameters dictionary. Defaults to None.

        Returns:
            List[Dict[str, Any]]: List of dictionary records returned by the query.
        """
        params = parameters or {}
        self.logger.debug("Executing Cypher:\n%s\nWith params: %s", query, params)

        try:
            # Case 1: Neo4jClient from backend.graph.neo4j_client with run_query
            if hasattr(self.client, "run_query"):
                return self.client.run_query(query, params=params)

            # Case 2: Custom or standard client with execute_query (Neo4j Driver 5+)
            elif hasattr(self.client, "execute_query"):
                # Neo4j official driver 5+ execute_query accepts keyword arguments
                result = self.client.execute_query(query, parameters=params)
                if hasattr(result, "records"):
                    return [
                        r.data() if hasattr(r, "data") else dict(r)  # type: ignore[call-overload]
                        for r in result.records
                    ]
                elif isinstance(result, list):
                    return [
                        r.data() if hasattr(r, "data") else (dict(r) if hasattr(r, "keys") else r)  # type: ignore[call-overload]
                        for r in result
                    ]
                return result  # type: ignore[no-any-return]

            # Case 3: Custom wrapper with .query() method
            elif hasattr(self.client, "query"):
                res = self.client.query(query, params)
                if isinstance(res, list):
                    return [
                        r.data() if hasattr(r, "data") else (dict(r) if hasattr(r, "keys") else r)  # type: ignore[call-overload]
                        for r in res
                    ]
                return res  # type: ignore[no-any-return]

            # Case 4: Session or connection with .run() method
            elif hasattr(self.client, "run"):
                res = self.client.run(query, params)
                if hasattr(res, "data"):
                    return res.data()  # type: ignore[no-any-return]
                return list(res)  # type: ignore[no-any-return]

            else:
                raise AttributeError(
                    f"Injected Neo4jClient instance '{type(self.client).__name__}' does not expose "
                    "a supported query execution method ('run_query', 'execute_query', 'query', or 'run')."
                )

        except Exception as exc:
            self.logger.error("Failed to execute Cypher query: %s. Error: %s", query, exc)
            raise

    # -------------------------------------------------------------------------
    # 2. INSERT ONE TRANSACTION
    # -------------------------------------------------------------------------
    def insert_transaction(self, tx: dict) -> dict:
        """Insert a single normalized blockchain transaction into Neo4j.

        This method inserts or updates the sender wallet node, inserts or updates
        the receiver wallet node, and creates a directed `[:SENT]` relationship
        from sender to receiver.

        Design Decisions:
        - Wallets are merged using `MERGE (w:Wallet {address: ...})` to prevent
          duplicate wallet nodes.
        - Addresses are normalized to lowercase to prevent casing mismatches
          (e.g., '0xABC' vs '0xabc').
        - Timestamps (`first_seen` / `last_seen`) are initialized on creation and
          conditionally adjusted on match.
        - The transaction edge `[:SENT]` is created using `CREATE` because each
          transaction represents a discrete financial transfer event. Both `amount`
          and `value` properties are recorded on the edge to support both ingestion
          standards and graph tracer algorithms.

        Args:
            tx (dict): Normalized transaction dictionary agreed upon with ingestion.
                Required format:
                {
                    "tx_hash": str,         # e.g., "0xabc123..."
                    "from_address": str,    # e.g., "0x1111..."
                    "to_address": str,      # e.g., "0x2222..."
                    "value": float,         # e.g., 2.5
                    "token": str,           # e.g., "ETH", "USDT"
                    "timestamp": int,       # Unix timestamp in seconds
                    "block_number": int     # Block height
                }

        Returns:
            dict: Summary dictionary containing details of the inserted relationship.

        Example:
            >>> tx = {
            ...     "tx_hash": "0x5c2b7f3...",
            ...     "from_address": "0x71c84f...12",
            ...     "to_address": "0x3892ab...99",
            ...     "value": 1.45,
            ...     "token": "ETH",
            ...     "timestamp": 1700000000,
            ...     "block_number": 19450123
            ... }
            >>> result = builder.insert_transaction(tx)
            >>> print(result["tx_hash"])
            '0x5c2b7f3...'
        """
        # Validate required dictionary keys
        required_keys = {"tx_hash", "from_address", "to_address", "value", "token", "timestamp", "block_number"}
        missing = required_keys - set(tx.keys())
        if missing:
            raise ValueError(f"Transaction dictionary is missing required keys: {sorted(missing)}")

        # Normalize address strings to lowercase and ensure correct numeric datatypes
        cleaned_tx = {
            "tx_hash": str(tx["tx_hash"]),
            "from_address": str(tx["from_address"]).strip().lower(),
            "to_address": str(tx["to_address"]).strip().lower(),
            "value": float(tx["value"]),
            "token": str(tx["token"]).upper(),
            "timestamp": int(tx["timestamp"]),
            "block_number": int(tx["block_number"]),
        }

        # Cypher Query: Inserting one transaction
        cypher = """
        // Step 1: MERGE sender wallet node (find existing or create if absent)
        MERGE (sender:Wallet {address: $from_address})
        // ON CREATE SET executes ONLY when the sender node is created for the very first time
        ON CREATE SET
            sender.first_seen = $timestamp,
            sender.last_seen = $timestamp,
            sender.created_at = timestamp()
        // ON MATCH SET executes when sender node already existed, maintaining accurate time bounds
        ON MATCH SET
            sender.last_seen = CASE WHEN $timestamp > coalesce(sender.last_seen, 0) THEN $timestamp ELSE sender.last_seen END,
            sender.first_seen = CASE WHEN $timestamp < coalesce(sender.first_seen, $timestamp) THEN $timestamp ELSE sender.first_seen END

        // Step 2: MERGE receiver wallet node (find existing or create if absent)
        MERGE (receiver:Wallet {address: $to_address})
        // ON CREATE SET executes ONLY when the receiver node is created for the very first time
        ON CREATE SET
            receiver.first_seen = $timestamp,
            receiver.last_seen = $timestamp,
            receiver.created_at = timestamp()
        // ON MATCH SET executes when receiver node already existed, maintaining accurate time bounds
        ON MATCH SET
            receiver.last_seen = CASE WHEN $timestamp > coalesce(receiver.last_seen, 0) THEN $timestamp ELSE receiver.last_seen END,
            receiver.first_seen = CASE WHEN $timestamp < coalesce(receiver.first_seen, $timestamp) THEN $timestamp ELSE receiver.first_seen END

        // Step 3: CREATE the directed SENT relationship representing this unique transfer event
        CREATE (sender)-[r:SENT {
            tx_hash: $tx_hash,
            amount: $value,
            value: $value,
            token: $token,
            timestamp: $timestamp,
            block_number: $block_number
        }]->(receiver)

        // Step 4: Return relationship details confirming successful insertion
        RETURN r.tx_hash AS tx_hash,
               sender.address AS from_address,
               receiver.address AS to_address,
               r.value AS value,
               r.amount AS amount,
               r.token AS token,
               r.timestamp AS timestamp,
               r.block_number AS block_number
        """

        records = self._execute(cypher, cleaned_tx)
        if records:
            return records[0]
        return cleaned_tx

    # -------------------------------------------------------------------------
    # 3. INSERT BATCH (BULK INSERT WITH UNWIND)
    # -------------------------------------------------------------------------
    def insert_batch(self, transactions: list[dict]) -> dict:
        """Bulk insert a batch of normalized blockchain transactions using UNWIND.

        Why this is dramatically faster:
        Instead of issuing individual network requests and starting independent
        database transactions for every single transfer, `UNWIND` streams the entire
        batch within a single round-trip and commits under one ACID transaction.
        This provides a 50x-100x performance boost essential for real-time blockchain
        ingestion.

        Args:
            transactions (list[dict]): A list of normalized transaction dictionaries,
                each matching the schema:
                {
                    "tx_hash": str,
                    "from_address": str,
                    "to_address": str,
                    "value": float,
                    "token": str,
                    "timestamp": int,
                    "block_number": int
                }

        Returns:
            dict: Summary containing inserted count, total submitted, and status.
                Format:
                {
                    "inserted_count": int,
                    "total_submitted": int,
                    "status": str
                }

        Example:
            >>> batch = [
            ...     {"tx_hash": "0x1", "from_address": "0xa", "to_address": "0xb", "value": 1.0, "token": "ETH", "timestamp": 100, "block_number": 1},
            ...     {"tx_hash": "0x2", "from_address": "0xb", "to_address": "0xc", "value": 0.9, "token": "ETH", "timestamp": 105, "block_number": 2}
            ... ]
            >>> result = builder.insert_batch(batch)
            >>> print(result["inserted_count"])
            2
        """
        if not transactions:
            self.logger.warning("insert_batch called with empty transaction list.")
            return {"inserted_count": 0, "total_submitted": 0, "status": "empty_batch"}

        # Normalize and clean each transaction in the batch
        cleaned_batch: List[Dict[str, Any]] = []
        for i, tx in enumerate(transactions):
            try:
                cleaned_batch.append({
                    "tx_hash": str(tx["tx_hash"]),
                    "from_address": str(tx["from_address"]).strip().lower(),
                    "to_address": str(tx["to_address"]).strip().lower(),
                    "value": float(tx["value"]),
                    "token": str(tx.get("token", "ETH")).upper(),
                    "timestamp": int(tx["timestamp"]),
                    "block_number": int(tx["block_number"]),
                })
            except KeyError as err:
                raise ValueError(
                    f"Transaction at index {i} is missing required field {err}: {tx}"
                ) from err

        # Cypher Query: Batch insertion using UNWIND
        cypher = """
        // Step 1: UNWIND expands the list parameter $batch into individual rows for iteration
        UNWIND $batch AS tx

        // Step 2: MERGE sender wallet node based on lowercase address
        MERGE (sender:Wallet {address: tx.from_address})
        // If sender node was newly created in this query, set initial timestamps
        ON CREATE SET
            sender.first_seen = tx.timestamp,
            sender.last_seen = tx.timestamp,
            sender.created_at = timestamp()
        // If sender node already existed, update timestamp boundaries
        ON MATCH SET
            sender.last_seen = CASE WHEN tx.timestamp > coalesce(sender.last_seen, 0) THEN tx.timestamp ELSE sender.last_seen END,
            sender.first_seen = CASE WHEN tx.timestamp < coalesce(sender.first_seen, tx.timestamp) THEN tx.timestamp ELSE sender.first_seen END

        // Step 3: MERGE receiver wallet node based on lowercase address
        MERGE (receiver:Wallet {address: tx.to_address})
        // If receiver node was newly created in this query, set initial timestamps
        ON CREATE SET
            receiver.first_seen = tx.timestamp,
            receiver.last_seen = tx.timestamp,
            receiver.created_at = timestamp()
        // If receiver node already existed, update timestamp boundaries
        ON MATCH SET
            receiver.last_seen = CASE WHEN tx.timestamp > coalesce(receiver.last_seen, 0) THEN tx.timestamp ELSE receiver.last_seen END,
            receiver.first_seen = CASE WHEN tx.timestamp < coalesce(receiver.first_seen, tx.timestamp) THEN tx.timestamp ELSE receiver.first_seen END

        // Step 4: CREATE the SENT relationship from sender to receiver
        CREATE (sender)-[r:SENT {
            tx_hash: tx.tx_hash,
            amount: tx.value,
            value: tx.value,
            token: tx.token,
            timestamp: tx.timestamp,
            block_number: tx.block_number
        }]->(receiver)

        // Step 5: Aggregate and return total count of inserted relationship edges
        RETURN count(r) AS inserted_count
        """

        records = self._execute(cypher, {"batch": cleaned_batch})
        inserted_count = records[0]["inserted_count"] if records else len(cleaned_batch)

        self.logger.info(
            "Batch insert complete: %d/%d transactions inserted.",
            inserted_count,
            len(transactions),
        )
        return {
            "inserted_count": inserted_count,
            "total_submitted": len(transactions),
            "status": "success",
        }

    # -------------------------------------------------------------------------
    # 4. LABEL ONE WALLET
    # -------------------------------------------------------------------------
    def label_wallet(self, address: str, label: str, entity_type: str) -> dict:
        """Tag a wallet address with an entity label and categorical classification.

        In blockchain investigations, identifying known addresses (e.g. centralized
        exchanges, crypto mixers, phishing scams, or ransomware operators) is
        critical for tracing funds to their cash-out exit point.

        Common Entity Types:
        - 'EXCHANGE': Binance, WazirX, Coinbase, Kraken
        - 'MIXER': Tornado Cash, ChipMixer, Blender
        - 'SCAM': Phishing, fake investment platforms, task fraud
        - 'RANSOMWARE': Identified extortion collection addresses
        - 'BRIDGE': Cross-chain bridge contracts
        - 'SANCTIONED': OFAC-sanctioned addresses

        Args:
            address (str): Target wallet blockchain address (e.g., "0x28c6c06298d514db089934071355e5743bf21d60").
            label (str): Human-readable name or specific tag (e.g., "Binance 14", "Tornado.Cash: Router").
            entity_type (str): Classification category (e.g., "EXCHANGE", "MIXER", "SCAM").

        Returns:
            dict: Updated wallet node properties.

        Example:
            >>> result = builder.label_wallet(
            ...     address="0x28c6c06298d514db089934071355e5743bf21d60",
            ...     label="Binance 14",
            ...     entity_type="EXCHANGE"
            ... )
            >>> print(result["entity_type"])
            'EXCHANGE'
        """
        normalized_address = str(address).strip().lower()
        normalized_entity_type = str(entity_type).strip().upper()
        normalized_label = str(label).strip()

        # Cypher Query: Labeling a wallet node
        cypher = """
        // Step 1: MERGE the wallet node so labeling works even if the wallet has not yet been seen in a transaction
        MERGE (w:Wallet {address: $address})
        // Step 2: Set the entity label (e.g. 'Binance 14') and entity type category (e.g. 'EXCHANGE')
        SET w.label = $label,
            w.entity_type = $entity_type,
            w.labeled_at = timestamp()
        // Step 3: Return the updated wallet node properties
        RETURN properties(w) AS wallet
        """

        records = self._execute(
            cypher,
            {
                "address": normalized_address,
                "label": normalized_label,
                "entity_type": normalized_entity_type,
            },
        )

        wallet_props = records[0]["wallet"] if records else {
            "address": normalized_address,
            "label": normalized_label,
            "entity_type": normalized_entity_type,
        }
        self.logger.info("Labeled wallet %s as '%s' (%s)", normalized_address, normalized_label, normalized_entity_type)
        return wallet_props

    # -------------------------------------------------------------------------
    # 5. LABEL WALLETS IN BATCH
    # -------------------------------------------------------------------------
    def label_wallets_batch(self, labels: list[dict]) -> dict:
        """Bulk label a collection of wallets using UNWIND.

        Efficiently loads address intelligence feeds (e.g., Etherscan Label Cloud,
        CryptoScamDB, OFAC sanctions lists) into the Neo4j graph in a single query.

        Args:
            labels (list[dict]): A list of dictionaries containing labeling info.
                Required format:
                [
                    {
                        "address": str,      # Wallet address
                        "label": str,        # Descriptive name, e.g. "Binance Hot Wallet"
                        "entity_type": str   # "EXCHANGE", "MIXER", "SCAM", etc.
                    },
                    ...
                ]

        Returns:
            dict: Summary of batch labeling operation.
                Format:
                {
                    "labeled_count": int,
                    "total_submitted": int,
                    "status": str
                }

        Example:
            >>> feed = [
            ...     {"address": "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be", "label": "Binance", "entity_type": "EXCHANGE"},
            ...     {"address": "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b", "label": "Tornado Cash", "entity_type": "MIXER"}
            ... ]
            >>> result = builder.label_wallets_batch(feed)
            >>> print(result["labeled_count"])
            2
        """
        if not labels:
            self.logger.warning("label_wallets_batch called with empty list.")
            return {"labeled_count": 0, "total_submitted": 0, "status": "empty_batch"}

        cleaned_batch: List[Dict[str, str]] = []
        for i, item in enumerate(labels):
            try:
                cleaned_batch.append({
                    "address": str(item["address"]).strip().lower(),
                    "label": str(item["label"]).strip(),
                    "entity_type": str(item["entity_type"]).strip().upper(),
                })
            except KeyError as err:
                raise ValueError(
                    f"Label entry at index {i} is missing required key {err}: {item}"
                ) from err

        # Cypher Query: Batch labeling using UNWIND
        cypher = """
        // Step 1: UNWIND expands the array of wallet tag entries into individual rows
        UNWIND $batch AS item
        // Step 2: MERGE wallet node to find existing or create new placeholder
        MERGE (w:Wallet {address: item.address})
        // Step 3: Update label, entity_type, and labeled_at timestamp
        SET w.label = item.label,
            w.entity_type = item.entity_type,
            w.labeled_at = timestamp()
        // Step 4: Count total wallet nodes updated
        RETURN count(w) AS labeled_count
        """

        records = self._execute(cypher, {"batch": cleaned_batch})
        labeled_count = records[0]["labeled_count"] if records else len(cleaned_batch)

        self.logger.info("Batch labeled %d/%d wallets.", labeled_count, len(labels))
        return {
            "labeled_count": labeled_count,
            "total_submitted": len(labels),
            "status": "success",
        }

    # -------------------------------------------------------------------------
    # 6. GET WALLET DETAILS
    # -------------------------------------------------------------------------
    def get_wallet(self, address: str) -> dict | None:
        """Retrieve all stored information about a specific wallet node.

        Fetches node properties (address, labels, classification, timestamps)
        along with topological metrics (incoming and outgoing degree counts)
        to assist investigators in understanding wallet activity at a glance.

        Args:
            address (str): Blockchain wallet address to look up.

        Returns:
            dict | None: Dictionary of wallet properties and degrees if found,
                or None if the wallet does not exist in the graph.

        Example:
            >>> wallet_data = builder.get_wallet("0x71c...12")
            >>> if wallet_data:
            ...     print(wallet_data["address"], wallet_data["out_degree"])
        """
        normalized_address = str(address).strip().lower()

        # Cypher Query: Fetch wallet properties and degree counts
        cypher = """
        // Step 1: Find wallet node matching the given address
        MATCH (w:Wallet {address: $address})
        // Step 2: Optionally match outgoing SENT relationships (funds sent out)
        OPTIONAL MATCH (w)-[out:SENT]->()
        // Step 3: Optionally match incoming SENT relationships (funds received in)
        OPTIONAL MATCH ()-[in:SENT]->(w)
        // Step 4: Aggregate property data and connection degrees
        RETURN properties(w) AS properties,
               count(DISTINCT out) AS out_degree,
               count(DISTINCT in) AS in_degree
        """

        records = self._execute(cypher, {"address": normalized_address})
        if not records or not records[0].get("properties"):
            return None

        row = records[0]
        wallet_dict = dict(row["properties"])
        wallet_dict["out_degree"] = row["out_degree"]
        wallet_dict["in_degree"] = row["in_degree"]
        return wallet_dict

    # -------------------------------------------------------------------------
    # 7. GET WALLET TRANSACTIONS (SENT / RECEIVED / BOTH)
    # -------------------------------------------------------------------------
    def get_wallet_transactions(self, address: str, direction: str = "both") -> list:
        """Retrieve all transactions associated with a wallet in the specified direction.

        Supports filtering by outgoing transfers, incoming transfers, or both.
        Results are ordered chronologically with the newest transactions first.

        Args:
            address (str): Target wallet address to query.
            direction (str, optional): Flow direction to filter by.
                Allowed values:
                - 'outgoing' (or 'out'): Transactions sent FROM this wallet.
                - 'incoming' (or 'in'): Transactions received BY this wallet.
                - 'both': All transactions where this wallet is sender or receiver.
                Defaults to 'both'.

        Returns:
            list[dict]: List of transaction dictionaries matching the search criteria.
                Each dictionary contains:
                {
                    "tx_hash": str,
                    "from_address": str,
                    "to_address": str,
                    "value": float,
                    "amount": float,
                    "token": str,
                    "timestamp": int,
                    "block_number": int,
                    "direction": str ('outgoing' or 'incoming')
                }

        Raises:
            ValueError: If an unsupported direction string is provided.

        Example:
            >>> txs = builder.get_wallet_transactions("0x71c...12", direction="outgoing")
            >>> for tx in txs:
            ...     print(f"Sent {tx['value']} {tx['token']} to {tx['to_address']}")
        """
        normalized_address = str(address).strip().lower()
        dir_clean = direction.strip().lower()

        if dir_clean in ("outgoing", "out", "from"):
            # Cypher Query: Outgoing transactions only
            cypher = """
            // Step 1: Match outgoing transactions where target wallet is the sender
            MATCH (w:Wallet {address: $address})-[r:SENT]->(to:Wallet)
            // Step 2: Project transaction details and direction tag
            RETURN r.tx_hash AS tx_hash,
                   w.address AS from_address,
                   to.address AS to_address,
                   r.amount AS value,
                   r.amount AS amount,
                   r.token AS token,
                   r.timestamp AS timestamp,
                   r.block_number AS block_number,
                   'outgoing' AS direction
            // Step 3: Order by timestamp descending (newest first)
            ORDER BY r.timestamp DESC
            """
        elif dir_clean in ("incoming", "in", "to"):
            # Cypher Query: Incoming transactions only
            cypher = """
            // Step 1: Match incoming transactions where target wallet is the receiver
            MATCH (from:Wallet)-[r:SENT]->(w:Wallet {address: $address})
            // Step 2: Project transaction details and direction tag
            RETURN r.tx_hash AS tx_hash,
                   from.address AS from_address,
                   w.address AS to_address,
                   r.amount AS value,
                   r.amount AS amount,
                   r.token AS token,
                   r.timestamp AS timestamp,
                   r.block_number AS block_number,
                   'incoming' AS direction
            // Step 3: Order by timestamp descending (newest first)
            ORDER BY r.timestamp DESC
            """
        elif dir_clean in ("both", "all"):
            # Cypher Query: Transactions in either direction
            cypher = """
            // Step 1: Match the target wallet node
            MATCH (w:Wallet {address: $address})
            // Step 2: Match any SENT edge connected to w in either direction
            MATCH (from:Wallet)-[r:SENT]->(to:Wallet)
            WHERE from = w OR to = w
            // Step 3: Project fields with computed direction relative to target wallet
            RETURN r.tx_hash AS tx_hash,
                   from.address AS from_address,
                   to.address AS to_address,
                   r.amount AS value,
                   r.amount AS amount,
                   r.token AS token,
                   r.timestamp AS timestamp,
                   r.block_number AS block_number,
                   CASE WHEN from.address = $address THEN 'outgoing' ELSE 'incoming' END AS direction
            // Step 4: Order chronologically with newest first
            ORDER BY r.timestamp DESC
            """
        else:
            raise ValueError(
                f"Invalid direction '{direction}'. Expected 'outgoing', 'incoming', or 'both'."
            )

        records = self._execute(cypher, {"address": normalized_address})
        return records

    # -------------------------------------------------------------------------
    # 8. GET DATABASE STATS
    # -------------------------------------------------------------------------
    def get_stats(self) -> dict:
        """Return global graph metrics and database summary counts.

        Computes summary statistics across the active graph database:
        - `total_wallets`: Count of all unique (:Wallet) nodes.
        - `total_transactions`: Count of all (:Wallet)-[:SENT]->(:Wallet) edges.
        - `labeled_wallets`: Wallets tagged with entity labels or classifications.
        - `exchanges_found`: Wallets classified as cryptocurrency exchanges.

        Returns:
            dict: Summary metrics dictionary:
                {
                    "total_wallets": int,
                    "total_transactions": int,
                    "labeled_wallets": int,
                    "exchanges_found": int
                }

        Example:
            >>> stats = builder.get_stats()
            >>> print(f"Graph contains {stats['total_wallets']} wallets and {stats['total_transactions']} txs.")
        """
        # Cypher Query: Isolated subquery metrics aggregation
        cypher = """
        // Subquery 1: Compute wallet metrics (total nodes, labeled nodes, exchange nodes)
        CALL {
            // Step 1: Match all wallet nodes optionally to support empty database state
            OPTIONAL MATCH (w:Wallet)
            // Step 2: Return aggregated counts using conditional expressions
            RETURN count(w) AS total_wallets,
                   count(CASE WHEN w.label IS NOT NULL OR w.entity_type IS NOT NULL THEN 1 END) AS labeled_wallets,
                   count(CASE WHEN toUpper(coalesce(w.entity_type, '')) = 'EXCHANGE' OR toUpper(coalesce(w.label, '')) = 'EXCHANGE' THEN 1 END) AS exchanges_found
        }
        // Subquery 2: Compute total transaction count across all SENT relationships
        CALL {
            // Step 3: Match all SENT relationships optionally
            OPTIONAL MATCH ()-[r:SENT]->()
            // Step 4: Return count of transaction edges
            RETURN count(r) AS total_transactions
        }
        // Step 5: Combine subquery results into a single result row
        RETURN total_wallets,
               total_transactions,
               labeled_wallets,
               exchanges_found
        """

        records = self._execute(cypher)
        if records:
            row = records[0]
            return {
                "total_wallets": int(row.get("total_wallets", 0)),
                "total_transactions": int(row.get("total_transactions", 0)),
                "labeled_wallets": int(row.get("labeled_wallets", 0)),
                "exchanges_found": int(row.get("exchanges_found", 0)),
            }

        return {
            "total_wallets": 0,
            "total_transactions": 0,
            "labeled_wallets": 0,
            "exchanges_found": 0,
        }

    # -------------------------------------------------------------------------
    # 9. DELETE INVESTIGATION (CLEANUP)
    # -------------------------------------------------------------------------
    def delete_investigation(self, addresses: list[str]) -> dict:
        """Remove specific wallet nodes and all their connected edges from the graph.

        Why DETACH DELETE is necessary:
        In Neo4j, graph referential integrity prevents deleting a node that still has
        relationships pointing to or from it. Attempting a standard `DELETE w` on a
        connected node will raise a `ConstraintViolationException`.
        `DETACH DELETE` automatically removes all connected incoming and outgoing
        edges before deleting the node itself.

        Args:
            addresses (list[str]): List of wallet addresses to remove.

        Returns:
            dict: Summary dictionary containing count of deleted wallets and status:
                {
                    "deleted_wallets": int,
                    "total_submitted": int,
                    "status": str
                }

        Example:
            >>> cleanup_list = ["0xabc...1", "0xdef...2"]
            >>> builder.delete_investigation(cleanup_list)
            {'deleted_wallets': 2, 'total_submitted': 2, 'status': 'success'}
        """
        if not addresses:
            self.logger.warning("delete_investigation called with empty address list.")
            return {"deleted_wallets": 0, "total_submitted": 0, "status": "empty_list"}

        normalized_addresses = [str(a).strip().lower() for a in addresses]

        # Cypher Query: Bulk DETACH DELETE using UNWIND
        cypher = """
        // Step 1: UNWIND the list of target addresses to iterate row by row
        UNWIND $addresses AS addr
        // Step 2: Match wallet nodes corresponding to each address
        MATCH (w:Wallet {address: addr})
        // Step 3: DETACH DELETE deletes all attached relationships (SENT) and then deletes the node
        DETACH DELETE w
        """

        self._execute(cypher, {"addresses": normalized_addresses})
        self.logger.info("Deleted %d wallet nodes and their incident edges.", len(normalized_addresses))

        return {
            "deleted_wallets": len(normalized_addresses),
            "total_submitted": len(addresses),
            "status": "success",
        }
