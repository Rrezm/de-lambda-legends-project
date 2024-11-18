import boto3
from pprint import pprint
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import io

s3 = boto3.client('s3')
bucket_name = "ingested-data-lambda-legends-24"
table_keys = [elem["Key"] for elem in s3.list_objects(Bucket=bucket_name)["Contents"]]
for key in table_keys:
    csv_object = s3.get_object(Bucket=bucket_name, Key=key)
    csv_content = s3.get_object(Bucket=bucket_name, Key=key)["Body"].read().decode('utf-8')
    dataframe = pd.read_csv(io.StringIO(csv_content))
    table = pa.Table.from_pandas(dataframe)
    parquet_buffer = io.BytesIO()
    pq.write_table(table, parquet_buffer)
    parquet_buffer.seek(0)
    parquet_key = key.replace('.csv', '.parquet')
    #print(parquet_buffer.getvalue())
    s3.put_object(Bucket='processed-data-lambda-legends-24', Key=parquet_key, Body=parquet_buffer.getvalue())