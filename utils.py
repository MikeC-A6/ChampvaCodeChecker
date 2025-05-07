import streamlit as st

def validate_file_type(file):
    """
    Validate if the uploaded file is of an accepted type.
    
    Args:
        file: The uploaded file object
        
    Returns:
        bool: True if file type is valid, False otherwise
    """
    valid_types = [
        'application/pdf',
        'image/jpeg', 
        'image/jpg',
        'image/png'
    ]
    
    # Check for PDF extension if mimetype detection fails
    if file.type not in valid_types:
        if file.name.lower().endswith('.pdf'):
            return True
        return False
    return True

def determine_document_type(analysis_result):
    """
    Determine the document type based on the analysis result.
    
    Args:
        analysis_result: The analysis result from the AI
        
    Returns:
        str: The document type (Superbill, EOB, Pharmacy Receipt, or Unknown)
    """
    if not analysis_result:
        return "Unknown"
    
    doc_type = analysis_result.get("document_type", "Unknown")
    return doc_type

def format_results(result):
    """
    Format the analysis results for display.
    
    Args:
        result: The analysis result dictionary
        
    Returns:
        str: Formatted results in markdown format
    """
    formatted_text = ""
    
    # Document type
    doc_type = result.get("document_type", "Unknown")
    formatted_text += f"**Document Type**: {doc_type}\n\n"
    
    # Document validity
    analysis = result.get("analysis", {})
    has_issues = analysis.get("has_issues", True)
    
    if not has_issues:
        formatted_text += "✅ **Status**: This document appears to be valid with proper medical codes.\n\n"
    else:
        formatted_text += "❌ **Status**: Issues found in this document.\n\n"
    
    # Missing codes
    missing_codes = analysis.get("missing_codes", [])
    if missing_codes:
        formatted_text += "**Missing Codes**:\n"
        for code in missing_codes:
            formatted_text += f"- {code}\n"
        formatted_text += "\n"
    
    # Invalid codes
    invalid_codes = analysis.get("invalid_codes", [])
    if invalid_codes:
        formatted_text += "**Invalid Codes**:\n"
        for code in invalid_codes:
            formatted_text += f"- {code}\n"
        formatted_text += "\n"
    
    # Wrong document type
    wrong_doc_type = analysis.get("wrong_document_type", False)
    if wrong_doc_type:
        expected_type = analysis.get("expected_type", "Unknown")
        formatted_text += f"**Wrong Document Type**: This does not appear to be a {expected_type} document.\n\n"
    
    # Additional notes
    notes = analysis.get("notes", "")
    if notes:
        formatted_text += f"**Notes**: {notes}\n\n"
    
    return formatted_text
