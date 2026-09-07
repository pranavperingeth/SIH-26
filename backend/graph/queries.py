"""
queries.py — Reusable Cypher Query Templates for ChainTrace Graph Database.

This module acts as a central reference library and constant catalog for all Cypher
queries executed against Neo4j in the ChainTrace fraud investigation platform.

Graph Schema Quick Reference:
-----------------------------
Nodes:
  (:Wallet {
      address: STRING,       # Ethereum / EVM address (e.g. '0x...')
      label: STRING,         # Entity classification ('UNKNOWN', 'EXCHANGE', 'SCAMMER', 'VICTIM', etc.)
      risk_score: FLOAT,     # Unified fraud risk score between 0.0 and 100.0
      entity_type: STRING,   # Node category (default 'WALLET')
      created_at: INTEGER    # Timestamp (milliseconds epoch) when added to graph
  })

Relationships:
  (:Wallet)-[:SENT {
      tx_hash: STRING,       # Blockchain transaction hash
      amount: FLOAT,         # Value moved (in native token or ether, e.g. 1.85)
      token: STRING,         # Asset symbol (default 'ETH')
      timestamp: INTEGER     # Epoch timestamp in milliseconds of tx execution
  }]->(:Wallet)

Every query is parameterized (using `$param_name` syntax) to prevent Cypher injection
vulnerabilities and enable Neo4j query plan caching for maximum performance.
"""

# =============================================================================
# WALLET NODE OPERATIONS
# =============================================================================

# MERGE_WALLET:
# Creates a Wallet node if it does not already exist in the graph database.
# If a node with the given address already exists, it is matched without creating a duplicate.
#
# Parameters:
#   $address    (str)  - Unique Ethereum wallet address (e.g., '0x1234...').
#   $label      (str)  - (Optional) Entity label (e.g., 'UNKNOWN', 'VICTIM', 'EXCHANGE').
#   $risk_score (float)- (Optional) Initial fraud risk score (defaults to 0.0).
#
# Cypher Mechanism:
#   - MERGE looks up the Wallet by `address` (unique constraint).
#   - ON CREATE SET only executes when a brand-new node is inserted, populating default
#     metadata such as created_at timestamp and default label.
MERGE_WALLET = """
MERGE (w:Wallet {address: $address})
ON CREATE SET
    w.label = coalesce($label, 'UNKNOWN'),
    w.risk_score = coalesce($risk_score, 0.0),
    w.entity_type = coalesce($entity_type, 'WALLET'),
    w.created_at = coalesce($created_at, timestamp())
RETURN w
"""

# LABEL_WALLET:
# Updates the intelligence classification label of an existing wallet.
# Used when an investigator, rule engine, or intelligence feed identifies a wallet's role
# (e.g. updating 'UNKNOWN' -> 'EXCHANGE' or 'SCAMMER').
#
# Parameters:
#   $address (str) - Target wallet address.
#   $label   (str) - New entity label ('EXCHANGE', 'MIXER', 'SCAMMER', 'VICTIM', etc.).
#
# Cypher Mechanism:
#   - MATCH finds the existing node.
#   - SET mutates the `label` property on that node.
LABEL_WALLET = """
MATCH (w:Wallet {address: $address})
SET w.label = $label
RETURN w
"""

# GET_WALLET:
# Retrieves a single wallet node and all its stored properties by address.
#
# Parameters:
#   $address (str) - The wallet address to search for.
#
# Returns:
#   The complete Wallet node object (including address, label, risk_score, etc.).
GET_WALLET = """
MATCH (w:Wallet {address: $address})
RETURN w
"""

# DELETE_WALLET:
# Deletes a specific wallet and all incoming/outgoing transactions attached to it.
#
# Parameters:
#   $address (str) - Address of the wallet to remove.
#
# Cypher Mechanism:
#   - DETACH DELETE severs and deletes all incident relationships (SENT edges) first,
#     then removes the Wallet node itself, preventing orphan constraint violations.
DELETE_WALLET = """
MATCH (w:Wallet {address: $address})
DETACH DELETE w
"""


# =============================================================================
# TRANSACTION RELATIONSHIP OPERATIONS (SENT EDGES)
# =============================================================================

# CREATE_TRANSACTION:
# Creates a directed SENT edge between two wallets representing a blockchain transfer.
# Ensures both sender and recipient wallets exist in the graph by using MERGE on both.
#
# Parameters:
#   $from_address (str)   - Sender wallet address.
#   $to_address   (str)   - Recipient wallet address.
#   $amount       (float) - Amount of crypto transferred (e.g. 2.5).
#   $tx_hash      (str)   - (Optional) Unique transaction hash on the blockchain.
#   $token        (str)   - (Optional) Asset token symbol (defaults to 'ETH').
#   $timestamp    (int)   - (Optional) Unix epoch timestamp in milliseconds.
#
# Cypher Mechanism:
#   - MERGE (from:Wallet ...) ensures the source wallet node exists.
#   - MERGE (to:Wallet ...) ensures the destination wallet node exists.
#   - CREATE (from)-[r:SENT ...]->(to) creates a brand-new directed edge.
#   - coalesce() sets sensible defaults if optional parameters are null.
CREATE_TRANSACTION = """
MERGE (from:Wallet {address: $from_address})
MERGE (to:Wallet {address: $to_address})
CREATE (from)-[r:SENT {
    tx_hash: coalesce($tx_hash, randomUUID()),
    amount: $amount,
    token: coalesce($token, 'ETH'),
    timestamp: coalesce($timestamp, timestamp())
}]->(to)
RETURN r
"""

# BATCH_INSERT:
# High-performance bulk ingestion of transactions using Cypher's UNWIND clause.
# Rather than issuing hundreds of individual queries across the network, this accepts
# a single list of transaction parameter dictionaries and executes them in one ACID batch.
#
# Parameters:
#   $transactions (list of dict) - List of transfer objects, where each dict has:
#       - from_address (str)
#       - to_address   (str)
#       - amount       (float)
#       - tx_hash      (str, optional)
#       - token        (str, optional)
#       - timestamp    (int, optional)
#
# Cypher Mechanism:
#   - UNWIND transforms the array of transaction maps into individual rows.
#   - MERGE creates or finds the sender and receiver nodes for each row.
#   - CREATE instantiates the SENT edge for each transaction.
#   - count(r) returns the total number of relationships created in this single batch.
BATCH_INSERT = """
UNWIND $transactions AS tx
MERGE (from:Wallet {address: tx.from_address})
MERGE (to:Wallet {address: tx.to_address})
CREATE (from)-[r:SENT {
    tx_hash: coalesce(tx.tx_hash, randomUUID()),
    amount: tx.amount,
    token: coalesce(tx.token, 'ETH'),
    timestamp: coalesce(tx.timestamp, timestamp())
}]->(to)
RETURN count(r) AS inserted_count
"""


# =============================================================================
# TRANSACTION RETRIEVAL QUERIES
# =============================================================================

# GET_OUTGOING_TXS:
# Fetches all transactions where the specified wallet is the SENDER (money moving OUT).
# Useful for tracking where suspect funds were disbursed.
#
# Parameters:
#   $address (str) - Address of the sender wallet.
#
# Returns:
#   Each transaction's hash, sender, recipient, amount, token, timestamp,
#   and the recipient's entity label (to quickly detect transfers to exchanges).
GET_OUTGOING_TXS = """
MATCH (from:Wallet {address: $address})-[r:SENT]->(to:Wallet)
RETURN r.tx_hash AS tx_hash,
       from.address AS from_address,
       to.address AS to_address,
       r.amount AS amount,
       r.token AS token,
       r.timestamp AS timestamp,
       to.label AS to_label,
       r,
       to
ORDER BY r.timestamp DESC
"""

# GET_INCOMING_TXS:
# Fetches all transactions where the specified wallet is the RECIPIENT (money moving IN).
# Useful for identifying victim deposits or feeder wallets.
#
# Parameters:
#   $address (str) - Address of the recipient wallet.
#
# Returns:
#   Each transaction's hash, sender, recipient, amount, token, timestamp,
#   and the sender's entity label.
GET_INCOMING_TXS = """
MATCH (from:Wallet)-[r:SENT]->(to:Wallet {address: $address})
RETURN r.tx_hash AS tx_hash,
       from.address AS from_address,
       to.address AS to_address,
       r.amount AS amount,
       r.token AS token,
       r.timestamp AS timestamp,
       from.label AS from_label,
       r,
       from
ORDER BY r.timestamp DESC
"""

# GET_ALL_TXS:
# Fetches both incoming and outgoing transactions for a wallet in a single query.
# Calculates a 'direction' column ('OUTGOING' vs 'INCOMING') based on whether the
# query wallet was the start node or end node of the relationship.
#
# Parameters:
#   $address (str) - Target wallet address.
#
# Returns:
#   Combined ledger of incoming and outgoing transfers sorted newest-first.
GET_ALL_TXS = """
MATCH (w:Wallet {address: $address})-[r:SENT]-(other:Wallet)
RETURN r.tx_hash AS tx_hash,
       startNode(r).address AS from_address,
       endNode(r).address AS to_address,
       r.amount AS amount,
       r.token AS token,
       r.timestamp AS timestamp,
       startNode(r).label AS from_label,
       endNode(r).label AS to_label,
       CASE WHEN startNode(r).address = $address THEN 'OUTGOING' ELSE 'INCOMING' END AS direction,
       r
ORDER BY r.timestamp DESC
"""


# =============================================================================
# GRAPH METRICS & COUNT QUERIES
# =============================================================================

# COUNT_WALLETS:
# Returns the total number of Wallet nodes currently indexed in the graph.
COUNT_WALLETS = """
MATCH (w:Wallet)
RETURN count(w) AS wallet_count
"""

# COUNT_TRANSACTIONS:
# Returns the total number of SENT relationships (edges) in the graph.
COUNT_TRANSACTIONS = """
MATCH ()-[r:SENT]->()
RETURN count(r) AS transaction_count
"""

# COUNT_LABELED:
# Returns the count of wallets that have an identified entity label (non-null and not 'UNKNOWN').
# Useful for measuring entity intelligence coverage across the dataset.
COUNT_LABELED = """
MATCH (w:Wallet)
WHERE w.label IS NOT NULL AND w.label <> 'UNKNOWN'
RETURN count(w) AS labeled_count
"""

# COUNT_EXCHANGES:
# Returns the total number of wallets classified as cryptocurrency exchanges (e.g. Binance, WazirX).
# Represents the number of potential cash-out / freezing endpoints known to the system.
COUNT_EXCHANGES = """
MATCH (w:Wallet)
WHERE w.label = 'EXCHANGE'
RETURN count(w) AS exchange_count
"""


# =============================================================================
# DATABASE ADMINISTRATION & TEST CLEANUP
# =============================================================================

# DELETE_ALL:
# Wipes the entire graph database by deleting all nodes and relationships.
# CAUTION: Strictly intended for automated test suites, staging sandboxes,
# and resetting demo states. Never use in production!
DELETE_ALL = """
MATCH (n)
DETACH DELETE n
"""


# =============================================================================
# PHASE 2 PREVIEW QUERIES
# =============================================================================
# The following queries represent advanced graph algorithms, variable-length path
# traversals, and structural pattern detection scheduled for Phase 2 implementation.
# They are kept here as a documented preview and reference.

# NOTE: Phase 2
# BFS_TRACE — Variable-length path from suspect to exchange (1 to 6 hops).
# Cypher variable-length syntax `[:SENT*1..6]` performs a breadth-first search up to 6
# hops away from a suspect wallet, tracing money laundering chains through intermediate
# mules until it hits a wallet with the 'EXCHANGE' label.
# Filters out micro-dust transactions (< 0.01) to prune noise.
#
# BFS_TRACE = """
# MATCH path = (start:Wallet {address: $suspect})-[:SENT*1..6]->(end:Wallet)
# WHERE end.label = 'EXCHANGE'
#   AND ALL(r IN relationships(path) WHERE r.amount > 0.01)
# RETURN path, length(path) AS hops,
#        [r IN relationships(path) | r.amount] AS amounts,
#        [node IN nodes(path) | node.address] AS trace_addresses
# ORDER BY hops ASC
# LIMIT 10
# """

# NOTE: Phase 2
# SHORTEST_PATH — Shortest path from suspect to any exchange.
# Uses Neo4j's optimized Dijkstra/BFS shortestPath() algorithm to find the absolute
# fastest cash-out path taken by stolen funds into an exchange.
#
# SHORTEST_PATH = """
# MATCH (start:Wallet {address: $suspect}), (end:Wallet {label: 'EXCHANGE'})
# MATCH path = shortestPath((start)-[:SENT*1..10]->(end))
# RETURN path, length(path) AS hops,
#        [node IN nodes(path) | node.address] AS path_nodes,
#        [r IN relationships(path) | r.amount] AS path_amounts
# ORDER BY hops ASC
# LIMIT 1
# """

# NOTE: Phase 2
# FAN_IN — Who sent money TO this wallet.
# Identifies fan-in aggregation patterns where dozens of small feeder accounts or victims
# send funds into a single consolidation wallet (a classic mule syndicate structure).
#
# FAN_IN = """
# MATCH (sender:Wallet)-[r:SENT]->(target:Wallet {address: $address})
# RETURN sender.address AS sender_address,
#        sender.label AS sender_label,
#        count(r) AS tx_count,
#        sum(r.amount) AS total_amount
# ORDER BY total_amount DESC
# """

# NOTE: Phase 2
# FAN_OUT — Where did this wallet SEND money.
# Identifies fan-out dispersal patterns where a wallet splits a large sum into multiple
# smaller payments to avoid AML thresholds (smurfing / peel chain behavior).
#
# FAN_OUT = """
# MATCH (source:Wallet {address: $address})-[r:SENT]->(receiver:Wallet)
# RETURN receiver.address AS receiver_address,
#        receiver.label AS receiver_label,
#        count(r) AS tx_count,
#        sum(r.amount) AS total_amount
# ORDER BY total_amount DESC
# """
