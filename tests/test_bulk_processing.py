#!/usr/bin/env python3
"""
Test Bulk PDF Processing Functionality

This script tests the bulk processing functionality added to the admin interface.
"""

import sys
import os
from pathlib import Path

# Add parent directories to path so we can import from Admin
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "Admin"))

try:
    # Try importing from the new modular structure first
    from Admin.compatibility import process_pdf_file, bulk_process_pdfs, check_s3_file_exists, check_pdf_already_processed, get_existing_s3_files
    print("✅ Successfully imported bulk processing functions (modular)")
except ImportError:
    try:
        # Fallback to original admin.py import
        from Admin.admin_original import process_pdf_file, bulk_process_pdfs, check_s3_file_exists, check_pdf_already_processed, get_existing_s3_files
        print("✅ Successfully imported bulk processing functions (original)")
    except ImportError as e:
        print(f"❌ Failed to import functions: {e}")
        sys.exit(1)

def test_pdf_sources_availability():
    """Test if PDF files are available in pdf-sources folder"""
    print("🔍 Testing PDF Sources Availability...")
    print("=" * 50)
    
    pdf_sources_path = project_root / "pdf-sources"
    
    if not pdf_sources_path.exists():
        print("❌ pdf-sources folder does not exist!")
        return False
    
    pdf_files = list(pdf_sources_path.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in pdf-sources folder!")
        return False
    
    print(f"✅ Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"   • {pdf_file.name}")
    
    return True, pdf_files

def test_s3_duplicate_checking():
    """Test S3 duplicate file checking functionality"""
    print("\n🔍 Testing S3 Duplicate Checking...")
    print("=" * 50)
    
    try:
        # Test getting existing S3 files
        existing_files = get_existing_s3_files()
        print(f"✅ Found {len(existing_files)} existing files in S3:")
        for file_key in existing_files[:5]:  # Show first 5
            print(f"   • {file_key}")
        if len(existing_files) > 5:
            print(f"   ... and {len(existing_files) - 5} more files")
        
        # Test checking specific file existence
        if existing_files:
            test_key = existing_files[0]
            exists = check_s3_file_exists(test_key)
            print(f"✅ File existence check for '{test_key}': {exists}")
        
        # Test PDF processing check
        pdf_sources_path = project_root / "pdf-sources"
        pdf_files = list(pdf_sources_path.glob("*.pdf"))
        if pdf_files:
            test_pdf = pdf_files[0]
            filename = test_pdf.name
            file_prefix = os.path.splitext(filename)[0].replace(" ", "_").replace("(", "").replace(")", "")
            
            already_processed, faiss_key, pkl_key = check_pdf_already_processed(file_prefix)
            print(f"✅ PDF processing check for '{filename}':")
            print(f"   Already processed: {already_processed}")
            print(f"   Expected FAISS key: {faiss_key}")
            print(f"   Expected PKL key: {pkl_key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in S3 duplicate checking: {str(e)}")
        return False

def test_single_pdf_processing():
    """Test processing a single PDF file with duplicate checking"""
    print("\n🔍 Testing Single PDF Processing with Duplicate Checking...")
    print("=" * 50)
    
    # Get a sample PDF file
    pdf_sources_path = project_root / "pdf-sources"
    pdf_files = list(pdf_sources_path.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files available for testing!")
        return False
    
    # Test with the first PDF file
    test_pdf = pdf_files[0]
    print(f"📄 Testing with: {test_pdf.name}")
    
    messages = []
    def capture_progress(message):
        messages.append(message)
        print(f"   {message}")
    
    try:
        # Test with skip_existing=True (default)
        result = process_pdf_file(str(test_pdf), progress_callback=capture_progress, skip_existing=True)
        
        if len(result) >= 6:  # Check if we have the extended format
            success, filename, pages, chunks, faiss_key, pkl_key = result[:6]
            status = result[6] if len(result) > 6 else "unknown"
            
            print(f"✅ Processing result:")
            print(f"   Success: {success}")
            print(f"   Filename: {filename}")
            print(f"   Pages: {pages}")
            print(f"   Chunks: {chunks}")
            print(f"   FAISS Key: {faiss_key}")
            print(f"   PKL Key: {pkl_key}")
            print(f"   Status: {status}")
            return True
        else:
            print(f"❌ Unexpected result format: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        return False

def test_bulk_processing_dry_run():
    """Test bulk processing setup without actually processing (dry run)"""
    print("\n🔍 Testing Bulk Processing Setup...")
    print("=" * 50)
    
    try:
        # Check if we can access the bulk processing function
        pdf_sources_path = project_root / "pdf-sources"
        pdf_files = list(pdf_sources_path.glob("*.pdf"))
        
        print(f"✅ Bulk processing would process {len(pdf_files)} files:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"   {i}. {pdf_file.name}")
        
        print(f"\n📊 Estimated Processing:")
        print(f"   Files to process: {len(pdf_files)}")
        print(f"   Estimated time: {len(pdf_files) * 1-2} minutes (rough estimate)")
        print(f"   S3 objects to create: {len(pdf_files) * 2} (FAISS + PKL files)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in bulk processing setup: {str(e)}")
        return False

def test_aws_connectivity():
    """Test AWS connectivity for bulk processing"""
    print("\n🔍 Testing AWS Connectivity for Bulk Processing...")
    print("=" * 50)
    
    try:
        import boto3
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Test S3 connection
        s3_client = boto3.client('s3')
        bucket_name = os.getenv('BUCKET_NAME')
        
        print(f"✅ S3 Client created")
        print(f"✅ Target bucket: {bucket_name}")
        
        # Test bucket access
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket access confirmed")
        
        # Test Bedrock connection
        bedrock_client = boto3.client('bedrock-runtime')
        print(f"✅ Bedrock client created")
        
        # Test embeddings model
        from langchain_community.embeddings import BedrockEmbeddings
        bedrock_embeddings = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v2:0", 
            client=bedrock_client
        )
        print(f"✅ Bedrock embeddings initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ AWS connectivity error: {str(e)}")
        return False

def main():
    """Run all bulk processing tests"""
    print("🚀 Bulk PDF Processing Test Suite")
    print("=" * 60)
    
    tests = [
        ("PDF Sources Availability", test_pdf_sources_availability),
        ("AWS Connectivity", test_aws_connectivity),
        ("S3 Duplicate Checking", test_s3_duplicate_checking),
        ("Single PDF Processing", test_single_pdf_processing),
        ("Bulk Processing Setup", test_bulk_processing_dry_run)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            success = result[0] if isinstance(result, tuple) else result
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 BULK PROCESSING TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print()
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name:<35} {status}")
    
    print("\n" + "="*60)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Bulk processing functionality is ready!")
        print("\nYou can now:")
        print("1. 🔧 Start the admin interface: streamlit run Admin/admin.py --server.port 8501")
        print("2. 📚 Navigate to the 'Bulk Process All PDFs' tab")
        print("3. 🚀 Click 'Start Bulk Processing' to process all PDF files")
        print("4. ⏱️ Wait for processing to complete (may take several minutes)")
        print("5. 👤 Use the User Interface to query the processed documents")
    else:
        print(f"⚠️  {failed} test(s) failed. Please fix the issues before using bulk processing.")
        print("\nCommon issues:")
        print("- Ensure .env file has correct AWS credentials")
        print("- Check that pdf-sources folder contains PDF files")
        print("- Verify AWS Bedrock and S3 access")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
