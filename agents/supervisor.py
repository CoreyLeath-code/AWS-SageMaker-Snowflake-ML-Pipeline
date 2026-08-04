from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from agents.config import load_config
from agents.sagemaker_ops_agent import SageMakerOpsAgent
from agents.snowflake_monitor_agent import SnowflakeMonitorAgent

logger = logging.getLogger("MLOps_Supervisor")


class MLOpsSupervisor:
    def __init__(self, config: dict[str, dict[str, Any]]) -> None:
        self.config = config
        self.sf_agent = SnowflakeMonitorAgent(config["snowflake"])
        self.sm_agent = SageMakerOpsAgent(config["sagemaker"])

    def run_pipeline_orchestration(self) -> None:
        new_records = self.sf_agent.check_new_arrivals()
        drift_status = self.sf_agent.inspect_data_drift()
        if drift_status or new_records >= self.config["snowflake"]["min_new_records_trigger"]:
            try:
                job_id = self.sm_agent.trigger_retraining(
                    "s3://my-snowflake-sagemaker-pipeline-bucket/features/latest/"
                )
                status = "SUCCESS" if self.sm_agent.verify_model_metrics(job_id) else "WARNING"
                self.log_to_daily_file(status, f"Training job {job_id} completed promotion evaluation.")
            except Exception:
                logger.exception("Pipeline execution failed during cloud infrastructure work.")
                self.log_to_daily_file("FAILED", "Pipeline failed during infrastructure execution.")
        else:
            self.log_to_daily_file("IDLE", "Data volume and drift properties remain within policy.")

    def log_to_daily_file(self, status: str, message: str) -> None:
        entry = f"| {datetime.now().strftime('%Y-%m-%d %H:%M')} | {status} | {message} |\n"
        with Path("DailyLog.md").open("a", encoding="utf-8") as ledger:
            ledger.write(entry)


if __name__ == "__main__":
    config_path = os.getenv(
        "AGENT_CONFIG_PATH",
        Path(__file__).resolve().parents[1] / "config" / "agent_config.yaml",
    )
    MLOpsSupervisor(load_config(config_path)).run_pipeline_orchestration()
