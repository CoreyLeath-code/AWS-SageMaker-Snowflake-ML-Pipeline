# tests/test_model_inference.py

import numpy as np
import pandas as pd
from unittest.mock import MagicMock
from src import model_inference


def test_predict_output():
    """
    Smoke-test: create a mock model and verify predict returns correct shape.
    """
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0, 1])
    mock_model.predict_proba.return_value = np.array([[0.9, 0.1], [0.2, 0.8]])

    test_input = pd.DataFrame(
        [[100.0, 0.2, 1, 0, 0]],
        columns=[
            'amount', 'feature2',
            'transaction_type_purchase',
            'transaction_type_transfer',
            'transaction_type_cash_withdrawal'
        ]
    )

    preds, probas = model_inference.predict(mock_model, test_input)
    assert preds is not None
    assert probas is not None


def test_write_predictions_upserts_without_replacing_table(monkeypatch):
    connection = MagicMock()
    monkeypatch.setattr(model_inference.snowflake.connector, "connect", MagicMock(return_value=connection), raising=False)

    model_inference.write_predictions_to_snowflake([101, 102], [0, 1], [0.2, 0.8])

    statements = connection.cursor.return_value.execute.call_args_list
    assert "CREATE TABLE IF NOT EXISTS" in statements[0].args[0]
    assert "CREATE OR REPLACE" not in statements[0].args[0]
    assert all("MERGE INTO fraud_predictions" in c.args[0] for c in statements[1:])
    assert [c.args[1] for c in statements[1:]] == [
        (101, False, 0.2),
        (102, True, 0.8),
    ]
    connection.commit.assert_called_once()
    connection.close.assert_called_once()


def test_write_predictions_rejects_bad_batch_before_opening_connection(monkeypatch):
    import pytest

    connector = MagicMock()
    monkeypatch.setattr(model_inference.snowflake.connector, "connect", connector, raising=False)
    for ids, preds, scores in [
        ([1], [0, 1], [0.2]),
        ([1, 1], [0, 1], [0.1, 0.9]),
        ([1], [1], [float("nan")]),
        ([1], [1], [1.01]),
        ([1], [2], [0.5]),
    ]:
        with pytest.raises(ValueError):
            model_inference.write_predictions_to_snowflake(ids, preds, scores)
    connector.assert_not_called()


def test_write_predictions_rolls_back_and_closes_on_error(monkeypatch):
    import pytest

    connection = MagicMock()
    connection.cursor.return_value.execute.side_effect = RuntimeError("warehouse error")
    monkeypatch.setattr(model_inference.snowflake.connector, "connect", MagicMock(return_value=connection), raising=False)

    with pytest.raises(RuntimeError, match="warehouse error"):
        model_inference.write_predictions_to_snowflake([101], [1], [0.75])

    connection.rollback.assert_called_once()
    connection.close.assert_called_once()
