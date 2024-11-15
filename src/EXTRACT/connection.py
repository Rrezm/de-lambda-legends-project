from pg8000.native import Connection
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import json
import pg8000
from pg8000 import DatabaseError

def get_db_credentials(secret_name="credentials11"):
    client = boto3.client("secretsmanager", region_name="eu-west-2")
    try:   #try to receive the secret
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            raise Exception(f"The secret was not found") from e
    secret = response["SecretString"]
    credentials = json.loads(secret)
    return {
        "user": credentials["user"],
        "password": credentials["password"],
        "database": credentials["database"],
        "host": credentials["host"],
        "port": credentials["port"]
    }

def connect_to_db():
    credentials = get_db_credentials()
    if not credentials:
        return "Failed to retrieve credentials"
    try:
        conn = pg8000.connect(user=credentials["user"],
                              password=credentials["password"],
                              database=credentials["database"],
                              host=credentials["host"],
                              port=credentials["port"])
        return conn
    except pg8000.DatabaseError as de:
        msg = "Error connecting to database"
        raise DatabaseError(msg) from de

def close_conn(conn):
    conn.close()
