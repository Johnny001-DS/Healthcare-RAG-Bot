"""
Configuration module for the admin interface.
Handles environment variables, AWS clients, and global settings.
"""

import os
import boto3
from dotenv import load_dotenv
from langchain_community.embeddings import BedrockEmbeddings

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for AWS and application settings."""
    
    def __init__(self):
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_DEFAULT_REGION")
        self.s3_bucket = os.getenv('BUCKET_NAME')
        
        # Processing parameters
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.embedding_model_id = "amazon.titan-embed-text-v2:0"
        
        # Initialize AWS clients
        self._s3_client = None
        self._bedrock_client = None
        self._bedrock_embeddings = None
    
    @property
    def s3_client(self):
        """Lazy initialization of S3 client."""
        if self._s3_client is None:
            self._s3_client = boto3.client('s3')
        return self._s3_client
    
    @property
    def bedrock_client(self):
        """Lazy initialization of Bedrock client."""
        if self._bedrock_client is None:
            self._bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=self.aws_region
            )
        return self._bedrock_client
    
    @property
    def bedrock_embeddings(self):
        """Lazy initialization of Bedrock embeddings."""
        if self._bedrock_embeddings is None:
            self._bedrock_embeddings = BedrockEmbeddings(
                model_id=self.embedding_model_id, 
                client=self.bedrock_client
            )
        return self._bedrock_embeddings

# Global configuration instance
config = Config()
