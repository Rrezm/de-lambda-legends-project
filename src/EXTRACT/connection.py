from botocore.exceptions import ClientError
import boto3
import json
from pg8000 import DatabaseError
from pg8000.native import Connection
import logging

logger = logging.getLogger()
logger.setLevel("INFO")


def get_db_credentials(secret_name="db_credentials13"):
    """Retrieve database credentials from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name="eu-west-2")
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            raise Exception("The secret was not found") from e
    secret = response["SecretString"]
    credentials = json.loads(secret)
    return {
        "user": credentials["user"],
        "password": credentials["password"],
        "database": credentials["database"],
        "host": credentials["host"],
        "port": credentials["port"],
    }


def connect_to_db():
    """Establish connection to the database."""
    credentials = get_db_credentials()
    if not credentials:
        return "Failed to retrieve credentials"
    try:
        conn = Connection(
            user=credentials["user"],
            password=credentials["password"],
            database=credentials["database"],
            host=credentials["host"],
            port=credentials["port"],
        )
        return conn
    except DatabaseError as de:
        msg = "Error connecting to database"
        raise DatabaseError(msg) from de


def close_conn(conn):
    """Close the database connection."""
    conn.close()
