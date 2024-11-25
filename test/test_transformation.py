import pandas as pd
from src.TRANSFORM.lambda_transform import transform_staff


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
