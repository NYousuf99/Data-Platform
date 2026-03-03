# Documentation

This folder contains the full technical documentation for the data platform.
It is organised by concern — architecture, platform design, security, risk, 
operations, and deployment. Each section contains focused markdown files that 
together form the complete picture of how this system is designed, built, and operated.

---

## Structure

### Solutions Architecture
High level overview of the system and the key decisions that shaped it.
- `overview.md` — What we are building, why, and the high level design
- `flow-diagram.png` — End to end data flow from source to consumption
- `decisions/` — Architecture Decision Records (ADRs). One file per significant technical decision, recording what was decided and why

### Data Platform
The core of the documentation. Covers how data moves through the pipeline, 
how it is stored, governed, and consumed at each stage.
- `data-plane.md` — Introduction to the data plane and the medallion architecture used
- `zones.md` — Each zone (Landing, Bronze, Silver, Gold, Serving, Sandbox), their purpose, security, and consumers
- `data-types-formats.md` — File formats, table formats, compression, and encoding at each stage
- `data-contracts.md` — Schema agreements between producers and consumers including SLAs and versioning
- `partitioning-clustering.md` — How data is physically organised at each stage for query performance
- `catalogue-metadata.md` — How assets are registered, tagged, classified, and made discoverable
- `lineage.md` — How data flows from source system through each zone to the serving layer
- `lifecycle.md` — Retention policies, expiry rules, and archiving behaviour at each zone
- `observability.md` — What is monitored, how alerts are triggered, and what tools are used
- `access-control.md` — Roles, permissions, and governance per zone
- `orchestration.md` — How pipelines are triggered, scheduled, and sequenced

### Security
Covers how the platform is secured at the infrastructure and data level.
- `iam-roles.md` — AWS IAM roles and policies, what each role owns and can access
- `encryption.md` — Encryption at rest and in transit across all zones
- `pii-handling.md` — How personally identifiable information is identified, masked, and governed

### Risk
- `risk-register.md` — Known risks per zone with likelihood, impact, and mitigation for each

### Operations
Covers how the platform is run day to day.
- `runbook.md` — Step by step responses to common failures and incidents
- `slas.md` — Service level agreements for data freshness, pipeline completion, and availability

### Deployment
Covers how the platform is built and deployed.
- `deployment-guide.md` — How to deploy the platform from scratch including prerequisites
- `environment-promotion.md` — How changes move from development to staging to production
- `cdk-stacks.md` — Reference for each CDK stack, what it owns, and its dependencies

---

## Principles

- Each file covers one concern. If a file grows too large it should be split into a subfolder.
- Docs live next to the code so they change with it and are reviewed in pull requests.
- Architecture Decision Records are written at the time of the decision, not retrospectively.