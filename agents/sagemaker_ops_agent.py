from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import boto3

from agents.metrics import evaluate_promotion

logger = logging.getLogger("MLOps_Supervisor.SageMakerAgent")


class SageMakerOpsAgent:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.sm_client = boto3.client("sagemaker", region_name=config["region"])

    def trigger_retraining(self, data_s3_uri: str) -> str:
        job_name = f"snowflake-pipeline-retrain-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.sm_client.create_training_job(
            TrainingJobName=job_name,
            AlgorithmSpecification={"TrainingImage": self.config["image_uri"], "TrainingInputMode": "File"},
            RoleArn=self.config["role_arn"],
            InputDataConfig=[{"ChannelName": "train", "DataSource": {"S3DataSource": {"S3DataType": "S3Prefix", "S3Uri": data_s3_uri, "S3DataDistributionType": "FullyReplicated"}}, "ContentType": "csv"}],
            OutputDataConfig={"S3OutputPath": self.config["s3_output_path"]},
            ResourceConfig={"InstanceType": self.config["instance_type"], "InstanceCount": self.config["instance_count"], "VolumeSizeInGB": 30},
            StoppingCondition={"MaxRuntimeInSeconds": 86400},
        )
        return job_name

    def verify_model_metrics(self, job_name: str) -> bool:
        try:
            description = self.sm_client.describe_training_job(TrainingJobName=job_name)
        except Exception:
            logger.exception("Unable to retrieve SageMaker training-job metrics.")
            return False
        if description.get("TrainingJobStatus") != "Completed":
            return False

        evidence = evaluate_promotion(
            description.get("FinalMetricDataList", []),
            self.config["validation_metric_name"],
            float(self.config["target_accuracy_threshold"]),
        )
        if not evidence["promotable"]:
            logger.warning("Training job %s did not satisfy promotion evidence: %s", job_name, evidence)
            return False
        return True
