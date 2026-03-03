# Data Platform Architecture

> This document defines the semantic behaviour of the data platform. It describes what the data is, how it flows, and what guarantees it carries at each stage. Cloud provider names and tooling specifics belong in the Deployment Architecture — not here.

---

## 1. Data Plane Architecture

### 1.1 Purpose

The data plane is responsible for the movement, transformation, storage, and governance of data across all zones from ingestion to consumption.

**In scope:**
- Zone definitions and data state at each stage
- Ingestion patterns and contracts
- Data quality guarantees
- Retention and lifecycle policies
- Lineage and traceability

**Out of scope:**
- Specific cloud tooling (belongs in Deployment Architecture)
- Orchestration scheduling details (belongs in Orchestration)
- Infrastructure sizing (belongs in Deployment Architecture)

---

### 1.2 Medallion Architecture — Zone Overview

The platform uses a medallion architecture. Data moves through zones, each representing a higher level of quality, governance, and readiness for consumption.

| Zone | Stage | Data State | Write Model | Read Access | Retention | Quality Level |
|---|---|---|---|---|---|---|
| Landing | 0 | Raw, unvalidated, as-is from source | Append-only, source systems write directly | Ingestion pipelines only | 7–30 days | 0 — None |
| Bronze | 1 | Immutable copy with metadata tags | Append-only, no deletes, no updates | Pipeline engineers only | Indefinite / 5+ years | 1 — Registered |
| Silver | 2 | Validated, deduplicated, conformed | Pipeline writes only, PII governance enforced | Data team, role-based | 1–3 years | 2 — Validated |
| Gold | 3 | Aggregated, modelled, business-ready | Approved pipelines only | Broad analytics access | 3–7 years | 3 — Trusted |
| Platinum | 4 | Consumption-ready data products | No writes, read-optimised | End users, applications, APIs | Tied to Gold upstream | 4 — Certified |
| Sandbox | 5 | Experimental, unmanaged | Ephemeral, isolated from production | Data scientists and engineers only | 30–90 days | 0 — None |

---

### 1.3 Zone Detail

#### Landing
- Acts as a trust boundary. Data enters here from external sources and is not touched.
- No schema enforcement. No transformation. No validation.
- The only guarantee is that data arrived.
- Short-lived — data is promoted to Bronze and expired.

#### Bronze
- The immutable source of truth. Once written, data is never modified or deleted.
- Metadata is added on arrival: ingestion timestamp, source system ID, batch ID.
- Enables full replay — if downstream zones are corrupted, Bronze is the recovery point.
- Schema is registered but not enforced.

#### Silver
- First zone where data is trusted for analysis.
- Deduplication, null handling, type casting, and basic business rules are applied here.
- PII is masked or tokenised at this stage before flowing downstream.
- Schema is enforced on write.

#### Gold
- Business-ready. Aggregations, joins, derived metrics, and dimensional models live here.
- Facts, dimensions, and KPIs are materialised at this layer.
- Consumers do not need to understand the raw data model to use Gold.

#### Platinum
- The serving layer. Data products, materialised views, and APIs are exposed here.
- No transformation happens at this layer — it is pure consumption.
- Row-level security and consumer-facing data contracts govern access.

#### Sandbox
- Isolated from all production zones.
- No SLAs. No promotion to production without a review gate.
- Used for ML experimentation, ad-hoc exploration, and prototyping.

---

### 1.4 Data Quality Levels

Data quality is tracked as a level that increments as data moves through zones. A level is only assigned once the zone's quality criteria are met.

| Level | Zone | Criteria |
|---|---|---|
| 0 | Landing / Sandbox | No validation. Data arrived but no guarantees on content. |
| 1 | Bronze | Schema registered. Row count reconciled. Arrival SLA monitored. |
| 2 | Silver | Null checks passed. Dedup validated. Schema enforced. Business rules scored. |
| 3 | Gold | Metric reconciliation complete. Freshness SLA met. Golden dataset comparison passed. |
| 4 | Platinum | Consumer data contracts active. Query performance SLA met. Freshness alerts configured. |

---

### 1.5 Ingestion Model

Three ingestion patterns are supported. Each has a defined entry point and behaviour at Landing.

| Pattern | Description | Entry Point | Trigger |
|---|---|---|---|
| External Pull | Platform pulls data from an external API or service on a schedule | Landing zone | Scheduled or event-based |
| File Drop | Source system delivers files to a designated location | Landing zone | File arrival event |
| Streaming Push | Source system pushes events in near real-time | Landing zone (stream buffer) | Continuous / micro-batch |

- All patterns land in the Landing zone first before promotion to Bronze.
- Metadata tags are applied at the Bronze promotion step, not at Landing.
- Ingestion adapters are responsible for preserving the fidelity of the source data.

---

### 1.6 Data Contracts

A data contract is a formal agreement between a producer and a consumer on the structure, quality, and availability of a dataset.

| Field | Description | Example |
|---|---|---|
| Contract ID | Unique identifier | DC-001 |
| Producer | System or team writing the data | Ingestion pipeline |
| Consumer | System or team reading the data | Databricks, Redshift |
| Stage | Zone this contract governs | Silver |
| Schema Name | Agreed schema identifier | orders_clean_v2 |
| Fields | Agreed columns | order_id, customer_id, amount, created_at |
| Data Types | Agreed type per field | STRING, STRING, DECIMAL, TIMESTAMP |
| SLA | Freshness commitment | Data available within 1 hour of source event |
| Versioning | How changes are versioned | Semantic — v1, v2, v3 |
| Break Behaviour | What happens if the contract is violated | Alert fired, pipeline paused, consumer notified |

**Contract principles:**
- Producers own the contract definition. Consumers agree to it.
- Breaking schema changes require a version increment. Additive changes (new columns) are non-breaking.
- Contracts are defined at Silver and above. Landing and Bronze have no consumer contracts.

---

### 1.7 Data Types & Formats

| Stage | File Format | Table Format | Compression | Encoding | Schema Type | Supports Updates | Supports Spatial |
|---|---|---|---|---|---|---|---|
| Landing | JSON, CSV, Avro, XML | None — raw files | None | Native source encoding | Schema-on-read | No — append only | No |
| Bronze | Parquet | None — managed files | Snappy | Dictionary encoding | Schema-on-read | No — immutable | No |
| Silver | Parquet | Open table format v2 | Snappy | Dictionary + RLE encoding | Schema-on-write | Yes — row-level deletes supported | No |
| Gold | Parquet | Open table format v3 | Zstandard | Dictionary + RLE encoding | Schema-on-write | Yes — merge/upsert supported | Yes — where geospatial data present |
| Platinum | Materialised views, external tables | Dependent on serving engine | N/A | N/A | Schema-on-write | No — read-only | Dependent on serving engine |
| Sandbox | Parquet or raw files | Open table format v2 or none | Snappy | Dictionary encoding | Schema-on-read | Yes | Optional |

---

### 1.8 Partitioning & Clustering

Partitioning determines how data is physically organised on storage. Clustering determines how data is sorted within a partition for query performance.

| Stage | Partition Key | Partition Strategy | Cluster Key | Sort Order | Partition Pruning | Notes |
|---|---|---|---|---|---|---|
| Landing | arrival_date | By day | None | None | No | Transient — not optimised for query |
| Bronze | source_system + ingestion_date | By source and day | None | None | Yes | Immutable — never repartitioned |
| Silver | domain + event_date | By domain and day | entity_id | ASC | Yes | Avoid high-cardinality partition keys |
| Gold | domain + reporting_date | By domain and month | metric_key | ASC | Yes | Optimised for aggregation queries |
| Platinum | Dependent on serving engine | Dependent on serving engine | Dependent on serving engine | Dependent on serving engine | Yes | Managed by serving layer |
| Sandbox | None or ingestion_date | Flexible | None | None | Optional | No constraints — experimental |

---

### 1.9 Lifecycle & Retention

Lifecycle policy governs how long data exists at each zone and what happens to it at expiry.

| Stage | Retention Period | Expiry Trigger | Action at Expiry | Replay Guarantee | Notes |
|---|---|---|---|---|---|
| Landing | 7–30 days | Age-based | Delete | No | Data must be promoted to Bronze before expiry |
| Bronze | Indefinite / 5+ years | Manual or regulatory | Archive then delete | Yes — full replay from Bronze | Core recovery point for the platform |
| Silver | 1–3 years | Age-based | Delete | Partial — replay from Bronze | PII deletion requests trigger immediate removal |
| Gold | 3–7 years | Age-based | Delete | No — rebuild from Silver | Retention tied to reporting and regulatory requirements |
| Platinum | Tied to Gold upstream | Upstream expiry | Delete | No | Serving layer mirrors Gold retention |
| Sandbox | 30–90 days | Age-based + auto-expiry | Delete | No | Ephemeral by design |

---

### 1.10 Metadata & Lineage

Every asset in the platform is registered and traceable.

**Asset registration — what is captured per asset:**

| Field | Description | Example |
|---|---|---|
| Asset Name | Name of the table or dataset | orders_silver |
| Asset Type | What kind of asset | Iceberg Table, S3 Prefix, Materialised View |
| Owner | Responsible team or person | Data Engineering |
| Zone | Which zone it belongs to | Silver |
| Tags | Discovery labels | orders, finance, pii |
| Classification | Sensitivity level | Confidential |
| PII Flag | Whether PII is present | Yes |
| Registered In | Catalogue tool | Data catalogue |
| Searchable | Discoverable in catalogue | Yes |

**Lineage model:**

| Source System | Landing | Bronze | Silver | Gold | Platinum | Transformation Logic | Frequency |
|---|---|---|---|---|---|---|---|
| External API | raw_api_drop | api_bronze | api_silver | api_gold | api_reporting | Dedup on entity_id, join to reference table, aggregate by domain | Hourly |

- Lineage is captured at the pipeline level — every promotion step records source and target.
- Column-level lineage is captured at Silver and above where schema is enforced.
- Lineage records are immutable once written.

---

## 2. Solutions Architecture

### 2.1 Purpose

This section describes how real workloads interact with the data platform. Where the Data Plane Architecture defines the laws, Solutions Architecture describes how those laws are applied to specific use cases.

---

### 2.2 Integration Patterns

| Pattern | Producer | Ingestion Adapter | Data Plane Entry | Control Trigger | Typical Latency |
|---|---|---|---|---|---|
| Scheduled API Pull | External REST API | Pull adapter — scheduled job | Landing zone | Time-based schedule | Minutes to hours |
| File-based Delivery | External system, SFTP, S3 | File watcher / event listener | Landing zone | File arrival event | Minutes |
| Streaming Push | IoT device, event stream | Stream consumer / micro-batch adapter | Landing zone stream buffer | Continuous | Seconds to minutes |
| Database CDC | Operational database | Change data capture connector | Landing zone | Transaction log event | Near real-time |

---

### 2.3 Non-Functional Requirements

| Requirement | Category | Target | Notes |
|---|---|---|---|
| Pipeline completion | Latency | Bronze available within 15 minutes of landing | Per standard batch ingestion |
| Silver freshness | Freshness | Silver available within 1 hour of Bronze | SLA defined in data contract |
| Gold freshness | Freshness | Gold available within 2 hours of Silver | Dependent on transformation complexity |
| Landing availability | Availability | 99.9% write availability | Source systems must be able to land data |
| Bronze durability | Durability | 99.999999999% (11 nines) | Immutable, replicated storage |
| Sandbox isolation | Isolation | Zero access to production zones | Hard boundary enforced at access control level |

---

## 3. Deployment Architecture

### 3.1 Environment Model

| Environment | Purpose | Isolation | Promotion Gate |
|---|---|---|---|
| Development | Active development and testing | Fully isolated from staging and production | Pull request review + automated tests pass |
| Staging | Pre-production validation | Isolated from production, mirrors production config | Manual approval by platform owner |
| Production | Live platform | Fully isolated | Manual approval + change record |

- Each environment has its own storage, compute, and access controls.
- No data flows from production to development or staging.
- Synthetic or anonymised datasets are used in development and staging.

---

### 3.2 Infrastructure Layout

| Component | Type | Zone Served | Notes |
|---|---|---|---|
| Object storage — Landing | Cloud object storage | Landing | Short lifecycle policy, write access for ingestion roles only |
| Object storage — Bronze | Cloud object storage | Bronze | Versioning enabled, immutable policy, long retention |
| Object storage — Silver | Cloud object storage | Silver | Open table format, PII masking enforced |
| Object storage — Gold | Cloud object storage | Gold | Open table format v3, spatial support enabled |
| Serving engine | Analytical query engine | Platinum | Materialised views, row-level security |
| Compute — ingestion | Serverless functions | Landing → Bronze | Event-driven, short-lived |
| Compute — processing | Distributed compute | Bronze → Silver | Batch or streaming |
| Compute — transformation | Distributed compute | Silver → Gold | Scheduled batch |
| Container runtime | Container image | All | Decoupled runtime, independently versioned and deployed |

---

### 3.3 Security Implementation

| Control | Zone Applied | Mechanism | Notes |
|---|---|---|---|
| Encryption at rest | All zones | Server-side encryption, platform-managed keys | Applied by default on all storage |
| Encryption in transit | All zones | TLS 1.2 minimum | Enforced on all data movement |
| IAM role separation | All zones | Least-privilege roles per zone | Ingestion role cannot read Silver or Gold |
| PII masking | Silver onwards | Tokenisation at promotion step | Raw PII never leaves Bronze |
| Row-level security | Platinum | Serving engine access controls | Consumer sees only their permitted rows |
| Sandbox isolation | Sandbox | Hard network and IAM boundary | No cross-zone access possible |

---

### 3.4 CI/CD & Runtime

| Stage | Trigger | Action | Gate |
|---|---|---|---|
| PR opened | Code push | Lint, unit tests, CDK synth, CDK diff | All checks must pass |
| PR merged to main | Merge | CDK deploy to development | Automatic |
| Release tag | Manual tag | CDK deploy to staging | Manual approval |
| Production release | Manual approval | CDK deploy to production | Manual approval + change record |
| Container image build | Change to docker-runtimes/ | Build and push versioned image | Automated tests pass |

- The container runtime image is built and versioned independently of the CDK stacks.
- Stacks reference a pinned image version — they do not build the image themselves.
- CDK stacks are deployed in dependency order: IAM → Storage → Ingestion → Processing → Transformation → Analytics.

---

## 4. Observability Architecture

### 4.1 Monitoring Philosophy

The platform monitors across four dimensions. Each dimension has a different owner and response expectation.

| Dimension | What it measures | Owner | Response SLA |
|---|---|---|---|
| Freshness | Is data arriving and being promoted on time | Data Engineering | 15 minutes |
| Volume | Are expected row counts being met | Data Engineering | 30 minutes |
| Quality | Are data quality rules passing | Data Engineering + Data Team | 1 hour |
| Schema | Has the structure of data changed unexpectedly | Data Engineering | Immediate |

---

### 4.2 Data Plane Metrics

| Stage | Metric | Type | Threshold | Frequency |
|---|---|---|---|---|
| Landing | Files arrived | Volume | Zero files in expected window = alert | Per ingestion schedule |
| Landing | File size | Volume | Greater than 3x average = alert | Per ingestion schedule |
| Bronze | Row count vs source | Volume | Variance greater than 1% = alert | Per batch |
| Bronze | Arrival SLA | Freshness | Bronze not available within 15 minutes of landing = alert | Continuous |
| Silver | Null rate per column | Quality | Null rate exceeds defined threshold = alert | Per batch |
| Silver | Dedup rate | Quality | Greater than 5% duplicates = alert | Per batch |
| Silver | Schema drift | Schema | Any unexpected column add, remove, or type change = alert | Per batch |
| Gold | Metric reconciliation | Quality | Gold metric varies from source metric by more than 0.1% = alert | Per batch |
| Gold | Freshness | Freshness | Gold not available within 2 hours of Silver = alert | Continuous |
| Platinum | Query SLA | Performance | P95 query time exceeds defined threshold = alert | Continuous |

---

### 4.3 Alerting Model

| Severity | Condition | Channel | Response Time | Owner |
|---|---|---|---|---|
| P1 — Critical | Data loss, pipeline completely down, Bronze unavailable | Paging system + Slack | 15 minutes | On-call engineer |
| P2 — High | SLA breach, schema drift detected, quality score below threshold | Slack | 1 hour | Data Engineering |
| P3 — Medium | Volume anomaly, elevated null rate, slow query | Slack | 4 hours | Data Engineering |
| P4 — Low | Non-critical threshold warnings, sandbox issues | Email or log | Next business day | Pipeline owner |

---

### 4.4 Runbook Summary

Each failure scenario has a corresponding runbook entry. The categories are:

| Scenario | Zone | First Response | Recovery Path |
|---|---|---|---|
| Files not arriving at Landing | Landing | Check source system connectivity and ingestion adapter logs | Replay from source once connectivity restored |
| Bronze promotion failure | Landing → Bronze | Check compute logs, validate file format | Re-trigger promotion job, validate row count after |
| Schema drift detected at Silver | Silver | Halt pipeline, inspect incoming schema | Update schema registry, review data contract, re-promote |
| Quality score failure at Silver | Silver | Quarantine failing records, alert data contract owner | Investigate source, fix upstream, replay affected batch |
| Gold metric reconciliation failure | Gold | Compare Gold metric to Silver source | Identify transformation logic issue, rerun transformation |
| Serving layer query SLA breach | Platinum | Check query plan, check materialised view freshness | Refresh materialised view, optimise query or add clustering |

---

## 5. Risk Register

| Risk | Zone | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| Source system delivers malformed data | Landing | High | Low — Landing is isolated | Schema-on-read, no downstream impact until Bronze promotion |
| Bronze data corrupted or deleted | Bronze | Low | Critical — loss of replay capability | Immutable storage policy, versioning enabled, cross-region replication |
| PII leaked to Gold or Platinum | Silver | Low | Critical — regulatory and legal exposure | PII masking enforced at Silver promotion, access control audit quarterly |
| Schema breaking change from producer | Silver | Medium | High — downstream pipelines fail | Data contracts with versioning, schema drift alerting, break behaviour defined |
| Sandbox data used in production | Sandbox | Low | High — untested data in production | Hard IAM boundary, no promotion path without review gate |
| Pipeline SLA breach impacting consumers | Gold | Medium | Medium — delayed reporting | Freshness alerting, consumer notification via data contract break behaviour |
| Regulatory data deletion request not honoured | Silver / Gold | Low | Critical — compliance failure | PII flag in catalogue, deletion propagation policy, audit trail in lineage |
