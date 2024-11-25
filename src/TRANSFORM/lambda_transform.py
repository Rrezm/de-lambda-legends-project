import boto3
import pandas as pd
import io
from datetime import datetime
import awswrangler as wr
import logging


logger = logging.getLogger()
logger.setLevel("INFO")


def transform_staff(df_dict):
    dim_staff_df = df_dict["staff_df"][
            ["staff_id", "first_name", "last_name", "email_address"]
        ]
    dim_staff_df["department_name"] = (
        df_dict["department_df"]["department_name"]
    )
    dim_staff_df["location"] = df_dict["department_df"]["location"]
    return dim_staff_df


def transform_counterparty(df_dict):
    dim_counterparty_df = df_dict["counterparty_df"][
            ["counterparty_id", "counterparty_legal_name"]
        ]
    dim_counterparty_df["counterparty_legal_address_line_1"] = (
        df_dict["address_df"]["address_line_1"]
    )
    dim_counterparty_df["counterparty_legal_address_line_2"] = (
        df_dict["address_df"]["address_line_2"]
    )
    dim_counterparty_df["counterparty_legal_district"] = (
        df_dict["address_df"]["district"]
    )
    dim_counterparty_df["counterparty_legal_city"] = (
        df_dict["address_df"]["city"]
    )
    dim_counterparty_df["counterparty_legal_postal_code"] = (
        df_dict["address_df"]["postal_code"]
    )
    dim_counterparty_df["counterparty_legal_country"] = (
        df_dict["address_df"]["country"]
    )
    dim_counterparty_df["counterparty_legal_phone_number"] = (
        df_dict["address_df"]["phone"]
    )
    return dim_counterparty_df


def transform_currency(df_dict):
    dim_currency_df = (
        df_dict["currency_df"][["currency_id", "currency_code"]]
    )
    dim_currency_df["currency_name"] = (
        df_dict["currency_df"]["currency_code"].replace(
            {'GBP': 'Pounds', 'USD': 'Dollars', 'EUR': 'Euros'}
        )
    )
    return dim_currency_df


def transform_design(df_dict):
    dim_design_df = df_dict["design_df"][[
                                "design_id",
                                "design_name",
                                "file_location",
                                "file_name"
                            ]]
    return dim_design_df


def transform_location(df_dict):
    dim_location_df = df_dict["address_df"][[
                                "address_line_1",
                                "address_line_2",
                                "district", "city",
                                "postal_code",
                                "country",
                                "phone"
                            ]]
    dim_location_df["location_id"] = df_dict["address_df"]["address_id"]
    dim_location_df = dim_location_df[
                                "location_id",
                                "address_line_1",
                                "address_line_2",
                                "district",
                                "city",
                                "postal_code",
                                "country",
                                "phone"
                            ]

    return dim_location_df


def transform_date():
    dim_time_df = pd.DataFrame(
        {"date_id": pd.date_range("2020-01-01", "2025-12-31")}
        )
    dim_time_df['year'] = dim_time_df['date_id'].dt.year
    dim_time_df['month'] = dim_time_df['date_id'].dt.month
    dim_time_df['day'] = dim_time_df['date_id'].dt.day
    dim_time_df['day_of_week'] = dim_time_df['date_id'].dt.dayofweek + 1
    dim_time_df['day_name'] = dim_time_df['date_id'].dt.day_name()
    dim_time_df['month_name'] = dim_time_df['date_id'].dt.month_name()
    dim_time_df['quarter'] = dim_time_df['date_id'].dt.quarter
    return dim_time_df


def transform_fact(df_dict):
    fact_sales_df = df_dict["sales_order_df"][[
                                        "sales_order_id",
                                        "counterparty_id",
                                        "units_sold",
                                        "unit_price",
                                        "currency_id",
                                        "design_id",
                                        "agreed_payment_date",
                                        "agreed_delivery_date",
                                        "agreed_delivery_location_id"
                                    ]]
    fact_sales_df["sales_staff_id"] = df_dict["sales_order_df"]["staff_id"]
    fact_sales_df.index.name = "sales_record_id"
    fact_sales_df["created_date"] = (
        df_dict["sales_order_df"]["created_at"].str.split(" ").str[0]
    )
    fact_sales_df["created_time"] = (
        df_dict["sales_order_df"]["created_at"].str.split(" ").str[1]
    )
    fact_sales_df["last_updated_date"] = (
        df_dict["sales_order_df"]["last_updated"].str.split(" ").str[0]
    )
    fact_sales_df["last_updated_time"] = (
        df_dict["sales_order_df"]["last_updated"].str.split(" ").str[1]
    )
    return fact_sales_df


def setup(s3, bucket_name):
    tk = [i["Key"] for i in s3.list_objects(Bucket=bucket_name)["Contents"]]
    df_dict = {}

    for key in tk:
        csv_content = s3.get_object(Bucket=bucket_name,
                                    Key=key)["Body"].read().decode('utf-8')
        name = key.split("/")[1][:-4]
        dataframe = pd.read_csv(io.StringIO(csv_content))
        df_dict[f"{name}_df"] = dataframe

    return df_dict


def lambda_handler(event, context):
    parquet_bucket_name = "processed-data-lambda-legends-24"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    folder_name = f"Tables_at_{timestamp}"
    try:
        logger.info("Getting individual tables and transforming")
        s3 = boto3.client('s3')
        bucket_name = "ingested-data-lambda-legends-24"
        df_dict = setup(s3, bucket_name)
        df_list = []
        df_list.append(("counterparty", transform_counterparty(df_dict)))
        df_list.append(("currency", transform_currency(df_dict)))
        df_list.append(("staff", transform_staff(df_dict)))
        df_list.append(("date", transform_date()))
        df_list.append(("design", transform_design(df_dict)))
        df_list.append(("fact", transform_fact(df_dict)))
        df_list.append(("location", transform_location(df_dict)))
        for name, dataframe in df_list:
            wr.s3.to_parquet(
                        path=(
                            f"s3://{parquet_bucket_name}/{folder_name}/{name}"
                        ),
                        df=dataframe, dataset=True
                    )
        logger.info(f"Successfully uploaded to {parquet_bucket_name}")
    except Exception as e:
        logger.error(f"Error with transformation occurred with {e}")
