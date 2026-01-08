"""
Compatibility layer for backward compatibility with existing code.

This module provides the same interface as the old admin.py file to ensure
that existing tests and external dependencies continue to work.
"""

# Import all the main functions from the new modular structure
# Handle both relative and absolute imports
try:
    from .config import config
    from .s3_operations import s3_manager
    from .pdf_processor import pdf_processor
    from .bulk_processor import bulk_processor
except ImportError:
    from config import config
    from s3_operations import s3_manager
    from pdf_processor import pdf_processor
    from bulk_processor import bulk_processor

# Re-export all the original function names for backward compatibility
def check_s3_file_exists(s3_key):
    """Backward compatibility wrapper for S3 file existence check."""
    return s3_manager.check_file_exists(s3_key)

def get_existing_s3_files():
    """Backward compatibility wrapper for getting existing S3 files."""
    return s3_manager.get_existing_files()

def check_pdf_already_processed(file_prefix):
    """Backward compatibility wrapper for PDF processing check."""
    return s3_manager.check_pdf_already_processed(file_prefix)

def split_text(text, chunk_size, chunk_overlap, original_filename):
    """Backward compatibility wrapper for text splitting."""
    return pdf_processor.split_text(text, original_filename)

def create_vector_store(request_id, chunks, file_prefix="my_faiss"):
    """Backward compatibility wrapper for vector store creation."""
    return pdf_processor.create_vector_store(request_id, chunks, file_prefix)

def process_pdf_file(pdf_path, progress_callback=None, skip_existing=True):
    """Backward compatibility wrapper for PDF file processing."""
    return pdf_processor.process_pdf_file(pdf_path, progress_callback, skip_existing)

def bulk_process_pdfs(skip_existing=True):
    """Backward compatibility wrapper for bulk PDF processing."""
    results = bulk_processor.process_all_pdfs(skip_existing)
    bulk_processor.display_results_summary(results)
    return results

# Export configuration values for backward compatibility
S3_BUCKET = config.s3_bucket
s3_client = config.s3_client
bedrock_client = config.bedrock_client
bedrock_embeddings = config.bedrock_embeddings
region = config.aws_region
