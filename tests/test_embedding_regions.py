#!/usr/bin/env python3
"""
Test Titan Embeddings in Different Regions

Check which regions have Titan Text Embeddings V2 available
"""

import boto3
import os
from dotenv import load_dotenv
from langchain_community.embeddings import BedrockEmbeddings

def test_embedding_in_region(region):
    """Test Titan embeddings in a specific region"""
    print(f"Testing Titan Embeddings in {region}...")
    
    try:
        # Create Bedrock client for specific region
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=region
        )
        
        # Test Titan embeddings
        bedrock_embeddings = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v2:0", 
            client=bedrock_client
        )
        
        # Try to generate an embedding
        test_text = "Test embedding generation"
        embedding = bedrock_embeddings.embed_query(test_text)
        
        print(f"✅ {region}: WORKING - Generated embedding of length {len(embedding)}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "AccessDeniedException" in error_msg:
            print(f"❌ {region}: ACCESS DENIED - Model not enabled or not available")
        elif "ValidationException" in error_msg:
            print(f"❌ {region}: VALIDATION ERROR - Model not available")
        else:
            print(f"❌ {region}: ERROR - {error_msg}")
        return False

def main():
    """Test embeddings in common regions"""
    load_dotenv()
    
    print("🔍 Testing Titan Text Embeddings V2 Availability")
    print("=" * 60)
    
    current_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    print(f"Current configured region: {current_region}")
    print()
    
    # Common regions where Bedrock is available
    test_regions = [
        'us-east-1',     # N. Virginia
        'us-east-2',     # Ohio  
        'us-west-2',     # Oregon
        'eu-west-1',     # Ireland
        'ap-southeast-1' # Singapore
    ]
    
    working_regions = []
    
    for region in test_regions:
        success = test_embedding_in_region(region)
        if success:
            working_regions.append(region)
    
    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    
    if working_regions:
        print(f"✅ Working regions: {', '.join(working_regions)}")
        
        if current_region not in working_regions:
            print(f"\n⚠️  ISSUE FOUND:")
            print(f"   Your current region ({current_region}) doesn't have Titan embeddings enabled")
            print(f"   Recommended solutions:")
            print(f"   1. Enable model access in {current_region} via AWS Console")
            print(f"   2. Or change to a working region like: {working_regions[0]}")
        else:
            print(f"\n✅ Your current region ({current_region}) is working!")
            
    else:
        print("❌ No working regions found. Check your AWS model access permissions.")
    
    return working_regions

if __name__ == "__main__":
    main()
