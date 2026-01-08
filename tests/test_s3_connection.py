#!/usr/bin/env python3
"""
Test S3 Connection Script

This script tests your AWS S3 connection using credentials from .env file.
Run this to verify your AWS setup is working correctly.
"""

import boto3
import os
from dotenv import load_dotenv

def test_s3_connection():
    """Test S3 connection and list buckets"""
    print("🔍 Testing S3 Connection...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if credentials are loaded
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    bucket_name = os.getenv('BUCKET_NAME')
    
    print(f"Region: {region}")
    print(f"Bucket Name: {bucket_name}")
    print(f"Access Key: {access_key[:10] if access_key and access_key != 'your_access_key_here' else 'NOT SET'}...")
    print()
    
    # Check if credentials are still placeholders
    if access_key == 'your_access_key_here' or secret_key == 'your_secret_key_here':
        print("❌ ERROR: Please update your .env file with real AWS credentials!")
        print("Current values are still placeholders.")
        return False
    
    if not access_key or not secret_key:
        print("❌ ERROR: AWS credentials not found in .env file!")
        return False
    
    try:
        # Create S3 client
        print("Creating S3 client...")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Test connection by listing buckets
        print("Testing connection...")
        response = s3_client.list_buckets()
        
        print("✅ S3 Connection Successful!")
        print(f"Found {len(response['Buckets'])} buckets:")
        
        for bucket in response['Buckets']:
            print(f"  - {bucket['Name']} (created: {bucket['CreationDate'].strftime('%Y-%m-%d')})")
        
        # Test specific bucket if provided
        if bucket_name:
            print(f"\nTesting access to bucket: {bucket_name}")
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                print(f"✅ Bucket '{bucket_name}' is accessible!")
            except Exception as e:
                print(f"❌ Cannot access bucket '{bucket_name}': {str(e)}")
                print("Make sure the bucket exists and you have permissions.")
        
        return True
        
    except Exception as e:
        print(f"❌ S3 Connection Failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your AWS credentials in .env file")
        print("2. Verify your AWS account has S3 access")
        print("3. Check if your region is correct")
        print("4. Ensure your IAM user has S3 permissions")
        return False

def test_bedrock_connection():
    """Test Bedrock connection"""
    print("\n🔍 Testing Bedrock Connection...")
    print("=" * 50)
    
    try:
        # Create Bedrock client
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        # List available models
        print("Testing Bedrock access...")
        response = bedrock_client.list_foundation_models()
        
        print("✅ Bedrock Connection Successful!")
        print(f"Found {len(response['modelSummaries'])} available models")
        
        # Check for available models
        embedding_models = [model for model in response['modelSummaries'] 
                           if 'embed' in model['modelId'].lower()]
        text_models = [model for model in response['modelSummaries'] 
                      if 'nova' in model['modelId'].lower() or 'titan' in model['modelId'].lower()]
        
        if embedding_models:
            print("✅ Embedding models found:")
            for model in embedding_models[:3]:
                print(f"  - {model['modelId']}")
        
        if text_models:
            print("✅ Text generation models found:")
            for model in text_models[:3]:
                print(f"  - {model['modelId']}")
        
        if not embedding_models and not text_models:
            print("⚠️  No suitable models found. You may need to request access.")
        
        return True
        
    except Exception as e:
        print(f"❌ Bedrock Connection Failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Request access to Amazon Bedrock in AWS Console")
        print("2. Enable Titan models in Bedrock model access")
        print("3. Check if Bedrock is available in your region")
        return False

if __name__ == "__main__":
    print("🚀 AWS Connection Test")
    print("=" * 50)
    
    # Test S3
    s3_success = test_s3_connection()
    
    # Test Bedrock
    bedrock_success = test_bedrock_connection()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"S3 Connection: {'✅ PASS' if s3_success else '❌ FAIL'}")
    print(f"Bedrock Connection: {'✅ PASS' if bedrock_success else '❌ FAIL'}")
    
    if s3_success and bedrock_success:
        print("\n🎉 All tests passed! Your AWS setup is ready.")
        print("You can now run:")
        print("  streamlit run Admin/admin.py --server.port 8501")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
