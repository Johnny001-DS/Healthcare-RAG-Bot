#!/usr/bin/env python3
"""
Test User Interface Configuration

Verify that the user interface will work with Nova Lite
"""

import boto3
import os
from dotenv import load_dotenv

def test_user_config():
    """Test the user interface configuration"""
    print("🔍 Testing User Interface Configuration")
    print("=" * 50)
    
    load_dotenv()
    region = os.getenv('AWS_DEFAULT_REGION')
    
    try:
        # Test Bedrock client creation (like user app)
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=region
        )
        
        print(f"✅ Bedrock client created for region: {region}")
        
        # Test Converse API (like user app)
        test_prompt = "What is health insurance?"
        
        response = bedrock_client.converse(
            modelId="us.amazon.nova-lite-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [{"text": test_prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 100,
                "temperature": 0.7
            }
        )
        
        # Extract response (like user app)
        if 'output' in response and 'message' in response['output']:
            output_text = response['output']['message']['content'][0]['text']
            print("✅ Nova Lite Converse API: WORKING")
            print(f"   Sample response: {output_text[:100]}...")
            print()
            print("🎉 Your user interface should now work for questions!")
            return True
        else:
            print("❌ Invalid response format from Nova Lite")
            return False
            
    except Exception as e:
        print(f"❌ User Interface Test: FAILED")
        print(f"   Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_user_config()
