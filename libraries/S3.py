import boto3, configparser
from botocore.exceptions import ClientError
import logging

config = configparser.ConfigParser()
config.read('configs.ini')
configS3 = config['S3']
bucket = configS3['aws_bucket']

def upload(file, name):
    s3_client = boto3.client('s3', 
        endpoint_url=configS3['aws_endpoint'],
        aws_access_key_id = configS3['aws_access_key_id'],
        aws_secret_access_key = configS3['aws_secret_access_key'],
        region_name = configS3['aws_region']
    )

    try:
        response = s3_client.upload_file(file, bucket, name, ExtraArgs={'ACL':'public-read'})
    except ClientError as e:
        logging.error(e)

    return f"{configS3['aws_endpoint']}/{bucket}/{name}"