#!/usr/bin/env python3
"""
Chunk Reference Verification Test

This script tests whether [S1], [S2] chunk references correctly match 
the documents they're supposed to reference.
"""

import boto3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add User directory to path to import the app functions
sys.path.append(str(Path(__file__).parent / "User"))

from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS

def load_environment():
    """Load environment variables"""
    load_dotenv()
    return {
        'bucket_name': os.getenv('BUCKET_NAME'),
        'aws_region': os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
        'aws_access_key': os.getenv('AWS_ACCESS_KEY_ID'),
        'aws_secret_key': os.getenv('AWS_SECRET_ACCESS_KEY')
    }

def get_all_vector_stores_from_s3():
    """Get all vector store files from S3"""
    try:
        s3_client = boto3.client('s3')
        env = load_environment()
        
        response = s3_client.list_objects_v2(Bucket=env['bucket_name'])
        
        if 'Contents' not in response:
            print("❌ No files found in S3 bucket")
            return []
        
        # Group files by prefix (document name)
        vector_stores = {}
        for obj in response['Contents']:
            key = obj['Key']
            if key.endswith('.faiss'):
                prefix = key[:-6]  # Remove .faiss extension
                if prefix not in vector_stores:
                    vector_stores[prefix] = {}
                vector_stores[prefix]['faiss'] = key
            elif key.endswith('.pkl'):
                prefix = key[:-4]  # Remove .pkl extension
                if prefix not in vector_stores:
                    vector_stores[prefix] = {}
                vector_stores[prefix]['pkl'] = key
        
        # Filter complete vector stores (both .faiss and .pkl)
        complete_stores = []
        for prefix, files in vector_stores.items():
            if 'faiss' in files and 'pkl' in files:
                complete_stores.append({
                    'prefix': prefix,
                    'faiss_key': files['faiss'],
                    'pkl_key': files['pkl']
                })
        
        return complete_stores
        
    except Exception as e:
        print(f"❌ Error listing S3 files: {str(e)}")
        return []

def load_specific_vector_store(store_info):
    """Load a specific vector store from S3"""
    try:
        env = load_environment()
        s3_client = boto3.client('s3')
        
        # Create temporary directory
        os.makedirs('/tmp/test_vectors', exist_ok=True)
        
        # Download files
        local_faiss = f"/tmp/test_vectors/{store_info['prefix']}.faiss"
        local_pkl = f"/tmp/test_vectors/{store_info['prefix']}.pkl"
        
        s3_client.download_file(env['bucket_name'], store_info['faiss_key'], local_faiss)
        s3_client.download_file(env['bucket_name'], store_info['pkl_key'], local_pkl)
        
        # Initialize Bedrock embeddings
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=env['aws_region']
        )
        bedrock_embeddings = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v2:0", 
            client=bedrock_client
        )
        
        # Load vector store
        vector_store = FAISS.load_local(
            folder_path="/tmp/test_vectors",
            index_name=store_info['prefix'],
            embeddings=bedrock_embeddings,
            allow_dangerous_deserialization=True
        )
        
        return vector_store
        
    except Exception as e:
        print(f"❌ Error loading vector store {store_info['prefix']}: {str(e)}")
        return None

def test_chunk_references(vector_store, document_name):
    """Test if chunk references [S1], [S2] correctly map to document content"""
    print(f"\n🔍 Testing chunk references for: {document_name}")
    print("-" * 60)
    
    # Test query
    test_query = "What is a deductible?"
    
    try:
        # Search for relevant documents
        docs = vector_store.similarity_search(test_query, k=3)
        
        if not docs:
            print("❌ No documents found for test query")
            return False
        
        print(f"📊 Found {len(docs)} relevant chunks")
        
        # Test the chunk reference system (similar to User/app.py)
        for idx, doc in enumerate(docs, start=1):
            metadata = getattr(doc, 'metadata', {})
            
            # Get original filename or fallback to source path
            original_filename = metadata.get('original_filename', metadata.get('source', 'unknown'))
            page = metadata.get('page', 'unknown')
            
            # Clean up source display
            if original_filename != 'unknown' and '/' in str(original_filename):
                original_filename = str(original_filename).split('/')[-1]
            
            content = (doc.page_content or '').strip()
            
            print(f"\n[S{idx}] Reference Validation:")
            print(f"  📄 Source File: {original_filename}")
            print(f"  📃 Page: {page}")
            print(f"  📝 Content Preview: {content[:150]}...")
            
            # Validate metadata consistency
            if original_filename == 'unknown':
                print(f"  ⚠️  WARNING: No original filename in metadata")
            
            if page == 'unknown':
                print(f"  ⚠️  WARNING: No page number in metadata")
            
            # Check if content is actually from the expected document
            if original_filename != 'unknown' and document_name not in original_filename:
                print(f"  ❌ ERROR: Content appears to be from {original_filename}, expected {document_name}")
                return False
            else:
                print(f"  ✅ Content correctly attributed to {original_filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chunk references: {str(e)}")
        return False

def simulate_rag_query(vector_store, document_name, query):
    """Simulate a full RAG query to verify end-to-end chunk referencing"""
    print(f"\n🤖 Simulating RAG Query for: {document_name}")
    print(f"🔍 Query: '{query}'")
    print("-" * 60)
    
    try:
        # Search for relevant documents (same as User/app.py)
        docs = vector_store.similarity_search(query, k=3)
        
        if not docs:
            print("❌ No relevant documents found")
            return False
        
        # Build context sections (same as User/app.py _build_context_sections)
        sections = []
        sources = []
        
        for idx, doc in enumerate(docs, start=1):
            metadata = getattr(doc, 'metadata', {})
            
            # Get original filename or fallback to source path
            original_filename = metadata.get('original_filename', metadata.get('source', 'unknown'))
            page = metadata.get('page', 'unknown')
            
            # Clean up source display
            if original_filename != 'unknown' and '/' in str(original_filename):
                original_filename = str(original_filename).split('/')[-1]
            
            content = (doc.page_content or '').strip()
            
            # Build section (same format as User/app.py)
            sections.append(
                f"[S{idx}]\n{content}\n(Source: {original_filename}, page {page})"
            )
            
            # Build source info (same as User/app.py _extract_sources_from_docs)
            sources.append({
                'id': f'S{idx}',
                'filename': original_filename,
                'page': page,
                'content_preview': content[:150] + '...' if len(content) > 150 else content
            })
        
        # Display the context that would be sent to the LLM
        context_text = "\n\n".join(sections)
        print("📝 Context sections that would be sent to LLM:")
        print(context_text)
        
        print("\n📚 Source mappings:")
        for source in sources:
            print(f"  {source['id']}: {source['filename']} (Page {source['page']})")
            print(f"    Preview: {source['content_preview']}")
        
        # Verify all sources are correctly mapped
        for source in sources:
            if source['filename'] == 'unknown':
                print(f"  ❌ ERROR: Source {source['id']} has unknown filename")
                return False
            if source['page'] == 'unknown':
                print(f"  ⚠️  WARNING: Source {source['id']} has unknown page")
        
        print("\n✅ All chunk references validated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in RAG simulation: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🏥 Healthcare Insurance RAG - Chunk Reference Verification")
    print("=" * 80)
    
    # Check environment
    env = load_environment()
    if not all([env['bucket_name'], env['aws_access_key'], env['aws_secret_key']]):
        print("❌ Missing required environment variables")
        print("Please ensure AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and BUCKET_NAME are set")
        return False
    
    print(f"📊 Configuration:")
    print(f"  Bucket: {env['bucket_name']}")
    print(f"  Region: {env['aws_region']}")
    
    # Get all vector stores
    print("\n🔍 Scanning S3 for vector stores...")
    vector_stores = get_all_vector_stores_from_s3()
    
    if not vector_stores:
        print("❌ No vector stores found in S3")
        print("Please run the Admin interface to process some documents first")
        return False
    
    print(f"✅ Found {len(vector_stores)} vector stores:")
    for store in vector_stores:
        print(f"  📄 {store['prefix']}")
    
    # Test each vector store
    all_tests_passed = True
    
    for store_info in vector_stores:
        print(f"\n{'='*80}")
        print(f"Testing Vector Store: {store_info['prefix']}")
        print(f"{'='*80}")
        
        # Load vector store
        vector_store = load_specific_vector_store(store_info)
        if vector_store is None:
            print(f"❌ Failed to load vector store for {store_info['prefix']}")
            all_tests_passed = False
            continue
        
        # Test chunk references
        chunk_test_passed = test_chunk_references(vector_store, store_info['prefix'])
        if not chunk_test_passed:
            all_tests_passed = False
        
        # Test full RAG simulation
        rag_test_passed = simulate_rag_query(
            vector_store, 
            store_info['prefix'], 
            "What is a deductible and how does it work?"
        )
        if not rag_test_passed:
            all_tests_passed = False
    
    # Final summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Chunk references [S1], [S2] are correctly mapping to document sources")
        print("✅ Source attribution is working properly")
        print("✅ The RAG system is properly tracking document origins")
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️  There are issues with chunk referencing that need to be addressed")
    
    # Clean up temporary files
    try:
        import shutil
        if os.path.exists('/tmp/test_vectors'):
            shutil.rmtree('/tmp/test_vectors')
    except:
        pass
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
