from src.EXTRACT.put_data_s3 import put_data_in_s3
from moto import mock_aws
import boto3

@mock_aws
def test_files_are_put_in_s3():
    s3 = boto3.client("s3")
    bucket_name = "test_bucket"
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint':'eu-west-2'})
    put_data_in_s3(s3, bucket_name)
    object_list = s3.list_objects(Bucket=bucket_name)
    keys = [item["Key"] for item in object_list["Contents"]]
    expected_keys = ['address',
                     'counterparty',
                     'currency',
                     'department',
                     'design',
                     'payment',
                     'payment_type',
                     'purchase_order',
                     'sales_order',
                     'staff',
                     'transaction']
    assert keys == expected_keys
    currency = s3.get_object(Bucket=bucket_name, Key='currency')['Body'].read().decode('utf-8')
    expected_currency = ('currency_id,currency_code,created_at,last_updated\r\n'
                         '1,GBP,2022-11-03 14:20:49.962000,2022-11-03 14:20:49.962000\r\n'
                         '2,USD,2022-11-03 14:20:49.962000,2022-11-03 14:20:49.962000\r\n'
                         '3,EUR,2022-11-03 14:20:49.962000,2022-11-03 14:20:49.962000\r\n')
    assert currency == expected_currency