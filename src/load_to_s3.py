import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

class S3DataLoader:
    def __init__(self):
        # Initialize the S3 client using our secure credentials
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name='us-east-1' # Change this if your bucket is in a different region
        )

    def upload_directory(self, local_dir: str, s3_prefix: str):
        """Walks through a local directory and uploads all files to an S3 prefix (folder)."""
        if not os.path.exists(local_dir):
            print(f"Directory {local_dir} does not exist. Skipping.")
            return

        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                
                # Create the S3 key (the path inside the bucket)
                # Example: raw/NA1_12345.json
                s3_key = f"{s3_prefix}/{file}"
                
                print(f"Uploading {local_path} to s3://{BUCKET_NAME}/{s3_key}...")
                
                try:
                    self.s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
                except ClientError as e:
                    print(f"Failed to upload {file}: {e}")

if __name__ == "__main__":
    if not BUCKET_NAME:
        raise ValueError("S3_BUCKET_NAME not found in .env file!")

    loader = S3DataLoader()
    
    # 1. Upload Raw JSON files to the "raw" folder in S3
    print("--- Uploading Raw Data ---")
    loader.upload_directory(local_dir="raw_data", s3_prefix="raw")
    
    # 2. Upload Transformed CSV files to the "processed" folder in S3
    print("\n--- Uploading Processed Data ---")
    loader.upload_directory(local_dir="processed_data", s3_prefix="processed")
    
    print("\nAll uploads complete!")