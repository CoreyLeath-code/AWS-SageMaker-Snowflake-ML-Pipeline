from pathlib import Path

import pytest

from agents.config import load_config


def test_repository_config_has_required_non_secret_fields():
    config = load_config(Path(__file__).parents[1] / "config" / "agent_config.yaml")

    assert config["sagemaker"]["validation_metric_name"] == "validation:roc_auc"
    assert config["snowflake"]["min_new_records_trigger"] == 10000


def test_config_rejects_missing_required_fields(tmp_path):
    path = tmp_path / "invalid.yaml"
    path.write_text("snowflake: {}\nsagemaker: {}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing"):
        load_config(path)
