<div align="center">

# 🔗 ChainTrace
### *Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges*

<br/>

> Built by **Team Blockies** 🧱 for **Smart India Hackathon 2026**
> 
> Problem Statement ID: **26183** &nbsp;|&nbsp; Organization: **Ministry of Home Affairs** &nbsp;|&nbsp; Department: **I4C, CIS Division**

<br/>

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Ethereum](https://img.shields.io/badge/Ethereum-EVM-3C3C3D?style=for-the-badge&logo=ethereum&logoColor=white)](https://ethereum.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)

<br/>

[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML-189BCC?style=for-the-badge)](https://xgboost.readthedocs.io)
[![SHAP](https://img.shields.io/badge/SHAP-Explainable_AI-FF6B6B?style=for-the-badge)](https://shap.readthedocs.io)

<br/>

![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Blockchain](https://img.shields.io/badge/Blockchain-Ethereum%20%7C%20EVM-blueviolet?style=flat-square)
![Theme](https://img.shields.io/badge/Theme-Blockchain_%26_Cybersecurity-orange?style=flat-square)

</div>

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Our Solution](#-our-solution)
- [How It Works](#-how-it-works)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Graph Analysis](#-graph-analysis)
- [Fraud Detection Engine](#-fraud-detection-engine)
- [Risk Scoring System](#-risk-scoring-system)
- [Explainable AI](#-explainable-ai)
- [Real-Time Pipeline](#-real-time-pipeline)
- [API Reference](#-api-reference)
- [Database Design](#-database-design)
- [Security](#-security)
- [Getting Started](#-getting-started)
- [Docker Deployment](#-docker-deployment)
- [Future Scope](#-future-scope)
- [Team Blockies](#-team-blockies)

---

## 🚨 Problem Statement

> **SIH 2026 | Problem ID: 26183**
> 
> Cyber fraud victims increasingly report **suspect cryptocurrency wallet addresses** used by fraudsters for fund collection in cases involving:

| Fraud Type | Description |
|---|---|
| 📈 Investment Scams | Fake investment platforms promising high returns |
| 📋 Task-Based Frauds | Fake job/task platforms stealing deposits |
| 🔞 Sextortion | Blackmail via intimate images |
| 💻 Ransomware | Encrypted files held for ransom |
| 🎣 Phishing | Credential theft targeting crypto wallets |
| 🌑 Darknet Transactions | Illegal goods/services on dark markets |
| 🏛️ Organized Cybercrime | Structured financial criminal networks |

**The Challenge:** During investigations, reported wallets are often the first hop in a complex money-laundering chain. Fraudsters move stolen crypto through dozens of intermediate wallets — using mixers, peel chains, and chain-hopping — before cashing out at a cryptocurrency exchange. Manually tracing this trail takes weeks. By then, the funds are gone.

---

## 💡 Our Solution

**ChainTrace** is an AI-powered blockchain investigation platform that automates the entire trace-to-freeze pipeline — from a victim-reported wallet address to identifying the final exchange where stolen funds are cashed out.

```
Victim reports wallet  →  ChainTrace traces the money  →  Police freezes the exchange account
```

### What sets ChainTrace apart:

| Capability | Description |
|---|---|
| 🕸️ **Automated Fund Tracing** | BFS graph traversal traces money through up to 6 hops automatically |
| 🧠 **AI-Powered Detection** | XGBoost model trained on 203K labeled transactions detects laundering patterns |
| 📐 **Rule Engine** | Catches peel chains, fan-in/fan-out, velocity anomalies, and mixer interactions |
| 🏦 **Exchange Identification** | Automatically identifies the destination exchange (Binance, WazirX, etc.) |
| 💯 **Risk Scoring (0–100)** | Unified score combining ML + Rules + Graph position |
| 🔍 **Explainable AI** | SHAP-powered explanations for every risk score — court-admissible reasoning |
| ⚡ **Real-Time Monitoring** | WebSocket alerts when watched wallets move funds |
| 📄 **Auto-Generated Reports** | Law-enforcement-ready PDF reports for freeze requests |

---

## ⚙️ How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   1. INGEST         2. TRACE          3. ANALYZE      4. ACT    │
│                                                                  │
│   Victim reports    BFS algorithm     ML + Rules      Identify  │
│   suspect wallet →  follows the   →   score every  →  exchange  │
│   address           money through     wallet in       & generate│
│                     Neo4j graph       the path        PDF report│
│                     (up to 6 hops)                              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Step-by-step:**

1. **Input** — An investigator submits a suspect wallet address via the dashboard or API
2. **Ingestion** — ChainTrace fetches the wallet's complete transaction history from the Ethereum blockchain (via Etherscan/Alchemy APIs), including all ETH and ERC-20 token transfers
3. **Graph Construction** — All transactions are loaded into a Neo4j graph database as wallet nodes connected by transaction edges
4. **Fund Tracing** — A Breadth-First Search (BFS) algorithm traces the money forward, hopping from wallet to wallet, pruning dust transactions and innocent bystanders
5. **Fraud Detection** — Each wallet in the traced path is analyzed by a 4-layer detection engine (Rules → Behavioral Features → ML Model → Graph Algorithms)
6. **Risk Scoring** — A unified score (0–100) is computed combining ML confidence, rule triggers, and graph position
7. **Exchange Detection** — When the traced path hits a wallet belonging to a known exchange (from our intelligence database), the trace stops and the exchange is identified
8. **Alert & Report** — A real-time WebSocket alert is pushed to the investigator's dashboard, and a PDF report is auto-generated for law enforcement action

---

## ✨ Key Features

### 🕸️ Interactive Graph Visualization
Visualize the complete fund-flow network from victim to exchange using Cytoscape.js. Click any node to see risk scores, transaction history, and SHAP explanations.

### 📊 Investigator Dashboard
A purpose-built React dashboard for law enforcement officers — submit wallets, track investigations, receive live alerts, and export reports.

### 🔴 Live Alert System
Real-time WebSocket notifications when:
- A watched wallet moves funds
- A high-risk pattern is detected
- An exchange is identified as the fund destination

### 📄 Law Enforcement Reports
Auto-generated PDF reports containing:
- Full traced path with transaction hashes
- Risk scores and explanations for every hop
- Final exchange identified
- Recommended action (freeze request template)
- All evidence formatted for legal proceedings

### 🏦 Address Intelligence Database
Built-in database of 10,000+ labeled addresses — exchanges, mixers, scam wallets, sanctioned entities — sourced from Etherscan, CryptoScamDB, and OFAC sanctions lists.

---

## 🛠️ Tech Stack

### ⚙️ Backend

| Technology | Purpose | Badge |
|---|---|---|
| Python 3.12+ | Core backend & analytics | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| FastAPI | REST API & WebSocket server | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) |
| Pydantic v2 | Request/response validation | ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white) |
| SQLAlchemy | Database ORM | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square) |
| Celery | Background task processing | ![Celery](https://img.shields.io/badge/Celery-37814A?style=flat-square&logo=celery&logoColor=white) |
| Redis | Cache, queue & real-time pub/sub | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white) |

### ⛓️ Blockchain

**Supported Networks:**

![Ethereum](https://img.shields.io/badge/Ethereum-3C3C3D?style=for-the-badge&logo=ethereum&logoColor=white)
![BNB Chain](https://img.shields.io/badge/BNB_Smart_Chain-F0B90B?style=for-the-badge&logo=binance&logoColor=black)
![Polygon](https://img.shields.io/badge/Polygon-8247E5?style=for-the-badge&logo=polygon&logoColor=white)

**Data Providers:**

[![Alchemy](https://img.shields.io/badge/Alchemy-363FF9?style=flat-square&logo=alchemy&logoColor=white)](https://alchemy.com)
[![Etherscan](https://img.shields.io/badge/Etherscan_API-21325B?style=flat-square)](https://etherscan.io/apis)
[![Infura](https://img.shields.io/badge/Infura-FF6B2B?style=flat-square)](https://infura.io)

| Library | Purpose |
|---|---|
| `web3.py` | EVM blockchain interaction |
| `ABI decoding` | Smart contract event parsing |
| `JSON-RPC` | Direct node communication |
| [Orbit](https://github.com/s0md3v/Orbit) | Open-source recursive wallet crawler — reference for ingestion layer |
| [BlockTracker](https://github.com/thisiskeanyvy/blocktracker) | Open-source transaction tree builder — reference for BFS tracer & probability scoring |

### 🗄️ Databases

| Database | Purpose | Badge |
|---|---|---|
| SQLite / PostgreSQL | Relational store — investigations, users, alerts, risk scores | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) |
| Neo4j 5 | Graph DB — wallet relationships, fund-flow tracing, BFS | ![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=flat-square&logo=neo4j&logoColor=white) |
| Redis 7 | Caching, task queues, WebSocket pub/sub | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white) |

### 🧪 ML & AI

| Library | Purpose | Badge |
|---|---|---|
| XGBoost | Primary fraud classifier | ![XGBoost](https://img.shields.io/badge/XGBoost-189BCC?style=flat-square) |
| scikit-learn | ML toolkit (Random Forest, Isolation Forest) | ![sklearn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white) |
| SHAP | Explainable AI — human-readable risk explanations | ![SHAP](https://img.shields.io/badge/SHAP-FF6B6B?style=flat-square) |
| Pandas / NumPy | Data processing & feature extraction | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) |

**Training Data:** [Elliptic Bitcoin Dataset](https://www.kaggle.com/datasets/ellipticco/elliptic-data-set) — 203,769 labeled transactions (licit / illicit / unknown)

### 🎨 Frontend

| Technology | Purpose | Badge |
|---|---|---|
| React 18 | Investigator Dashboard | ![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black) |
| TypeScript | Type-safe development | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white) |
| Cytoscape.js | Interactive graph visualization | ![Cytoscape](https://img.shields.io/badge/Cytoscape.js-F7A800?style=flat-square) |
| Tailwind CSS | UI styling | ![Tailwind](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white) |
| Recharts | Analytics charts | ![Recharts](https://img.shields.io/badge/Recharts-22B5BF?style=flat-square) |

### 🐳 DevOps

| Technology | Purpose | Badge |
|---|---|---|
| Docker Compose | Multi-service orchestration | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) |
| GitHub Actions | CI/CD pipeline | ![Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white) |

---

## 🏗️ System Architecture

```
                         ┌─────────────────────┐
                         │     BLOCKCHAINS      │
                         │  Ethereum / EVM      │
                         └──────────┬──────────┘
                                    │
                              RPC / APIs
                            (Alchemy/Etherscan)
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │   BLOCKCHAIN INGESTION    │
                    │   Web3.py / Etherscan API │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │   DATA PROCESSING LAYER   │
                    │  Python / AsyncIO / Celery │
                    └─────────────┬─────────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
          ┌────────────┐   ┌────────────┐   ┌────────────┐
          │   SQLite   │   │   Neo4j    │   │   Redis    │
          │  (Cases,   │   │  (Graph,   │   │  (Cache,   │
          │   Alerts)  │   │ Fund Flow) │   │  Queues)   │
          └──────┬─────┘   └──────┬─────┘   └──────┬─────┘
                 │                │                │
                 └────────────────┼────────────────┘
                                  ▼
                    ┌───────────────────────────┐
                    │     FEATURE EXTRACTION    │
                    │  Transaction + Graph +    │
                    │   Behavioral Features     │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼                           ▼
            ┌─────────────┐             ┌─────────────┐
            │ Rule Engine │             │  ML Models  │
            │ (Heuristic) │             │ XGBoost/IF  │
            └──────┬──────┘             └──────┬──────┘
                   │                           │
                   └─────────────┬─────────────┘
                                 ▼
                     ┌────────────────────────┐
                     │    RISK SCORE ENGINE   │
                     │  0 ──────────────── 100│
                     └────────────┬───────────┘
                                  │
                     ┌────────────┴───────────┐
                     ▼                        ▼
              ┌─────────────┐          ┌─────────────┐
              │ Alert Engine│          │  SHAP / XAI │
              │  + Reports  │          │ Explanations│
              └──────┬──────┘          └──────┬──────┘
                     │                        │
                     └───────────┬────────────┘
                                 ▼
                       ┌──────────────────┐
                       │   FastAPI        │
                       │  REST + WS API   │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  React Dashboard │
                       ├──────────────────┤
                       │ • Risk Scores    │
                       │ • Graph Tracer   │
                       │ • Fund Flow      │
                       │ • Live Alerts    │
                       │ • Case Manager   │
                       │ • Report Export  │
                       └──────────────────┘
```

---

## 🕸️ Graph Analysis

### Fund Flow Tracing

ChainTrace builds a directed graph of all wallet-to-wallet transactions and traces the money forward using BFS:

```
(Victim)
    │
    │ 2.0 ETH
    ▼
(Scam Wallet)          ← Reported by victim
    │
    │ 1.95 ETH
    ▼
(Intermediate Wallet)  ← Hop 1 — flagged by velocity rule
    │
    │ 1.90 ETH
    ▼
(Aggregator)           ← Hop 2 — flagged by fan-in pattern
    │
    │ 1.85 ETH
    ▼
(Exchange Hot Wallet)  ← TARGET IDENTIFIED: Binance
                          Freeze request issued ✓
```

### Graph Schema (Neo4j)

```cypher
// Nodes
(:Wallet {address, label, risk_score, entity_type, first_seen, last_seen})
(:Exchange {name, address, kyc_required})
(:SmartContract {address, protocol, verified})

// Relationships
(:Wallet)-[:SENT {amount, token, timestamp, tx_hash}]->(:Wallet)
(:Wallet)-[:DEPOSITED_TO {amount, timestamp}]->(:Exchange)
(:Wallet)-[:INTERACTED_WITH]->(:SmartContract)
```

### Core Tracing Query

```cypher
MATCH path = (start:Wallet {address: $suspect})-[:SENT*1..6]->(end:Wallet)
WHERE end.label = 'EXCHANGE'
  AND ALL(r IN relationships(path) WHERE r.amount > 0.01)
RETURN path, length(path) AS hops,
       [r IN relationships(path) | r.amount] AS amounts
ORDER BY hops ASC
LIMIT 10
```

### Graph Algorithms (Neo4j GDS)

| Algorithm | Use Case |
|---|---|
| BFS / Variable-length paths | N-hop fund tracing |
| `shortestPath()` | Fastest route to exchange |
| PageRank | Wallet importance scoring |
| Louvain Community Detection | Fraud ring identification |
| Degree Analysis | Fan-in / fan-out behavior |

---

## 🔎 Fraud Detection Engine

4-layer detection — not a single model:

### Layer 1 — Rule-Based Detection

```python
RULES = [
    "interaction_with_known_malicious_wallet",
    "high_transaction_velocity",          # Funds forwarded within minutes
    "large_fan_in",                       # Many senders → one wallet
    "large_fan_out",                      # One wallet → many receivers
    "peel_chain_pattern",                 # Sent > 90% of received amount
    "rapid_fund_movement",                # < 10 min between receive → send
    "mixer_interaction",                  # Interacted with Tornado Cash etc.
    "excessive_hops",                     # > 5 intermediate wallets
    "round_tripping",                     # Funds cycle back to earlier wallet
]
```

### Layer 2 — Behavioral Feature Extraction

```python
FEATURES = {
    "transaction_frequency":     "Tx count per hour/day",
    "transaction_volume":        "Total value moved (ETH)",
    "average_transaction_value": "Mean tx size",
    "wallet_age":                "Days since first tx",
    "in_degree":                 "Number of unique senders",
    "out_degree":                "Number of unique receivers",
    "fund_velocity":             "Time between receive → send",
    "balance_ratio":             "total_sent / total_received",
    "min_time_between_tx":       "Fastest consecutive tx delay",
    "unique_counterparties":     "Distinct wallets interacted with",
}
```

### Layer 3 — Machine Learning

| Model | Type | Use Case |
|---|---|---|
| **XGBoost** | Supervised | Primary fraud classifier (trained on Elliptic) |
| **Random Forest** | Supervised | Baseline comparison |
| **Isolation Forest** | Unsupervised | Anomaly detection when labels unavailable |

### Layer 4 — Graph Neural Networks *(Advanced)*

```
PyTorch Geometric
├── GCN  — Graph Convolutional Networks
├── GAT  — Graph Attention Networks
└── GraphSAGE — Inductive node embedding
```

---

## 📊 Risk Scoring System

```
               ┌──────────────────┐
               │ Transaction Data │
               └────────┬─────────┘
                        ▼
            ┌───────────────────────┐
            │   Feature Extraction  │
            └───────────┬───────────┘
                        ▼
      ┌─────────────────┼─────────────────┐
      ▼                 ▼                 ▼
 Rule Engine       ML Model         Graph Position
 (max 40 pts)     (max 40 pts)      (max 20 pts)
      ▼                 ▼                 ▼
      └─────────────────┼─────────────────┘
                        ▼
                Risk Score Engine
                        ▼
                  0 ─────────── 100
```

| Score Range | Risk Level | Action |
|---|---|---|
| 🟢 **0 – 30** | LOW | Monitor |
| 🟡 **31 – 60** | MEDIUM | Flag for review |
| 🟠 **61 – 80** | HIGH | Escalate to analyst |
| 🔴 **81 – 100** | CRITICAL | Immediate alert + auto-report |

---

## 🧠 Explainable AI

Every risk score is accompanied by a human-readable explanation — critical for legal proceedings:

```
┌─────────────────────────────────────────────────┐
│  WALLET RISK REPORT                             │
│  Address: 0xAbCd...1234                         │
│                                                 │
│  Risk Score:  ████████████████████░░  91 / 100  │
│  Risk Level:  🔴 CRITICAL                       │
│                                                 │
│  Contributing Factors:                          │
│  ✓ Connected to 3 known suspicious wallets      │
│  ✓ 43 transactions within 10 minutes            │
│  ✓ Funds passed through 7 intermediate wallets  │
│  ✓ High fan-in behaviour detected               │
│  ✓ Funds reached a high-risk entity (Binance)   │
│                                                 │
│  SHAP Feature Importance:                       │
│  fund_velocity      ████████░░  0.82            │
│  number_of_hops     ██████░░░░  0.61            │
│  in_degree          █████░░░░░  0.54            │
│  wallet_age         ███░░░░░░░  0.31            │
└─────────────────────────────────────────────────┘
```

---

## ⚡ Real-Time Pipeline

```
New Blockchain Transaction
          ▼
    Event Listener (Alchemy WebSocket)
          ▼
     Redis Queue
          ▼
 Celery Transaction Processor
          ▼
 Feature Extraction + Fraud Detection
          ▼
 Risk Score Computation
          ▼
 Alert Generation
          ▼
 WebSocket Push → Investigator Dashboard 🖥️
```

---

## 🌐 API Reference

### REST Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/investigate` | Submit a wallet for investigation |
| `GET` | `/api/wallet/{address}` | Get wallet details & entity labels |
| `GET` | `/api/wallet/{address}/transactions` | Get full transaction history |
| `GET` | `/api/wallet/{address}/graph` | Get fund-flow graph (Cytoscape format) |
| `GET` | `/api/wallet/{address}/risk` | Get risk score + SHAP explanation |
| `GET` | `/api/wallet/{address}/alerts` | Get alerts for a wallet |
| `POST` | `/api/report` | Submit a victim report |
| `GET` | `/api/investigations` | List all investigations |
| `GET` | `/api/investigations/{id}` | Get investigation details |
| `GET` | `/api/investigations/{id}/report` | Download PDF report |
| `GET` | `/api/alerts` | List all triggered alerts |
| `GET` | `/api/health` | Service health check |

### WebSocket

```
ws://host/ws/investigations/{id}
```

| Event | Description |
|---|---|
| `status_update` | Investigation progress (INGESTING → TRACING → COMPLETED) |
| `new_transaction` | Watched wallet moved funds |
| `risk_score_updated` | Score recalculated |
| `alert_triggered` | Fraud pattern detected |
| `exchange_identified` | Destination exchange found |

---

## 🗄️ Database Design

### Relational (SQLite / PostgreSQL)

```
Users ──────────────── Investigations
  │                         │
  └── Roles (RBAC)          ├── WalletRisk (scores + SHAP reasons)
                            ├── Alerts
                            └── WalletReports (victim submissions)
```

### Graph (Neo4j)

```
(:Wallet)-[:SENT {amount, token, tx_hash, timestamp}]->(:Wallet)
(:Wallet)-[:DEPOSITED_TO]->(:Exchange)
(:Wallet)-[:INTERACTED_WITH]->(:SmartContract)
```

### Cache (Redis)

| Key Pattern | Purpose |
|---|---|
| `wallet:risk:{address}` | Cached risk scores (TTL: 5min) |
| `celery:tasks:*` | Background task queue |
| `ws:room:{investigation_id}` | WebSocket pub/sub channel |
| `rate:limit:{ip}` | API rate limiting |

---

## 🕵️ Address Intelligence

Built-in database of known blockchain entities:

| Entity Type | Examples |
|---|---|
| `EXCHANGE` | Binance, WazirX, Coinbase, Kraken |
| `MIXER` | Tornado Cash, ChipMixer |
| `SCAM` | Known phishing / investment scam wallets |
| `RANSOMWARE` | Identified ransomware collection addresses |
| `BRIDGE` | Cross-chain bridge contracts |
| `SANCTIONED` | OFAC-sanctioned wallets |

**Sources:** Etherscan Label Cloud, CryptoScamDB, Bitcoin Abuse DB, OFAC Sanctions List, Manual OSINT

---

## 🔐 Security

| Feature | Implementation |
|---|---|
| Authentication | JWT tokens |
| Authorization | Role-Based Access Control (RBAC) |
| Roles | `ADMIN`, `INVESTIGATOR`, `ANALYST`, `VIEWER` |
| Password storage | bcrypt hashing |
| API protection | Rate limiting (Redis), input validation (Pydantic) |
| Data security | HTTPS, CORS, SQL injection protection (ORM), audit logging |
| Secrets | Environment variables (`.env`) |

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.12+
Docker & Docker Compose
Alchemy or Etherscan API Key
```

### Quick Start

```bash
# 1. Clone
git clone https://github.com/blockies/chaintrace.git
cd chaintrace

# 2. Start infrastructure
docker-compose up -d

# 3. Backend setup
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # Add your API keys

# 4. Run
uvicorn api.main:app --reload --port 8000

# 5. Open
# API Docs:  http://localhost:8000/docs
# Neo4j:     http://localhost:7474
# Dashboard: http://localhost:3000
```

### Environment Variables

```env
# Blockchain
ALCHEMY_API_KEY=your_alchemy_key
ETHERSCAN_API_KEY=your_etherscan_key

# Databases
DATABASE_URL=sqlite:///./chaintrace.db
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your_super_secret_key
```

---

## 🐳 Docker Deployment

```bash
docker-compose up -d

# Services:
# ├── backend       → http://localhost:8000
# ├── frontend      → http://localhost:3000
# ├── neo4j         → http://localhost:7474
# ├── redis         → localhost:6379
# ├── celery        → Background worker
# └── flower        → http://localhost:5555 (task monitoring)
```

---

## 🔮 Future Scope

| Enhancement | Description |
|---|---|
| 🌐 Multi-chain support | Bitcoin, Tron (USDT-TRC20), Solana |
| 🧬 Graph Neural Networks | GCN/GAT for advanced pattern detection |
| 🤝 I4C Integration | Direct API integration with NCRP portal |
| 📱 Mobile app | Field investigator mobile interface |
| 🔄 Cross-chain tracing | Track funds across bridge protocols |
| 📡 Mempool monitoring | Detect fraud before transactions confirm |

---

## 📖 Open Source References

ChainTrace builds on ideas from the following open-source tools:

| Project | Author | What we learned / adapted |
|---------|--------|---------------------------|
| [**Orbit**](https://github.com/s0md3v/Orbit) | s0md3v | Recursive wallet crawling strategy — adapted into `ingestion/recursive_fetch.py` for multi-hop transaction ingestion |
| [**BlockTracker**](https://github.com/thisiskeanyvy/blocktracker) | thisiskeanyvy | Transaction tree-climbing algorithm + probability scoring on traced paths — adapted into `graph/tracer.py` for bidirectional fund tracing |

> Both tools are MIT/open-source licensed. We use their **algorithmic concepts** as a reference, not their code directly. Our implementation is purpose-built for Neo4j, Etherscan, and the SIH investigation pipeline.

---

## 🧱 Team Blockies

<div align="center">

| Member | Role |
|--------|------|
| **Hanin** | Blockchain Ingestion (Web3.py, Etherscan, Orbit) |
| **Pranav** | Graph Engine (Neo4j, BFS Tracer, BlockTracker) |
| **James** | ML / AI (XGBoost, SHAP, Elliptic) + PPT |
| **Neeraj** | Backend API (FastAPI, SQLAlchemy) |
| **Super** | Rule Engine & Address Intelligence |
| **Savio** | Infrastructure (Docker, Redis, Celery) |

**Smart India Hackathon 2026** &nbsp;|&nbsp; **Ministry of Home Affairs** &nbsp;|&nbsp; **I4C, CIS Division**

</div>

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by Team Blockies 🧱**

*Tracing fraud, one block at a time. ⛓️*

[![GitHub](https://img.shields.io/badge/GitHub-Team_Blockies-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/blockies)

</div>
