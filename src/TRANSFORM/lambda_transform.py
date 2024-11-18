import boto3
from pprint import pprint
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import io

s3 = boto3.client('s3')
bucket_name = "ingested-data-lambda-legends-24"
table_keys = [elem["Key"] for elem in s3.list_objects(Bucket=bucket_name)["Contents"]]
df_dict = {}

for key in table_keys:
    csv_object = s3.get_object(Bucket=bucket_name, Key=key)
    csv_content = s3.get_object(Bucket=bucket_name, Key=key)["Body"].read().decode('utf-8')
    name = key.split("/")[1][:-4]
    dataframe = pd.read_csv(io.StringIO(csv_content))
    df_dict[f"{name}_df"] = dataframe

dim_staff_df = df_dict["staff_df"][["staff_id", "first_name", "last_name", "email_address"]]
dim_staff_df["department_name"] = df_dict["department_df"][["department_name"]]
dim_staff_df["location"] = df_dict["department_df"][["location"]]

print(dim_staff_df)

#     table = pa.Table.from_pandas(dataframe)
#     parquet_buffer = io.BytesIO()
#     pq.write_table(table, parquet_buffer)
#     parquet_buffer.seek(0)
#     parquet_key = key.replace('.csv', '.parquet')
#     #print(parquet_buffer.getvalue())
#     s3.put_object(Bucket='processed-data-lambda-legends-24', Key=parquet_key, Body=parquet_buffer.getvalue())