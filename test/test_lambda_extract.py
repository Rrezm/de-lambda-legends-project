from src.EXTRACT.lambda_extract import read_and_put_data, read_all_tables
from moto import mock_aws
from unittest.mock import patch, MagicMock
import boto3
import pytest
from pprint import pprint

@mock_aws
@patch("src.EXTRACT.lambda_extract.get_db_credentials")
@patch("src.EXTRACT.lambda_extract.connect_to_db")
def test_extract(mock_connect_to_db, mock_get_db_credentials):
    mock_get_db_credentials.return_value = {
        "user": "test_user",
        "password": "test_password",
        "host": "test_host",
        "database": "test_database",
        "port": 5432,
    }
    mock_connection = MagicMock()
    mock_connect_to_db.return_value = mock_connection
    mock_connection.run.side_effect = [
        [("staff_id", "first_name")],  
        [(1, "Test1"), (2, "Test2")],  
    ]
    s3 = boto3.client("s3", region_name="eu-west-2")
    s3.create_bucket(Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
    read_and_put_data("staff", "test-bucket", s3, "test_folder")
    objects = s3.list_objects_v2(Bucket="test-bucket")
    assert "Contents" in objects 
    uploaded_file_key = objects["Contents"][0]["Key"]
    response = s3.get_object(Bucket="test-bucket", Key=uploaded_file_key)
    staff = response["Body"].read().decode("utf-8")
    assert "staff_id,first_name", "1,Test1" and "2,Test2" in staff


# @mock_aws
# def test_files_are_put_in_s3():
#     s3 = boto3.client("s3", region_name='eu-west-2')
#     bucket_name = 'test-bucket'
#     s3.create_bucket(Bucket="test-bucket", CreateBucketConfiguration={'LocationConstraint':'eu-west-2'})
#     read_all_tables(bucket_name, s3)
#     table_names = s3.list_objects(Bucket='test-bucket')
#     assert len(table_names['Contents']) == 11

# @mock_aws
# @patch("src.EXTRACT.lambda_extract.get_db_credentials")
# @patch("src.EXTRACT.lambda_extract.connect_to_db")
# def test_tables_uploaded_to_s3(mock_connect_to_db, mock_get_db_credentials):
#     mock_get_db_credentials.return_value = {
#         "user": "test_user",
#         "password": "test_password",
#         "host": "test_host",
#         "database": "test_database",
#         "port": 5432,
#     }
#     mock_connection = MagicMock()
#     mock_connect_to_db.return_value = mock_connection
#     mock_connection.run.side_effect = [
#         [("staff_id", "first_name")],  
#         [(1, "Test1"), (2, "Test2")],  
#     ]
#     mock_connection.run.side_effect = [
#         [("last_name", "location")],  
#         [(1, "Test1"), (2, "Test2")],  
#     ]
#     s3 = boto3.client("s3", region_name="eu-west-2")
#     s3.create_bucket(Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
#     table_names  = ["table1", "table2"]
#     for table in table_names:
#         read_and_put_data(table, "test-bucket", s3)
#     objects = s3.list_objects_v2(Bucket="test-bucket")
#     pprint(objects)
#     assert len(objects["Contents"]) == len(table_names)
