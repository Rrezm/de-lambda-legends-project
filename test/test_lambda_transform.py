from src.TRANSFORM.lambda_transform import setup, transform_staff
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from moto import mock_aws
import boto3


@pytest.fixture
def mock_data():
    return {
        "staff_df": pd.DataFrame({
            "staff_id": [1, 2],
            "first_name": ["John", "Jane"],
            "last_name": ["Doe", "Smith"],
            "email_address": ["john.doe@example.com", "jane.smith@example.com"],
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
    assert list(transformed.columns) == ["staff_id", "first_name", "last_name", "email_address", "department_name", "location"]

@mock_aws
def test_setup():
    bucket_name = "ingested-data-lambda-legends-24"
    s3 = boto3.client("s3", region_name="eu-west-2")
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-2"
            }
        )
    mock_csv_content = "staff_id,first_name,last_name,email_address\n1,John,Doe,john.doe@example.com\n2,Jane,Smith,jane.smith@example.com"
    s3.put_object(Bucket=bucket_name, Key="folder/mock_file.csv", Body=mock_csv_content)
    result = setup()
    assert isinstance(result, list)
    # assert len(result) > 0
    # assert all(isinstance(df, pd.DataFrame) for df in result)


