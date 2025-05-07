import os
import requests
import json
import base64
from openai import OpenAI

# API Keys from environment variables
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def process_document_ocr(file_path):
    """
    Process a document using Mistral's OCR API to extract text.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        str: Extracted text from the document
        
    Raises:
        ValueError: If API key is missing or API returns an error
        Exception: For other processing errors
    """
    if not MISTRAL_API_KEY:
        raise ValueError("Mistral API key not found in environment variables")
    
    # Read the file as bytes
    with open(file_path, "rb") as file:
        file_bytes = file.read()
    
    # Encode the file as base64
    file_base64 = base64.b64encode(file_bytes).decode('utf-8')
    
    # Get file extension to determine content type
    file_ext = file_path.split('.')[-1].lower()
    if file_ext == "pdf":
        content_type = "application/pdf"
    elif file_ext in ("jpg", "jpeg"):
        content_type = "image/jpeg"
    else:
        content_type = f"image/{file_ext}"
        
    # Check file size
    file_size_mb = len(file_base64) / 1024 / 1024  # Convert to MB
    if file_size_mb > 10:
        raise ValueError(f"File is too large ({file_size_mb:.1f} MB). Please use a smaller file (under 10 MB).")
    
    # Prepare the API request
    url = "https://api.mistral.ai/v1/ocr"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistral-ocr-latest",
        "document": {
            "type": "document_url",
            "document_url": f"data:{content_type};base64,{file_base64}"
        },
        "include_image_base64": False
    }
    
    # Make the API request
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        ocr = response.json()
        # Extract text from all pages and join with double newlines
        extracted_text = "\n\n".join(p["markdown"] for p in ocr.get("pages", []))
        return extracted_text
    else:
        raise ValueError(f"OCR API Error: {response.status_code} - {response.text}")

def analyze_document_content(extracted_text):
    """
    Analyze the document content using OpenAI's Responses API to check for missing or invalid medical codes.
    
    Args:
        extracted_text: The extracted text from the document
        
    Returns:
        dict: Analysis results
        
    Raises:
        ValueError: If API key is missing or API returns an error
        Exception: For other analysis errors
    """
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
    
    system_prompt = """
    You are an expert medical coder helping to validate CHAMPVA claim support documents.
    
    Analyze the provided document text and identify:
    1. The document type (Superbill, EOB, or Pharmacy Receipt)
    2. Whether all required medical codes are present and valid
    3. Any missing or invalid medical codes
    4. If the document is the wrong type
    
    Requirements for each document type:
    - Superbill: Must contain CPT codes, ICD-10 diagnosis codes, and provider information
    - EOB (Explanation of Benefits): Must contain CPT codes, dates of service, and payment information
    - Pharmacy Receipt: Must contain NDC (National Drug Code), medication name, and cost information
    
    Respond with a JSON object in the following format:
    {
        "document_type": "Superbill|EOB|Pharmacy Receipt|Unknown",
        "has_issues": true|false,
        "missing_codes": ["list of missing code types"],
        "invalid_codes": ["list of invalid codes found"],
        "wrong_document_type": true|false,
        "expected_type": "expected document type if wrong",
        "errors": ["detailed error messages"],
        "notes": "any additional notes or observations"
    }
    """
    
    # Try using gpt-4.1 first, fallback to gpt-4.1-mini if it fails
    models_to_try = ["gpt-4.1", "gpt-4.1-mini", "gpt-4"]
    
    for model in models_to_try:
        try:
            # Use the Responses API with the correct parameters
            response = openai_client.responses.create(
                model=model,
                instructions=system_prompt,
                input=extracted_text,
                format="json_object",
                temperature=0.3
            )
            
            # Get the response content and parse as JSON
            try:
                # The response is available via output_text
                result = json.loads(response.output_text)
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, try the next model
                continue
                
        except Exception as model_error:
            # Check if it's a model-related error
            error_str = str(model_error).lower()
            if "model" in error_str or "not found" in error_str:
                # Try the next model
                continue
            else:
                # For other errors, raise the exception
                raise model_error
    
    # If all models fail, raise an exception
    raise ValueError("Failed to analyze document with all available models.")
