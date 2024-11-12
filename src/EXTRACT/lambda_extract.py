from pg8000.native import Connection
from dotenv import load_dotenv
import os
import boto3
import csv

load_dotenv(override=True) ## states whether the existing os env variables(logins) should be overwritten by the .env file.

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


def read_data(table_name):
    conn = connect_to_db() # connects to the DB created in previous file 
    result =  conn.run(f"SELECT * FROM {table_name};") # queries all row from 
    keys = conn.run(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';") # retrives column names/headers for the table
    close_conn(conn)

    new_keys = [i for key in keys for i in key] # Flattens the list so the csv writer does not enounter any issues, otherwise it will appear as tuples 
    with open(f'/tmp/{table_name}.csv', 'w', newline='') as csvfile: # creates csv file in write mode 
        writer = csv.writer(csvfile) # creates csv writer object 
        writer.writerow(new_keys) # writes the headers(column names) as the first row 
        writer.writerows(result) # writes all rows of data from the specified table row by row 

    
def read_all_tables():
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
        read_data(name)



def put_data_in_s3(event, context):
    s3 = boto3.client('s3')
    bucket_name = "ingested-data-lambda-legends-24"
    read_all_tables()
    file_names = os.listdir(path='data')
    for file_name in file_names:
        name = file_name.split('.')[0]
        s3.upload_file(f'/tmp/{file_name}', bucket_name, name)