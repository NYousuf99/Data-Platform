# Data Pipeline Lifecycles – Reference Documentation

This document summarizes the **Data, Software, and Operational lifecycles** for our Medallion-style data pipeline project. It aligns with **industry standards** and **AWS/Databricks best practices**.

---

## 1. Data Lifecycle

The Medallion architecture organizes data into **Bronze, Silver, and Gold zones**. Each stage refines the data progressively.

| Stage / Zone | Input | Output | Processing | Storage | Consumers | Notes |
|--------------|-------|--------|------------|---------|-----------|-------|
| **Ingress**  | External APIs / Clients | Bronze (raw) | None | S3 Landing Bucket | None | API Gateway writes directly; raw source of truth |
| **Ingestion** | Bronze | Silver (validated) | Light validation: schema checks, dedup, timestamps, CSV only | S3 | ML Engineers, Analysts | Event or batch-driven Lambda/Step Functions |
| **Processing** | Silver | Gold (curated, analytics-ready) | ETL, standardization, missing data handling | S3 + Redshift / Glue | Analysts, BI tools | Heavier processing, ready for queries |
| **Analytics** | Gold | BI / Reports | Query + aggregation | Redshift / Athena / QuickSight | Data Analysts, BI Users | Optional presentation layer; dashboards, reporting |

**References:**

- [Databricks Medallion Architecture](https://docs.databricks.com/gcp/en/lakehouse/medallion.html?utm_source=chatgpt.com)  
- [AWS Data Lake Storage Constructs](https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Storage/data-lake-storage?utm_source=chatgpt.com)  
- [Medallion Architecture Community Guide](https://datadef.io/guides/en/medallion-architecture?utm_source=chatgpt.com)

---

## 2. Software / Development Lifecycle

Modern DevOps best practices guide **development, packaging, testing, and deployment**.

| Phase | Tool / Stack | Action | Output | Notes |
|-------|-------------|--------|--------|------|
| **Dev** | `functions/` + `src/` | Write code, helper libs | Local code, packaged wheels | Functions separated by stack (Ingress, Ingestion, Processing) |
| **Build** | `docker-runtimes` | Build runtime image including shared libs | Docker base image | Lightweight, reusable across environments |
| **Package** | `functions/` | Reference runtime image, build function image | Docker function image | Keeps Lambda images small and decoupled |
| **Test** | Pytest / unit tests | Run tests against functions & stacks | Test reports | Unit tests for CDK stacks & Lambdas |
| **CI/CD** | GitLab CI/CD + `uv run cdk deploy` | Deploy to AWS | Live stacks/resources | Deployment order: Storage → Ingress → Ingestion → Processing → Analytics |
| **Release / Prod** | CDK | Deploy stable version | Production pipeline | Branching strategy, tagging, environment isolation |

**Reference:**  
- [AWS Well-Architected DevOps Guidance](https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/development-lifecycle.html?utm_source=chatgpt.com)

---

## 3. Operational Lifecycle

Describes **how the system runs, is monitored, and maintained** in production.

| Component | Monitoring | Alerts / Actions | Notes |
|-----------|------------|-----------------|------|
| **Ingress API Gateway** | CloudWatch metrics: requests, throttling | Lambda / SNS alerts if failure | API key monitoring, throttle limits |
| **S3 Buckets** | S3 metrics: PUT, GET, storage | SNS alerts on errors | Retention policies; `RETAIN` on buckets |
| **Lambdas / Step Functions** | CloudWatch logs, X-Ray | Auto-retries, DLQ | Monitor event failures, performance |
| **Processing / ETL** | Glue job metrics, Lambda metrics | Alerts on job failure | Ensure Silver → Gold transformations run correctly |
| **Analytics / Redshift** | Query metrics, usage | Alerts on failed queries or failed dashboard refresh | Ensure Gold datasets are accessible and consistent |
| **CI/CD / Deployment** | Pipeline logs, CDK deploy outputs | Rollback / failure notifications | Monitors deployment success across environments |

**References:**  
- [AWS Data Lake Storage Lifecycle](https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Storage/data-lake-storage?utm_source=chatgpt.com)  
- [Medallion Architecture Operational Guide](https://www.digitalbricks.ai/build-innovate/medallion-architecture?utm_source=chatgpt.com)  

---

## Diagram Suggestion (Horizontal)

