from pg8000.native import Connection
import boto3
import csv
import json
import io
from botocore.exceptions import ClientError
from pg8000 import DatabaseError
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel("INFO")


def get_db_credentials(secret_name="db_credentials22"):
    """
    Retrieve database credentials from AWS Secrets Manager.
    Raise error if not able to get secret.

            Parameters:
                    secret_name: Name of the secret in AWS secrets manager,
                                 default is db_credentials22.

            Returns:
                    Credentials for the database.
    """
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
    """
    Establish connection to the database using the get_db_credentials function.

            Returns:
                    pg8000.native connection which is used to run sql queries.
    """
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


def read_and_put_data(table_name, bucket_name, s3, folder_name):
    """
    Connect to database, extract the data using sql queries,
    convert query return to csv format and save to the S3 bucket

            Parameters:
                    table_name: Name of the table to get the data from.
                    bucket_name: Name of the bucket to put the data into.
                    s3: boto3 s3 client.
                    folder_name: Name of folder with timestamp.

            Returns:
                    No returns, only putting the data into S3.
    """
    conn = connect_to_db()  # Connects to the database
    result = conn.run(f"SELECT * FROM {table_name};")  # Queries all rows
    keys = conn.run(
        """SELECT column_name FROM information_schema.columns
        WHERE table_name = :tn;""", tn=table_name
    )  # Retrieves column names
    close_conn(conn)

    new_keys = [i for key in keys for i in key]  # Flatten the list
    csv_buffer = io.StringIO()  # Creates an in-memory file-like object
    writer = csv.writer(csv_buffer)  # Creates a CSV writer object
    writer.writerow(new_keys)  # Writes headers (column names)
    writer.writerows(result)  # Writes all rows of data

    csv_buffer.seek(0)  # Resets the file pointer
    file_name = f"{folder_name}/{table_name}.csv"
    s3.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=csv_buffer.getvalue(),
    )


def read_all_tables(event, context):
    """
    Read multiple tables and upload them all to an S3 bucket.
    Have a timestamp to group each extraction by time.

            Parameters:
                    event: Data that is passed to the function.
                    context: Information about the function configuration.

            Returns:
                    No returns, only putting the data into S3.
    """
    table_names = [
        "counterparty",
        "currency",
        "department",
        "design",
        "staff",
        "sales_order",
        "address",
        "payment",
        "purchase_order",
        "payment_type",
        "transaction",
    ]

    s3 = boto3.client("s3")
    bucket_name = "ingested-data-lambda-legends-24"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    folder_name = f"Tables_at_{timestamp}"
    try:
        logger.info("Getting individual tables and loading them to bucket")
        for name in table_names:
            read_and_put_data(name, bucket_name, s3, folder_name)
        logger.info(f"Successfully uploaded to {bucket_name}")
    except Exception as e:
        logger.error(f"Error with extraction occurred with {e}")
