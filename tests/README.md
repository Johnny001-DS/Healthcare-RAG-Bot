# RAG-LLM Healthcare Insurance Test Suite

This directory contains all test files for the RAG-LLM Healthcare Insurance project.

## Test Files

### Infrastructure Tests
- `test_s3_connection.py` - Tests AWS S3 connectivity and bucket access
- `test_bedrock_simple.py` - Tests Amazon Bedrock model access and invocation
- `test_boto3.py` - Tests boto3 configuration and basic AWS connectivity

### Component Tests
- `test_embedding_regions.py` - Tests embedding generation across different AWS regions
- `test_nova_converse.py` - Tests Amazon Nova model conversation capabilities
- `test_admin_embedding.py` - Tests admin interface embedding functionality
- `test_user_interface.py` - Tests user interface configuration and setup
- `test_bulk_processing.py` - Tests bulk PDF processing functionality for admin interface

### Integration Tests
- `test_complete_system.py` - End-to-end test of the entire RAG system

## Running Tests

### Quick Start
From the project root directory, run:

```bash
# Using Python directly
python3 run_tests.py

# Or using the shell script (recommended)
./run_tests.sh
```

### Running Individual Tests
You can also run individual test files:

```bash
python3 tests/test_s3_connection.py
python3 tests/test_bedrock_simple.py
# ... etc
```

## Test Output

The test runner provides:
- ✅ **Pass/Fail status** for each test
- 📊 **Summary statistics** (total, passed, failed)
- ⏱️ **Execution time** for the entire suite
- 🔧 **Next steps** based on results

## Prerequisites

1. **Environment Setup**: Ensure your `.env` file is configured with:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION`
   - `BUCKET_NAME`

2. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   # or if using Admin requirements:
   pip install -r Admin/requirements.txt
   ```

3. **AWS Access**: Ensure your AWS account has access to:
   - Amazon S3
   - Amazon Bedrock
   - Required models (Titan Embeddings, Nova Lite)

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify AWS credentials in `.env` file
   - Check IAM permissions for S3 and Bedrock

2. **Model Access Errors**
   - Request access to Amazon Bedrock in AWS Console
   - Enable required models in Bedrock model access

3. **Region Errors**
   - Ensure your region supports Bedrock
   - Update `AWS_DEFAULT_REGION` in `.env`

4. **Timeout Errors**
   - Check network connectivity
   - Verify AWS service status

### Getting Help

If tests fail:
1. Review the detailed error output
2. Check the troubleshooting tips in test output
3. Verify your AWS configuration
4. Ensure all dependencies are installed

## Test Development

When adding new tests:
1. Name files with `test_` prefix
2. Include a main function for standalone execution
3. Add comprehensive error handling and user-friendly output
4. Update this README with new test descriptions
