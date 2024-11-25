from pg8000.native import Connection
import boto3
import json
import io
from botocore.exceptions import ClientError
from pg8000 import DatabaseError
import logging
from datetime import datetime
import pandas as pd

logger = logging.getLogger()
logger.setLevel("INFO")


def get_db_credentials(secret_name="db_credentials23"):
    """Retrieve datawarehouse credentials from AWS Secrets Manager."""
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


def connect_to_db1():
    """Establish connection to the database."""
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


def read_data():
    s3 = boto3.client('s3')
    bucket_name = "processed-data-lambda-legends-24"
    tk = [i["Key"] for i in s3.list_objects(Bucket=bucket_name)["Contents"]]
    latest_date = max(
        tk,
        key=lambda x: datetime.strptime(x.split("/")[0][10:],
                                        "%Y-%m-%d_%H:%M:%S")
    )
    latest_keys = [
        key for key in tk if latest_date.split("/")[0] in key
    ]
    df_dict = {}

    for key in latest_keys:
        parquet_content = s3.get_object(Bucket=bucket_name,
                                        Key=key)["Body"].read()
        df = pd.read_parquet(io.BytesIO(parquet_content))
        df = df.fillna("None")
        table_name = key.split("/")[1]
        df_dict[table_name] = df

    return df_dict


def input_data_psql(event, context):
    conn = connect_to_db1()
    try:
        logger.info("Getting individual tables and loading into datawarehouse")
        df_dict = read_data()
        conn.run("DELETE FROM fact_sales_order;")
        conn.run("DELETE FROM dim_staff;")
        conn.run("DELETE FROM dim_counterparty;")
        conn.run("DELETE FROM dim_currency;")
        conn.run("DELETE FROM dim_design;")
        conn.run("DELETE FROM dim_location;")
        conn.run("DELETE FROM dim_date;")

        for index, row in df_dict["staff"].iterrows():
            conn.run("""INSERT INTO dim_staff (
                    staff_id, first_name, last_name,
                    department_name, location, email_address
                    )
                        VALUES (:si, :fn, :ln, :dn, :l, :ea);
                    """,
                    si=row["staff_id"],
                    fn=row["first_name"],
                    ln=row["last_name"],
                    dn=row["department_name"],
                    l=row["location"],
                    ea=["email_address"])

        for index, row in df_dict["counterparty"].iterrows():
            conn.run("""INSERT INTO dim_counterparty (
                    counterparty_id,
                    counterparty_legal_name,
                    counterparty_legal_address_line_1,
                    counterparty_legal_address_line_2,
                    counterparty_legal_district,
                    counterparty_legal_city,
                    counterparty_legal_postal_code,
                    counterparty_legal_country,
                    counterparty_legal_phone_number
                    )
                        VALUES (
                    :ci, :cln, :clal1, :clal2, :cld,
                    :clc, :clpc, :clcountry, :clpn
                    );
                    """,
                    ci=row["counterparty_id"],
                    cln=row["counterparty_legal_name"],
                    clal1=row["counterparty_legal_address_line_1"],
                    clal2=row["counterparty_legal_address_line_2"],
                    cld=row["counterparty_legal_district"],
                    clc=row["counterparty_legal_city"],
                    clpc=row["counterparty_legal_postal_code"],
                    clcountry=row["counterparty_legal_country"],
                    clpn=row["counterparty_legal_phone_number"])

        for index, row in df_dict["currency"].iterrows():
            conn.run("""INSERT INTO dim_currency (
                    currency_id, currency_code, currency_name
                    )
                        VALUES (:ci, :cc, :cn);
                    """,
                    ci=row["currency_id"],
                    cc=row["currency_code"],
                    cn=row["currency_name"])

        for index, row in df_dict["design"].iterrows():
            conn.run("""INSERT INTO dim_design (
                    design_id, design_name, file_location, file_name
                    )
                        VALUES (:di, :dn, :fl, :fn);
                    """,
                    di=row["design_id"],
                    dn=row["design_name"],
                    fl=row["file_location"],
                    fn=row["file_name"])

        for index, row in df_dict["location"].iterrows():
            conn.run("""INSERT INTO dim_location (
                    location_id, address_line_1, address_line_2,
                    district, city, postal_code, country, phone
                    )
                        VALUES (:li, :al1, :al2, :d, :c, :pc, :country, :p);
                    """,
                    li=row["location_id"],
                    al1=row["address_line_1"],
                    al2=row["address_line_2"],
                    d=row["district"],
                    c=row["city"],
                    pc=row["postal_code"],
                    country=row["country"],
                    p=["phone"])

        for index, row in df_dict["date"].iterrows():
            conn.run("""INSERT INTO dim_date (
                    date_id, year, month, day,
                    day_of_week, day_name, month_name, quarter
                    )
                        VALUES (:di, :y, :m, :d, :dow, :dn, :mn, :q);
                    """,
                    di=row["date_id"],
                    y=row["year"],
                    m=row["month"],
                    d=row["day"],
                    dow=row["day_of_week"],
                    dn=["day_name"],
                    mn=row["month_name"],
                    q=row["quarter"])

        for index, row in df_dict["fact"].iterrows():
            conn.run("""INSERT INTO fact_sales_order
                    (sales_order_id, created_date,
                    created_time, last_updated_date,
                    last_updated_time, sales_staff_id,
                    counterparty_id, units_sold, unit_price,
                    currency_id, design_id, agreed_payment_date,
                    agreed_delivery_date, agreed_delivery_location_id)
                        VALUES (
                    :soi, :cd, :ct, :lud, :lut, :ssi,
                    :ci, :us, :up, :currencyi, :di, :apd, :add, :adli);
                    """,
                    soi=row["sales_order_id"],
                    cd=row["created_date"],
                    ct=row["created_time"],
                    lud=row["last_updated_date"],
                    lut=row["last_updated_time"],
                    ssi=row["sales_staff_id"],
                    ci=row["counterparty_id"],
                    us=row["units_sold"],
                    up=row["unit_price"],
                    currencyi=row["currency_id"],
                    di=row["design_id"],
                    apd=row["agreed_payment_date"],
                    add=row["agreed_delivery_date"],
                    adli=row["agreed_delivery_location_id"])

        close_conn(conn)
        logger.info(f"Successfully uploaded to the datawarehouse")
        
    except Exception as e:
        logger.error(f"Error with transformation occurred with {e}")
