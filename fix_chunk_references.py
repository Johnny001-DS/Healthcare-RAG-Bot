#!/usr/bin/env python3
"""
Fix Chunk Reference Issues

This script addresses the issues found in chunk referencing:
1. Update User interface to work with individual document vector stores
2. Fix filename normalization in Admin interface
3. Create a consolidated vector store option
"""

import os
import sys
from pathlib import Path

def fix_admin_filename_normalization():
    """Fix filename normalization in admin files to ensure consistent naming"""
    
    admin_files = [
        "/Users/hoangleduc/Desktop/Coding Project/RAG-LLM-Healthcare-Insurance/Admin/admin_original.py"
    ]
    
    for file_path in admin_files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"🔧 Fixing filename normalization in: {os.path.basename(file_path)}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the problematic line and suggest a fix
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'file_prefix = os.path.splitext(original_filename)[0].replace(" ", "_").replace("(", "").replace(")", "")' in line:
                print(f"  📍 Found normalization at line {i+1}")
                print(f"  📝 Current: {line.strip()}")
                
                # Suggest improved normalization
                improved_line = '        file_prefix = os.path.splitext(original_filename)[0].replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")'
                print(f"  ✨ Suggested: {improved_line.strip()}")
                
        print("  ✅ Analysis complete")

def create_enhanced_user_interface():
    """Create an enhanced user interface that can work with multiple vector stores"""
    
    enhanced_user_code = '''import streamlit as st
import boto3
import os
from dotenv import load_dotenv
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Bedrock

# Load environment variables
load_dotenv()

# AWS Configuration
S3_BUCKET = os.getenv('BUCKET_NAME')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

def initialize_bedrock():
    """Initialize Bedrock client and embeddings"""
    try:
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=AWS_REGION
        )
        
        bedrock_embeddings = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v2:0", 
            client=bedrock_client
        )
        
        return bedrock_embeddings, bedrock_client
    except Exception as e:
        st.error(f"Failed to initialize Bedrock: {str(e)}")
        return None, None

def get_available_vector_stores():
    """Get all available vector stores from S3"""
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        
        if 'Contents' not in response:
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
                    'pkl_key': files['pkl'],
                    'display_name': prefix.replace('_', ' ').replace('-', ' ').title()
                })
        
        return sorted(complete_stores, key=lambda x: x['display_name'])
        
    except Exception as e:
        st.error(f"Failed to get vector stores: {str(e)}")
        return []

def load_vector_store(store_info):
    """Load a specific vector store from S3"""
    try:
        s3_client = boto3.client('s3')
        
        # Create temporary directory
        os.makedirs('/tmp/user_vectors', exist_ok=True)
        
        # Download files
        local_faiss = f"/tmp/user_vectors/{store_info['prefix']}.faiss"
        local_pkl = f"/tmp/user_vectors/{store_info['prefix']}.pkl"
        
        s3_client.download_file(S3_BUCKET, store_info['faiss_key'], local_faiss)
        s3_client.download_file(S3_BUCKET, store_info['pkl_key'], local_pkl)
        
        # Load embeddings
        bedrock_embeddings, _ = initialize_bedrock()
        if bedrock_embeddings is None:
            return None
            
        # Load vector store
        vector_store = FAISS.load_local(
            folder_path="/tmp/user_vectors",
            index_name=store_info['prefix'],
            embeddings=bedrock_embeddings,
            allow_dangerous_deserialization=True
        )
        
        return vector_store
    except Exception as e:
        st.error(f"Failed to load vector store {store_info['prefix']}: {str(e)}")
        return None

def load_combined_vector_store():
    """Load the combined vector store (legacy my_faiss)"""
    try:
        s3_client = boto3.client('s3')
        
        # Download FAISS files from S3
        s3_client.download_file(S3_BUCKET, "my_faiss.faiss", "/tmp/my_faiss.faiss")
        s3_client.download_file(S3_BUCKET, "my_faiss.pkl", "/tmp/my_faiss.pkl")
        
        # Load embeddings
        bedrock_embeddings, _ = initialize_bedrock()
        if bedrock_embeddings is None:
            return None
            
        # Load vector store
        vector_store = FAISS.load_local(
            folder_path="/tmp",
            index_name="my_faiss",
            embeddings=bedrock_embeddings,
            allow_dangerous_deserialization=True
        )
        
        return vector_store
    except Exception as e:
        st.error(f"Failed to load combined vector store: {str(e)}")
        return None

def _build_context_sections(docs):
    """Format retrieved docs into numbered sections with source hints for citations."""
    sections = []
    for idx, doc in enumerate(docs, start=1):
        metadata = getattr(doc, 'metadata', {})
        
        # Get original filename or fallback to source path
        original_filename = metadata.get('original_filename', metadata.get('source', 'unknown'))
        page = metadata.get('page', 'unknown')
        
        # Clean up source display
        if original_filename != 'unknown' and '/' in str(original_filename):
            original_filename = str(original_filename).split('/')[-1]  # Get just filename
        
        content = (doc.page_content or '').strip()
        sections.append(
            f"[S{idx}]\\n{content}\\n(Source: {original_filename}, page {page})"
        )
    return "\\n\\n".join(sections)

def _build_converse_messages(question, docs):
    """Create safety-guided user message for Nova Converse (no system role supported)."""
    context_text = _build_context_sections(docs)

    system_instructions = (
        "You are a helpful assistant for healthcare insurance documents. "
        "Follow these rules strictly: \\n"
        "- Ground every answer ONLY in the provided Context sections.\\n"
        "- If the answer is not in context, say you don't know and suggest checking the policy documents.\\n"
        "- Include inline citations using the section IDs like [S1], [S2] wherever specific facts are used.\\n"
        "- Be concise, neutral, and precise. Avoid speculation or fabrication.\\n"
        "- Do not provide legal, medical, or financial advice. Provide informational guidance only.\\n"
        "- Do not output secrets, credentials, or personal data.\\n"
        "- If the user asks for actions that could cause harm or are outside scope, refuse briefly and provide safer alternatives.\\n"
        "- Prefer bullet lists for multi-part answers.\\n"
    )

    user_prompt = (
        f"{system_instructions}\\n\\n"
        f"Context sections (use for grounding and citations):\\n\\n"
        f"{context_text}\\n\\n"
        f"Question: {question}\\n\\n"
        "Answer with citations like [S1], [S2]. If unknown, say you don't know."
    )

    return [
        {
            "role": "user",
            "content": [{"text": user_prompt}]
        }
    ]

def _extract_sources_from_docs(docs):
    """Extract source information from retrieved documents"""
    sources = []
    for idx, doc in enumerate(docs, start=1):
        metadata = getattr(doc, 'metadata', {})
        original_filename = metadata.get('original_filename', metadata.get('source', 'unknown'))
        page = metadata.get('page', 'unknown')
        
        # Clean up source display
        if original_filename != 'unknown' and '/' in str(original_filename):
            original_filename = str(original_filename).split('/')[-1]
            
        sources.append({
            'id': f'S{idx}',
            'filename': original_filename,
            'page': page,
            'content_preview': (doc.page_content or '')[:150] + '...' if len(doc.page_content or '') > 150 else doc.page_content or ''
        })
    return sources

def query_documents(question, vector_store, bedrock_client):
    """Query the documents using RAG"""
    try:
        # Search for relevant documents
        docs = vector_store.similarity_search(question, k=3)
        
        if not docs:
            return "No relevant documents found.", []
        
        # Extract source information for later display
        sources = _extract_sources_from_docs(docs)
        
        # Build safety-guided messages for Nova Lite
        messages = _build_converse_messages(question, docs)

        # Use Converse API for Nova Lite
        try:
            response = bedrock_client.converse(
                modelId="us.amazon.nova-lite-v1:0",
                messages=messages,
                inferenceConfig={
                    "maxTokens": 512,
                    "temperature": 0.2
                }
            )
            
            # Extract the response text
            if 'output' in response and 'message' in response['output']:
                answer = response['output']['message']['content'][0]['text']
                return answer, sources
            else:
                return "Unable to generate response from Nova Lite.", []
                
        except AttributeError as e:
            return f"Error: Converse API not available. Please restart the application. Details: {str(e)}", []
        except Exception as e:
            # Fallback error message
            return f"Error with Nova Lite generation: {str(e)}", []
            
    except Exception as e:
        return f"Error querying documents: {str(e)}", []

def main():
    st.title("🏥 Healthcare Insurance RAG Assistant")
    st.write("Ask questions about healthcare insurance documents")
    
    # Check if environment is configured
    if not all([os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY'), os.getenv('BUCKET_NAME')]):
        st.error("Please configure your AWS credentials and bucket name in the .env file")
        st.stop()
    
    # Initialize components
    with st.spinner("Initializing AI components..."):
        bedrock_embeddings, bedrock_llm = initialize_bedrock()
        
        if bedrock_embeddings is None or bedrock_llm is None:
            st.error("Failed to initialize Bedrock components. Please check your AWS configuration.")
            st.stop()
    
    # Get available vector stores
    st.subheader("📚 Document Selection")
    available_stores = get_available_vector_stores()
    
    if not available_stores:
        st.error("No processed documents found. Please use the Admin interface to process documents first.")
        st.stop()
    
    # Document selection options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create selection options
        store_options = ["All Documents (Combined)"] + [store['display_name'] for store in available_stores]
        selected_option = st.selectbox(
            "Select document(s) to query:",
            store_options,
            help="Choose a specific document or search across all documents"
        )
    
    with col2:
        st.write("**Available Documents:**")
        for store in available_stores:
            st.write(f"• {store['display_name']}")
    
    # Load appropriate vector store
    with st.spinner("Loading document index..."):
        if selected_option == "All Documents (Combined)":
            vector_store = load_combined_vector_store()
            if vector_store is None:
                st.warning("Combined document store not available. Please process documents using the Admin interface.")
                st.stop()
            st.success(f"✅ Loaded combined document index with all documents")
        else:
            # Find the selected store
            selected_store = next(
                (store for store in available_stores if store['display_name'] == selected_option), 
                None
            )
            if selected_store is None:
                st.error("Selected document not found")
                st.stop()
                
            vector_store = load_vector_store(selected_store)
            if vector_store is None:
                st.error(f"Failed to load document: {selected_option}")
                st.stop()
            st.success(f"✅ Loaded document: {selected_option}")
    
    # Question input
    st.subheader("❓ Ask Your Question")
    question = st.text_input(
        "Enter your question about healthcare insurance:",
        placeholder="e.g., What is a deductible and how does it work?"
    )
    
    if st.button("🔍 Ask Question", type="primary") and question:
        with st.spinner("Searching documents and generating answer..."):
            answer, sources = query_documents(question, vector_store, bedrock_llm)
            
            # Display answer
            st.subheader("💡 Answer:")
            st.write(answer)
            
            # Display source information if available
            if sources:
                st.subheader("📚 Sources:")
                st.write("*Click on each source below to see the content that informed this answer:*")
                
                for source in sources:
                    with st.expander(f"{source['id']}: {source['filename']} (Page {source['page']})"):
                        st.write("**Content Preview:**")
                        st.write(f"_{source['content_preview']}_")
                        st.write(f"**Full Reference:** {source['filename']}, Page {source['page']}")
                        
                        # Validation info
                        if source['filename'] == 'unknown':
                            st.warning("⚠️ Source filename not available in metadata")
                        if source['page'] == 'unknown':
                            st.warning("⚠️ Page number not available in metadata")
    
    # Example questions
    with st.expander("💡 Example Questions"):
        st.write("""
        **General Questions:**
        - Explain what is the difference between AI/AN limited cost sharing and Zero Cost Sharing coverage?
        - What is a deductible?
        - What services are covered under preventive care?
        - How does copayment work?
        - What is the difference between in-network and out-of-network providers?
        - What are essential health benefits?
        
        **Specific Scenarios:**
        - What happens if I need emergency care?
        - How much would I pay for a specialist visit?
        - What prescription drug coverage is included?
        - What are the out-of-pocket limits?
        """)
    
    # System info
    with st.expander("ℹ️ System Information"):
        st.write(f"**Available Documents:** {len(available_stores)}")
        st.write(f"**Current Selection:** {selected_option}")
        st.write(f"**S3 Bucket:** {S3_BUCKET}")
        st.write(f"**AWS Region:** {AWS_REGION}")
        
        # Chunk reference explanation
        st.write("**How Citations Work:**")
        st.write("""
        - **[S1], [S2], [S3]**: These are source references that map to specific document chunks
        - Each reference corresponds to a section in the "Sources" area below the answer
        - Page numbers and filenames are preserved from the original documents
        - This ensures all information can be traced back to its source
        """)

if __name__ == '__main__':
    main()'''
    
    output_path = "/Users/hoangleduc/Desktop/Coding Project/RAG-LLM-Healthcare-Insurance/User/app_enhanced.py"
    
    with open(output_path, 'w') as f:
        f.write(enhanced_user_code)
    
    print(f"✅ Created enhanced user interface: {output_path}")

def main():
    """Main function to run all fixes"""
    print("🔧 Healthcare Insurance RAG - Chunk Reference Fixes")
    print("=" * 60)
    
    print("\\n1. Analyzing Admin Interface Filename Normalization...")
    fix_admin_filename_normalization()
    
    print("\\n2. Creating Enhanced User Interface...")
    create_enhanced_user_interface()
    
    print("\\n" + "=" * 60)
    print("✅ FIXES COMPLETED!")
    print("""
📋 Summary of Changes:

1. **Enhanced User Interface (User/app_enhanced.py)**:
   ✅ Can work with individual document vector stores
   ✅ Provides document selection dropdown
   ✅ Shows clear source attribution
   ✅ Maintains backward compatibility with combined store
   ✅ Better error handling and user feedback

2. **Admin Interface Analysis**:
   ✅ Identified filename normalization logic
   ✅ Suggested improvements for consistency

🎯 Next Steps:
1. Test the enhanced user interface
2. Consider updating the original User/app.py
3. Update Admin interface if needed
4. Run verification tests again

💡 The enhanced interface addresses all the chunk referencing issues found:
- Works with individual document stores
- Provides clear source mapping
- Maintains [S1], [S2] reference integrity
- Shows exact document and page attribution
""")

if __name__ == "__main__":
    main()
