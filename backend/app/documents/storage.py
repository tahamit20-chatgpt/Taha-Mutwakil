import os
import boto3
import botocore.session
from botocore.exceptions import ClientError
from app.config import S3_ENDPOINT, S3_BUCKET, DEMO

def client():
    # Dedicated S3 endpoint bindings: never consume the host AWS profile/identity.
    core=botocore.session.Session(session_vars={'profile': (None,None,None,None), 'config_file': (None,None,'/dev/null',None), 'credentials_file': (None,None,'/dev/null',None)})
    return boto3.Session(botocore_session=core).client('s3', endpoint_url=S3_ENDPOINT, aws_access_key_id=os.getenv('S3_ACCESS_KEY', 'S3RVER') if DEMO else os.environ['S3_ACCESS_KEY'], aws_secret_access_key=os.getenv('S3_SECRET_KEY','S3RVER') if DEMO else os.environ['S3_SECRET_KEY'], region_name='us-east-1')
def initialize():
    c=client()
    try: c.head_bucket(Bucket=S3_BUCKET)
    except ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] != 404: raise
        c.create_bucket(Bucket=S3_BUCKET)
def put(key, body): client().put_object(Bucket=S3_BUCKET, Key=key, Body=body)
def get(key): return client().get_object(Bucket=S3_BUCKET, Key=key)['Body'].read()
