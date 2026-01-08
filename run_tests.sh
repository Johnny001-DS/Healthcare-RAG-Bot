#!/bin/bash
# 
# Test Runner Script for RAG-LLM Healthcare Insurance
# 
# This script runs all tests in the tests/ directory.
# Usage: ./run_tests.sh
#

echo "🚀 Starting RAG-LLM Healthcare Insurance Test Suite..."
echo "=================================================="

# Check if Python virtual environment should be activated
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Run the Python test runner
python3 run_tests.py

# Deactivate virtual environment if it was activated
if [ -d "venv" ]; then
    deactivate
fi
