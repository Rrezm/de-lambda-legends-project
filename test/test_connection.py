from unittest.mock import patch, MagicMock
from src.EXTRACT.connection import get_db_credentials, connect_to_db
import pytest
from pg8000 import DatabaseError
import boto3
from moto import mock_aws
import json


@mock_aws
def test_get_db_credentials_works():
    secret_name = "my-test-conn"
    secret_value = {
        "user": "test_user",
        "password": "test_password",
        "host": "test_host",
        "database": "test_database",
        "port": "test_port",
    }
    secret_client = boto3.client("secretsmanager", region_name="eu-west-2")
    secret_client.create_secret(Name=secret_name, SecretString=json.dumps(secret_value))
    result = get_db_credentials(secret_name="my-test-conn")
    assert result == secret_value
    assert result["user"] == "test_user"
    assert result["password"] == "test_password"
    assert result["host"] == "test_host"
    assert result["database"] == "test_database"
    assert result["port"] == "test_port"


@mock_aws
def test_get_db_credentions_with_error():
    secret_name = "my-test-conn"
    secret_value = {
        "user": "test_user",
        "password": "test_password",
        "host": "test_host",
        "database": "test_database",
        "port": "test_port",
    }
    secret_client = boto3.client("secretsmanager", region_name="eu-west-2")
    secret_client.create_secret(Name=secret_name, SecretString=json.dumps(secret_value))
    with pytest.raises(Exception, match="The secret was not found"):
        get_db_credentials(secret_name="1")


@patch("src.EXTRACT.connection.Connection")
@patch("src.EXTRACT.connection.get_db_credentials")
def test_connect_to_db_success(mock_get_db_credentials, mock_pg8000_connect):
    mock_get_db_credentials.return_value = {
        "user": "test_user",
        "password": "test_password",
        "host": "test_host",
        "database": "test_database",
        "port": 5432,
    }
    mock_conn = MagicMock()
    mock_pg8000_connect.return_value = mock_conn
    conn = connect_to_db()
    mock_get_db_credentials.assert_called_once()
    mock_pg8000_connect.assert_called_once_with(
        user="test_user",
        password="test_password",
        host="test_host",
        database="test_database",
        port=5432,
    )
    assert conn == mock_conn


@patch("src.EXTRACT.connection.get_db_credentials")
def test_connect_to_db_no_credentials(mock_get_db_credentials):
    mock_get_db_credentials.return_value = None
    result = connect_to_db()
    mock_get_db_credentials.assert_called_once()
    assert result == "Failed to retrieve credentials"


@patch("src.EXTRACT.connection.Connection")
@patch("src.EXTRACT.connection.get_db_credentials")
def test_connect_with_error(mock_get_db_credentials, mock_pg8000_connect):
    mock_get_db_credentials.return_value = {
        "user": "test_user",
        "password": "test_password",
        "host": "test_host",
        "database": "test_database",
        "port": 5432,
    }
    mock_pg8000_connect.side_effect = DatabaseError("Connection failed")
    with pytest.raises(DatabaseError) as excinfo:
        connect_to_db()
    mock_get_db_credentials.assert_called_once()
    mock_pg8000_connect.assert_called_once_with(
        user="test_user",
        password="test_password",
        host="test_host",
        database="test_database",
        port=5432,
    )
    assert str(excinfo.value) == "Error connecting to database"
