# Changelog

All notable changes to AWS SageMaker + Snowflake MLOps Pipeline are documented here.

This project uses Semantic Versioning with tags in the form `vMAJOR.MINOR.PATCH`.

## [Unreleased]

No unreleased changes are currently documented.

## [1.0.0] - 2026-08-22

### Added

- L6 engineering audit with prioritized cloud/MLOps hardening gaps.
- README architecture and system-design Mermaid flowcharts.
- Clean-checkout Quickstart and reproducibility contract.
- Research-style metrics/evidence section that avoids invented model-quality numbers.
- Extended technical Q&A and explicit trust-boundary documentation.
- Semantic-tag release workflow.
- GitHub Release source archive plus SHA-256 checksum.
- GHCR container publishing for version tags and `latest`.

### Documentation corrections

- Clarified that the drift method is currently an example hook returning false, not a validated PSI implementation.
- Clarified that offline CI does not prove live AWS/Snowflake integration reliability.
- Clarified that a promotable training result is not equivalent to model deployment approval.
- Clarified that training latency, cost, ROC-AUC, calibration, drift quality, and fairness are not currently published as measured results.

### Known limitations

- Snowflake query failures can currently collapse to a zero-record result.
- SageMaker job lifecycle orchestration lacks a bounded polling/state-machine contract.
- Training-data lineage uses a fixed S3 path in the supervisor.
- No held-out model-quality study or production deployment/rollback evidence is included.
- Release artifacts do not yet include SBOM attachment or provenance attestations.
