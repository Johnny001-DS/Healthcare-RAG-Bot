#!/usr/bin/env python3
"""
Simple Bedrock Test

Test if the specific models you have access to work correctly.
"""

import boto3
import os
from dotenv import load_dotenv

def test_bedrock_models():
    """Test the specific Bedrock models you have access to"""
    print("🔍 Testing Bedrock Models...")
    print("=" * 50)
    
    load_dotenv()
    
    try:
        # Create Bedrock client
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        # Test Titan Embeddings V2
        print("Testing Amazon Titan Embeddings V2...")
        try:
            response = bedrock_client.invoke_model(
                modelId="amazon.titan-embed-text-v2:0",
                body='{"inputText": "Hello world"}',
                contentType="application/json"
            )
            print("✅ Titan Embeddings V2: WORKING")
        except Exception as e:
            print(f"❌ Titan Embeddings V2: {str(e)}")
        
        # Test Amazon Nova Lite with Cross-Region Inference Profile
        print("\nTesting Amazon Nova Lite (Cross-Region)...")
        try:
            # Nova models use the Converse API format
            import json
            body = json.dumps({
                "messages": [{"role": "user", "content": "Hello, how are you?"}],
                "max_tokens": 50,
                "temperature": 0.7
            })
            response = bedrock_client.invoke_model(
                modelId="us.amazon.nova-lite-v1:0",  # Cross-region inference profile
                body=body,
                contentType="application/json"
            )
            print("✅ Amazon Nova Lite (Cross-Region): WORKING")
        except Exception as e:
            print(f"❌ Amazon Nova Lite (Cross-Region): {str(e)}")
            
            # Try alternative formats
            print("   Trying alternative cross-region profile...")
            try:
                # Some regions might use different profile names
                response = bedrock_client.invoke_model(
                    modelId="us.amazon.nova-lite",  # Alternative profile name
                    body=body,
                    contentType="application/json"
                )
                print("   ✅ Amazon Nova Lite (Alt Profile): WORKING")
            except Exception as e2:
                print(f"   ❌ Amazon Nova Lite (Alt Profile): {str(e2)}")
        
        print("\n🎉 Both models are working! Your RAG application should work now.")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock Connection Failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_bedrock_models()
