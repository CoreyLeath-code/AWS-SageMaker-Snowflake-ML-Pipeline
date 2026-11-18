"""Model inference helpers and non-destructive Snowflake prediction storage."""

from __future__ import annotations

import math
import os
from numbers import Integral

import joblib
import snowflake.connector


def load_model(model_path="models/fraud_detection_model.joblib"):
    """Load a trusted, pre-generated model artifact."""
    return joblib.load(model_path)


def predict(model, input_data):
    predictions = model.predict(input_data)
    probabilities = model.predict_proba(input_data)[:, 1]
    return predictions, probabilities


def write_predictions_to_snowflake(transaction_ids, predictions, probabilities):
    """Upsert validated fraud scores without deleting previously stored rows.

    A transaction ID identifies one prediction in this demo table. Production
    deployments need a warehouse-enforced deduplication/transaction strategy.
    """
    # Validate the *entire* batch before any database write is attempted.
    rows = list(zip(transaction_ids, predictions, probabilities, strict=True))
    if not rows:
        return

    prepared = []
    seen = set()
    for tx_id, prediction, probability in rows:
        if isinstance(tx_id, bool) or not isinstance(tx_id, Integral):
            raise ValueError("transaction IDs must be integers")
        key = int(tx_id)
        if key in seen:
            raise ValueError("duplicate transaction ID in batch")
        seen.add(key)

        if prediction not in (0, 1, False, True):
            raise ValueError("predictions must be binary")
        probability_value = float(probability)
        if not math.isfinite(probability_value) or not 0 <= probability_value <= 1:
            raise ValueError("fraud probabilities must be finite and within [0, 1]")
        prepared.append((key, bool(prediction), probability_value))

    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fraud_predictions (
                transaction_id INT,
                is_fraud_predicted BOOLEAN,
                fraud_probability FLOAT
            )
            """
        )
        merge_sql = """
            MERGE INTO fraud_predictions AS target
            USING (
                SELECT %s AS transaction_id,
                       %s AS is_fraud_predicted,
                       %s AS fraud_probability
            ) AS source
            ON target.transaction_id = source.transaction_id
            WHEN MATCHED THEN UPDATE SET
                is_fraud_predicted = source.is_fraud_predicted,
                fraud_probability = source.fraud_probability
            WHEN NOT MATCHED THEN INSERT
                (transaction_id, is_fraud_predicted, fraud_probability)
            VALUES
                (source.transaction_id, source.is_fraud_predicted,
                 source.fraud_probability)
        """
        for row in prepared:
            cursor.execute(merge_sql, row)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conn.close()
