#!/usr/bin/env python3
"""
Test Admin Embedding Configuration

Verify that the admin script will work with current configuration
"""

import sys
import os
sys.path.append('/Users/hoangleduc/Desktop/Coding Project/RAG-LLM-Healthcare-Insurance')

from dotenv import load_dotenv
import boto3
from langchain_community.embeddings import BedrockEmbeddings

def test_admin_config():
    """Test the admin configuration"""
    print("🔍 Testing Admin Interface Configuration")
    print("=" * 50)
    
    # Load environment like admin script does
    load_dotenv()
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_DEFAULT_REGION")
    bucket = os.getenv('BUCKET_NAME')
    
    print(f"Region: {region}")
    print(f"Bucket: {bucket}")
    print(f"Access Key: {access_key[:10] if access_key else 'None'}...")
    print()
    
    try:
        # Test Bedrock client creation (like admin script)
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region
        )
        
        # Test embeddings (like admin script)
        bedrock_embeddings = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v2:0", 
            client=bedrock_client
        )
        
        # Test embedding generation
        test_text = "Sample healthcare document text for testing embeddings."
        embedding = bedrock_embeddings.embed_query(test_text)
        
        print("✅ Admin Configuration Test: PASSED")
        print(f"   Bedrock client: ✅ Created successfully")
        print(f"   Embeddings: ✅ Generated {len(embedding)}-dim vector")
        print(f"   Region: ✅ {region} working correctly")
        print()
        print("🎉 Your admin interface should now work for PDF uploads!")
        
        return True
        
    except Exception as e:
        print("❌ Admin Configuration Test: FAILED")
        print(f"   Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_admin_config()
