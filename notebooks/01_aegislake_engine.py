# Databricks notebook source
# DBTITLE 1,Cell 1
# Write the Skill Rulebook
rule_payload = """# Enterprise Governed Skill: AegisLake Medallion & Orchestration Policy
# Asset ID: enterprise_dw.governance.skill_gold_pipeline_orchestration

[Directives]
1. Bronze Layer (Raw):
   - Append-only. Must record ingestion metadata: `_ingest_time` (TIMESTAMP) and `_source_file` (STRING).
2. Silver Layer (Cleansed & Enriched):
   - Deduplicated on business primary keys using Delta Lake `MERGE INTO`.
   - Dynamic PII Masking: Customer names must be masked using `CONCAT(LEFT(customer_name, 2), '****')`.
3. Gold Layer (Curated & Aggregated):
   - Liquid Clustering: Mandatory `CLUSTER BY (region_id)`.
   - Audit Stamps: Must append `CURRENT_TIMESTAMP() AS _created_at`.
4. Orchestration Standard:
   - Failure tolerance: Minimum 3 retries with 60-second backoff.
   - Security: secureInput=true, secureOutput=true.
"""

dbutils.fs.put("/Volumes/aegis_fraud_workspace/fraud_surveillance_lake/raw_landing/aegislake_rules.md", rule_payload, overwrite=True)
print("✅ Cell 1: Governance rulebook successfully persisted to DBFS.")

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE DATABASE IF NOT EXISTS governance_mesh;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE governance_mesh.catalog_skills (
# MAGIC     skill_id STRING,
# MAGIC     skill_name STRING,
# MAGIC     storage_path STRING,
# MAGIC     allowed_roles ARRAY<STRING>,
# MAGIC     compliance_tier STRING,
# MAGIC     updated_at TIMESTAMP
# MAGIC ) USING DELTA;
# MAGIC
# MAGIC INSERT INTO governance_mesh.catalog_skills VALUES
# MAGIC (
# MAGIC   'SKILL_001',
# MAGIC   'aegislake_medallion_policy',
# MAGIC   '/FileStore/skills/aegislake_rules.md',
# MAGIC   ARRAY('senior_de', 'lead_architect', 'data_engineer'),
# MAGIC   'tier_1_pci_gdpr',
# MAGIC   CURRENT_TIMESTAMP()
# MAGIC );
# MAGIC
# MAGIC SELECT * FROM governance_mesh.catalog_skills;

# COMMAND ----------

# DBTITLE 1,Cell 3
# Emulate MCP Dynamic Retrieval with Access Control
def mcp_fetch_governed_skill(skill_name: str, current_user_role: str) -> str:
    catalog_df = spark.table("governance_mesh.catalog_skills").filter(f"skill_name = '{skill_name}'")
    
    if catalog_df.count() == 0:
        return f"ERROR: Skill '{skill_name}' not found."
    
    row = catalog_df.first()
    allowed_roles = row["allowed_roles"]
    
    if current_user_role not in allowed_roles:
        return f"❌ ACCESS_DENIED: Role '{current_user_role}' lacks EXECUTE privilege on '{skill_name}'."
    
    file_path = row["storage_path"]
    if file_path == "/FileStore/skills/aegislake_rules.md":
        file_path = "/Volumes/aegis_fraud_workspace/fraud_surveillance_lake/raw_landing/aegislake_rules.md"
    rules = dbutils.fs.head(file_path)
    return f"🔓 AUTHORIZED:\n\n{rules}"

# Verification
print(mcp_fetch_governed_skill("aegislake_medallion_policy", current_user_role="data_engineer"))
print(mcp_fetch_governed_skill("aegislake_medallion_policy", current_user_role="guest_contractor"))

# COMMAND ----------

# Automated CI/CD Review Engine
def aegislake_pr_gatekeeper(pr_id: str, author: str, target_layer: str, sql_diff: str) -> bool:
    print("=" * 70)
    print(f"🤖 AUDITING PULL REQUEST: [{pr_id}] by @{author} | TARGET: [{target_layer.upper()}]")
    print("=" * 70)
    
    violations = []
    sql_upper = sql_diff.upper()
    sql_lower = sql_diff.lower()
    
    if target_layer.lower() == "bronze":
        if "_ingest_time" not in sql_lower or "_source_file" not in sql_lower:
            violations.append("Bronze Directive Failed: Missing `_ingest_time` or `_source_file`.")
    elif target_layer.lower() == "silver":
        if "MERGE INTO" not in sql_upper:
            violations.append("Silver Directive Failed: Missing Delta `MERGE INTO` deduplication.")
        if "****" not in sql_diff:
            violations.append("Silver Directive Failed: PII exposed! Missing dynamic masking ('****').")
    elif target_layer.lower() == "gold":
        if "CLUSTER BY" not in sql_upper:
            violations.append("Gold Directive Failed: Missing Liquid Clustering `CLUSTER BY (region_id)`.")
        if "_created_at" not in sql_lower:
            violations.append("Gold Directive Failed: Missing mandatory audit column `_created_at`.")
            
    if violations:
        print("❌ STATUS: REJECTED (MERGE BLOCKED)")
        for v in violations:
            print(f"  🔴 {v}")
        print("=" * 70 + "\n")
        return False
    else:
        print("✅ STATUS: APPROVED (100% Policy Adherence)")
        print("=" * 70 + "\n")
        return True

# Test Scenarios
bad_silver_sql = "CREATE TABLE silver.orders AS SELECT order_id, customer_name FROM bronze.orders;"
good_gold_sql = """
CREATE OR REPLACE TABLE enterprise_gold.sales_kpis
CLUSTER BY (region_id) AS
SELECT region_id, COUNT(order_id) AS orders, CURRENT_TIMESTAMP() AS _created_at
FROM enterprise_silver.orders GROUP BY region_id;
"""

aegislake_pr_gatekeeper("PR-101", "dev_user", "silver", bad_silver_sql)
aegislake_pr_gatekeeper("PR-102", "hmuddam", "gold", good_gold_sql)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE DATABASE IF NOT EXISTS enterprise_bronze;
# MAGIC CREATE DATABASE IF NOT EXISTS enterprise_silver;
# MAGIC CREATE DATABASE IF NOT EXISTS enterprise_gold;
# MAGIC
# MAGIC -- 1. BRONZE (Append-Only)
# MAGIC CREATE OR REPLACE TABLE enterprise_bronze.raw_orders (
# MAGIC     order_id STRING, customer_name STRING, region_id STRING,
# MAGIC     total_amount DOUBLE, _ingest_time TIMESTAMP, _source_file STRING
# MAGIC ) USING DELTA;
# MAGIC
# MAGIC INSERT INTO enterprise_bronze.raw_orders VALUES
# MAGIC ('ORD_01', 'Harish Muddam', 'SOUTH', 14500.0, CURRENT_TIMESTAMP(), 'landing/orders_1.json'),
# MAGIC ('ORD_02', 'Sunita Rao', 'NORTH', 7800.0, CURRENT_TIMESTAMP(), 'landing/orders_1.json'),
# MAGIC ('ORD_01', 'Harish Muddam', 'SOUTH', 14500.0, CURRENT_TIMESTAMP(), 'landing/orders_2.json');
# MAGIC
# MAGIC -- 2. SILVER (Deduplication + PII Dynamic Masking)
# MAGIC CREATE TABLE IF NOT EXISTS enterprise_silver.orders (
# MAGIC     order_id STRING, masked_customer_name STRING, region_id STRING,
# MAGIC     total_amount DOUBLE, _processed_at TIMESTAMP
# MAGIC ) USING DELTA;
# MAGIC
# MAGIC MERGE INTO enterprise_silver.orders AS target
# MAGIC USING (
# MAGIC     SELECT order_id, CONCAT(LEFT(customer_name, 2), '****') AS masked_customer_name,
# MAGIC            region_id, total_amount, CURRENT_TIMESTAMP() AS _processed_at,
# MAGIC            ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY _ingest_time DESC) as rank
# MAGIC     FROM enterprise_bronze.raw_orders
# MAGIC ) AS source
# MAGIC ON target.order_id = source.order_id
# MAGIC WHEN MATCHED AND source.rank = 1 THEN
# MAGIC     UPDATE SET target.masked_customer_name = source.masked_customer_name,
# MAGIC                target.region_id = source.region_id, target.total_amount = source.total_amount,
# MAGIC                target._processed_at = source._processed_at
# MAGIC WHEN NOT MATCHED AND source.rank = 1 THEN
# MAGIC     INSERT (order_id, masked_customer_name, region_id, total_amount, _processed_at)
# MAGIC     VALUES (source.order_id, source.masked_customer_name, source.region_id, source.total_amount, source._processed_at);
# MAGIC
# MAGIC -- 3. GOLD (Liquid Clustered Aggregation)
# MAGIC CREATE OR REPLACE TABLE enterprise_gold.sales_kpis
# MAGIC CLUSTER BY (region_id) AS
# MAGIC SELECT region_id, COUNT(order_id) AS total_orders, SUM(total_amount) AS total_revenue,
# MAGIC        CURRENT_TIMESTAMP() AS _created_at
# MAGIC FROM enterprise_silver.orders GROUP BY region_id;
# MAGIC
# MAGIC SELECT * FROM enterprise_gold.sales_kpis;