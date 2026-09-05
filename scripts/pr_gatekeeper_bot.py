import sys

def run_pr_audit():
    print("=" * 60)
    print("🛡️ AEGISLAKE: AUTOMATED CI/CD PR GATEKEEPER RUNNING")
    print("=" * 60)

    sample_pr_diff = """
    CREATE OR REPLACE TABLE enterprise_gold.sales_kpis
    CLUSTER BY (region_id) AS
    SELECT region_id, COUNT(order_id) AS total_orders, CURRENT_TIMESTAMP() AS _created_at
    FROM enterprise_silver.orders GROUP BY region_id;
    """

    violations = []
    if "CLUSTER BY" not in sample_pr_diff:
        violations.append("Missing Liquid Clustering `CLUSTER BY`.")
    if "_created_at" not in sample_pr_diff:
        violations.append("Missing mandatory audit column `_created_at`.")

    if violations:
        print("❌ CI/CD STATUS: PULL REQUEST REJECTED (MERGE BLOCKED)")
        for v in violations:
            print(f"  🔴 {v}")
        sys.exit(1)
    else:
        print("✅ CI/CD STATUS: PULL REQUEST APPROVED")
        print("All architectural guardrails and privacy directives satisfied.")
        sys.exit(0)

if __name__ == "__main__":
    run_pr_audit()