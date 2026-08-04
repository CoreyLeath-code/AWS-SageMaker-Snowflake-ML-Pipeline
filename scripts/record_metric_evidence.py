from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agents.config import load_config
from agents.metrics import evaluate_promotion


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/agent_config.yaml")
    parser.add_argument("--metrics-json", required=True)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def _final_metrics(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        payload = payload.get("FinalMetricDataList", payload)
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ValueError("Metric payload must be a list or contain FinalMetricDataList")
    return payload


def main() -> None:
    args = _parse_args()
    config = load_config(args.config)["sagemaker"]
    source = Path(args.metrics_json)
    raw = source.read_bytes()
    record = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "training_commit": os.getenv("GITHUB_SHA", "local-uncommitted"),
        "job_name": args.job_name,
        "metric_payload_sha256": hashlib.sha256(raw).hexdigest(),
        "runner": {"python": platform.python_version(), "platform": platform.platform()},
        "promotion_evidence": evaluate_promotion(
            _final_metrics(json.loads(raw)),
            config["validation_metric_name"],
            float(config["target_accuracy_threshold"]),
        ),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
