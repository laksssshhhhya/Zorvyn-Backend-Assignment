# Zorvyn Finance Data & Access Control Backend

## Architecture of Trust

Financial systems require absolute precision and unassailable historical records. This backend rejects the anti-pattern of storing floating balances in single database columns. Instead, it implements a strict **Double-Entry Ledger**. Every financial state is a derived consequence of an immutable, self-balancing history of debits and credits. This guarantees that balances are always mathematically reconciled and immune to anomalous single-sided updates.

## Core Features

- **User & Role Governance:** Access control is enforced via a strict Role-Based Access Control (RBAC) model ensuring the **Principle of Least Privilege**.
  - *Admins* possess unrestricted visibility, including raw system audit trails.
  - *Analysts* are permitted to explicitly record transactions and query live metrics.
  - *Viewers* are highly restricted, limited solely to safe read operations against aggregated data.
- **The Ledger System:** Modeled precisely around standard accounting concepts. A parent `Transaction` entity cleanly routes to self-balancing `LedgerEntry` records targeting specific `Account` targets.
- **Intelligent Dashboards:** Summary endpoints bypass inefficient Python-side loops, directly leveraging database-layer SQL aggregations against the ledger table to instantly calculate real-time **Net Balance** and an expense-tracked **Burn Rate**.

## Defensive Engineering & Compliance

- **Immutable Audit Trail:** Engineered for SOC 2 and ISO 27001 readiness. Every state-mutating request automatically logs the invoker's identity, the target entity, the precise action taken, and a payload of the details. This system history is strictly append-only.
- **Precision Guardrails:** Floating-point approximations are explicitly disallowed. The system enforces strongly-typed `Decimal` representations for all currency operations, coupled with strict Pydantic payload validation to reject malformed inbound data and eliminate structural rounding errors.

## Assumptions & Trade-offs

During system architecture, specific technical trade-offs were made to optimize for review clarity:
1. **Flat Hierarchy for Review Velocity:** The business logic, database schemas, and API routes are strictly segregated across a flat, 4-file structure within the root directory rather than buried across a complex layered service architecture.
2. **Simplified RBAC Injection:** Full JWT authentication was simulated. Strict header-based auth (`X-User-Role`) is utilized to enforce identical dependency injection mechanisms while allowing engineering counterparts to trivially swap user contexts via browser tooling.
3. **Zero-Config Portability:** SQLite serves as the underlying persistence layer. This provides an embedded database format, allowing the entire application to boot dynamically without requiring reviewers to provision PostgreSQL or handle local Docker networking.

## 3-Step Quick Start

This artifact requires zero external infrastructure configurations. Assuming a standard Python environment is present, any reviewer can spin up the application in seconds.

**1. Install Core Dependencies**
```bash
pip install fastapi uvicorn sqlmodel
```

**2. Boot the Server**
```bash
uvicorn main:app --reload
```

**3. Explore the API Interactively**
Navigate to [http://localhost:8000/docs](http://localhost:8000/docs). 
The interactive Swagger interface will explicitly map out the endpoints. To cleanly authenticate your requests, simply provide a valid internal role (`Admin`, `Analyst`, `Viewer`) when queried. Database scheme generation handles itself silently upon application boot.
