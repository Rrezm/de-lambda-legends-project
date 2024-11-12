import os
from src.EXTRACT.read_data import read_all_tables
import boto3

s3 = boto3.client('s3')
bucket_name = "ingested-data-lambda-legends-24"

def put_data_in_s3(s3, bucket_name):
    read_all_tables()
    file_names = os.listdir(path='data')
    for file_name in file_names:
        name = file_name.split('.')[0]
        s3.upload_file(f'data/{file_name}', bucket_name, name)
