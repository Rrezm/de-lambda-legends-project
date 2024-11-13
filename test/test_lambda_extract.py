from src.EXTRACT.lambda_extract import read_and_put_data, read_all_tables, connect_to_db, close_conn
from moto import mock_aws
import boto3
from pprint import pprint

@mock_aws
def test_extract():
    s3 = boto3.client("s3", region_name='eu-west-2')
    s3.create_bucket(Bucket="test-bucket", CreateBucketConfiguration={'LocationConstraint':'eu-west-2'})
    read_and_put_data('staff', "test-bucket", s3)
    staff = s3.get_object(Bucket='test-bucket', Key='staff.csv')['Body'].read().decode('utf-8')
    assert 'staff_id,first_name,last_name,department_id,email_address,created_at,last_updated' in staff


@mock_aws
def test_files_are_put_in_s3():
    s3 = boto3.client("s3", region_name='eu-west-2')
    bucket_name = 'test-bucket'
    s3.create_bucket(Bucket="test-bucket", CreateBucketConfiguration={'LocationConstraint':'eu-west-2'})
    read_all_tables(bucket_name, s3)
    table_names = s3.list_objects(Bucket='test-bucket')
    assert len(table_names['Contents']) == 11

