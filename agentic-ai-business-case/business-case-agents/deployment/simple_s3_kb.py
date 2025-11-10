#!/usr/bin/env python3

import boto3
import json
from pathlib import Path

class SimpleS3KB:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.s3 = boto3.client('s3', region_name=region)
        
    def create_s3_bucket(self):
        """Create S3 bucket"""
        bucket_name = f'business-case-kb-{self.region}'
        
        try:
            if self.region == 'us-east-1':
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            print(f"✓ Created S3 bucket: {bucket_name}")
        except self.s3.exceptions.BucketAlreadyOwnedByYou:
            print(f"✓ S3 bucket exists: {bucket_name}")
        
        return bucket_name
    
    def upload_partner_data(self, bucket_name):
        """Upload partner data"""
        data_dir = Path(__file__).parent.parent / 'anypartner_data'
        
        for file_path in data_dir.rglob('*'):
            if file_path.is_file():
                s3_key = f"partner-data/{file_path.name}"
                self.s3.upload_file(str(file_path), bucket_name, s3_key)
                print(f"  ✓ Uploaded: {file_path.name}")
        
        return bucket_name
    
    def deploy(self):
        """Deploy simple S3-based knowledge system"""
        print("\n=== Simple S3 Knowledge Base Setup ===\n")
        
        # Create bucket and upload data
        bucket_name = self.create_s3_bucket()
        self.upload_partner_data(bucket_name)
        
        # Save config
        config = {'bucket_name': bucket_name, 'type': 's3_simple'}
        
        config_path = Path(__file__).parent / 'kb_config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✓ Setup complete! Config: {config_path}")
        print("Use the query_partner_knowledge() function in your agents")
        
        return config

if __name__ == "__main__":
    setup = SimpleS3KB()
    setup.deploy()
