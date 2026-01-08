# 🏥 RAG-LLM Healthcare Insurance Assistant

An intelligent healthcare insurance document assistant powered by **Amazon Bedrock** and **Retrieval-Augmented Generation (RAG)**. This application transforms complex healthcare insurance PDFs into an interactive knowledge base, allowing you to get instant, accurate answers to your questions using state-of-the-art AI models.

**Built with ❤️ for healthcare insurance professionals.**

## 👤 Author

**Karan Badlani**

## ✨ Key Features

- **📄 Smart PDF Processing**: Upload healthcare insurance documents via an intuitive Streamlit interface.
- **🧠 AI-Powered Embeddings**: Generate high-quality embeddings using **Amazon Titan Text Embeddings V2**.
- **💬 Intelligent Q&A**: Ask natural language questions and get contextual answers using **Amazon Nova Lite**.
- **☁️ Cloud Storage**: Automatically store FAISS vector indexes in **Amazon S3** for scalability.
- **🔄 Cross-Region Support**: Leverage AWS cross-region inference for optimal performance.
- **⚙️ Easy Configuration**: Simple environment variable setup.
- **🎯 Healthcare Focused**: Optimized for insurance terminology, policies, and procedures.

## 🎥 Demos

### 🔍 Data Query Interface
![DataQuery](https://github.com/user-attachments/assets/198dc793-28e2-4541-9501-2ba00d27206d)

### 📚 Batch Processing Feature  
![BatchProcessing_small](https://github.com/user-attachments/assets/3236d685-f939-4a7e-a6c0-92bfba17697c)

## 📋 Prerequisites

Before you begin, ensure you have the following:

- **Python 3.8+**: A modern Python environment.
- **AWS Account**: With access to **Amazon Bedrock** and **S3**.
- **S3 Bucket**: A dedicated bucket for storing FAISS vector indexes.
- **Model Access**: Enable `Amazon Titan Text Embeddings V2` and `Amazon Nova Lite` in the AWS Bedrock Console.

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone <repo-url>
cd RAG-LLM-Healthcare-Insurance
```

### 2. Set Up Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r Admin/requirements.txt
```

### 3. Configure AWS Credentials
Create a `.env` file in the project root with your AWS details:
```env
AWS_ACCESS_KEY_ID=your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key
AWS_DEFAULT_REGION=us-east-2
BUCKET_NAME=your_s3_bucket_name
```

### 4. Enable AWS Bedrock Models
1. Navigate to the **AWS Bedrock Console** → **Model Access**.
2. Request access to:
   - `Amazon Titan Text Embeddings V2`
   - `Amazon Nova Lite`
3. Wait for approval (usually instantaneous).

## 🎯 Usage

### Admin Interface (Document Processing)
The Admin interface allows you to upload and process PDF documents to create the knowledge base.

```bash
streamlit run Admin/admin.py --server.port 8501
```
**Access:** [http://localhost:8501](http://localhost:8501)

**Capabilities:**
- **Single File Upload**: Process individual PDFs.
- **Bulk Processing**: Automatically process all PDFs in the `pdf-sources` directory.
- **Real-time Tracking**: Monitor processing status and results.

### User Interface (Interactive Q&A)
The User interface enables you to query the processed documents.

```bash
streamlit run User/app.py --server.port 8502
```
**Access:** [http://localhost:8502](http://localhost:8502)

**Capabilities:**
- **Natural Language Queries**: Ask questions like "What is the deductible?"
- **Context-Aware Answers**: Receive precise responses based on your documents.
- **Source Attribution**: See which documents contributed to the answer.

## 🔧 Technical Architecture

The application follows a modular architecture (v2.0) designed for scalability and maintainability:

- **Configuration**: Centralized AWS client management (`config.py`).
- **Storage**: S3 file operations and duplicate checking (`s3_operations.py`).
- **Processing**: PDF text extraction and vector creation (`pdf_processor.py`).
- **Orchestration**: Coordination of bulk processing tasks (`bulk_processor.py`).
- **UI Components**: Reusable Streamlit components (`ui_components.py`).

**Tech Stack:** Streamlit, LangChain, FAISS, Amazon Bedrock (Titan V2, Nova Lite), Amazon S3.

## 🧪 Testing

Run the comprehensive test suite to verify your setup:

```bash
# Run all tests
./run_tests.sh
```

Or run specific tests:
```bash
# Test AWS connectivity
python3 tests/test_s3_connection.py

# Test AI model access
python3 tests/test_bedrock_simple.py
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🆘 Troubleshooting

- **AccessDeniedException**: Ensure you have enabled model access in the AWS Bedrock Console.
- **ValidationException**: Check that your AWS region supports the selected models.
- **ConversationNotFound**: Try restarting the Streamlit app or upgrading `boto3`.

---
