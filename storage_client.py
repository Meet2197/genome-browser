import boto3
from botocore.client import Config

MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin123"
BUCKET = "genome-browser"

s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

def ensure_bucket():
    existing = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    if BUCKET not in existing:
        s3.create_bucket(Bucket=BUCKET)

def upload_file(local_path: str, object_name: str):
    ensure_bucket()
    s3.upload_file(local_path, BUCKET, object_name)
    return f"{MINIO_ENDPOINT}/{BUCKET}/{object_name}"

def get_presigned_url(object_name: str, expires_in=3600):
    return s3.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET, "Key": object_name}, ExpiresIn=expires_in
    )