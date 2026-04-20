"""Modernization opportunity identification module for AWS migration analysis."""

import pandas as pd
import streamlit as st

from prompt_library.modernization_opportunity.inventory_analysis_prompt import (
    get_invventory_analysis_prompt,
)
from prompt_library.modernization_opportunity.onprem_architecture_prompt import (
    get_onprem_architecture_prompt,
)
from prompt_library.modernization_opportunity.modernization_pathways_prompt import (
    get_modernization_pathways_prompt,
)
from utils.bedrock_client import (
    invoke_bedrock_model_with_reasoning,
    invoke_bedrock_model_for_image_analysis,
    invoke_bedrock_model_claude_3_5,
)
from utils.config import load_css
from utils.file_handler import validate_file_size
from utils.image_processor import resize_image, convert_image_to_base64, get_image_type


inventory_analysis = ""
if "inventory_analysis" not in st.session_state:
    st.session_state["inventory_analysis"] = "inventory_analysis"
if "modz_analysis" not in st.session_state:
    st.session_state["modz_analysis"] = "modz_analysis"
if "onprem_architecture" not in st.session_state:
    st.session_state["onprem_architecture"] = "onprem_architecture"

# Load external CSS
load_css()


def validate_file_uploads(inventory_file, target_arch_file):
    """
    Validate uploaded files using standardized validation.
    
    Args:
        inventory_file: Uploaded inventory CSV file
        target_arch_file: Uploaded architecture image file (optional)
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not inventory_file:
        return False, "Please upload an IT inventory CSV file"

    # Validate inventory file size
    is_valid, error_msg = validate_file_size(inventory_file)
    if not is_valid:
        return False, f"Inventory file error: {error_msg}"

    # Validate architecture file if provided
    if target_arch_file:
        is_valid, error_msg = validate_file_size(target_arch_file)
        if not is_valid:
            return False, f"Architecture file error: {error_msg}"

    return True, "Files are valid"


# Title and description
def page_details():
    """Display page header and description for modernization opportunity identification."""
    # Enhanced page header using CSS classes
    st.markdown(
        """
    <div class="page-header">
        <h1>Identify Modernisation Opportunity</h1>
        <p>Using On-Premises Discovery Data</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Description section using CSS classes
    st.markdown(
        """
    <div class="info-card">
        <p>
            You can identify AWS modernisation opportunities based on your IT inventory. 
            Upload your IT inventory as a CSV file, define the scope of modernisation, 
            and optionally provide an on-premises architecture image for comprehensive analysis.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


# Function to analyze target architecture image
def analyze_onprem_architecture(image_bytes):
    """
    Analyze on-premises architecture from image bytes.
    
    Args:
        image_bytes: Image data as bytes
        
    Returns:
        Analysis result string or None if error occurs
    """
    try:
        # Resize image if necessary
        image_bytes = resize_image(image_bytes)
        base64_image = convert_image_to_base64(image_bytes)

        prompt_template = get_onprem_architecture_prompt(base64_image)

        # Truncate the base64 image if the prompt exceeds the token limit
        max_prompt_length = 100000  # Adjust based on the actual token limit
        truncated_base64_image = base64_image[
            : max_prompt_length - len(prompt_template) - 100
        ]  # Leave some buffer for the template

        prompt = prompt_template.format(truncated_base64_image)

        return invoke_bedrock_model_3_5(prompt, max_tokens=10000, temperature=0.5)
    except ValueError as ve:
        st.error(f"Error analyzing target architecture: {str(ve)}")
        return None
    except (ConnectionError, TimeoutError) as ce:
        st.error(f"Network error analyzing target architecture: {str(ce)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error analyzing target architecture: {str(e)}")
        return None


# Function to recommend modernisation pathways
def generate_inventory_analysis(inventory_df):
    """
    Generate inventory analysis from DataFrame.
    
    Args:
        inventory_df: Pandas DataFrame containing inventory data
        
    Returns:
        Analysis response string or None if error occurs
    """
    try:
        prompt = get_invventory_analysis_prompt(inventory_df)
        inventory_analysis = invoke_bedrock_model_with_reasoning(prompt)
        print("*" * 80)
        print(inventory_analysis["reasoning"])
        return inventory_analysis["response"]
    except ValueError as ve:
        st.error(f"Error generating inventory analysis: {str(ve)}")
        return None
    except (ConnectionError, TimeoutError) as ce:
        st.error(f"Network error generating inventory analysis: {str(ce)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error generating inventory analysis: {str(e)}")
        return None


def generate_architecture_analysis(target_arch_file):
    """
    Generate architecture analysis from uploaded file.
    
    Args:
        target_arch_file: Uploaded architecture image file
        
    Returns:
        Architecture description string or None if error occurs
    """
    try:
        onprem_image = target_arch_file.getvalue()
        encoded_image = convert_image_to_base64(onprem_image)
        image_type = get_image_type(target_arch_file.name)
        prompt = get_onprem_architecture_prompt()
        arch_description = invoke_bedrock_model_for_image_analysis(
            encoded_image, prompt, image_type
        )
        return arch_description
    except ValueError as ve:
        st.error(f"Error generating architecture analysis: {str(ve)}")
        return None
    except (ConnectionError, TimeoutError) as ce:
        st.error(f"Network error generating architecture analysis: {str(ce)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error generating architecture analysis: {str(e)}")
        return None


# Function to recommend modernisation pathways
def recommend_modernisation_pathways(
    inventory_df, scope_text, architecture_description=None
):
    """
    Recommend modernization pathways based on inventory and architecture.
    
    Args:
        inventory_df: Pandas DataFrame containing inventory data
        scope_text: Scope description text
        architecture_description: Optional architecture description
        
    Returns:
        Modernization pathways response string or None if error occurs
    """
    try:
        prompt = get_modernization_pathways_prompt(
            inventory_df, architecture_description, scope_text
        )
        modernization_pathways = invoke_bedrock_model_with_reasoning(prompt)
        print("*" * 80)
        print(modernization_pathways["reasoning"])
        return modernization_pathways["response"]
    except ValueError as ve:
        st.error(f"Error parsing modernisation recommendations: {str(ve)}")
        return None
    except (ConnectionError, TimeoutError) as ce:
        st.error(f"Network error parsing modernisation recommendations: {str(ce)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error parsing modernisation recommendations: {str(e)}")
        return None


if __name__ == "__main__":
    page_details()

    # File uploads
    col1, col2 = st.columns(2)
    with col1:
        inventory_file = st.file_uploader("Upload IT Inventory (CSV)", type=["csv"])
    with col2:
        target_arch_file = st.file_uploader(
            "Upload On premises architecture (optional)", type=["jpg", "jpeg", "png"]
        )
    # Scope text area
    scope_text = st.text_area(
        "Provide scope details", placeholder="Migration and Modernization", height=150
    )
    st.divider()
    if st.button("Analyze Inventory", type="primary"):
        if inventory_file is None:
            st.error("Please upload an IT inventory CSV file.")
        elif not scope_text:
            st.error("Please provide modernisation scope.")
        else:
            arch_description = None
            # Enhanced expander for inventory data using CSS classes
            st.markdown(
                """
            <div class="results-section">
                <h3>Data Preview</h3>
            </div>
            """,
                unsafe_allow_html=True,
            )

            with st.expander("Inventory Data", expanded=True):
                inventory_df = pd.read_csv(inventory_file)
                st.markdown(
                    f"**IT Inventory Overview** - {len(inventory_df)} records found"
                )
                st.dataframe(inventory_df)

            if target_arch_file:
                with st.expander("On-prem Architecture", expanded=True):
                    st.markdown("**Architecture Diagram**")
                    st.image(target_arch_file, width="stretch")
            with st.spinner("Analyzing inventory data..."):
                # Read inventory file
                inventory_analysis = generate_inventory_analysis(inventory_df)
                st.session_state["inventory_analysis"] = inventory_analysis
            # Process target architecture if provided
            if target_arch_file:
                with st.spinner(
                    "Inventory analysis competed. Now analyzing target architecture..."
                ):
                    arch_description = generate_architecture_analysis(target_arch_file)
                    if arch_description:
                        st.session_state["onprem_architecture"] = arch_description

    if st.session_state["inventory_analysis"] != "inventory_analysis":
        st.markdown(
            """
        <div class="results-section">
            <h3>Analysis Results</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        with st.expander("Inventory Analysis", expanded=True):
            st.markdown("**Comprehensive IT Infrastructure Analysis**")
            st.write(st.session_state["inventory_analysis"])
            st.download_button(
                label="Download Analysis Report",
                data=st.session_state["inventory_analysis"],
                file_name="inventory_analysis.md",
                mime="text/markdown",
            )

    if st.session_state["onprem_architecture"] != "onprem_architecture":
        with st.expander("Architecture Analysis", expanded=True):
            st.markdown("**On-Premises Architecture Assessment**")
            st.write(st.session_state["onprem_architecture"])
            st.download_button(
                label="Download Architecture Report",
                data=st.session_state["onprem_architecture"],
                file_name="onprem_architecture.md",
                mime="text/markdown",
            )

    modz_recommendations = ""
    if st.button("Provide modernisation recommendations", type="primary"):
        if inventory_file is None:
            st.error("Please upload an IT inventory CSV file.")
        elif not scope_text:
            st.error("Please provide modernisation scope.")
        else:
            with st.spinner("Generating modernisation recommendations..."):
                inventory_df = pd.read_csv(inventory_file)
                arch_description = st.session_state["onprem_architecture"]
                modz_recommendations = recommend_modernisation_pathways(
                    inventory_df, scope_text, arch_description
                )
                st.session_state["modz_analysis"] = modz_recommendations

    if st.session_state["modz_analysis"] != "modz_analysis":
        st.markdown(
            """
        <div class="results-section">
            <h3>Modernisation Recommendations</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        with st.expander("Modernisation Strategy", expanded=True):
            st.markdown("**AWS Modernisation Pathway Recommendations**")
            st.write(st.session_state["modz_analysis"])
            st.download_button(
                label="Download Modernisation Strategy",
                data=st.session_state["modz_analysis"],
                file_name="aws_modernisation_approach.md",
                mime="text/markdown",
            )
