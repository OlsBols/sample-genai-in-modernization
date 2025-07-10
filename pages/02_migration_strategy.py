"""
Migration Strategy Module

This page provides functionality to develop AWS migration patterns and planning
from AWS Calculator CSV exports.
"""

import io

import pandas as pd
import streamlit as st

# pylint: disable=import-error
from utils.bedrock_client import invoke_bedrock_model_without_reasoning
from utils.prompts_lib import get_migration_patterns_prompt

if "strategy_text" not in st.session_state:
    st.session_state["strategy_text"] = "strategy_text"


def parse_aws_calculator_data(csv_data):
    """
    Parse AWS Calculator CSV data and return a pandas DataFrame.
    
    Args:
        csv_data (str): Raw CSV data as string
        
    Returns:
        pd.DataFrame or None: Parsed dataframe or None if parsing fails
    """
    try:
        # Skip initial rows to find the actual table headers
        lines = csv_data.splitlines()
        start_idx = 0
        for i, line in enumerate(lines):
            if "Group hierarchy,Region,Description" in line:
                start_idx = i
                break
        # Read CSV from the header row
        dataframe = pd.read_csv(io.StringIO('\n'.join(lines[start_idx:])),
                               encoding='utf-8')
        return dataframe
    except (pd.errors.EmptyDataError, pd.errors.ParserError, ValueError) as error:
        st.error(f"Error parsing CSV data: {error}")
        return None


def page_details():
    """Display the page title and description."""
    # Define the app title and description
    st.title("Develop migration patterns and planning from AWS Calculator")
    st.markdown("Upload your AWS Calculator CSV export to generate an "
                "optimised migration strategy.")


def develop_migration_strategy(calculator_csv_data, migration_scope_text):
    """
    Develop migration strategy based on CSV data and scope text.
    
    Args:
        calculator_csv_data (pd.DataFrame): Parsed AWS calculator data
        migration_scope_text (str): Migration scope details
    """
    prompt = get_migration_patterns_prompt(calculator_csv_data, migration_scope_text)
    strategy_text = invoke_bedrock_model_without_reasoning(prompt)
    if strategy_text:
        st.session_state["strategy_text"] = strategy_text
        with st.expander("Migration Strategy"):
            st.markdown(st.session_state["strategy_text"])
        st.download_button(
            label="Download Strategy",
            data=st.session_state["strategy_text"],
            file_name="aws_migration_strategy.md",
            mime="text/markdown")
        st.session_state["strategy_text"] = strategy_text


if __name__ == "__main__":
    page_details()
    # File uploader for AWS Calculator CSV
    uploaded_file = st.file_uploader("Upload AWS Calculator CSV", type=["csv"])
    # Optional scope text area
    scope_text = st.text_area("Optional: Enter migration scope details", height=150)
    # Process the file when uploaded
    if uploaded_file is not None:
        try:
            calc_csv_data = parse_aws_calculator_data(
                uploaded_file.read().decode("utf-8"))
            st.subheader("AWS Calculator Data")
            with st.expander("AWS Calculator Data"):
                st.dataframe(calc_csv_data)
        except (UnicodeDecodeError, AttributeError) as error:
            st.error(f"Error processing the CSV file: {str(error)}")
            st.info("Please ensure your CSV file follows the expected "
                    "AWS Calculator export format.")
    if st.button("Generate Migration Strategy", type="primary"):
        with st.spinner('Generating your migration strategy... '
                        'This may take a few minutes'):
            develop_migration_strategy(calc_csv_data, scope_text)
