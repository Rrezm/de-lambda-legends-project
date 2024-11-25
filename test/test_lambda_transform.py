from src.TRANSFORM.lambda_transform import setup, transform_staff
import pytest
import pandas as pd
from moto import mock_aws
import boto3


@pytest.fixture
def mock_data():
    return {
        "staff_df": pd.DataFrame({
            "staff_id": [1, 2],
            "first_name": ["John", "Jane"],
            "last_name": ["Doe", "Smith"],
            "email_address": ["john.doe@example.com",
                              "jane.smith@example.com"],
            "department_name": ["HR", "IT"],
            "location": ["New York", "London"]
        }),
        "department_df": pd.DataFrame({
            "department_name": ["HR", "IT"],
            "location": ["New York", "London"]
        })
    }


def test_transform_staff(mock_data):
    transformed = transform_staff(mock_data)
    assert isinstance(transformed, pd.DataFrame)
    assert list(transformed.columns) == [
                            "staff_id",
                            "first_name",
                            "last_name",
                            "email_address",
                            "department_name",
                            "location"
                        ]


@mock_aws
def test_setup():
    bucket_name = "test-ingested-data-lambda-legends-24"
    s3 = boto3.client("s3", region_name="eu-west-2")
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-2"
            }
        )
    mock_csv_content1 = """staff_id,first_name,last_name,email_address\n
                            1,John,Doe,john.doe@example.com\n
                            2,Jane,Smith,jane.smith@example.com"""
    s3.put_object(Bucket=bucket_name,
                  Key="folder/mock_file1.csv",
                  Body=mock_csv_content1)
    mock_csv_content2 = "staff_id,first_name\n1,Jo\n2,Jan"
    s3.put_object(Bucket=bucket_name,
                  Key="folder/mock_file2.csv",
                  Body=mock_csv_content2)
    result = setup(s3, bucket_name)
    assert isinstance(result, dict)
    assert list(result.keys()) == ['mock_file1_df', 'mock_file2_df']
    # assert len(result) > 0
    # assert all(isinstance(df, pd.DataFrame) for df in result)
