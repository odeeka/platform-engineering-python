# Platform Engineering Practice Projects

This repository outlines a set of progressive, production-oriented projects designed to build real-world engineering skills for cloud, platform, and distributed systems roles.

Each project focuses on practical system design, resilience, observability, and production behavior - not just syntax.

---

## 1. Preflight / Dependency Checker (CLI Tool)

**Goal:**  
Validate service dependencies before deployment.

**Core Features:**

- DNS resolution check
- TCP connectivity check
- HTTP health endpoint check
- Configurable timeout handling
- Retry with exponential backoff
- Structured JSON logging
- Proper exit codes (0/1)
- CLI flags and argument parsing
- Unit tests
- Dockerfile
- CI pipeline integration

**Engineering Focus:**

- Networking fundamentals
- Error handling strategy
- Resilience patterns
- Clean CLI design

---

## 2. Config Validator + Policy Engine

**Goal:**  
Validate service configuration files during CI.

**Core Features:**

- YAML/JSON parsing
- Required field validation
- Type validation
- Environment-specific rules (dev/stage/prod)
- Policy enforcement (e.g. no `latest` image tag, minimum replicas)
- Structured validation report (JSON output)
- Error vs warning classification
- Unit tests
- GitHub Actions (or other CI) integration

**Engineering Focus:**

- Domain modeling
- Validation architecture
- Policy abstraction
- CI-driven quality gates

---

## 3. Minimal REST API with Observability

**Goal:**  
Build a production-ready microservice.

**Core Features:**

- REST endpoints (`/health`, `/metrics`, `/work`)
- Structured logging
- Request ID propagation
- Graceful shutdown (SIGTERM handling)
- Per-request timeout management
- Basic metrics (latency, request count)
- Docker containerization
- Integration tests

**Engineering Focus:**

- HTTP lifecycle management
- Concurrency handling
- Service shutdown behavior
- Observability best practices

---

## 4. Rate Limiter + Circuit Breaker Proxy

**Goal:**  
Build a resilient reverse proxy service.

**Core Features:**

- Forward requests to upstream service
- QPS-based rate limiting
- Circuit breaker implementation
- Retry with exponential backoff
- Timeout configuration
- Shared state management
- Metrics export
- Concurrency-safe implementation

**Engineering Focus:**

- Distributed systems patterns
- Fault tolerance
- Backpressure handling
- State management under concurrency

---

## 5. Cloud Policy / Resource Checker (CLI Tool)

**Goal:**  
Validate cloud infrastructure configurations.

**Core Features:**

- Cloud SDK integration (AWS/GCP/Azure)
- Resource existence validation
- IAM policy validation
- Security checks (e.g. public bucket detection)
- Structured reporting output
- Authentication handling
- CI integration support

**Engineering Focus:**

- Cloud APIs
- Security mindset
- Infrastructure validation
- Platform tooling design

---

## 6. Worker Pool / Job Runner

**Goal:**  
Implement a concurrent job processing service.

**Core Features:**

- Queue consumer implementation
- Configurable worker pool
- Graceful shutdown support
- Retry failed jobs
- Dead-letter queue handling
- Concurrency safety guarantees
- Metrics and structured logging

**Engineering Focus:**

- Concurrency models
- State consistency
- Fault tolerance
- Throughput vs reliability tradeoffs

---

## Quality Expectations (Applies to All Projects)

Each project should include:

- Clear README documentation
- CLI usage examples
- Structured logging (JSON preferred)
- Proper error handling
- Timeout and cancellation logic
- Unit tests
- Dockerfile
- CI pipeline configuration
- Versioning and release process

---

## Recommended Order

1. Preflight Checker  
2. Config Validator  
3. REST API with Observability  
4. Worker Pool  
5. Rate Limiter Proxy  
6. Cloud Policy Checker  

This sequence builds progressively from networking and validation toward distributed systems and cloud-native engineering.

---

## Objective

By completing these projects with production-level quality standards, you will develop:

- Strong cloud-native engineering skills
- Real-world distributed systems thinking
- Production resilience patterns
- Platform engineering competence
