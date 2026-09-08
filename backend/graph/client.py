"""
client.py — Direct / alias module for Neo4jClient.

This file provides a clean import alias for `backend.graph.neo4j_client.Neo4jClient`.
Allows developers and test runners to import using either:
    from client import Neo4jClient
or:
    from neo4j_client import Neo4jClient
"""

try:
    from .neo4j_client import Neo4jClient
except (ImportError, ValueError):
    from neo4j_client import Neo4jClient

__all__ = ["Neo4jClient"]
