import boto3
import os
from read_data import read_all_tables

def put_data_in_s3():
    s3 = boto3.client("s3")
    read_all_tables()
    files = os.listdir(path='data')
    for file in files:
        s3.put_object(Bucket=)