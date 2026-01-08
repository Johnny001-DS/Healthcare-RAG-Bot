#!/usr/bin/env python3
"""
Test Nova Lite with Converse API

This script tests Nova Lite using the correct Converse API format
"""

import boto3
import os
from dotenv import load_dotenv

def test_nova_converse():
    """Test Nova Lite using the Converse API"""
    print("🔍 Testing Nova Lite with Converse API...")
    print("=" * 50)
    
    load_dotenv()
    
    try:
        # Create Bedrock client
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        # Test Nova Lite with Converse API
        print("Testing Nova Lite with Converse API...")
        try:
            response = bedrock_client.converse(
                modelId="us.amazon.nova-lite-v1:0",  # Cross-region inference profile
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": "Hello! Please say hi back."}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 50,
                    "temperature": 0.7
                }
            )
            
            # Extract response
            if 'output' in response and 'message' in response['output']:
                output_text = response['output']['message']['content'][0]['text']
                print("✅ Nova Lite Converse API: WORKING")
                print(f"Response: {output_text}")
                return True
            else:
                print("❌ Nova Lite Converse API: No valid response structure")
                return False
                
        except Exception as e:
            print(f"❌ Nova Lite Converse API: {str(e)}")
            
            # Try without cross-region profile
            print("Trying direct model access...")
            try:
                response = bedrock_client.converse(
                    modelId="amazon.nova-lite-v1:0",
                    messages=[
                        {
                            "role": "user", 
                            "content": [{"text": "Hello! Please say hi back."}]
                        }
                    ],
                    inferenceConfig={
                        "maxTokens": 50,
                        "temperature": 0.7
                    }
                )
                
                if 'output' in response and 'message' in response['output']:
                    output_text = response['output']['message']['content'][0]['text']
                    print("✅ Nova Lite Direct Access: WORKING")
                    print(f"Response: {output_text}")
                    return True
                    
            except Exception as e2:
                print(f"❌ Nova Lite Direct Access: {str(e2)}")
                return False
        
    except Exception as e:
        print(f"❌ Bedrock Connection Failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_nova_converse()
    if success:
        print("\n🎉 Nova Lite is working! Your RAG application should work now.")
    else:
        print("\n⚠️ Nova Lite test failed. Check your model access permissions.")
