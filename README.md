# CHAMPVA Document Validator

A Streamlit web application that validates CHAMPVA claim-support documents for missing or invalid medical codes using OCR and AI analysis.

## Overview

This application helps users validate if their CHAMPVA claim-support documents contain all the required medical codes and information. It performs the following functions:

1. Accepts document uploads (PDF, JPG, PNG) up to 3 files
2. Extracts text from documents using Mistral's OCR API
3. Analyzes the extracted text using OpenAI's Responses API to identify:
   - Document type (Superbill, EOB, or Pharmacy Receipt)
   - Missing or invalid medical codes
   - Other potential issues with the document
4. Displays a detailed analysis for each document

## System Architecture

The application consists of three main components:

### 1. Streamlit UI (`app.py`)

The front-end interface built with Streamlit that handles:
- Document upload functionality
- Processing management
- Results display

### 2. API Handler (`api_handler.py`)

Manages communication with external APIs:
- `process_document_ocr()`: Processes documents using Mistral's OCR API to extract text
- `analyze_document_content()`: Analyzes extracted text using OpenAI's Responses API

### 3. Utility Functions (`utils.py`)

Contains helper functions for:
- File validation
- Document type determination
- Results formatting

## Dependencies

- Python 3.11+
- Streamlit 1.45.0+
- OpenAI Python SDK 1.30+
- Requests 2.32.3+

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```
   export MISTRAL_API_KEY="your_mistral_api_key"
   export OPENAI_API_KEY="your_openai_api_key"
   ```
4. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## How It Works

### Document Upload Flow

1. User uploads 1-3 documents through the Streamlit UI
2. When "Process Documents" is clicked, each document is processed sequentially
3. Each document is:
   - Validated for supported file types
   - Saved to a temporary file
   - Processed with OCR to extract text
   - Analyzed with OpenAI to identify issues
   - Results are stored in the session state

### OCR Processing

The OCR process uses Mistral's OCR API:
1. Document is read as bytes and encoded in base64
2. Content type is determined based on file extension
3. Document is sent to Mistral's API endpoint
4. Extracted text is retrieved and returned

### AI Analysis

The analysis uses OpenAI's Responses API:
1. The extracted text is sent to OpenAI with a prompt that defines:
   - Requirements for each document type
   - Expected JSON response format
2. The application tries multiple models in sequence (gpt-4.1, gpt-4.1-mini, gpt-4)
3. The JSON response is parsed and returned

### Results Display

Results are displayed in an expandable format showing:
- Document type
- Validation status
- Missing codes
- Invalid codes
- Detailed issues
- Additional notes

## Updating the Application

### Updating Dependencies

Update the dependencies in `pyproject.toml`:

```python
[project]
dependencies = [
    "openai>=1.30",
    "requests>=2.32.3",
    "streamlit>=1.45.0",
]
```

### Updating the OCR Provider

If you need to change the OCR provider or update the OCR implementation:

1. Modify the `process_document_ocr()` function in `api_handler.py`
2. Update the API endpoint, headers, and payload structure
3. Adjust the response parsing to match the new provider's output format

### Updating the AI Analysis Provider

To update the AI provider or model:

1. Modify the `analyze_document_content()` function in `api_handler.py`
2. Update the system prompt as needed for better results
3. Update the models list in `models_to_try`
4. Adjust the API parameters as necessary

Example for updating OpenAI models:

```python
# Try newer models when they become available
models_to_try = ["gpt-5", "gpt-4.1", "gpt-4.1-mini"]
```

### Modifying the Document Types and Requirements

To add or modify the document types and their requirements:

1. Update the system prompt in `analyze_document_content()` with new document types and requirements
2. Update the `determine_document_type()` function in `utils.py` if needed
3. Modify the `format_results()` function in `utils.py` to display new fields or information

### Adding New Features

To add new features:

1. **Document Comparison**: Implement logic to compare multiple documents for consistency
2. **User Authentication**: Add user login functionality to save results
3. **Document Template Detection**: Add ability to detect specific document templates
4. **Batch Processing**: Implement a queue system for processing multiple documents

## Troubleshooting

### Common Issues

1. **OpenAI API Error**: If you encounter errors with OpenAI's Responses API:
   - Ensure your API key is valid and has sufficient credits
   - Check that the model names in `models_to_try` are current
   - Make sure the API parameters are correct for the current OpenAI SDK version

2. **Mistral OCR Error**: If OCR is failing:
   - Check the Mistral API key
   - Verify the document format is supported
   - Check if the document size exceeds the 10MB limit

3. **No Text Extracted**: If OCR returns empty text:
   - Make sure the document has machine-readable text (not handwritten)
   - Check if the document is properly scanned and legible
   - Try using a clearer scan or image of the document

## Best Practices for Updates

When updating the application:

1. **Test API Changes**: Always test API changes with sample documents before deploying
2. **Version Control**: Make incremental changes and maintain version control
3. **Error Handling**: Ensure robust error handling for all API calls
4. **Documentation**: Update this README with any significant changes
5. **Dependencies**: Regularly update dependencies to maintain security and compatibility

## License

[Include your license information here] 