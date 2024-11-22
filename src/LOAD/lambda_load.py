from pg8000.native import Connection
import boto3
import csv
import json
import io
from botocore.exceptions import ClientError
from pg8000 import DatabaseError
import logging
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd

logger = logging.getLogger()
logger.setLevel("INFO")


def get_db_credentials(secret_name="db_credentials22"):
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


def connect_to_db1():
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

# def connect_to_db():
#     credentials = get_db_credentials()
#     if not credentials:
#         raise Exception("Failed to retrieve credentials")
#     try:
#         connection_string = (
#             f"postgresql+pg8000://{credentials['user']}:{credentials['password']}@"
#             f"{credentials['host']}:{credentials['port']}/{credentials['database']}"
#         )
#         engine = create_engine(connection_string)
#         return engine
#     except Exception as e:
#         msg = "Error connecting to database"
#         raise Exception(msg) from e


def close_conn(conn):
    """Close the database connection."""
    conn.close()


def read_data():
    engine = connect_to_db1()
    s3 = boto3.client('s3')
    bucket_name = "processed-data-lambda-legends-24"
    table_keys = [elem["Key"] for elem in s3.list_objects(Bucket=bucket_name)["Contents"]]

    for key in table_keys:
        parquet_content = s3.get_object(Bucket=bucket_name, Key=key)["Body"].read()
        df = pd.read_parquet(io.BytesIO(parquet_content))
        table_name = key.split("/")[1]
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False
        )

read_data()
# conn = connect_to_db1()
# print(conn.run('SELECT * FROM counterparty'))