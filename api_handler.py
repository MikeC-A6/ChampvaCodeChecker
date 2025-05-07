import os
import requests
import json
import base64
import streamlit as st

# API Keys from environment variables
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def process_document_ocr(file_path):
    """
    Process a document using Mistral's OCR API to extract text.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        str: Extracted text from the document
    """
    if not MISTRAL_API_KEY:
        raise ValueError("Mistral API key not found in environment variables")
    
    try:
        # Read the file as bytes
        with open(file_path, "rb") as file:
            file_bytes = file.read()
        
        # Encode the file as base64
        file_base64 = base64.b64encode(file_bytes).decode('utf-8')
        
        # Prepare the API request
        url = "https://api.mistral.ai/v1/vision/chat/completions"
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistral-large",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all the text from this document, preserving formatting as much as possible."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{file_base64}"
                            }
                        }
                    ]
                }
            ]
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            extracted_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return extracted_text
        else:
            st.error(f"OCR API Error: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        st.error(f"Error during OCR processing: {str(e)}")
        return None

def analyze_document_content(extracted_text):
    """
    Analyze the document content using OpenAI's API to check for missing or invalid medical codes.
    
    Args:
        extracted_text: The extracted text from the document
        
    Returns:
        dict: Analysis results
    """
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
    
    try:
        # Prepare the API request
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
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
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": extracted_text}
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}
            }
            
            # Make the API request
            response = requests.post(url, headers=headers, json=payload)
            
            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                result_json = response_data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                
                try:
                    # Parse the JSON response
                    result = json.loads(result_json)
                    return result
                except json.JSONDecodeError:
                    continue  # Try next model if JSON parsing fails
            
            # If we get a model-related error, try the next model
            if response.status_code == 404 or "model" in response.text.lower():
                continue
            
            # For other errors, raise an exception
            response.raise_for_status()
        
        # If all models fail, return an error result
        return {
            "document_type": "Unknown",
            "has_issues": True,
            "errors": ["Failed to analyze document with all available models."],
            "notes": "The system encountered an error while analyzing this document."
        }
    
    except Exception as e:
        st.error(f"Error during document analysis: {str(e)}")
        return {
            "document_type": "Unknown",
            "has_issues": True,
            "errors": [f"Analysis error: {str(e)}"],
            "notes": "The system encountered an error while analyzing this document."
        }
