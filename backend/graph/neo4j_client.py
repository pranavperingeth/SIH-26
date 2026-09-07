"""
Neo4j Client Connection Manager — ChainTrace Platform
=====================================================

This module provides a production-ready, beginner-friendly wrapper around the
official Neo4j Python Driver (`neo4j.GraphDatabase`).

Why Neo4j in ChainTrace?
------------------------
In cryptocurrency fraud investigations (e.g., tracking stolen Ethereum or ERC-20
tokens), money moves through complex paths:
  Victim Wallet -> Mule Wallet 1 -> Mule Wallet 2 -> Mixer -> Exchange Deposit Address

In a traditional relational database (like PostgreSQL or MySQL), finding paths across
multiple hops requires expensive, slow recursive SQL JOINs.
In Neo4j (a native Graph Database):
- Wallets and Transactions are stored as "Nodes" (vertices).
- Money movements are stored as "Edges" (relationships, e.g., [:TRANSFERRED_TO]).
- Multi-hop graph traversals (like Breadth-First Search / BFS) run in milliseconds!

Key Responsibilities of this Module:
------------------------------------
1. Connection Management:
   - Connects to the Neo4j instance using the binary Bolt protocol (`bolt://localhost:7687`).
   - Manages a pool of connections via `GraphDatabase.driver`.
   - Supports environment variable configuration via `os.getenv` for 12-factor app architecture.

2. Safe Cypher Query Execution:
   - Cypher is the declarative query language for Neo4j (analogous to SQL for relational DBs).
   - Enforces query parameterization (`params`) to prevent Cypher injection attacks and
     allow Neo4j's query planner to cache execution plans.

3. Session & Resource Lifecycle:
   - Sessions in Neo4j are lightweight contexts for transactions.
   - Automatically handles opening and closing sessions cleanly.
   - Implements Python's Context Manager protocol (`__enter__` and `__exit__`),
     allowing usage with the `with Neo4jClient() as client:` syntax.

4. Connectivity Verification:
   - Provides `verify_connection()` to ping the database during app startup or health checks.

Author: Team Blockies (Pranav's Domain)
Hackathon: Smart India Hackathon 2026
"""

# ==============================================================================
# 1. Imports and Dependencies
# ==============================================================================

# `os` provides access to system environment variables (e.g., reading .env values
# like NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD without hardcoding secrets).
import os

# `logging` allows us to emit structured diagnostic messages at different levels
# (DEBUG, INFO, WARNING, ERROR). This is far better than print() in production
# because it can be filtered, timestamped, and routed to files or monitoring tools.
import logging

# `typing` provides type hints that improve IDE autocompletion, static analysis,
# and code readability for beginners and teammates.
from typing import Any, Dict, List, Optional, Union

# Import the official Neo4j Python driver components.
# `GraphDatabase` is the main entry point to create a Driver instance.
# `Driver` is the connection pool manager that holds open TCP sockets to Neo4j.
# `Session` represents a single conversational context with the database.
from neo4j import GraphDatabase, Driver, Session

# Import specific exceptions raised by Neo4j so we can catch and handle them gracefully:
# - `Neo4jError`: Base class for all errors originating from the Neo4j database engine.
# - `ServiceUnavailable`: Raised when the database cannot be reached (e.g., container stopped).
# - `AuthError`: Raised when the username or password is incorrect.
from neo4j.exceptions import Neo4jError, ServiceUnavailable, AuthError


# ==============================================================================
# 2. Module Logger Setup
# ==============================================================================

# Create a logger specific to this module. Using __name__ ("backend.graph.neo4j_client")
# ensures that log messages clearly show which file they came from.
logger = logging.getLogger(__name__)


# ==============================================================================
# 3. Neo4jClient Class Definition
# ==============================================================================

class Neo4jClient:
    """
    Thread-safe connection manager and query executor for the Neo4j Graph Database.

    This class abstracts away the low-level details of connection pooling, session
    lifecycles, and transaction handling. It provides a clean, pythonic interface
    for running Cypher queries and retrieving results as standard Python dictionaries.

    Supported Usage Patterns:
    -------------------------
    Pattern 1: Context Manager (Recommended - handles auto-closing)
        ```python
        with Neo4jClient() as client:
            records = client.run_query("MATCH (w:Wallet) RETURN w.address AS address LIMIT 10")
            for record in records:
                print(record["address"])
        ```

    Pattern 2: Manual Lifecycle (Useful for long-lived app state, e.g. FastAPI startup/shutdown)
        ```python
        client = Neo4jClient()
        if client.verify_connection():
            data = client.run_query_single("MATCH (w:Wallet {address: $addr}) RETURN w", {"addr": "0x123..."})
        client.close()
        ```
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ) -> None:
        """
        Initialize the Neo4j client and establish the driver connection pool.

        Parameters:
        -----------
        uri : Optional[str]
            The Bolt or Neo4j protocol connection URL.
            If None, reads from the `NEO4J_URI` environment variable.
            Default fallback: "bolt://localhost:7687".
            (Bolt is Neo4j's fast binary protocol; port 7687 is the standard Bolt port).

        user : Optional[str]
            The username for Neo4j authentication.
            If None, reads from `NEO4J_USER` or `NEO4J_USERNAME` environment variables.
            Default fallback: "neo4j".

        password : Optional[str]
            The password for Neo4j authentication.
            If None, reads from the `NEO4J_PASSWORD` environment variable.
            Default fallback: "chaintrace123".

        database : Optional[str]
            The specific Neo4j database name to run queries against.
            In Neo4j 4.x and 5.x Community Edition, the default database is "neo4j".
            If None, reads from `NEO4J_DATABASE` or defaults to "neo4j".

        Design Decision:
        ----------------
        We prioritize explicit arguments passed to the constructor. If an argument
        is not provided (or is None), we fall back to system environment variables
        (loaded via os.getenv), and finally to sensible local development defaults.
        This makes the class work seamlessly in local testing, Docker Compose,
        and production Kubernetes/cloud environments without changing any code!
        """
        # Step 1: Resolve the connection URI.
        # Check explicit parameter -> then environment variable -> then default localhost Bolt port.
        self.uri: str = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")

        # Step 2: Resolve the authentication username.
        # Check explicit parameter -> then NEO4J_USER -> then NEO4J_USERNAME -> then "neo4j".
        self.user: str = (
            user
            or os.getenv("NEO4J_USER")
            or os.getenv("NEO4J_USERNAME")
            or "neo4j"
        )

        # Step 3: Resolve the authentication password.
        # Check explicit parameter -> then NEO4J_PASSWORD -> then default "chaintrace123".
        self.password: str = password or os.getenv("NEO4J_PASSWORD", "chaintrace123")

        # Step 4: Resolve the target database name.
        # Neo4j supports multi-tenancy; "neo4j" is the standard default database name.
        self.database: str = database or os.getenv("NEO4J_DATABASE", "neo4j")

        # Step 5: Initialize the driver reference as None before creating it.
        # The `Driver` object is thread-safe and manages an internal pool of connections.
        self._driver: Optional[Driver] = None

        # Step 6: Create the driver instance using the resolved credentials.
        self._initialize_driver()

    def _initialize_driver(self) -> None:
        """
        Internal helper method to instantiate the official Neo4j Driver.

        Design Decision:
        ----------------
        `GraphDatabase.driver` does NOT immediately open network sockets to the database;
        it configures the connection pool and client security settings. The actual socket
        connection happens when the first query is run or when `verify_connectivity()` is called.
        We wrap this in a try-except block to catch invalid URI schemes or configuration errors early.
        """
        try:
            logger.info(
                f"[Neo4jClient] Initializing Neo4j driver connection to: {self.uri} "
                f"(user: {self.user}, target database: {self.database})"
            )

            # Create the driver using the Bolt URI and basic auth tuple (username, password).
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
            )
            logger.info("[Neo4jClient] Driver initialized successfully.")

        except Exception as e:
            # If the driver cannot even be created (e.g. malformed URI scheme), log the critical error.
            logger.error(
                f"[Neo4jClient] Failed to initialize Neo4j driver with URI '{self.uri}': {e}",
                exc_info=True,
            )
            # We re-raise the exception so the caller is immediately aware that setup failed.
            raise

    # ==========================================================================
    # 4. Connection Verification
    # ==========================================================================

    def verify_connection(self) -> bool:
        """
        Verify that the Neo4j database is online, reachable, and ready to accept queries.

        This method performs a two-step health check:
        1. Calls the driver's built-in `verify_connectivity()` to validate network access
           and credentials against the database cluster.
        2. Executes a lightweight ping query (`RETURN 1 AS alive`) inside a session to ensure
           the query execution pipeline is fully operational.

        Returns:
        --------
        bool:
            `True` if connection succeeded and database responded properly.
            `False` if Neo4j is offline, unreachable, or credentials failed.

        Beginner Note:
        --------------
        Always call `verify_connection()` during application startup (e.g., in a FastAPI
        lifespan event) before allowing user requests to hit the server. This provides fast,
        descriptive feedback if Docker containers are not running yet.
        """
        # Ensure driver object exists before attempting communication
        if self._driver is None:
            logger.warning("[Neo4jClient] verify_connection called but driver is None.")
            return False

        try:
            logger.info(f"[Neo4jClient] Verifying connectivity to Neo4j at {self.uri}...")

            # Step 1: Built-in driver connectivity verification.
            # This checks routing tables, socket availability, and auth tokens.
            self._driver.verify_connectivity()

            # Step 2: Run a trivial ping query (`RETURN 1 AS alive`) through a session.
            # If the query runs and returns 1, we know the Cypher execution engine is healthy.
            result = self.run_query_single("RETURN 1 AS alive")
            if result and result.get("alive") == 1:
                logger.info("[Neo4jClient] Connection verified successfully! Neo4j is ALIVE.")
                return True

            logger.warning(f"[Neo4jClient] Health check query returned unexpected result: {result}")
            return False

        except AuthError as e:
            # Username or password was incorrect.
            logger.error(
                f"[Neo4jClient] Authentication failed for user '{self.user}'. "
                f"Please verify NEO4J_USER and NEO4J_PASSWORD: {e}"
            )
            return False

        except ServiceUnavailable as e:
            # Database service is down or network port 7687 is blocked.
            logger.error(
                f"[Neo4jClient] Neo4j service unavailable at '{self.uri}'. "
                f"Is the Neo4j Docker container running? Run 'docker ps' or 'docker-compose up -d neo4j'. "
                f"Details: {e}"
            )
            return False

        except Exception as e:
            # Catch any unexpected network, TLS, or system errors.
            logger.error(
                f"[Neo4jClient] Unexpected error verifying connection to Neo4j: {e}",
                exc_info=True,
            )
            return False

    # ==========================================================================
    # 5. Query Execution Methods
    # ==========================================================================

    def run_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query with parameters and return ALL matching records as a list of dictionaries.

        Parameters:
        -----------
        query : str
            The Cypher query string to execute.
            Example: "MATCH (w:Wallet {address: $address})-[r:TRANSFERRED_TO]->(m:Wallet) RETURN m.address AS destination, r.amount_eth AS amount"

        params : Optional[Dict[str, Any]]
            A dictionary of parameters to bind to the Cypher query.
            Example: {"address": "0x71c...a39"}
            Default is None, which will be treated as an empty dictionary `{}`.

        Returns:
        --------
        List[Dict[str, Any]]:
            A list of dictionaries where each dictionary represents one record (row).
            Keys correspond to the Cypher RETURN aliases, and values are converted
            into standard Python types (strings, ints, floats, lists, dicts).
            If no records matched, returns an empty list `[]`.

        CRITICAL SECURITY CONCEPT: Cypher Injection Prevention
        -------------------------------------------------------
        NEVER use Python string formatting (f"MATCH (w:Wallet {w.address})") to build Cypher queries!
        If a malicious user submits an address containing Cypher syntax, they could delete your graph!
        Always use query parameters (`$param_name`) and pass the values via the `params` argument:
            SAFE:   client.run_query("MATCH (w:Wallet {address: $addr}) RETURN w", {"addr": user_input})
            UNSAFE: client.run_query(f"MATCH (w:Wallet {{address: '{user_input}'}}) RETURN w")  <-- BAD!

        Performance Benefit:
        --------------------
        Parameterized queries allow Neo4j's Cypher compiler to cache the execution plan.
        Running the same query with different parameter values is up to 10x faster!
        """
        # Ensure parameters dictionary is never None to prevent driver errors
        parameters = params if params is not None else {}

        # Check that driver is active before attempting to open a session
        if self._driver is None:
            raise RuntimeError(
                "[Neo4jClient] Driver is closed or uninitialized. Cannot execute query."
            )

        # Log query execution at DEBUG level so production logs aren't flooded,
        # but developers can enable DEBUG logging to inspect queries during development.
        logger.debug(f"[Neo4jClient] Running query: {query} with params: {parameters}")

        try:
            # We open a session using Python's `with` statement.
            # A Session represents a conversation with the database.
            # Using the context manager guarantees that the session is closed and its
            # underlying TCP connection is returned to the driver pool when done!
            with self._driver.session(database=self.database) as session:
                # `session.run()` sends the Cypher query and parameters to Neo4j over Bolt.
                # It returns a `Result` cursor which streams records back from the server.
                result = session.run(query, parameters=parameters)

                # `record.data()` converts the internal Neo4j `Record` object into a clean,
                # standard Python dictionary. This makes it trivial to convert to JSON in FastAPI
                # or pass to Pandas DataFrames for machine learning models.
                records: List[Dict[str, Any]] = [record.data() for record in result]

                logger.debug(f"[Neo4jClient] Query returned {len(records)} record(s).")
                return records

        except Neo4jError as e:
            # Catch Cypher syntax errors, constraint violations, or database lock timeouts.
            logger.error(
                f"[Neo4jClient] Cypher execution error while running query:\nQuery: {query}\nParams: {parameters}\nError: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            # Catch any unexpected network dropouts or deserialization bugs.
            logger.error(
                f"[Neo4jClient] Unexpected error executing query:\nQuery: {query}\nParams: {parameters}\nError: {e}",
                exc_info=True,
            )
            raise

    def run_query_single(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a Cypher query expected to return at most ONE record, and return it as a dictionary.

        Parameters:
        -----------
        query : str
            The Cypher query string to execute.
            Example: "MATCH (w:Wallet {address: $address}) RETURN w.risk_score AS risk, w.is_exchange AS is_exchange"

        params : Optional[Dict[str, Any]]
            A dictionary of parameters to safely bind to the query.
            Example: {"address": "0x28c6c06298d514db089934071355e5743bf21d60"}

        Returns:
        --------
        Optional[Dict[str, Any]]:
            - A dictionary containing the record's fields if a match was found.
            - `None` if the query returned zero records.

        Why this method is useful:
        --------------------------
        Many graph queries in blockchain analysis search for a single unique entity,
        such as checking if a specific transaction hash already exists, retrieving a wallet's
        labels, or getting an aggregate count (e.g. `COUNT(n)`).
        Using `run_query_single()` saves the caller from having to write `records[0] if records else None`.
        """
        # Ensure parameters dictionary is never None
        parameters = params if params is not None else {}

        # Check driver state
        if self._driver is None:
            raise RuntimeError(
                "[Neo4jClient] Driver is closed or uninitialized. Cannot execute query."
            )

        logger.debug(f"[Neo4jClient] Running single-record query: {query} with params: {parameters}")

        try:
            # Open a scoped session with automatic cleanup
            with self._driver.session(database=self.database) as session:
                result = session.run(query, parameters=parameters)

                # `result.single()` fetches the first record from the result stream.
                # If there are no records, it returns None.
                record = result.single()

                # If no record was found, return None immediately
                if record is None:
                    logger.debug("[Neo4jClient] Query returned 0 records (None).")
                    return None

                # Convert the single Neo4j Record to a clean Python dictionary
                data: Dict[str, Any] = record.data()
                logger.debug(f"[Neo4jClient] Single query result: {data}")
                return data

        except Neo4jError as e:
            logger.error(
                f"[Neo4jClient] Cypher error in run_query_single:\nQuery: {query}\nParams: {parameters}\nError: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            logger.error(
                f"[Neo4jClient] Unexpected error in run_query_single:\nQuery: {query}\nParams: {parameters}\nError: {e}",
                exc_info=True,
            )
            raise

    # ==========================================================================
    # 6. Resource Cleanup & Context Manager Methods
    # ==========================================================================

    def close(self) -> None:
        """
        Close the Neo4j driver and release all active connection pool resources.

        Why closing is essential:
        -------------------------
        Each open connection in the connection pool maintains an active TCP socket
        to the Neo4j server. Failing to close the driver can lead to socket exhaustion,
        connection leaks, and memory bloat on both client and database machines.

        This method is idempotent: calling it multiple times is completely safe.
        """
        if self._driver is not None:
            logger.info("[Neo4jClient] Closing Neo4j driver and terminating connection pool...")
            try:
                self._driver.close()
                logger.info("[Neo4jClient] Neo4j driver closed successfully.")
            except Exception as e:
                logger.warning(f"[Neo4jClient] Warning during driver close: {e}")
            finally:
                # Set driver to None so subsequent calls know it has been closed
                self._driver = None

    def __enter__(self) -> "Neo4jClient":
        """
        Enter the runtime context related to this object (Python Context Manager).

        This enables using the class in a `with` statement:
            ```python
            with Neo4jClient() as client:
                client.run_query("MATCH (n) RETURN count(n) AS count")
            ```

        Returns:
        --------
        Neo4jClient:
            Returns self so it can be bound to the target variable in `as client`.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """
        Exit the runtime context related to this object.

        Automatically calls `self.close()` when the execution block leaves the `with`
        statement, even if an unhandled exception was raised inside the block!

        Parameters:
        -----------
        exc_type : Optional[type]
            The exception class (if an exception was raised inside the `with` block).
        exc_val : Optional[BaseException]
            The exception instance (value).
        exc_tb : Optional[Any]
            The traceback object.

        Design Decision:
        ----------------
        We return `None` (falsy) so that if an exception occurred within the `with` block,
        Python will propagate the exception upward rather than silently swallowing it.
        """
        self.close()

    # ==========================================================================
    # 7. Helper Properties
    # ==========================================================================

    @property
    def driver(self) -> Optional[Driver]:
        """
        Direct access to the underlying Neo4j Driver instance.

        Useful if an advanced component requires access to driver-level features
        such as managed write transactions (`session.execute_write(...)`).
        """
        return self._driver

    @property
    def is_closed(self) -> bool:
        """
        Check if the driver connection pool has been closed.

        Returns:
        --------
        bool: True if closed (driver is None), False if active.
        """
        return self._driver is None


# ==============================================================================
# 8. Interactive Test & Quick-Start Block
# ==============================================================================

if __name__ == "__main__":
    """
    Direct Execution Test Block
    ---------------------------
    You can run this file directly with Python to verify your Neo4j configuration:
        $ python -m backend.graph.neo4j_client
        OR
        $ python backend/graph/neo4j_client.py

    This test:
    1. Reads environment configuration.
    2. Instantiates Neo4jClient via the context manager.
    3. Runs verify_connection().
    4. Executes a test parameterized Cypher query.
    5. Cleans up automatically.
    """
    # Configure logging output to standard console with clear formatting
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print("\n" + "=" * 70)
    print(" 🔗 ChainTrace — Neo4j Connection Manager Diagnostic Test")
    print("=" * 70)

    # Instantiate the client using the context manager
    print(f"\n[1] Attempting connection using defaults / .env settings...")
    try:
        with Neo4jClient() as client:
            print(f"    Target URI:      {client.uri}")
            print(f"    Target User:     {client.user}")
            print(f"    Target Database: {client.database}")

            # Step 1: Health check
            print("\n[2] Checking database health via verify_connection()...")
            is_alive = client.verify_connection()

            if is_alive:
                print("    >>> SUCCESS: Neo4j is online and reachable! 🚀")

                # Step 2: Test query execution
                print("\n[3] Running a parameterized test query...")
                test_query = """
                RETURN 
                    $greeting AS message,
                    2026 AS hackathon_year,
                    'ChainTrace' AS project
                """
                test_params = {"greeting": "Hello Neo4j from Team Blockies!"}
                result = client.run_query_single(test_query, test_params)

                print(f"    Query Result: {result}")
                print("\n[4] All tests passed! Connection manager is working perfectly.")
            else:
                print("    >>> WARNING: Neo4j is not reachable.")
                print("    To start Neo4j locally via Docker, run:")
                print("        docker-compose up -d neo4j")
                print("    Or verify that Neo4j is running on port 7687.")

    except Exception as err:
        print(f"\n[!] Diagnostic test encountered an exception: {err}")

    print("\n" + "=" * 70 + "\n")
