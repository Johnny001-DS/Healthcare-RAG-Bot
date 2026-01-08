#!/usr/bin/env python3
"""
RAG-LLM Healthcare Insurance Application

This application provides two interfaces:
1. Admin interface (Admin/admin.py) - For uploading and processing PDF documents
2. User interface (User/app.py) - For querying processed documents

Usage:
- Admin: streamlit run Admin/admin.py --server.port 8501
- User:  streamlit run User/app.py --server.port 8502

Make sure to configure your .env file with AWS credentials before running.
"""

import sys
import os

def print_usage():
    print(__doc__)
    print("\nTo run the applications:")
    print("Admin Interface: streamlit run Admin/admin.py --server.port 8501")
    print("User Interface:  streamlit run User/app.py --server.port 8502")

if __name__ == "__main__":
    print_usage()
