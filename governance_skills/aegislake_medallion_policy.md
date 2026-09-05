# Enterprise Governed Skill: AegisLake Medallion & Orchestration Policy
# Asset ID: enterprise_dw.governance.skill_gold_pipeline_orchestration

[Directives]
1. Bronze Layer (Raw):
   - Append-only. Must record ingestion metadata: _ingest_time and _source_file.
2. Silver Layer (Cleansed & Enriched):
   - Deduplicated on business primary keys using Delta Lake MERGE INTO.
   - Dynamic PII Masking: Customer names must be masked using CONCAT(LEFT(customer_name, 2), '****').
3. Gold Layer (Curated & Aggregated):
   - Liquid Clustering: Mandatory CLUSTER BY (region_id).
   - Audit Stamps: Must append CURRENT_TIMESTAMP() AS _created_at.
4. Orchestration Standard:
   - Failure tolerance: Minimum 3 retries with 60-second backoff.
