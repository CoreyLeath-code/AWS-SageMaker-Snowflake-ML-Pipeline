import math
from collections.abc import Iterable, Mapping
from typing import Any


def extract_finite_metric(final_metrics: Iterable[Mapping[str, Any]], metric_name: str) -> float | None:
    """Return a named finite metric from SageMaker's FinalMetricDataList."""

    for metric in final_metrics:
        if metric.get("MetricName") != metric_name:
            continue
        try:
            value = float(metric["Value"])
        except (KeyError, TypeError, ValueError):
            return None
        return value if math.isfinite(value) else None
    return None


def evaluate_promotion(
    final_metrics: Iterable[Mapping[str, Any]], metric_name: str, threshold: float
) -> dict[str, float | str | bool | None]:
    """Evaluate a configured metric without inventing a fallback measurement."""

    metric_value = extract_finite_metric(final_metrics, metric_name)
    return {"metric_name": metric_name, "metric_value": metric_value, "threshold": threshold, "promotable": metric_value is not None and metric_value >= threshold}
