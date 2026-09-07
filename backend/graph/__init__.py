"""Graph Engine Module — Pranav's Domain

This module handles everything related to Neo4j:
- Connecting to the database (neo4j_client.py)
- Creating the graph schema/constraints (schema.py)
- Inserting transactions as nodes and edges (builder.py)
- Reusable Cypher query templates (queries.py)

Phase 1: neo4j_client + schema + builder
Phase 2: tracer.py (BFS fund tracing) will be added here
"""

from .schema import (
    SCHEMA_QUERIES,
    NODE_LABELS,
    RELATIONSHIP_TYPES,
    init_schema,
    drop_all,
    get_schema_info,
)

try:
    from .neo4j_client import Neo4jClient
except ImportError:
    Neo4jClient = None  # type: ignore

try:
    from .builder import GraphBuilder
except ImportError:
    GraphBuilder = None  # type: ignore

from . import queries

__all__ = [
    "Neo4jClient",
    "GraphBuilder",
    "queries",
    "SCHEMA_QUERIES",
    "NODE_LABELS",
    "RELATIONSHIP_TYPES",
    "init_schema",
    "drop_all",
    "get_schema_info",
]
