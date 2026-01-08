"""
UI components module.
Contains reusable Streamlit UI components for the admin interface.
"""

import os
import uuid
from pathlib import Path
from typing import List

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader

# Handle both relative and absolute imports
try:
    from .config import config
    from .pdf_processor import pdf_processor
    from .s3_operations import s3_manager
    from .bulk_processor import bulk_processor
except ImportError:
    from config import config
    from pdf_processor import pdf_processor
    from s3_operations import s3_manager
    from bulk_processor import bulk_processor

class AdminUIComponents:
    """Contains UI components for the admin interface."""
    
    def __init__(self):
        self.pdf_processor = pdf_processor
        self.s3_manager = s3_manager
        self.bulk_processor = bulk_processor
    
    def render_single_file_upload_tab(self):
        """Render the single file upload tab."""
        st.header("Single PDF File Processing")
        st.write("Upload a single PDF file to process it individually.")
        
        # Upload the file
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        if uploaded_file is not None:
            self._process_single_uploaded_file(uploaded_file)
    
    def render_bulk_processing_tab(self):
        """Render the bulk processing tab."""
        st.header("Bulk PDF Processing")
        st.write("Process all PDF files in the `pdf-sources` folder automatically.")
        
        # Show available files
        project_root = Path(__file__).parent.parent
        pdf_sources_path = project_root / "pdf-sources"
        pdf_files = self.bulk_processor.find_pdf_files(pdf_sources_path)
        
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
        
        # Processing options
        skip_existing = self._render_processing_options()
        
        # Show current S3 status
        if skip_existing:
            self._render_s3_status_expander()
        
        # Bulk processing button
        if st.button("🚀 Start Bulk Processing", type="primary", use_container_width=True):
            self._handle_bulk_processing(skip_existing)
        
        # Add helpful information
        self._render_help_sections()
    
    def _process_single_uploaded_file(self, uploaded_file):
        """Process a single uploaded file."""
        # Get request ID
        request_id = str(uuid.uuid4())
        st.write(f"Request ID: {request_id}")
        saved_file_name = f"{request_id}.pdf"
        
        # Save the uploaded file to the local directory
        with open(saved_file_name, "wb") as w:
            w.write(uploaded_file.getvalue())
        
        try:
            # Load the file into a Langchain loader
            loader = PyPDFLoader(saved_file_name)
            pages = loader.load_and_split()
            st.write(f"📖 Loaded {len(pages)} pages")
            
            # Split the text into chunks
            original_filename = uploaded_file.name
            chunks = self.pdf_processor.split_text(pages, original_filename)
            st.write(f"✂️ Splitting the text into chunks. Splitted Documents length: {len(chunks)}")
            
            # Show sample chunks
            self._render_sample_chunks(chunks)
            
            st.write("🔄 Creating vector store...")
            
            # Create file prefix for S3 naming
            file_prefix = self.pdf_processor._clean_filename_for_s3(original_filename)
            
            # Check if file already exists
            self._handle_existing_file_check(file_prefix, request_id, chunks, saved_file_name)
            
        finally:
            # Clean up the temporary file
            if os.path.exists(saved_file_name):
                os.remove(saved_file_name)
    
    def _render_sample_chunks(self, chunks: List):
        """Render sample chunks in an expander."""
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
    
    def _handle_existing_file_check(self, file_prefix: str, request_id: str, chunks: List, saved_file_name: str):
        """Handle checking for existing files and processing."""
        already_processed, existing_faiss_key, existing_pkl_key = self.s3_manager.check_pdf_already_processed(file_prefix)
        
        if already_processed:
            st.info("⚠️ This file already has a vector store in S3!")
            st.write(f"📁 Existing files: `{existing_faiss_key}`, `{existing_pkl_key}`")
            
            overwrite = st.checkbox("Overwrite existing vector store", value=False)
            if not overwrite:
                st.warning("Processing cancelled. Check the box above to overwrite existing files.")
                return
        
        try:
            success, faiss_key, pkl_key = self.pdf_processor.create_vector_store(request_id, chunks, file_prefix)
            if success:
                st.success("✅ Vector store created successfully!")
                st.write(f"📤 Uploaded to S3:")
                st.write(f"   - FAISS index: `{faiss_key}`")
                st.write(f"   - Pickle file: `{pkl_key}`")
            else:
                st.error("❌ Vector store creation failed")
        except Exception as e:
            st.error(f"❌ Error creating vector store: {str(e)}")
    
    def _render_processing_options(self) -> bool:
        """Render processing options and return skip_existing setting."""
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
        
        return skip_existing
    
    def _render_s3_status_expander(self):
        """Render S3 status expander."""
        with st.expander("📁 View Current S3 Files"):
            try:
                existing_files = self.s3_manager.get_existing_files()
                if existing_files:
                    st.write(f"**Found {len(existing_files)} files in S3 bucket:**")
                    for file_key in sorted(existing_files):
                        st.write(f"  • {file_key}")
                else:
                    st.write("No files found in S3 bucket.")
            except Exception as e:
                st.error(f"Error checking S3: {str(e)}")
    
    def _handle_bulk_processing(self, skip_existing: bool):
        """Handle bulk processing execution."""
        st.write("🔄 Starting bulk processing...")
        
        # Run bulk processing with options
        results = self.bulk_processor.process_all_pdfs(skip_existing=skip_existing)
        
        # Display results
        if results:
            self.bulk_processor.display_results_summary(results)
            
            # Show final summary message
            self._display_final_summary(results)
    
    def _display_final_summary(self, results: List):
        """Display final summary message."""
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
    
    def _render_help_sections(self):
        """Render help and information sections."""
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
            st.write(f"""
            **Processing Parameters:**
            - Chunk Size: {config.chunk_size} characters
            - Chunk Overlap: {config.chunk_overlap} characters
            - Embedding Model: {config.embedding_model_id}
            - Vector Store: FAISS
            - Storage: Amazon S3
            
            **File Naming Convention:**
            - Original: `document name.pdf`
            - S3 Keys: `document_name.faiss` and `document_name.pkl`
            """)
        
        # Show current S3 bucket info
        st.write("---")
        st.subheader("☁️ S3 Configuration")
        st.write(f"**Bucket:** `{config.s3_bucket}`")
        st.write(f"**Region:** `{config.aws_region}`")

# Global UI components instance
ui_components = AdminUIComponents()
