from src.LOAD.lambda_load import connect_to_db1
from src.LOAD.lambda_load import input_data_psql
from unittest.mock import patch


@patch("src.LOAD.lambda_load.get_db_credentials")
def test_connect_to_db(mock_get_db_credentials):
    mock_get_db_credentials.return_value = {
        "user": "test_user",
        "password": "test_password",
        "database": "test_database",
        "host": "localhost",
        "port": "5432",
    }
    conn = connect_to_db1()
    assert conn is not None


@patch("src.LOAD.lambda_load.get_db_credentials")
@patch("src.LOAD.lambda_load.read_data")
def test_psql_empty(mock_read_data, mock_get_db_credentials):
    mock_get_db_credentials.return_value = {
        "user": "test_user",
        "password": "test_password",
        "database": "test_database",
        "host": "localhost",
        "port": "5432",
    }
    mock_read_data.return_value = {}
    result = input_data_psql({}, None)
    assert result is None
