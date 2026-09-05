# 🛡️ AegisLake: Governed Lakehouse Orchestration Mesh

> Decoupling enterprise prompt engineering and compliance rules into first-class Unity Catalog assets with automated CI/CD PR gating and a native Databricks App management portal.

---

## 🏗️ Architectural Overview

```
```
aegislake-governed-mesh/assets/Architecture.png

```

---
## 🖥️ Live Databricks App UI & Control Center

Hosted natively on Databricks Apps, enabling platform architects to monitor real-time compliance and execute zero-downtime policy hot-swaps.

### 1. Catalog Skill Registry
Enforcing governance rules as catalog securables with active Model Context Protocol (MCP) bridges.
![Catalog Skill Registry](assets/01_catalog_skill_registry.png)

### 2. CI/CD Automated PR Gatekeeper Feed
Live audit stream recording bot decisions and blocking PRs violating PII or performance directives.
![PR Audit Feed](assets/02_pr_audit_logs.png)

### 3. Dynamic Zero-Downtime Policy Hot-Swap
Modifying Lakehouse directives centrally and propagating updates across coding agents instantly.
![Dynamic Policy Hot-Swap](assets/03_dynamic_policy_hotswap.png)

---

## 🔍 End-to-End Medallion Governance Inspector

### 4. Bronze Layer (Raw & Unprocessed)
Raw ingestion batches with source lineage timestamps and unmasked identifiers:
![Bronze Layer](assets/04_lakehouse_bronze_layer_inspector.png)

### 5. Silver Layer (Deduplication & Dynamic PII Masking)
Idempotent Delta Lake `MERGE INTO` with dynamic masking applied to sensitive identifiers:
![Silver Layer](assets/05_lakehouse_silver_layer_inspector.png)

### 6. Gold Layer (Liquid Clustered Aggregations)
Aggregated business KPIs clustered by region (`CLUSTER BY region_id`) with lineage stamps:
![Gold Layer](assets/06_lakehouse_gold_layer_inspector.png)

---

## 🛠️ Tech Stack
* **Lakehouse Engine:** Databricks, Delta Lake (Liquid Clustering, Delta MERGE), PySpark
* **Application Layer:** Databricks Apps, Streamlit, Python 3.10
* **Governance & Security:** Unity Catalog Securables, RBAC, Dynamic PII Masking
* **CI/CD & Agentic Ops:** GitHub Actions, Model Context Protocol (MCP)
* **Orchestration:** Databricks Workflows (Daily Scheduled Jobs with Automated Retries)
