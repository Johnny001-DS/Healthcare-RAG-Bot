"""
Refactored Admin Interface for Healthcare Insurance PDF Processing System.

This is the main entry point for the admin interface, using a modular architecture
with clear separation of concerns.

Modules:
- config: Configuration and AWS client management
- s3_operations: S3 file operations
- pdf_processor: PDF processing and vector store creation
- bulk_processor: Bulk processing coordination
- ui_components: Streamlit UI components
"""

import streamlit as st
from ui_components import ui_components

def main():
    """Main function for the admin interface."""
    st.title("🏥 Healthcare Insurance PDF Processing System")
    st.write("Process healthcare insurance documents to create searchable vector stores.")
    
    # Create tabs for different processing options
    tab1, tab2 = st.tabs(["📄 Single File Upload", "📚 Bulk Process All PDFs"])
    
    with tab1:
        ui_components.render_single_file_upload_tab()
    
    with tab2:
        ui_components.render_bulk_processing_tab()

if __name__ == '__main__':
    main()
