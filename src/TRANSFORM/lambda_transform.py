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

dim_counterparty_df = df_dict["counterparty_df"][["counterparty_id", "counterparty_legal_name"]]
dim_counterparty_df["counterparty_legal_address_line_1"] = df_dict["address_df"][["address_line_1"]]
dim_counterparty_df["counterparty_legal_address_line_2"] = df_dict["address_df"][["address_line_2"]]
dim_counterparty_df["counterparty_legal_district"] = df_dict["address_df"][["district"]]
dim_counterparty_df["counterparty_legal_city"] = df_dict["address_df"][["city"]]
dim_counterparty_df["counterparty_legal_postal_code"] = df_dict["address_df"][["postal_code"]]
dim_counterparty_df["counterparty_legal_country"] = df_dict["address_df"][["country"]]
dim_counterparty_df["counterparty_legal_phone_number"] = df_dict["address_df"][["phone"]]

dim_currency_df = df_dict["currency_df"][["currency_id", "currency_code"]] #currency name

dim_design_df = df_dict["design_df"][["design_id", "design_name", "file_location", "file_name"]]

dim_location_df = df_dict["address_df"][["address_line_1", "address_line_2", "district", "city", "postal_code", "country", "phone"]]
dim_location_df["location_id"] = df_dict["sales_order_df"][["agreed_delivery_location_id"]]
dim_location_df = dim_location_df[["location_id", "address_line_1", "address_line_2", "district", "city", "postal_code", "country", "phone"]]

# dim_date_df = df_dict["sales_order_df"][[]]
# dim_date_df = df_dict["sales_order_df"][[]]
#print(df_dict["sales_order_df"])
# print(dim_location_df)
# print(dim_counterparty_df)

fact_sales_df = df_dict["sales_order_df"][["sales_order_id", "counterparty_id", "units_sold", "unit_price", "currency_id", "agreed_payment_date", "agreed_delivery_date", "agreed_delivery_location_id"]] # needs create dates
fact_sales_df["sales_staff_id"] = df_dict["sales_order_df"][["staff_id"]]
fact_sales_df.index.name = "sales_record_id"
print(fact_sales_df)

#     table = pa.Table.from_pandas(dataframe)
#     parquet_buffer = io.BytesIO()
#     pq.write_table(table, parquet_buffer)
#     parquet_buffer.seek(0)
#     parquet_key = key.replace('.csv', '.parquet')
#     #print(parquet_buffer.getvalue())
#     s3.put_object(Bucket='processed-data-lambda-legends-24', Key=parquet_key, Body=parquet_buffer.getvalue())