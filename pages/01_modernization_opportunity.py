"""
This page provides functionality to analyse IT inventory data and architecture
images to generate AWS modernisation recommendations.
"""


import streamlit as st
import pandas as pd

from utils.bedrock_client import (invoke_bedrock_model_for_image_analysis,
                                  invoke_bedrock_model_with_reasoning)
from utils.image_processor import (convert_image_to_base64, get_image_type,
                                   resize_image)
from utils.prompts_lib import (get_invventory_analysis_prompt,
                               get_modernization_pathways_prompt,
                               get_onprem_architecture_prompt)


INVENTORY_ANALYSIS = ""
if "inventory_analysis" not in st.session_state:
    st.session_state["inventory_analysis"] = "inventory_analysis"
if "modz_analysis" not in st.session_state:
    st.session_state["modz_analysis"] = "modz_analysis"
if "onprem_architecture" not in st.session_state:
    st.session_state["onprem_architecture"] = "onprem_architecture"


def page_details():
    """Display page title and description."""
    st.title("Identify modernisation opportunity using on-premises discovery data")
    st.markdown("""
    You can identify AWS modernisation opportunities based on your IT inventory.
    Upload your IT inventory as a CSV file, define the scope of modernisation,
    and optionally provide an on-premises architecture image.
    """)


def analyze_onprem_architecture(image_bytes):
    """
    Analyse on-premises architecture image.
    
    Args:
        image_bytes: Binary image data
        
    Returns:
        Analysis result or None if error occurs
    """
    try:
        # Resize image if necessary
        image_bytes = resize_image(image_bytes)
        base64_image = convert_image_to_base64(image_bytes)

        prompt_template = get_onprem_architecture_prompt(base64_image)

        # Truncate the base64 image if the prompt exceeds the token limit
        max_prompt_length = 100000  # Adjust based on the actual token limit
        truncated_base64_image = base64_image[:max_prompt_length -
                                              len(prompt_template) - 100]

        prompt = prompt_template.format(truncated_base64_image)

        return invoke_bedrock_model_with_reasoning(prompt)
    except (ValueError, ConnectionError) as error:
        st.error(f"Error analysing target architecture: {str(error)}")
        return None


def generate_inventory_analysis(inventory_data_df):
    """
    Generate inventory analysis from DataFrame.
    
    Args:
        inventory_data_df: Pandas DataFrame containing inventory data
        
    Returns:
        Analysis response or None if error occurs
    """
    try:
        prompt = get_invventory_analysis_prompt(inventory_data_df)
        analysis_result = invoke_bedrock_model_with_reasoning(prompt)
        print("*" * 80)
        print(analysis_result["reasoning"])
        return analysis_result["response"]
    except (ValueError, KeyError) as error:
        st.error(f"Error generating inventory analysis: {str(error)}")
        st.text(INVENTORY_ANALYSIS)
        return None


def generate_architecture_analysis(architecture_file):
    """
    Generate architecture analysis from uploaded file.
    
    Args:
        architecture_file: Uploaded architecture image file
        
    Returns:
        Architecture description or None if error occurs
    """
    try:
        onprem_image = architecture_file.getvalue()
        encoded_image = convert_image_to_base64(onprem_image)
        image_type = get_image_type(architecture_file.name)
        prompt = get_onprem_architecture_prompt()
        arch_description = invoke_bedrock_model_for_image_analysis(
            encoded_image, prompt, image_type)
        return arch_description
    except (ValueError, AttributeError) as error:
        st.error(f"Error generating architecture analysis: {str(error)}")
        st.text(INVENTORY_ANALYSIS)
        return None


def recommend_modernisation_pathways(inventory_data_df, modernisation_scope,
                                   architecture_description=None):
    """
    Recommend modernisation pathways based on inventory and scope.
    
    Args:
        inventory_data_df: Pandas DataFrame containing inventory data
        modernisation_scope: Text describing modernisation scope
        architecture_description: Optional architecture description
        
    Returns:
        Modernisation recommendations or None if error occurs
    """
    try:
        prompt = get_modernization_pathways_prompt(
            inventory_data_df, architecture_description, modernisation_scope)
        modernization_pathways = invoke_bedrock_model_with_reasoning(prompt)
        print("*" * 80)
        print(modernization_pathways["reasoning"])
        return modernization_pathways["response"]
    except (ValueError, KeyError) as error:
        st.error(f"Error parsing modernisation recommendations: {str(error)}")
        return None


if __name__ == "__main__":
    page_details()

    # File uploads
    col1, col2 = st.columns(2)
    with col1:
        inventory_file = st.file_uploader(
            "📤 Upload IT Inventory (CSV)", type=['csv'])
    with col2:
        target_arch_file = st.file_uploader(
            "📤 Upload On-premises architecture (optional)",
            type=['jpg', 'jpeg', 'png'])
    # Scope text area
    scope_text = st.text_area("Provide scope details",
                              placeholder="Migration and Modernisation",
                              height=150)
    st.divider()

    if st.button("Analyse Inventory", type="primary"):
        if inventory_file is None:
            st.error("Please upload an IT inventory CSV file.")
        elif not scope_text:
            st.error("Please provide modernisation scope.")
        else:
            ARCH_DESCRIPTION = None
            with st.expander("Inventory Data"):
                inventory_df = pd.read_csv(inventory_file)
                st.subheader("IT Inventory")
                st.dataframe(inventory_df)

            if target_arch_file:
                with st.expander("On-prem Architecture"):
                    st.subheader("Architecture")
                    st.image(target_arch_file)

            with st.spinner("Analysing inventory data..."):
                # Read inventory file
                inventory_analysis = generate_inventory_analysis(inventory_df)
                st.session_state["inventory_analysis"] = inventory_analysis

            # Process target architecture if provided
            if target_arch_file:
                with st.spinner("Inventory analysis completed. "
                               "Now analysing target architecture..."):
                    ARCH_DESCRIPTION = generate_architecture_analysis(
                        target_arch_file)
                    if ARCH_DESCRIPTION:
                        st.session_state["onprem_architecture"] = \
                            ARCH_DESCRIPTION

    if st.session_state["inventory_analysis"] != "inventory_analysis":
        st.subheader("Inventory Analysis")
        with st.expander("Inventory analysis"):
            st.write(st.session_state["inventory_analysis"])
            st.download_button(
                label="Download output",
                data=st.session_state["inventory_analysis"],
                file_name="inventory_analysis.md",
                mime="text/markdown")

    if st.session_state["onprem_architecture"] != "onprem_architecture":
        st.subheader("Architecture Analysis")
        with st.expander("Architecture analysis"):
            st.write(st.session_state["onprem_architecture"])
            st.download_button(
                label="Download output",
                data=st.session_state["onprem_architecture"],
                file_name="onprem_architecture.md",
                mime="text/markdown")

    MODZ_RECOMMENDATIONS = ""
    if st.button("Provide modernisation recommendations", type="primary"):
        if inventory_file is None:
            st.error("Please upload an IT inventory CSV file.")
        elif not scope_text:
            st.error("Please provide modernisation scope.")
        else:
            with st.spinner("Generating modernisation recommendations..."):
                inventory_df = pd.read_csv(inventory_file)
                ARCH_DESCRIPTION = st.session_state["onprem_architecture"]
                MODZ_RECOMMENDATIONS = recommend_modernisation_pathways(
                    inventory_df, scope_text, ARCH_DESCRIPTION)
                st.session_state["modz_analysis"] = MODZ_RECOMMENDATIONS

    if st.session_state["modz_analysis"] != "modz_analysis":
        st.subheader("Modernisation Strategy")
        with st.expander("Modernisation Strategy"):
            st.write(st.session_state["modz_analysis"])
            st.download_button(
                label="Download output",
                data=st.session_state["modz_analysis"],
                file_name="aws_modernisation_strategy.md",
                mime="text/markdown"
            )
