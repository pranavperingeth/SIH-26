<div align="center">

# 🔗 ChainTrace
### *Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges*

<br/>

> Built by **Team Blockies** 🧱 for **Smart India Hackathon 2026**
> 
> Problem Statement ID: **26183** &nbsp;|&nbsp; Organization: **Ministry of Home Affairs** &nbsp;|&nbsp; Department: **I4C, CIS Division**

<br/>

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Ethereum](https://img.shields.io/badge/Ethereum-EVM-3C3C3D?style=for-the-badge&logo=ethereum&logoColor=white)](https://ethereum.org)

<br/>

[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-GNN-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)

<br/>

![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active_Development-yellow?style=flat-square)
![Blockchain](https://img.shields.io/badge/Blockchain-Ethereum%20%7C%20EVM-blueviolet?style=flat-square)
![Theme](https://img.shields.io/badge/Theme-Blockchain_%26_Cybersecurity-orange?style=flat-square)

</div>

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Our Solution](#-our-solution)
- [Team Blockies](#-team-blockies)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Fraud Detection Engine](#-fraud-detection-engine)
- [Risk Scoring System](#-risk-scoring-system)
- [API Reference](#-api-reference)
- [Real-Time Pipeline](#-real-time-pipeline)
- [Database Design](#-database-design)
- [Security](#-security)
- [Development Roadmap](#-development-roadmap)
- [Getting Started](#-getting-started)
- [Docker Deployment](#-docker-deployment)
- [Contributing](#-contributing)

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

**The Challenge:** During investigations, reported wallets are often intermediary hops in a complex money-laundering chain, making it extremely difficult to identify the final exchange where funds are cashed out — and serve a legal freeze request.

---

## 💡 Our Solution

**ChainTrace** is a real-time blockchain analytics platform that:

1. 🔍 **Ingests** suspect wallet addresses reported by victims
2. 🕸️ **Traces** fund flows through N-hop graph traversal
3. 🧠 **Detects** fraud patterns using ML + rule-based engines
4. 🏦 **Identifies** the final cryptocurrency exchange receiving funds
5. 📊 **Scores** risk from 0–100 with Explainable AI (SHAP)
6. ⚡ **Alerts** investigators in real-time via WebSocket dashboard
7. 📄 **Generates** law-enforcement-ready reports automatically

---

## 🧱 Team Blockies

<div align="center">

| Member | Role |
|--------|------|
| [Add member] | Team Lead / Blockchain Engineer |
| [Add member] | ML / Data Science |
| [Add member] | Backend Engineer |
| [Add member] | Frontend / UI |
| [Add member] | DevOps / Security |
| [Add member] | Research / Analytics |

**Team Name:** `Blockies` &nbsp;|&nbsp; **SIH 2026**

</div>

---

## 🛠️ Tech Stack

### 🎨 Frontend

| Technology | Purpose | Badge |
|---|---|---|
| React 18 | Investigator Dashboard UI | ![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black) |
| TypeScript 5 | Type-safe frontend development | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white) |
| Vite | Build tooling & HMR | ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white) |
| Tailwind CSS | Utility-first UI styling | ![Tailwind](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white) |
| Cytoscape.js | Interactive graph visualization | ![Cytoscape](https://img.shields.io/badge/Cytoscape.js-F7A800?style=flat-square) |
| Recharts | Analytics charts | ![Recharts](https://img.shields.io/badge/Recharts-22B5BF?style=flat-square) |
| Axios | REST API communication | ![Axios](https://img.shields.io/badge/Axios-5A29E4?style=flat-square&logo=axios&logoColor=white) |

### ⚙️ Backend

| Technology | Purpose | Badge |
|---|---|---|
| Python 3.12+ | Core backend & analytics | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| FastAPI | REST API & WebSocket server | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) |
| Pydantic v2 | Request/response validation | ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white) |
| SQLAlchemy | Database ORM | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square) |
| Uvicorn | ASGI server | ![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=flat-square) |
| Celery | Background task processing | ![Celery](https://img.shields.io/badge/Celery-37814A?style=flat-square&logo=celery&logoColor=white) |
| Redis | Cache, queue & pub/sub | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white) |

### ⛓️ Blockchain Integration

**Initial Network Support:**

![Ethereum](https://img.shields.io/badge/Ethereum-3C3C3D?style=for-the-badge&logo=ethereum&logoColor=white)
![BNB Chain](https://img.shields.io/badge/BNB_Smart_Chain-F0B90B?style=for-the-badge&logo=binance&logoColor=black)
![Polygon](https://img.shields.io/badge/Polygon-8247E5?style=for-the-badge&logo=polygon&logoColor=white)

**Future Support:**

![Bitcoin](https://img.shields.io/badge/Bitcoin-F7931A?style=flat-square&logo=bitcoin&logoColor=white)
![Tron](https://img.shields.io/badge/Tron-FF0013?style=flat-square&logo=tron&logoColor=white)
![Solana](https://img.shields.io/badge/Solana-9945FF?style=flat-square&logo=solana&logoColor=white)

**Data Providers:**

[![Alchemy](https://img.shields.io/badge/Alchemy-363FF9?style=flat-square&logo=alchemy&logoColor=white)](https://alchemy.com)
[![Infura](https://img.shields.io/badge/Infura-FF6B2B?style=flat-square)](https://infura.io)
[![Etherscan](https://img.shields.io/badge/Etherscan_API-21325B?style=flat-square)](https://etherscan.io/apis)
[![QuickNode](https://img.shields.io/badge/QuickNode-4590F7?style=flat-square)](https://quicknode.com)

| Library | Purpose |
|---|---|
| `web3.py` | EVM blockchain interaction |
| `ethers.js` | Frontend blockchain interaction |
| `ABI decoding` | Smart contract event parsing |
| `JSON-RPC` | Direct node communication |

### 🗄️ Databases

| Database | Purpose | Badge |
|---|---|---|
| PostgreSQL 16 | Primary relational store (users, cases, alerts) | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) |
| Neo4j | Graph DB for wallet relationships & fund flow | ![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=flat-square&logo=neo4j&logoColor=white) |
| Redis 7 | Caching, task queues, real-time pub/sub | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white) |

### 🧪 ML & Data Science

| Library | Purpose | Badge |
|---|---|---|
| PyTorch | Deep learning & GNN | ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white) |
| PyTorch Geometric | Graph neural networks | ![PyG](https://img.shields.io/badge/PyG-3C2179?style=flat-square&logo=pytorch&logoColor=white) |
| scikit-learn | Classical ML models | ![sklearn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white) |
| XGBoost | Gradient boosted trees | ![XGBoost](https://img.shields.io/badge/XGBoost-189BCC?style=flat-square) |
| SHAP | Explainable AI | ![SHAP](https://img.shields.io/badge/SHAP-FF6B6B?style=flat-square) |
| NetworkX | Graph algorithms & analysis | ![NetworkX](https://img.shields.io/badge/NetworkX-orange?style=flat-square) |
| Pandas / NumPy | Data processing | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) |

---

## 🏗️ System Architecture

```
                         ┌─────────────────────┐
                         │     BLOCKCHAINS      │
                         │  Ethereum / EVM      │
                         └──────────┬──────────┘
                                    │
                              RPC / APIs
                            (Alchemy/Infura)
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │   BLOCKCHAIN INGESTION    │
                    │    Web3.py / JSON-RPC     │
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
          │ PostgreSQL │   │   Neo4j    │   │   Redis    │
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
                ┌─────────────────┼──────────────────┐
                ▼                 ▼                  ▼
        ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
        │ Rule Engine │   │  ML Models  │   │ GNN Models  │
        │ (Heuristic) │   │ XGBoost/RF  │   │  GCN / GAT  │
        └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
               │                 │                  │
               └─────────────────┼──────────────────┘
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
              │  (I4C LEA)  │          │ Explanations│
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

### 📦 Data Ingestion Pipeline

```
Blockchain
    ↓
RPC / Blockchain API
    ↓
Data Ingestion Service
    ↓
Transaction Normalization
    ↓
Transaction Database
    ↓
Graph Construction
    ↓
Fraud Detection Engine
```

**Fields captured per transaction:**

| Field | Description |
|---|---|
| `wallet_address` | Sender / receiver address |
| `transaction_hash` | Unique tx identifier |
| `from_address` | Originating wallet |
| `to_address` | Destination wallet |
| `amount` | Value transferred |
| `token` | ETH / ERC-20 token |
| `block_number` | Chain block height |
| `timestamp` | Block timestamp |
| `gas_info` | Gas used, gas price |
| `contract_interactions` | Smart contract calls |
| `erc20_transfers` | Token transfer events |
| `tx_status` | Success / Reverted |

---

## 🕸️ Graph Analysis

### Fund Flow Graph Model

```
(Victim)
    │
    │ transfer
    ▼
(Scam Wallet)          ← Reported by victim
    │
    ▼
(Intermediate Wallet)  ← Hop 1
    │
    ▼
(Aggregator)           ← Hop 2  — Clustering heuristic
    │
    ▼
(Exchange Hot Wallet)  ← TARGET — Freeze request sent here
```

### Graph Schema (Neo4j / Cypher)

```cypher
// Nodes
(:Wallet {address, label, risk_score, entity_type})
(:Exchange {name, address, kyc_required})
(:SmartContract {address, protocol, verified})

// Relationships
(:Wallet)-[:SENT {amount, token, timestamp, tx_hash}]->(:Wallet)
(:Wallet)-[:DEPOSITED_TO {amount, timestamp}]->(:Exchange)
(:Wallet)-[:INTERACTED_WITH]->(:SmartContract)
```

### Graph Algorithms Deployed

| Algorithm | Use Case |
|---|---|
| BFS / DFS | N-hop fund tracing |
| Shortest Path | Fastest route to exchange |
| Connected Components | Cluster detection |
| Degree Analysis | Fan-in / fan-out behavior |
| PageRank | Wallet importance scoring |
| Community Detection | Organized fraud ring identification |

---

## 🔎 Fraud Detection Engine

The system uses **4 layered detection**, not a single model:

### Layer 1 — Rule-Based Detection

```python
RULES = [
    "interaction_with_known_malicious_wallet",
    "high_transaction_velocity",          # > N tx/hour
    "unusual_transaction_volume",
    "large_fan_in",                       # Many senders → one wallet
    "large_fan_out",                      # One wallet → many receivers
    "rapid_fund_movement",                # < 10 min between receive → send
    "excessive_hops",                     # > 5 intermediate wallets
    "suspicious_fund_flow_pattern",
    "interaction_with_known_high_risk_entity",
]
```

### Layer 2 — Behavioral Feature Extraction

```python
BEHAVIORAL_FEATURES = {
    "transaction_frequency":     "Tx count per hour/day",
    "transaction_volume":        "Total USD value moved",
    "average_transaction_value": "Mean tx size",
    "wallet_age":                "Days since first tx",
    "in_degree":                 "Number of unique senders",
    "out_degree":                "Number of unique receivers",
    "unique_counterparties":     "Distinct wallets interacted with",
    "fund_velocity":             "Time between receive → send",
    "number_of_hops":            "Graph depth from victim",
    "time_between_transactions": "Average inter-tx delay",
}
```

### Layer 3 — Machine Learning Models

| Model | Type | Use Case |
|---|---|---|
| **Random Forest** | Supervised | Classification with labeled data |
| **XGBoost** | Supervised | High-performance gradient boosting |
| **LightGBM** | Supervised | Fast large-scale training |
| **Isolation Forest** | Unsupervised | Anomaly detection (no labels needed) |
| **Logistic Regression** | Supervised | Interpretable baseline |

> **Supervised** when labeled fraud data is available — **Unsupervised/Anomaly** when labels are scarce.

### Layer 4 — Graph Neural Networks *(Advanced)*

```
PyTorch Geometric
├── GCN  — Graph Convolutional Networks
├── GAT  — Graph Attention Networks  
└── GraphSAGE — Inductive node embedding

Tasks:
├── Node Classification  → Is this wallet malicious?
├── Edge Classification  → Is this transaction fraudulent?
└── Graph Embeddings     → Wallet fingerprinting
```

> ⚠️ GNN is an **advanced enhancement**. The system is fully functional without it.

---

## 🧠 Explainable AI

Every risk score is accompanied by a human-readable explanation:

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

**Technology:** [SHAP](https://shap.readthedocs.io) + custom rule-narrative generator

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
 Rule Engine       ML Model         Graph Analysis
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

## ⚡ Real-Time Processing Pipeline

```
New Blockchain Transaction
          ▼
    Event Listener
    (WebSocket RPC)
          ▼
     Redis Queue
          ▼
 Celery Transaction Processor
          ▼
 Feature Extraction
          ▼
 Fraud Detection Engine
          ▼
 Risk Score Computation
          ▼
 Alert Generation
          ▼
 WebSocket Push
          ▼
 Investigator Dashboard 🖥️
```

> **Note:** Apache Kafka is optional. For the SIH prototype, **Redis + Celery + AsyncIO** is sufficient for real-time processing.

---

## 🌐 API Reference

### REST Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/investigate` | Submit wallet for investigation |
| `GET` | `/api/wallet/{address}` | Get wallet details & labels |
| `GET` | `/api/wallet/{address}/transactions` | Get transaction history |
| `GET` | `/api/wallet/{address}/graph` | Get fund-flow graph data |
| `GET` | `/api/wallet/{address}/risk` | Get risk score & explanation |
| `GET` | `/api/wallet/{address}/alerts` | Get alerts for wallet |
| `POST` | `/api/report` | Submit victim report |
| `GET` | `/api/investigations` | List all investigations |
| `GET` | `/api/investigations/{id}` | Get investigation details |
| `GET` | `/api/health` | Service health check |

### WebSocket

```
ws://host/ws/investigations/{id}
```

Real-time events pushed to the dashboard:

| Event | Description |
|---|---|
| `new_transaction` | New on-chain transaction detected |
| `risk_score_updated` | Risk score recalculated |
| `alert_triggered` | Fraud pattern detected |
| `graph_updated` | New wallet hop discovered |
| `exchange_identified` | Fund destination exchange found |

---

## 🗄️ Database Design

### PostgreSQL Schema

```
Users ──────────────── Investigations
  │                         │
  └── Roles (RBAC)          ├── ReportedWallets
                            ├── Transactions
                            ├── RiskScores
                            ├── Alerts
                            └── CaseHistory
```

### Neo4j Graph Schema

```
Wallets ──[SENT]──▶ Wallets
Wallets ──[DEPOSITED_TO]──▶ Exchanges
Wallets ──[INTERACTED_WITH]──▶ SmartContracts
Wallets ──[HOLDS]──▶ Tokens
```

### Redis Usage

| Key Pattern | Purpose |
|---|---|
| `wallet:risk:{address}` | Cached risk scores (TTL: 5min) |
| `celery:tasks:*` | Background task queue |
| `ws:room:{investigation_id}` | WebSocket pub/sub channel |
| `rate:limit:{ip}` | API rate limiting |
| `tx:pending:{hash}` | Pending tx temporary store |

---

## 🕵️ Address Intelligence Database

The system maintains an internal intelligence database:

```python
class AddressLabel(BaseModel):
    address: str
    entity_type: EntityType     # SCAM | PHISHING | RANSOMWARE |
                                # EXCHANGE | MIXER | BRIDGE |
                                # GAMBLING | UNKNOWN
    risk_level: RiskLevel       # LOW | MEDIUM | HIGH | CRITICAL
    source: str                 # "I4C" | "CryptoScamDB" | "Manual"
    confidence: float           # 0.0 – 1.0
    first_seen: datetime
    last_seen: datetime
```

---

## 🔐 Security

### Authentication & Authorization

```
JWT (JSON Web Tokens)
OAuth 2.0 (where applicable)
Role-Based Access Control (RBAC)
```

### RBAC Roles

| Role | Permissions |
|---|---|
| `ADMIN` | Full system access, user management |
| `INVESTIGATOR` | Create/manage cases, view all data |
| `ANALYST` | Run ML models, view risk reports |
| `VIEWER` | Read-only access to reports |

### Security Checklist

- [x] HTTPS enforced
- [x] Passwords hashed (bcrypt)
- [x] API key authentication
- [x] Rate limiting (Redis-backed)
- [x] Input validation (Pydantic)
- [x] SQL injection protection (SQLAlchemy ORM)
- [x] CORS configuration
- [x] Secrets in environment variables (`.env`)
- [x] Audit logging for all state changes
- [x] XSS prevention

---

## 🧪 Testing

### Backend Testing

```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Testing

```bash
npm run test          # Vitest
npm run test:coverage # Coverage report
```

### API Testing

```bash
# Swagger UI available at:
http://localhost:8000/docs

# ReDoc at:
http://localhost:8000/redoc
```

### Load Testing *(Optional)*

```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

---

## 🗺️ Development Roadmap

```
Phase 1 ✅  Ethereum + Web3.py integration
     ↓
Phase 2 ✅  FastAPI backend skeleton
     ↓
Phase 3 🔄  PostgreSQL schema & migrations
     ↓
Phase 4 🔄  Transaction ingestion pipeline
     ↓
Phase 5 ⬜  Neo4j graph construction
     ↓
Phase 6 ⬜  BFS-based fund tracing
     ↓
Phase 7 ⬜  Rule-based risk scoring
     ↓
Phase 8 ⬜  React investigator dashboard
     ↓
Phase 9 ⬜  Real-time WebSocket monitoring
     ↓
Phase 10 ⬜  ML anomaly detection
     ↓
Phase 11 ⬜  Explainable AI (SHAP)
     ↓
Phase 12 ⬜  Graph Neural Networks (GNN)
```

> **The MVP works without ML/GNN.** ML components enhance an already-functional investigation pipeline — they are not the foundation.

---

## 🚀 Getting Started

### Prerequisites

```bash
# Required
Python 3.12+
Node.js 20+
Docker & Docker Compose
PostgreSQL 16
Neo4j 5
Redis 7

# Blockchain API Key (any one)
Alchemy / Infura / QuickNode API Key
```

### Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/blockies/chaintrace.git
cd chaintrace

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys and DB credentials

# 4. Run database migrations
alembic upgrade head

# 5. Start backend
uvicorn app.main:app --reload --port 8000

# 6. Frontend setup (new terminal)
cd ../frontend
npm install
npm run dev
```

### Environment Variables

```env
# Blockchain
ALCHEMY_API_KEY=your_alchemy_key
ETHERSCAN_API_KEY=your_etherscan_key

# Databases
DATABASE_URL=postgresql://user:password@localhost:5432/chaintrace
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
ENVIRONMENT=development
DEBUG=true
```

---

## 🐳 Docker Deployment

```bash
# Start all services
docker-compose up -d

# Services started:
# ├── frontend     → http://localhost:3000
# ├── backend      → http://localhost:8000
# ├── postgres     → localhost:5432
# ├── neo4j        → http://localhost:7474
# ├── redis        → localhost:6379
# └── ml-service   → http://localhost:8001
```

### `docker-compose.yml` Services

```yaml
services:
  frontend:    # React + Vite
  backend:     # FastAPI + Uvicorn
  postgres:    # PostgreSQL 16
  neo4j:       # Neo4j 5
  redis:       # Redis 7
  ml-service:  # Python ML microservice
  celery:      # Background task worker
```

---

## 🤝 Contributing

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name

# 2. Make your changes

# 3. Run tests
pytest && npm run test

# 4. Commit
git commit -m "feat: your feature description"

# 5. Push and open PR
git push origin feature/your-feature-name
```

### Commit Convention

```
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
style:    Formatting changes
refactor: Code restructuring
test:     Adding tests
chore:    Build/tooling changes
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by Team Blockies 🧱**

*Smart India Hackathon 2026 | Ministry of Home Affairs | I4C, CIS Division*

---

[![GitHub](https://img.shields.io/badge/GitHub-Team_Blockies-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/blockies)

*Tracing fraud, one block at a time. ⛓️*

</div>
