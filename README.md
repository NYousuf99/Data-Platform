# Data Platform

A modular, event-driven data platform implementing a Medallion (Bronze/Silver/Gold) architecture using AWS CDK.  
The system is designed to demonstrate real-world data engineering patterns including ingress,ingestion, validation, processing, orchestration, and analytics delivery.

## Architecture Overview

This project implements a staged data pipeline with clear separation between ingress, ingestion, processing, and analytics layers.

External data enters through controlled ingress points, lands in a raw Bronze zone, undergoes validation in Silver, and is curated into Gold for analytics consumption. The system is event-driven, reproducible, and cost-conscious.

The architecture prioritizes:
- Clear ownership boundaries  
- Event-driven workflows  
- Data lifecycle separation  
- Infrastructure as Code  
- Minimal persistent compute 



## Data Flow

1. External systems send data through API Gateway into an S3 Bronze bucket.  
2. Event triggers validate and standardize files into the Silver zone.  
3. Processing jobs curate data into Gold (Redshift / Athena).  
4. Analytics tools consume Gold datasets.



data-pipeline/
├── stacks/ # Infrastructure (AWS CDK)
├── lambdas/ # Runtime logic
├── docker/ # Runtime images
├── ci/ # CI/CD pipelines
└── app.py # CDK entrypoint



Each layer owns a single responsibility to reduce coupling and improve maintainability.

---

## Technology Stack

- AWS CDK (Infrastructure as Code)  
- AWS Lambda (Compute)  
- Amazon S3 (Storage)  
- AWS Step Functions (Orchestration)  
- AWS Glue / Athena / Redshift (Processing & Analytics)  
- Docker + ECR (Runtime images)  
- UV (Python dependency management)  
- GitLab CI/CD (Automation)  

---

## Local Development

Dependencies are managed using `uv` and defined in `pyproject.toml`.

Commands are executed inside the project environment using:

### bash
uv run <command>



------

## Deployment

Infrastructure is deployed via GitLab CI/CD pipelines.
Each stack is versioned and deployed independently using AWS CDK.

## Cost Awareness

The system is designed to minimize cost by using event-driven compute and avoiding always-on resources.
Expensive services (e.g., Glue, Redshift) are only used when necessary.

## Design Principles

- Clear ownership boundaries
- Event-driven architecture
- Data lifecycle separation
- Reproducible infrastructure
- Minimal persistent compute
- Cost-conscious design
- Future Improvements
- VPC isolation
- Streaming ingestion
- Schema registry
- Data quality metrics
- Governance tooling



---

This README already signals:

- System-level thinking  
- Architecture awareness  
- Deployment maturity  
- Cost awareness  
- Engineering discipline  

When someone opens this repo, they won’t think *“tutorial project.”*  
They’ll think *“this person understands platforms.”*

Next step, when you’re ready:  
We can design the **Ingress stack** and write its README section properly so your project starts with a strong foundation.
