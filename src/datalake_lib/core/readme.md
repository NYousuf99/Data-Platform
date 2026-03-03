# Section Overview 

## Key

- [ ] **Purpose:** 
What the module *does*. Describes the functional role achieves.

- [ ] **Responsibilities**
What specific **tasks**, **operations** and **behaviour**. Describes what the module is accountable for.

- [ ] **Intent:**

Why the module *exists* and how it should be *used*. Explains desgin reasoning, architectural constraints and usage.

## Core
core
│   ├── https.py
│   ├── models.py
│   ├── settings.py
|   └── storage.py

The *core* package represents the foundational layer of the data lake library.

Files in this directory define foundational primitives and infrastructure boundaries. Their behaviour follow these patterns:

- [ ] Unspecialised
- [ ] Runtime agnostic except explicitly defined infrastructure boundaries
- [ ] Free from *Business Logic*
- [ ] Contains only controlled infrastructure boundaries
- [ ] Responsible for external tool interactions
- [ ] Responsible for error handling

As a result this layer (*core*) defines the reusable nature that higher layers (*Business Logic*, *Infrastructure patterns*) in the platform will inhert. Staying true to these patterns these functions should not contain domain specific knowledge. 

## Design Philosophy

### Core Responsibilities

- [ ] HTTP communication
- [ ] Data models and validators
- [ ] Environment Configuration
- [ ] Storage abdaptors
- [ ] Structured Error handling

## Infrastructure awarenes 

The *core* package contains two types of components:

**infastructure agnostic components**
- [ ] models.py
- [ ] https.py 

These modules remain runtime agnostic.

**Infrastructure boundary components**

- [ ] settings.py 
- [ ] storage.py

These modules interface directly with the runtime environment and thus may contain some provider specific logic (AWS,CI etc). Thus when altering backend these modules require reviewing.

## File responsibilities

### https.py

**Purpose** 

Provides standardies HTTP client layer for handling and interacting with external APIs.

**Responsibilities**

- [ ] Calling HTTP requests
- [ ] Handling timeouts and connection failures
- [ ] Handling bespoke status codes via mapping
- [ ] Raising structured errors and exceptions
- [ ] Returning validated responses
- [ ] Implements retry logic where appropraite or fail fast where appropriate based on status code

**Intent** 

- [ ] No *Business Logic*
- [ ] Consistent error handling across the system


### models.py

**Purpose**

Defines core data structures used across the system.

**Responsibilities**

- [ ] Validates  structures and types
- [ ] Provides consistent schemas via schema locking 
- [ ] Encapulates transformation logic 


**Intent**

- [ ] Define data strcutures and not meaning or use case
- [ ] Reusable at all layers 
- [ ] Segregated for easy updates and changes


### settings.py

**Purpose**

Handling configuration loading and validation and lives at the infrastructure boundary.

**Responsibilities** 

- [ ] Reading Environment variables
- [ ] Fetching remote secrets
- [ ] Validationg required configuration
- [ ] Raising structured errors

**Intent**

- [ ] Fail fast on invalid configuration
- [ ] Avoid scattering configuration across the lifecycle of the project
- [ ] Centralises configuration handling and logic
- [ ] Business agnostic
- [ ] Does not contain domain specific behaviour 

### storage.py 

**Purpose** 

Defines the storage interface and system wide implementation and so ensures stable storage contracts for higher layers.

- [ ] Uploading and downloading objects 
- [ ] Handling storage level errors 
- [ ] Maintains consisten interface across storage backends at higher levels


**Intent**

- [ ] Encapsulates SDK usage
- [ ] Backend specific constraints
- [ ] Consistent storage interface


## Error Handling 

**Purpose**

This layer standardises error types in the intent that higher layer code can:

- [ ] Catch critical failures intentionally
- [ ] Distinguish the source of error
- [ ] Implements retry logic where appropraite or fail fast where appropriate

**Intent**

Errors should be:
- [ ] Typed
- [ ] Descriptive
- [ ] Deterministic 


## Separation Case for core

Why: 

- [ ] Reusability 
- [ ] System wide consistency 
- [ ] Traceability 
- [ ] Testability 
- [ ] Clear Architectural Boundaries 
- [ ] Reduced coupling either from infrastructure or *Business Logic* or both
- [ ] Changes only when *Business Logic* or infrastruture evolves


## Updates

The *core* layer should change rarely and if so should be  deliberate as their effects cascades across layers