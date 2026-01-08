"""
S3 operations module.
Handles all interactions with Amazon S3 including file checking, listing, and uploading.
"""

import streamlit as st

# Handle both relative and absolute imports
try:
    from .config import config
except ImportError:
    from config import config

class S3Manager:
    """Manages all S3 operations for the application."""
    
    def __init__(self):
        self.s3_client = config.s3_client
        self.bucket_name = config.s3_bucket
    
    def check_file_exists(self, s3_key: str) -> bool:
        """
        Check if a file exists in S3 bucket.
        
        Args:
            s3_key (str): The S3 key to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except self.s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                # Re-raise for other errors (permissions, etc.)
                raise
        except Exception:
            return False
    
    def get_existing_files(self) -> list:
        """
        Get list of all existing files in S3 bucket.
        
        Returns:
            list: List of S3 keys for existing files
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            st.error(f"Error listing S3 files: {str(e)}")
            return []
    
    def check_pdf_already_processed(self, file_prefix: str) -> tuple:
        """
        Check if both FAISS and PKL files exist for a PDF.
        
        Args:
            file_prefix (str): The file prefix to check
            
        Returns:
            tuple: (exists, faiss_key, pkl_key)
        """
        faiss_key = f"{file_prefix}.faiss"
        pkl_key = f"{file_prefix}.pkl"
        
        faiss_exists = self.check_file_exists(faiss_key)
        pkl_exists = self.check_file_exists(pkl_key)
        
        return faiss_exists and pkl_exists, faiss_key, pkl_key
    
    def upload_vector_store(self, local_faiss_path: str, local_pkl_path: str, 
                           s3_faiss_key: str, s3_pkl_key: str) -> bool:
        """
        Upload vector store files to S3.
        
        Args:
            local_faiss_path (str): Local path to FAISS file
            local_pkl_path (str): Local path to PKL file
            s3_faiss_key (str): S3 key for FAISS file
            s3_pkl_key (str): S3 key for PKL file
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            self.s3_client.upload_file(
                Filename=local_faiss_path, 
                Bucket=self.bucket_name, 
                Key=s3_faiss_key
            )
            self.s3_client.upload_file(
                Filename=local_pkl_path, 
                Bucket=self.bucket_name, 
                Key=s3_pkl_key
            )
            return True
        except Exception as e:
            st.error(f"Error uploading to S3: {str(e)}")
            return False

# Global S3 manager instance
s3_manager = S3Manager()
