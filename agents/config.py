from pathlib import Path
from typing import Any

import yaml

_REQUIRED_FIELDS = {
    "snowflake": {"account", "warehouse", "database", "schema", "table_name", "drift_threshold_psi", "min_new_records_trigger"},
    "sagemaker": {"region", "role_arn", "image_uri", "instance_type", "instance_count", "s3_output_path", "target_accuracy_threshold", "validation_metric_name"},
}


def load_config(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load non-secret agent configuration and reject incomplete settings."""

    with Path(path).open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    if not isinstance(config, dict):
        raise ValueError("Agent configuration must be a mapping")

    validated: dict[str, dict[str, Any]] = {}
    for section, required_fields in _REQUIRED_FIELDS.items():
        values = config.get(section)
        if not isinstance(values, dict):
            raise ValueError(f"Configuration section {section!r} must be a mapping")
        missing = required_fields.difference(values)
        if missing:
            raise ValueError(f"Configuration section {section!r} is missing: {', '.join(sorted(missing))}")
        validated[section] = values
    return validated
