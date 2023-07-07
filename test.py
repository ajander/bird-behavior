import boto3
import os

s3 = boto3.resource(
    service_name = 's3',
    region_name = os.getenv('AWS_DEFAULT_REGION'),
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
)

for bucket in s3.buckets.all():
    print(bucket.name)