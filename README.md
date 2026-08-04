# AWS SageMaker + Snowflake MLOps Pipeline

[![Offline verification](https://github.com/CoreyLeath-code/AWS-SageMaker-Snowflake-ML-Pipeline/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CoreyLeath-code/AWS-SageMaker-Snowflake-ML-Pipeline/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/CoreyLeath-code/AWS-SageMaker-Snowflake-ML-Pipeline)](LICENSE)

A research-oriented example that monitors Snowflake metadata and conditionally requests an AWS SageMaker training job.

> This is not an approved automated deployment system. Do not connect it to production data, models, or credentials without independent security, model-risk, and operational review.

## Implemented controls

- Non-secret agent configuration is validated from `config/agent_config.yaml`; credentials remain environment-provided.
- Promotion fails closed: a completed SageMaker job must return a finite configured metric in `FinalMetricDataList`.
- Offline tests and GitHub Actions validate the configuration and decision logic without AWS or Snowflake access.
- A JSON evidence utility records the metric payload hash, source commit, runtime, threshold, and decision.

## Local verification

Python 3.11 is used in CI.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m compileall -q agents scripts tests
pytest -q
```

Running the supervisor requires reviewed AWS identity, Snowflake credentials, network access, IAM policy, and data-governance controls. The test suite does not make cloud calls.

## Reproducible metric evidence

The promotion policy reads `sagemaker.validation_metric_name` and `target_accuracy_threshold` from the checked-in configuration. It never substitutes a simulated score.

```bash
python -m scripts.record_metric_evidence \
  --config config/agent_config.yaml \
  --metrics-json path/to/final-metrics.json \
  --job-name training-job-name \
  --output evidence/promotion.json
```

The resulting JSON contains a SHA-256 hash of the supplied metrics payload, `GITHUB_SHA` when available, job name, Python/platform data, metric name/value, threshold, and promotion decision.

| Metric / benchmark | Status | Reproducible record |
|---|---|---|
| Promotion metric | Measured only from a SageMaker result | `promotion_evidence.metric_name`, `metric_value`, `threshold`, `promotable` |
| Input integrity | Measured | `metric_payload_sha256` |
| Source provenance | Measured | `training_commit` |
| Runner environment | Measured | `runner` |
| Training latency, cost, ROC-AUC, drift, fairness | Not published | Require approved dataset and environment-specific study |

No numeric model-quality result is published in this README. CI emits evidence using a fixed fixture only to verify the artifact format; it is not a model-quality finding.

## Configuration

Edit [config/agent_config.yaml](config/agent_config.yaml) for non-secret settings. Set `AGENT_CONFIG_PATH` to use another approved configuration. Keep secrets in an approved secret manager or environment; never commit them.

## Limitations

- A completed SageMaker job is not, by itself, deployment approval.
- The drift check is an example control, not a complete data-quality or fairness assessment.
- CI intentionally avoids cloud calls; cloud integration needs a separately governed environment.

## License

MIT.