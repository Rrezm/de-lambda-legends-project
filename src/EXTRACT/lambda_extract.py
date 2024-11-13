from pg8000.native import Connection
from dotenv import load_dotenv
import os
import boto3
import csv
import io

load_dotenv(override=True) ## states whether the existing os env variables(logins) should be overwritten by the .env file.

s3= boto3.client("s3")
bucket_name = "ingested-data-lambda-legends-24"

def connect_to_db():
    return Connection(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT"))
    )

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
    
def read_all_tables(bucket_name, s3):
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
     
    for name in table_names:
        read_and_put_data(name, bucket_name, s3)
