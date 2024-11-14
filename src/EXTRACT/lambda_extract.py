from pg8000.native import Connection
from dotenv import load_dotenv
import os
import boto3
import csv
import json
import io
from botocore.exceptions import ClientError
from pg8000 import DatabaseError
import logging

logger = logging.getLogger()
logger.setLevel("INFO")


def get_db_credentials(secret_name="db_credentials9"):
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
        conn = Connection(user=credentials["user"],
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


def read_and_put_data(table_name, bucket_name, s3):
    conn = connect_to_db() # connects to the DB created in previous file 
    result =  conn.run(f"SELECT * FROM {table_name};") # queries all row from 
    keys = conn.run(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';") # retrives column names/headers for the table
    close_conn(conn)

    new_keys = [i for key in keys for i in key] # Flattens the list so the csv writer does not enounter any issues, otherwise it will appear as tuples 
    csv_buffer = io.StringIO() #creates an in-memory file-like object
    writer = csv.writer(csv_buffer) # creates csv writer object
    writer.writerow(new_keys) # writes the headers(column names) as the first row 
    writer.writerows(result) # writes all rows of data from the specified table row by row 

    csv_buffer.seek(0) #moves the file pointer back to the beginning
    s3.put_object(
        Bucket=bucket_name,
        Key=f"{table_name}.csv",
        Body=csv_buffer.getvalue()
    )
    
def read_all_tables(event, context):
    table_names = ['counterparty',
                'currency',
                'department',
                'design',
                'staff',
                'sales_order',
                'address',
                'payment',
                'purchase_order',
                'payment_type',
                'transaction']
    
    s3= boto3.client("s3")
    bucket_name = "ingested-data-lambda-legends-24"

    for name in table_names:
        read_and_put_data(name, bucket_name, s3)
    logger.info('Success')


