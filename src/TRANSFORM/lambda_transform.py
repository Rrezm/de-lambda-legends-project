import boto3

s3 = boto3.client('s3')
bucket_name = "ingested-data-lambda-legends-24"
s3.get_object(Bucket=bucket_name, Key=)