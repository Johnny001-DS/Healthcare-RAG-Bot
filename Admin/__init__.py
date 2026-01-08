"""
Admin package for Healthcare Insurance PDF Processing System.

This package provides a modular architecture for processing healthcare insurance
PDFs and creating searchable vector stores using AWS services.

Modules:
- config: Configuration and AWS client management
- s3_operations: Amazon S3 file operations
- pdf_processor: PDF processing and vector store creation
- bulk_processor: Bulk processing coordination
- ui_components: Streamlit UI components
"""

from .config import config
from .s3_operations import s3_manager
from .pdf_processor import pdf_processor
from .bulk_processor import bulk_processor
from .ui_components import ui_components

__all__ = [
    'config',
    's3_manager', 
    'pdf_processor',
    'bulk_processor',
    'ui_components'
]

__version__ = '2.0.0'
__author__ = 'Healthcare Insurance RAG Team'
