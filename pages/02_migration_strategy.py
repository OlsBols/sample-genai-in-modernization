"""Migration strategy development module for AWS Calculator data analysis."""

import io

import pandas as pd
import streamlit as st

from prompt_library.migration_patterns.migration_patterns_prompt import (
    get_migration_patterns_prompt,
)
from utils.bedrock_client import invoke_bedrock_model_without_reasoning
from utils.config import load_css
from utils.file_handler import validate_file_size


if "strategy_text" not in st.session_state:
    st.session_state["strategy_text"] = "strategy_text"

# Load external CSS
load_css()


def parse_aws_calculator_data(csv_data):
    """
    Parse AWS Calculator CSV data to extract relevant information.
    
    Args:
        csv_data: Raw CSV data as string
        
    Returns:
        Pandas DataFrame with parsed data or None if parsing fails
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
        df = pd.read_csv(io.StringIO("\n".join(lines[start_idx:])), encoding="utf-8")
        return df
    except ValueError as ve:
        st.error(f"Error parsing CSV data: {ve}")
        return None
    except (UnicodeDecodeError, pd.errors.EmptyDataError) as de:
        st.error(f"Data format error parsing CSV: {de}")
        return None
    except Exception as e:
        st.error(f"Unexpected error parsing CSV data: {e}")
        return None


def page_details():
    """Display page header and description for migration strategy development."""
    # Enhanced page header using CSS classes
    st.markdown(
        """
    <div class="page-header">
        <h1>Develop Migration Patterns and Planning</h1>
        <p>From AWS Calculator Data</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Description section using CSS classes
    st.markdown(
        """
    <div class="info-card">
        <p>
            Upload your AWS Calculator CSV export to generate an optimised migration 
            strategy with comprehensive planning and cost analysis.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def develop_migration_strategy(calc_csv_data, scope_text):
    """
    Develop migration strategy based on AWS Calculator data and scope.
    
    Args:
        calc_csv_data: Parsed AWS Calculator DataFrame
        scope_text: Migration scope description text
    """
    prompt = get_migration_patterns_prompt(calc_csv_data, scope_text)
    strategy_text = invoke_bedrock_model_without_reasoning(prompt)

    if strategy_text:
        st.session_state["strategy_text"] = strategy_text
        # st.markdown(st.session_state["strategy_text"])
        # print("*"*80)
        # print(strategy_text["reasoning"])
        # Enhanced results section using CSS classes
        st.markdown(
            """
        <div class="results-section">
            <h3>Migration Strategy Results</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        with st.expander("Migration Strategy", expanded=True):
            st.markdown("**AWS Migration Strategy & Planning**")
            st.markdown(st.session_state["strategy_text"])
            st.download_button(
                label="Download Migration Strategy",
                data=st.session_state["strategy_text"],
                file_name="aws_migration_strategy_with_plan.md",
                mime="text/markdown",
            )


if __name__ == "__main__":
    page_details()
    # File uploader for AWS Calculator CSV
    uploaded_file = st.file_uploader("Upload AWS Calculator CSV", type=["csv"])
    #   Optional scope text area
    scope_text = st.text_area("Optional: Enter migration scope details", height=150)
    # Process the file when uploaded
    if uploaded_file is not None:
        try:
            calc_csv_data = parse_aws_calculator_data(
                uploaded_file.read().decode("utf-8")
            )
            st.subheader("AWS Calculator Data")
            with st.expander("AWS Calculator Data"):
                st.dataframe(calc_csv_data)
        except ValueError as ve:
            st.error(f"Error processing the CSV file: {str(ve)}")
            st.info(
                "Please ensure your CSV file follows the expected AWS Calculator "
                "export format."
            )
        except (UnicodeDecodeError, pd.errors.EmptyDataError) as de:
            st.error(f"Data format error processing the CSV file: {str(de)}")
            st.info(
                "Please ensure your CSV file follows the expected AWS Calculator "
                "export format."
            )
        except Exception as e:
            st.error(f"Unexpected error processing the CSV file: {str(e)}")
            st.info(
                "Please ensure your CSV file follows the expected AWS Calculator "
                "export format."
            )
    if st.button("Generate Migration Strategy", type="primary"):
        if not uploaded_file:
            st.error("Please upload an AWS Calculator CSV file.")
        else:
            # Validate file size
            is_valid, error_msg = validate_file_size(uploaded_file)
            if not is_valid:
                st.error(f"File validation error: {error_msg}")
            else:
                with st.spinner(
                    "Generating your migration strategy... "
                    "This may take a few minutes"
                ):
                    develop_migration_strategy(calc_csv_data, scope_text)
