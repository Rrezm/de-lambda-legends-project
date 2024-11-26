from src.LOAD.lambda_load import connect_to_db1
from src.LOAD.lambda_load import input_data_psql
from unittest.mock import MagicMock, patch


@patch("src.LOAD.lambda_load.connect_to_db1")
def test_connect_to_db(mock_connect_to_db):
    mock_connect_to_db.return_value = MagicMock()
    conn = connect_to_db1()
    assert conn is not None


@patch("src.LOAD.lambda_load.read_data")
@patch("src.LOAD.lambda_load.connect_to_db1")
def test_psql_empty(mock_connect_to_db, mock_read_data):
    mock_connect_to_db.return_value = MagicMock()
    mock_read_data.return_value = {}
    result = input_data_psql({}, None)
    assert result is None
