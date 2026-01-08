
import boto3
import streamlit as st
import os
import uuid 
from dotenv import load_dotenv
import os
import glob
from pathlib import Path
import time

load_dotenv()
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_DEFAULT_REGION")
# Amazon S3 Configuration
S3_BUCKET = os.getenv('BUCKET_NAME')
s3_client = boto3.client('s3')

#Bedrock Configuration
from langchain_community.embeddings import BedrockEmbeddings

#Text Splitter | Split into chunks
from langchain.text_splitter import RecursiveCharacterTextSplitter

#FAISS Configuration
from langchain_community.vectorstores import FAISS
# import numpy as np

#Amazon Titan Configuration
# from langchain_community.embeddings import AmazonTitanEmbeddings

#pdf loader
from langchain_community.document_loaders import PyPDFLoader

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=region
)
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", client=bedrock_client)

def check_s3_file_exists(s3_key):
    """Check if a file exists in S3 bucket"""
    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=s3_key)
        return True
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            # Re-raise for other errors (permissions, etc.)
            raise
    except Exception:
        return False

def get_existing_s3_files():
    """Get list of all existing files in S3 bucket"""
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    except Exception as e:
        st.error(f"Error listing S3 files: {str(e)}")
        return []

def check_pdf_already_processed(file_prefix):
    """Check if both FAISS and PKL files exist for a PDF"""
    faiss_key = f"{file_prefix}.faiss"
    pkl_key = f"{file_prefix}.pkl"
    
    faiss_exists = check_s3_file_exists(faiss_key)
    pkl_exists = check_s3_file_exists(pkl_key)
    
    return faiss_exists and pkl_exists, faiss_key, pkl_key
def split_text(text, chunk_size, chunk_overlap, original_filename):
    """Split text into chunks and enrich metadata with original filename"""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(text)
    
    # Enrich metadata with original filename
    for chunk in chunks:
        if hasattr(chunk, 'metadata'):
            chunk.metadata['original_filename'] = original_filename
        else:
            chunk.metadata = {'original_filename': original_filename}
    
    return chunks
#create vector store
def create_vector_store(request_id, chunks, file_prefix="my_faiss"):
    """Create vector store and upload to S3 with custom naming"""
    #using FAISS
    #Using Bedrock Embeddings to create vector index
    vector_store_faiss = FAISS.from_documents(chunks,bedrock_embeddings)
    #save the vector store to the local directory
    #create a folder for the request id then save the vector store to the tmp folder
    file_name = f"{request_id}.bin"
    folder_path = "/tmp/"
    vector_store_faiss.save_local(index_name=file_name, folder_path=folder_path)
    
    # Use custom prefix for S3 keys to avoid conflicts
    s3_faiss_key = f"{file_prefix}.faiss"
    s3_pkl_key = f"{file_prefix}.pkl"
    
    #upload the file to the S3 bucket
    s3_client.upload_file(Filename=folder_path + file_name+'.faiss', Bucket=S3_BUCKET, Key=s3_faiss_key)
    s3_client.upload_file(Filename=folder_path + file_name+'.pkl', Bucket=S3_BUCKET, Key=s3_pkl_key)

    return True, s3_faiss_key, s3_pkl_key

def process_pdf_file(pdf_path, progress_callback=None, skip_existing=True):
    """Process a single PDF file and create vector store"""
    try:
        # Get original filename for metadata and S3 naming
        original_filename = os.path.basename(pdf_path)
        file_prefix = os.path.splitext(original_filename)[0].replace(" ", "_").replace("(", "").replace(")", "")
        
        if progress_callback:
            progress_callback(f"📄 Processing: {original_filename}")
        
        # Check if file already exists in S3
        if skip_existing:
            already_processed, existing_faiss_key, existing_pkl_key = check_pdf_already_processed(file_prefix)
            if already_processed:
                if progress_callback:
                    progress_callback(f"⏭️ Skipping {original_filename} - already exists in S3")
                    progress_callback(f"📁 Existing files: {existing_faiss_key}, {existing_pkl_key}")
                return True, original_filename, "N/A", "N/A", existing_faiss_key, existing_pkl_key, "skipped"
        
        # Generate unique request ID for this file
        request_id = str(uuid.uuid4())
        
        # Load the PDF file
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()
        
        if progress_callback:
            progress_callback(f"📖 Loaded {len(pages)} pages from {original_filename}")
        
        # Split text into chunks
        chunks = split_text(pages, 1000, 200, original_filename)
        
        if progress_callback:
            progress_callback(f"✂️ Created {len(chunks)} chunks from {original_filename}")
        
        # Create vector store
        success, faiss_key, pkl_key = create_vector_store(request_id, chunks, file_prefix)
        
        if success:
            if progress_callback:
                progress_callback(f"✅ Vector store created for {original_filename}")
                progress_callback(f"📤 Uploaded to S3: {faiss_key} and {pkl_key}")
            return True, original_filename, len(pages), len(chunks), faiss_key, pkl_key, "processed"
        else:
            if progress_callback:
                progress_callback(f"❌ Failed to create vector store for {original_filename}")
            return False, original_filename, len(pages), len(chunks), None, None, "failed"
            
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Error processing {original_filename}: {str(e)}")
        return False, original_filename, 0, 0, None, str(e), "error"

def bulk_process_pdfs(skip_existing=True):
    """Process all PDF files in the pdf-sources folder"""
    # Get the project root directory (one level up from Admin folder)
    project_root = Path(__file__).parent.parent
    pdf_sources_path = project_root / "pdf-sources"
    
    # Find all PDF files
    pdf_files = list(pdf_sources_path.glob("*.pdf"))
    
    if not pdf_files:
        st.error("No PDF files found in pdf-sources folder!")
        return
    
    # Check existing files in S3 if skipping duplicates
    if skip_existing:
        st.info("🔍 Checking for existing files in S3...")
        existing_files = get_existing_s3_files()
        st.write(f"Found {len(existing_files)} existing files in S3 bucket")
    
    st.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Create UI components for progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create scrollable container for real-time updates
    st.subheader("📝 Processing Log")
    log_container = st.container()
    with log_container:
        log_placeholder = st.empty()
    
    # Initialize log content
    log_messages = []
    # Generate unique session ID for this processing session
    session_id = str(uuid.uuid4())[:8]
    
    def update_progress(message):
        status_text.text(message)
        log_messages.append(message)
        # Keep only last 50 messages to prevent UI overload
        if len(log_messages) > 50:
            log_messages.pop(0)
        
        # Update scrollable log with latest messages
        # Use timestamp + session to ensure unique keys
        unique_key = f"log_area_{session_id}_{int(time.time() * 1000) % 10000}"
        with log_placeholder.container():
            st.text_area(
                "Real-time Processing Updates", 
                value="\n".join(log_messages),
                height=300,
                disabled=True,
                key=unique_key
            )
    
    results = []
    
    # Process each PDF file
    for i, pdf_path in enumerate(pdf_files):
        try:
            update_progress(f"🔄 Starting {i+1}/{len(pdf_files)}: {pdf_path.name}")
            
            # Process with duplicate checking
            process_result = process_pdf_file(
                str(pdf_path), 
                progress_callback=update_progress,
                skip_existing=skip_existing
            )
            
            # Handle the extended return format
            if len(process_result) == 7:
                success, filename, pages, chunks, faiss_key, pkl_key, status = process_result
            else:
                # Fallback for old format
                success, filename, pages, chunks, faiss_key, pkl_key = process_result
                status = "processed" if success else "failed"
            
            results.append({
                'filename': filename,
                'success': success,
                'pages': pages,
                'chunks': chunks,
                'faiss_key': faiss_key,
                'pkl_key': pkl_key,
                'status': status
            })
            
            # Update progress bar
            progress_bar.progress((i + 1) / len(pdf_files))
            
            # Add a small delay to prevent overwhelming the system
            time.sleep(0.3)
            
        except Exception as e:
            error_msg = f"❌ Failed to process {pdf_path.name}: {str(e)}"
            update_progress(error_msg)
            results.append({
                'filename': pdf_path.name,
                'success': False,
                'pages': 0,
                'chunks': 0,
                'faiss_key': None,
                'pkl_key': None,
                'status': 'error',
                'error': str(e)
            })
    
    # Display final results
    update_progress("🎉 Bulk processing completed!")
    status_text.text("🎉 Bulk processing completed!")
    
    # Summary metrics
    st.subheader("📊 Processing Summary")
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    skipped = sum(1 for r in results if r.get('status') == 'skipped')
    processed = sum(1 for r in results if r.get('status') == 'processed')
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Files", len(results))
    with col2:
        st.metric("Processed", processed, delta=f"+{processed}")
    with col3:
        st.metric("Skipped", skipped, delta=f"↻{skipped}")
    with col4:
        st.metric("Failed", failed, delta=f"-{failed}" if failed > 0 else None)
    
    # Detailed results table
    st.subheader("📋 Detailed Results")
    
    # Create tabs for different result types
    if skipped > 0:
        tab1, tab2, tab3 = st.tabs(["✅ All Results", "📁 Skipped Files", "🔄 Processed Files"])
    else:
        tab1, tab2 = st.tabs(["✅ All Results", "🔄 Processed Files"])
        tab3 = None
    
    with tab1:
        for result in results:
            if result['success']:
                if result.get('status') == 'skipped':
                    st.info(f"⏭️ {result['filename']} (Skipped - already exists)")
                    st.write(f"   📁 Existing S3 files: {result['faiss_key']}, {result['pkl_key']}")
                else:
                    st.success(f"✅ {result['filename']} (Newly processed)")
                    st.write(f"   📖 Pages: {result['pages']} | ✂️ Chunks: {result['chunks']}")
                    st.write(f"   📤 S3 Keys: {result['faiss_key']}, {result['pkl_key']}")
            else:
                st.error(f"❌ {result['filename']}")
                if 'error' in result:
                    st.write(f"   Error: {result['error']}")
    
    if tab3:  # Skipped files tab
        with tab3:
            skipped_files = [r for r in results if r.get('status') == 'skipped']
            if skipped_files:
                st.write(f"**{len(skipped_files)} files were skipped because they already exist in S3:**")
                for result in skipped_files:
                    st.info(f"📁 {result['filename']}")
                    st.write(f"   Existing files: {result['faiss_key']}, {result['pkl_key']}")
            else:
                st.write("No files were skipped.")
    
    with tab2:  # Processed files tab
        processed_files = [r for r in results if r.get('status') == 'processed']
        if processed_files:
            st.write(f"**{len(processed_files)} files were newly processed:**")
            for result in processed_files:
                st.success(f"✅ {result['filename']}")
                st.write(f"   📖 Pages: {result['pages']} | ✂️ Chunks: {result['chunks']}")
                st.write(f"   📤 S3 Keys: {result['faiss_key']}, {result['pkl_key']}")
        else:
            st.write("No files were newly processed.")
    
    return results

def main():
    st.title("🏥 Healthcare Insurance PDF Processing System")
    st.write("Process healthcare insurance documents to create searchable vector stores.")
    
    # Create tabs for different processing options
    tab1, tab2 = st.tabs(["📄 Single File Upload", "📚 Bulk Process All PDFs"])
    
    with tab1:
        st.header("Single PDF File Processing")
        st.write("Upload a single PDF file to process it individually.")
        
        #Upload the file
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        if uploaded_file is not None:
            #get the request id
            request_id = str(uuid.uuid4())
            st.write(f"Request ID: {request_id}")
            saved_file_name = f"{request_id}.pdf"
            
            #Save the uploaded file to the local directory  
            with open(saved_file_name, "wb") as w:
                #getvalue() returns the file content as bytes
                w.write(uploaded_file.getvalue())
            
            #Load the file into a Langchain loader
            loader = PyPDFLoader(saved_file_name)
            #Split the file into pages
            pages = loader.load_and_split()
            st.write(f"📖 Loaded {len(pages)} pages")
            
            #Split the text into chunks using the split_text function
            original_filename = uploaded_file.name
            chunks = split_text(pages, 1000, 200, original_filename)
            st.write(f"✂️ Splitting the text into chunks. Splitted Documents length: {len(chunks)}")
            
            # Show sample chunks
            with st.expander("📋 View Sample Chunks"):
                if len(chunks) > 0:
                    st.write("**Chunk 1:**")
                    st.write(chunks[0])
                if len(chunks) > 1:
                    st.write("**Chunk 2:**")
                    st.write(chunks[1])
                if len(chunks) > 2:
                    st.write("**Chunk 3:**")
                    st.write(chunks[2])

            st.write("🔄 Creating vector store...")
            
            # Create file prefix for S3 naming
            file_prefix = os.path.splitext(original_filename)[0].replace(" ", "_").replace("(", "").replace(")", "")
            
            # Check if file already exists
            already_processed, existing_faiss_key, existing_pkl_key = check_pdf_already_processed(file_prefix)
            if already_processed:
                st.info("⚠️ This file already has a vector store in S3!")
                st.write(f"📁 Existing files: `{existing_faiss_key}`, `{existing_pkl_key}`")
                
                overwrite = st.checkbox("Overwrite existing vector store", value=False)
                if not overwrite:
                    st.warning("Processing cancelled. Uncheck the box above to overwrite existing files.")
                    # Clean up the temporary file
                    if os.path.exists(saved_file_name):
                        os.remove(saved_file_name)
                    return
            
            try:
                success, faiss_key, pkl_key = create_vector_store(request_id, chunks, file_prefix)
                if success:
                    st.success("✅ Vector store created successfully!")
                    st.write(f"📤 Uploaded to S3:")
                    st.write(f"   - FAISS index: `{faiss_key}`")
                    st.write(f"   - Pickle file: `{pkl_key}`")
                else:
                    st.error("❌ Vector store creation failed")
            except Exception as e:
                st.error(f"❌ Error creating vector store: {str(e)}")
            
            # Clean up the temporary file
            if os.path.exists(saved_file_name):
                os.remove(saved_file_name)
    
    with tab2:
        st.header("Bulk PDF Processing")
        st.write("Process all PDF files in the `pdf-sources` folder automatically.")
        
        # Show available files
        project_root = Path(__file__).parent.parent
        pdf_sources_path = project_root / "pdf-sources"
        pdf_files = list(pdf_sources_path.glob("*.pdf"))
        
        if pdf_files:
            st.write(f"📁 Found {len(pdf_files)} PDF files in `pdf-sources` folder:")
            for pdf_file in pdf_files:
                st.write(f"   • {pdf_file.name}")
        else:
            st.warning("⚠️ No PDF files found in `pdf-sources` folder!")
            return
        
        st.write("---")
        
        # Add warning about processing time
        st.warning("⏱️ **Note:** Bulk processing may take several minutes depending on the number and size of PDF files. Each file will be processed sequentially to avoid overwhelming the system.")
        
        # Options for bulk processing
        st.write("**Processing Options:**")
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            skip_existing = st.checkbox(
                "Skip existing files", 
                value=True, 
                help="Skip files that already have vector stores in S3 to avoid duplicates"
            )
        
        with col_opt2:
            if skip_existing:
                st.info("✅ Will check S3 for existing files")
            else:
                st.warning("⚠️ Will overwrite existing files")
        
        # Show current S3 status
        if skip_existing:
            with st.expander("📁 View Current S3 Files"):
                try:
                    existing_files = get_existing_s3_files()
                    if existing_files:
                        st.write(f"**Found {len(existing_files)} files in S3 bucket:**")
                        for file_key in sorted(existing_files):
                            st.write(f"  • {file_key}")
                    else:
                        st.write("No files found in S3 bucket.")
                except Exception as e:
                    st.error(f"Error checking S3: {str(e)}")
        
        # Bulk processing button
        if st.button("🚀 Start Bulk Processing", type="primary", use_container_width=True):
            st.write("🔄 Starting bulk processing...")
            
            # Run bulk processing with options
            results = bulk_process_pdfs(skip_existing=skip_existing)
            
            # Show final summary
            if results:
                successful_count = sum(1 for r in results if r['success'])
                total_count = len(results)
                skipped_count = sum(1 for r in results if r.get('status') == 'skipped')
                processed_count = sum(1 for r in results if r.get('status') == 'processed')
                
                if successful_count == total_count:
                    if skipped_count > 0:
                        st.success(f"🎉 Processing completed! {processed_count} new files processed, {skipped_count} existing files skipped.")
                    else:
                        st.success(f"🎉 All {total_count} files processed successfully!")
                elif successful_count > 0:
                    st.warning(f"⚠️ {successful_count}/{total_count} files handled successfully ({processed_count} processed, {skipped_count} skipped). Check results above.")
                else:
                    st.error(f"❌ Failed to process any files. Check the error messages above.")
                
                # Show S3 bucket status
                if processed_count > 0:
                    st.info("💡 **Next Steps:** Your vector stores are now available in S3. You can use the User Interface to query these documents.")
                elif skipped_count > 0:
                    st.info("💡 **All files already exist in S3.** You can use the User Interface to query these documents.")
        
        # Add helpful information
        st.write("---")
        st.subheader("ℹ️ How Bulk Processing Works")
        st.write("""
        1. **Scans** the `pdf-sources` folder for all PDF files
        2. **Processes** each file individually (text extraction → chunking → embeddings)
        3. **Creates** separate FAISS vector stores for each document
        4. **Uploads** each vector store to S3 with unique naming
        5. **Reports** detailed results for each file
        
        Each document gets its own vector store, allowing for:
        - **Individual document queries**
        - **Better source attribution**
        - **Easier management and updates**
        """)
        
        # Show technical details
        with st.expander("🔧 Technical Details"):
            st.write("""
            **Processing Parameters:**
            - Chunk Size: 1000 characters
            - Chunk Overlap: 200 characters
            - Embedding Model: Amazon Titan Text Embeddings V2
            - Vector Store: FAISS
            - Storage: Amazon S3
            
            **File Naming Convention:**
            - Original: `document name.pdf`
            - S3 Keys: `document_name.faiss` and `document_name.pkl`
            """)
        
        # Show current S3 bucket info
        st.write("---")
        st.subheader("☁️ S3 Configuration")
        st.write(f"**Bucket:** `{S3_BUCKET}`")
        st.write(f"**Region:** `{region}`")



if __name__ == '__main__':
    main()