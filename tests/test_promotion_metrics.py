from agents.metrics import evaluate_promotion
from agents.sagemaker_ops_agent import SageMakerOpsAgent


class FakeSageMakerClient:
    def __init__(self, description):
        self.description = description

    def describe_training_job(self, **_kwargs):
        return self.description


def test_promotion_requires_a_named_finite_metric():
    evidence = evaluate_promotion(
        [{"MetricName": "validation:roc_auc", "Value": 0.91}],
        "validation:roc_auc",
        0.88,
    )

    assert evidence["promotable"] is True
    assert evidence["metric_value"] == 0.91
    assert evaluate_promotion([], "validation:roc_auc", 0.88)["promotable"] is False
    assert evaluate_promotion(
        [{"MetricName": "validation:roc_auc", "Value": "nan"}],
        "validation:roc_auc",
        0.88,
    )["promotable"] is False


def test_agent_fails_closed_for_missing_final_metric():
    agent = SageMakerOpsAgent.__new__(SageMakerOpsAgent)
    agent.config = {"validation_metric_name": "validation:roc_auc", "target_accuracy_threshold": 0.88}
    agent.sm_client = FakeSageMakerClient(
        {"TrainingJobStatus": "Completed", "FinalMetricDataList": []}
    )

    assert agent.verify_model_metrics("job-1") is False
