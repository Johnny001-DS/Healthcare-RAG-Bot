#!/usr/bin/env python3
"""
Complete System Test

Test all components: S3, Embeddings, and Text Generation
"""

import boto3
import os
from dotenv import load_dotenv
from langchain_community.embeddings import BedrockEmbeddings

def test_complete_system():
    """Test the complete RAG system"""
    print("🚀 Complete RAG System Test")
    print("=" * 50)
    
    load_dotenv()
    
    # Test S3 Connection
    print("🔍 Testing S3 Connection...")
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_buckets()
        bucket_name = os.getenv('BUCKET_NAME')
        
        print(f"✅ S3 Connection: WORKING")
        print(f"   Found {len(response['Buckets'])} buckets")
        print(f"   Target bucket: {bucket_name}")
        
        # Test bucket access
        if bucket_name:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket Access: WORKING")
        
        s3_success = True
    except Exception as e:
        print(f"❌ S3 Connection: FAILED - {str(e)}")
        s3_success = False
    
    print()
    
    # Test Bedrock Embeddings
    print("🔍 Testing Bedrock Embeddings...")
    try:
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        bedrock_embeddings = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v2:0", 
            client=bedrock_client
        )
        
        # Test embedding generation
        test_text = "This is a test document for embedding generation."
        embeddings = bedrock_embeddings.embed_query(test_text)
        
        print(f"✅ Bedrock Embeddings: WORKING")
        print(f"   Generated embedding vector of length: {len(embeddings)}")
        
        embeddings_success = True
    except Exception as e:
        print(f"❌ Bedrock Embeddings: FAILED - {str(e)}")
        embeddings_success = False
    
    print()
    
    # Test Nova Lite Text Generation
    print("🔍 Testing Nova Lite Text Generation...")
    try:
        response = bedrock_client.converse(
            modelId="us.amazon.nova-lite-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "What is health insurance? Give a brief answer."}]
                }
            ],
            inferenceConfig={
                "maxTokens": 100,
                "temperature": 0.7
            }
        )
        
        if 'output' in response and 'message' in response['output']:
            output_text = response['output']['message']['content'][0]['text']
            print(f"✅ Nova Lite Text Generation: WORKING")
            print(f"   Sample response: {output_text[:100]}...")
            
            text_gen_success = True
        else:
            print(f"❌ Nova Lite Text Generation: FAILED - Invalid response format")
            text_gen_success = False
            
    except Exception as e:
        print(f"❌ Nova Lite Text Generation: FAILED - {str(e)}")
        text_gen_success = False
    
    print("\n" + "=" * 50)
    print("📊 SYSTEM STATUS:")
    print(f"S3 Storage:        {'✅ WORKING' if s3_success else '❌ FAILED'}")
    print(f"Embeddings:        {'✅ WORKING' if embeddings_success else '❌ FAILED'}")
    print(f"Text Generation:   {'✅ WORKING' if text_gen_success else '❌ FAILED'}")
    
    if s3_success and embeddings_success and text_gen_success:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("Your RAG application is ready to use:")
        print("  Admin Interface: streamlit run Admin/admin.py --server.port 8501")
        print("  User Interface:  streamlit run User/app.py --server.port 8502")
        return True
    else:
        print("\n⚠️  Some components failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    test_complete_system()
