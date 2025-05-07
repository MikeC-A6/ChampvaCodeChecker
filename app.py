import streamlit as st
import os
import base64
import tempfile
from utils import validate_file_type, determine_document_type, format_results
from api_handler import process_document_ocr, analyze_document_content

st.set_page_config(
    page_title="CHAMPVA Document Validator",
    page_icon="📄",
    layout="wide"
)

def main():
    st.title("CHAMPVA Claim Document Validator")
    
    st.markdown("""
    This application checks CHAMPVA claim-support documents for missing or invalid medical codes.
    
    **Upload up to three document types:**
    - Superbill
    - Explanation of Benefits (EOB)
    - Pharmacy receipts
    
    Supported file formats: PDF, JPG, PNG
    """)
    
    # Session state initialization
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
        
    # Document upload section
    st.header("Document Upload")
    
    uploaded_files = st.file_uploader(
        "Upload your CHAMPVA claim-support documents (max 3 files)",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="document_uploader"
    )
    
    # Check if files have been uploaded
    if uploaded_files:
        if len(uploaded_files) > 3:
            st.warning("Please upload a maximum of 3 files.")
            uploaded_files = uploaded_files[:3]
        
        st.session_state.uploaded_files = uploaded_files
        
        # Display uploaded files
        st.subheader("Uploaded Documents")
        for i, file in enumerate(uploaded_files):
            file_type = file.type
            file_size = file.size / 1024  # Size in KB
            st.text(f"{i+1}. {file.name} ({file_type}, {file_size:.1f} KB)")
        
        # Process button
        process_button = st.button("Process Documents", type="primary", disabled=st.session_state.processing)
        
        if process_button:
            # Clear previous results
            st.session_state.results = []
            st.session_state.processing = True
            
            with st.spinner("Processing your documents... This may take a moment."):
                # Process each document
                for file in uploaded_files:
                    try:
                        # Validate file
                        if not validate_file_type(file):
                            st.error(f"Invalid file type for {file.name}. Only PDF and image formats are supported.")
                            continue
                        
                        # Create a temporary file to save the uploaded file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as temp_file:
                            temp_file.write(file.getvalue())
                            temp_file_path = temp_file.name
                        
                        # Extract text with OCR
                        with st.status(f"Processing {file.name}..."):
                            st.write("Extracting text with OCR...")
                            extracted_text = process_document_ocr(temp_file_path)
                            
                            if not extracted_text:
                                st.error(f"Failed to extract text from {file.name}")
                                continue
                            
                            st.write("Analyzing document content...")
                            # Analyze the document with OpenAI
                            analysis_result = analyze_document_content(extracted_text)
                            
                            # Determine document type
                            doc_type = determine_document_type(analysis_result)
                            
                            # Add to results with filename
                            result = {
                                "filename": file.name,
                                "document_type": doc_type,
                                "analysis": analysis_result
                            }
                            st.session_state.results.append(result)
                            st.write(f"Completed processing {file.name}")
                        
                        # Clean up temporary file
                        os.unlink(temp_file_path)
                    
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")
            
            st.session_state.processing = False
            st.success("Document processing complete!")
            st.rerun()
    
    # Display results if available
    if st.session_state.results:
        display_results()

def display_results():
    st.header("Analysis Results")
    
    # Display summary of findings
    has_issues = any(
        result["analysis"].get("has_issues", True)
        for result in st.session_state.results
    )
    
    if has_issues:
        st.warning("⚠️ Issues were found in your documents. See details below.")
    else:
        st.success("✅ All documents appear to be valid with proper medical codes.")
    
    # Display detailed results for each document
    for i, result in enumerate(st.session_state.results):
        with st.expander(f"Document {i+1}: {result['filename']} ({result['document_type']})", expanded=True):
            formatted_results = format_results(result)
            st.markdown(formatted_results)
            
            # If there are specific errors, list them
            if "errors" in result["analysis"] and result["analysis"]["errors"]:
                st.subheader("Detailed Issues")
                for error in result["analysis"]["errors"]:
                    st.error(error)

if __name__ == "__main__":
    main()
