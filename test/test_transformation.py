import pytest
import pandas as pd
from src.TRANSFORM.lambda_transform import transform_staff, setup
import pytest
from unittest.mock import patch, Mock


def test_transform_staff():
    # creating a fake sample data
    df_dict = {
        "staff_df": pd.DataFrame(
            {
                "staff_id": [1, 2],
                "first_name": ["Jake", "Nancy"],
                "last_name": ["Jackson", "Pelosi"],
                "email_address": ["jake@gmail.com", "nancy@gmail.com"],
            }
        ),
        "department_df": pd.DataFrame(
            {"department_name": ["IT", "HR"], "location": ["LD", "BR"]}
        ),
    }

    # my expected output
    transformed_df = transform_staff(df_dict)

    assert transformed_df.shape == (2, 6)  # 2 rows, 6 columns
    assert "location" in transformed_df.columns
    assert transformed_df["staff_id"].iloc[0] == 1
    assert transformed_df["department_name"].iloc[0] == "IT"


# def test_setup_with_mock():
#     # Mock S3 client
#     mock_s3 = Mock()

#     # Mock the return values for S3 list_objects and get_object
#     mock_s3.list_objects.return_value = {
#         "Contents": [{"Key": "prefix/staff.csv"}, {"Key": "prefix/counterparty.csv"}]
#     }
#     mock_body = Mock()
#     mock_body.read.return_value = (
#         b"staff_id,first_name,last_name,email_address\n1,Jake,Jackson,jake@gmail.com\n"
#     )
#     mock_s3.get_object.return_value = {"Body": mock_body}

#     # Patch boto3 client
#     with patch("boto3.client", return_value=mock_s3):
#         df_list = setup()

#     # Assertions
#     assert len(df_list) > 0  # Ensure at least one DataFrame is returned
#     assert isinstance(
#         df_list[0], pd.DataFrame
#     )  # Ensure the first item in the list is a DataFrame
