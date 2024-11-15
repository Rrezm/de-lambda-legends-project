from src.EXTRACT.connection import get_db_credentials, connect_to_db, close_conn
import pytest
import boto3
from moto import mock_aws
import json

@mock_aws
def test_get_db_credentials_works():
    secret_name = "my-test-conn"
    secret_value = {"user":"test_user", 
                    "password": "test_password", 
                    "host": "test_host", 
                    "database": "test_database", 
                    "port": "test_port"}
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
    secret_value = {"user":"test_user", 
                    "password": "test_password", 
                    "host": "test_host", 
                    "database": "test_database", 
                    "port": "test_port"}
    secret_client = boto3.client("secretsmanager", region_name="eu-west-2")
    secret_client.create_secret(Name=secret_name, SecretString=json.dumps(secret_value))
    with pytest.raises(Exception, match=f"The secret was not found"):
        get_db_credentials(secret_name="1")

# @mock_aws
# def test_connect_to_db_works():
#     secret_name = "my-test-conn"
#     secret_value = {"user":"test_user", 
#                     "password": "test_password", 
#                     "host": "test_host", 
#                     "database": "test_database", 
#                     "port": "test_port"}
#     secret_client = boto3.client("secretsmanager", region_name="eu-west-2")
#     secret_client.create_secret(Name=secret_name, SecretString=json.dumps(secret_value))
#     conn = connect_to_db()
#     assert conn is not None
#     close_conn(conn)
