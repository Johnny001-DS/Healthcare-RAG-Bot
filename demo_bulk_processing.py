#!/usr/bin/env python3
"""
Bulk Processing Demo Script

This script demonstrates the bulk PDF processing functionality without using Streamlit.
Use this for testing or automated processing of PDF files.
"""

import sys
import os
from pathlib import Path

# Add Admin directory to path
project_root = Path(__file__).parent
sys.path.append(str(project_root / "Admin"))

def main():
    """Demo the bulk processing functionality"""
    print("🚀 RAG-LLM Healthcare Insurance - Bulk Processing Demo")
    print("=" * 60)
    
    try:
        # Try importing from the new modular structure first
        from Admin.compatibility import process_pdf_file, bulk_process_pdfs
        print("✅ Successfully imported processing functions (modular)")
    except ImportError:
        try:
            # Fallback to direct import from Admin
            from admin import bulk_process_pdfs, process_pdf_file
            print("✅ Successfully imported processing functions (original)")
        except ImportError as e:
            print(f"❌ Failed to import functions: {e}")
            print("Make sure you're running this from the project root directory.")
            return False
    
    # Check PDF sources
    pdf_sources_path = project_root / "pdf-sources"
    pdf_files = list(pdf_sources_path.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in pdf-sources folder!")
        return False
    
    print(f"📁 Found {len(pdf_files)} PDF files in pdf-sources:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"   {i}. {pdf_file.name}")
    
    print("\n" + "=" * 60)
    
    # Check existing files in S3
    print("\n🔍 Checking for existing files in S3...")
    try:
        from Admin.compatibility import get_existing_s3_files, check_pdf_already_processed
    except ImportError:
        from admin import get_existing_s3_files, check_pdf_already_processed
    
    existing_s3_files = get_existing_s3_files()
    print(f"Found {len(existing_s3_files)} existing files in S3 bucket")
    
    # Check which PDFs are already processed
    already_processed = []
    needs_processing = []
    
    for pdf_file in pdf_files:
        filename = pdf_file.name
        file_prefix = os.path.splitext(filename)[0].replace(" ", "_").replace("(", "").replace(")", "")
        already_exists, faiss_key, pkl_key = check_pdf_already_processed(file_prefix)
        
        if already_exists:
            already_processed.append((filename, faiss_key, pkl_key))
        else:
            needs_processing.append(filename)
    
    if already_processed:
        print(f"\n📁 {len(already_processed)} files already processed:")
        for filename, faiss_key, pkl_key in already_processed[:3]:  # Show first 3
            print(f"   ✅ {filename}")
        if len(already_processed) > 3:
            print(f"   ... and {len(already_processed) - 3} more")
    
    if needs_processing:
        print(f"\n🔄 {len(needs_processing)} files need processing:")
        for filename in needs_processing[:5]:  # Show first 5
            print(f"   📄 {filename}")
        if len(needs_processing) > 5:
            print(f"   ... and {len(needs_processing) - 5} more")
    
    # Ask user if they want to proceed
    print("\n" + "=" * 60)
    skip_existing = input("Skip files that already exist in S3? (Y/n): ").lower() != 'n'
    
    if skip_existing and not needs_processing:
        print("✅ All files already exist in S3! No processing needed.")
        return True
    
    files_to_process = needs_processing if skip_existing else [f.name for f in pdf_files]
    
    if files_to_process:
        response = input(f"Process {len(files_to_process)} files? This may take several minutes. (y/N): ")
        if response.lower() != 'y':
            print("❌ Processing cancelled by user.")
            return False
    else:
        print("✅ No files need processing.")
        return True
    
    print("\n🔄 Starting bulk processing...")
    print("=" * 60)
    
    # Process files one by one with detailed output
    results = []
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📄 Processing {i}/{len(pdf_files)}: {pdf_path.name}")
        print("-" * 40)
        
        def progress_callback(message):
            print(f"   {message}")
        
        try:
            process_result = process_pdf_file(
                str(pdf_path), 
                progress_callback=progress_callback,
                skip_existing=skip_existing
            )
            
            # Handle extended return format
            if len(process_result) >= 7:
                success, filename, pages, chunks, faiss_key, pkl_key, status = process_result
            else:
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
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                'filename': pdf_path.name,
                'success': False,
                'pages': 0,
                'chunks': 0,
                'faiss_key': None,
                'pkl_key': None,
                'error': str(e)
            })
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 BULK PROCESSING SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    skipped = sum(1 for r in results if r.get('status') == 'skipped')
    processed = sum(1 for r in results if r.get('status') == 'processed')
    
    # Calculate totals only for processed files (not skipped ones)
    total_pages = sum(r['pages'] for r in results if r.get('status') == 'processed' and isinstance(r['pages'], int))
    total_chunks = sum(r['chunks'] for r in results if r.get('status') == 'processed' and isinstance(r['chunks'], int))
    
    print(f"Total Files: {len(results)}")
    print(f"Successful: {successful} ✅")
    print(f"  - Processed: {processed} 🔄")
    print(f"  - Skipped: {skipped} ⏭️")
    print(f"Failed: {failed} ❌")
    print(f"Pages Processed: {total_pages}")
    print(f"Chunks Created: {total_chunks}")
    print(f"S3 Objects Created: {processed * 2} (FAISS + PKL files)")
    
    print("\n📋 Detailed Results:")
    for result in results:
        if result['success']:
            if result.get('status') == 'skipped':
                print(f"⏭️ {result['filename']} (Skipped - already exists)")
                print(f"   📁 S3: {result['faiss_key']}, {result['pkl_key']}")
            else:
                print(f"✅ {result['filename']} (Newly processed)")
                print(f"   📖 Pages: {result['pages']} | ✂️ Chunks: {result['chunks']}")
                print(f"   📤 S3: {result['faiss_key']}, {result['pkl_key']}")
        else:
            print(f"❌ {result['filename']}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
    
    if successful == len(results):
        print(f"\n🎉 All {len(results)} files processed successfully!")
        print("\nNext Steps:")
        print("1. 👤 Start the User Interface: streamlit run User/app.py --server.port 8502")
        print("2. 🔍 Query your processed documents")
        print("3. ☁️ All vector stores are now available in your S3 bucket")
    else:
        print(f"\n⚠️ {failed} file(s) failed to process. Check the errors above.")
    
    return successful == len(results)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Processing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
