# AWS SageMaker + Snowflake MLOps Pipeline — L6 Engineering Audit

Audit date: 2026-08-22

Scope: orchestration architecture, cloud trust boundaries, Snowflake access, SageMaker lifecycle, promotion logic, CI/tests, reproducibility evidence, containerization, release automation, and documentation accuracy.

## Executive assessment

This repository has a solid portfolio-level control story: cloud credentials remain external, offline tests avoid live provider coupling, retraining is policy-triggered, and promotion fails closed unless the configured metric exists, is finite, and meets threshold. That is a better systems signal than merely showing AWS/Snowflake SDK calls.

The repository should not yet be described as a production MLOps platform. The largest blockers are incomplete drift detection, incomplete SageMaker lifecycle orchestration, limited cloud-failure semantics, missing governed model/data lineage, no held-out quality study, no deployment approval/rollback contract, and limited release provenance.

## Findings by priority

### P1 — Drift detection is a scaffold, not a validated control

`inspect_data_drift()` currently returns a fixed false result. The comments reference PSI conceptually, but no statistical detector is executed.

**Recommendation:** implement a versioned baseline, explicit feature bins/distributions, missing-value policy, minimum sample requirements, PSI/KS or another justified test, thresholds, false-positive analysis, and fixture-based regression tests.

### P1 — Snowflake failure semantics can suppress retraining signals

`check_new_arrivals()` catches broad exceptions and returns zero. A credential outage or query failure can therefore look like “no new records.”

**Recommendation:** distinguish zero rows from unavailable telemetry. Return structured status or raise a typed error so orchestration can fail closed rather than interpret infrastructure failure as healthy data state.

### P1 — SageMaker lifecycle is incomplete

The agent submits a training job and the supervisor immediately asks for metrics. There is no explicit polling/wait state machine, bounded deadline, retry policy, cancellation path, or idempotency token.

**Recommendation:** model submitted/in-progress/completed/failed/stopped states explicitly; use bounded polling with jitter; define maximum orchestration duration; make retry behavior idempotent; and test state transitions.

### P1 — Training-data lineage is hard-coded

The supervisor sends a fixed S3 prefix to retraining.

**Recommendation:** make the approved dataset URI/config artifact explicit, hash or version the data manifest, record it in promotion evidence, and prevent promotion when lineage metadata is missing.

### P1 — Promotion metric is necessary but not sufficient

A single configured metric threshold is a useful guardrail, but it does not establish generalization, calibration, robustness, fairness, or operational fitness.

**Recommendation:** add held-out evaluation with deterministic split/versioning, multiple metrics appropriate to the task, confidence intervals where useful, calibration/threshold analysis, and explicit model-risk approval separate from automated metric gating.

### P1 — Deployment approval is not modeled

A promotable result should not directly imply endpoint deployment.

**Recommendation:** introduce a separate immutable promotion artifact and explicit approval/deployment stage with environment, model digest, approver/policy identity, smoke test, rollback target, and deployment evidence.

### P2 — IAM and network controls are documented but not evidenced

The repo expects reviewed credentials but does not demonstrate least-privilege policy analysis, VPC assumptions, endpoint policies, KMS controls, or secret-manager integration.

**Recommendation:** add example least-privilege policies, threat model, secret source contract, and a deployment checklist that distinguishes examples from validated infrastructure.

### P2 — Observability is file-oriented

`DailyLog.md` records coarse orchestration state, but there is no structured metrics/tracing contract for cloud calls, state transitions, retries, promotion decisions, or correlation IDs.

**Recommendation:** emit structured logs and metrics with redacted identifiers, orchestration/job correlation IDs, cloud-call duration, retry counts, state-transition counters, and normalized failure categories.

### P2 — Benchmark evidence is correctly conservative but incomplete

The current repo records promotion evidence/provenance rather than inventing model-quality or cloud-performance numbers. That is good discipline. However, future cloud benchmarks should include repeat counts, instance class, region, image digest, dataset hash, runtime, cost methodology, and uncertainty.

### P2 — Release provenance can be strengthened

The v1.0.0 release prep adds a source archive, SHA-256 checksum, and GHCR image.

**Recommendation:** attach an SBOM, image digest manifest, artifact attestation/provenance, and optional signature. Record the exact release commit and container digest in release notes.

## Strong senior-engineering signals already present

- Promotion logic fails closed on missing/non-finite metrics.
- Tests can run without AWS or Snowflake credentials.
- Credentials are not embedded in checked-in agent configuration.
- Promotion evidence records payload integrity and runtime/source metadata.
- The repository distinguishes CI fixture evidence from model-quality findings.
- Container packaging supports reproducible distribution.
- Semantic-tag release automation is now defined for source and GHCR artifacts.

## Recommended implementation sequence

1. Typed Snowflake unavailable/error semantics.
2. Real drift detector with versioned baseline and tests.
3. SageMaker polling/state machine with deadlines and idempotency.
4. Immutable dataset/model lineage in evidence records.
5. Held-out evaluation and model-risk promotion policy.
6. Explicit approval/deployment/rollback stage.
7. Structured observability and failure injection.
8. SBOM, image digests, and provenance attestations.

## v1.0.0 portfolio release gate

A v1.0.0 portfolio baseline is reasonable if the README continues to describe this as a governed MLOps orchestration prototype rather than a production deployment system. Require green PR checks and keep all model-quality/cloud-performance numbers evidence-backed or explicitly unreported.
