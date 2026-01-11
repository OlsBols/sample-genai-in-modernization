"""Business case review module for AWS migration financial analysis."""

import streamlit as st

from prompt_library.business_case_validation.business_case_validation_prompt import (
    get_business_case_validation_prompt,
)
from utils.bedrock_client import invoke_bedrock_model_without_reasoning
from utils.config import load_css
from utils.file_handler import process_pdf_bytes, validate_file_size
from utils.pdf_processor import convert_pdf_to_images, prepare_content_for_claude


def analyse_pdf_document(uploaded_file):
    """
    Analyze PDF document for business case validation.
    
    Args:
        uploaded_file: Uploaded PDF file object
        
    Returns:
        Analysis result string or error message
    """
    if not uploaded_file:
        return "Please upload a PDF file."

    # Validate file size
    is_valid, error_msg = validate_file_size(uploaded_file)
    if not is_valid:
        return f"File validation error: {error_msg}"

    try:
        # Process PDF
        max_pages = 10
        pdf_document = process_pdf_bytes(uploaded_file)
        page_images = convert_pdf_to_images(pdf_document, max_pages)
        pdf_document.close()

        prompt = get_business_case_validation_prompt()
        # # Prepare content for Claude
        pdf_content_wtih_prompt = prepare_content_for_claude(page_images, prompt)

        # Get analysis from Claude
        response_text = invoke_bedrock_model_without_reasoning(pdf_content_wtih_prompt)
        return response_text

    except ValueError as ve:
        return f"Error processing PDF: {str(ve)}"
    except (ConnectionError, TimeoutError) as ce:
        return f"Network error processing PDF: {str(ce)}"
    except Exception as e:
        return f"Unexpected error processing PDF: {str(e)}"


# Load external CSS
load_css()


def page_details():
    """Display page header and description for business case review."""
    # Enhanced page header using CSS classes
    st.markdown(
        """
    <div class="page-header">
        <h1>AWS Business Case Review</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Description section using CSS classes with clean format
    st.markdown(
        """
    <div class="info-card">
        <p>
            The AWS TCO Analysis review provides a structured approach for evaluating 
            the financial implications and business value of AWS migration. This 
            comprehensive methodology reviews seven critical elements necessary for 
            accurate cost modelling and financial planning when transitioning to AWS services.
        </p>
        <p>
            The review encompasses initial inputs for estimation, detailed cost modelling, 
            business value assessment, optimisation strategies, comparative TCO analysis, 
            ongoing cost management, and holistic cloud value evaluation—ensuring 
            organisations can make informed decisions based on both financial and 
            strategic considerations.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Key elements section with markdown formatting preserved

    st.markdown("""
    **Key elements:**

    * **Input Collection**: Comprehensive gathering of compute, storage, network 
      requirements, existing infrastructure assessment, growth projections, and 
      strategic business objectives.
    * **Cost Modelling**: Multi-year projections with various usage scenarios, 
      pricing options (Reserved Instances, Savings Plans), and ROI calculations 
      showing both short and long-term benefits.
    * **Business Value**: Quantification of tangible and intangible benefits 
      including scalability improvements, reliability enhancements, and alignment 
      with key business objectives.
    * **Optimisation Strategies**: Right-sizing resources based on workload 
      requirements, leveraging cost-saving options, and eliminating inefficient 
      resource utilisation.
    * **Comparative Analysis**: Detailed comparison between on-premises and AWS costs, 
      accounting for infrastructure refresh cycles, operational efficiencies, and 
      migration planning.
    * **Cost Management**: Ongoing governance using AWS tools (Cost Explorer, 
      Trusted Advisor), licence optimisation, automation opportunities, and clear 
      accountability frameworks.
    * **Cloud Value Framework**: Holistic assessment covering cost savings, staff 
      productivity improvements, operational resilience, and business agility benefits.
    """)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
    <h2 class="text-secondary">Upload business case in PDF format</h2>
    """,
        unsafe_allow_html=True,
    )


def review_business_case(uploaded_file):
    """
    Review business case from uploaded PDF file.
    
    Args:
        uploaded_file: Uploaded PDF file object
    """
    response_text = analyse_pdf_document(uploaded_file)
    if response_text:
        # Enhanced results section using CSS classes
        st.markdown(
            """
        <div class="results-section">
            <h3>Business Case Review Results</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        with st.expander("Business Case Analysis", expanded=True):
            st.markdown("**Comprehensive Business Case Evaluation**")
            st.write(response_text)
            st.download_button(
                label="Download Business Case Review",
                data=response_text,
                file_name="aws_business_case_review.md",
                mime="text/markdown",
            )


if __name__ == "__main__":
    page_details()
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if st.button("Review Busienss Case", type="primary"):
        if uploaded_file:
            with st.spinner(
                "The business case is being reviewed. Please wait for the analysis "
                "to complete. This may take a few minutes."
            ):
                review_business_case(uploaded_file)
