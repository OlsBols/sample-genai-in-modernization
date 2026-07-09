"""Resource planning module for AWS migration team structure and allocation."""

import re

import streamlit as st

from prompt_library.resource_planning.resource_planning_prompt import (
    get_resource_planning_prompt,
)
from utils.bedrock_client import invoke_bedrock_model_with_reasoning
from utils.config import load_css
from utils.file_handler import read_csv_file, validate_file_size


def page_details():
    """Display page header and description for resource planning."""
    # Enhanced page header using CSS classes
    st.markdown(
        """
    <div class="page-header">
        <h1>Develop Resource Planning</h1>
        <p>Team Structure & Resource Allocation</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Description section using CSS classes
    st.markdown(
        """
    <div class="info-card">
        <p>
            Develop resource planning based on three key inputs: (1) migration strategy, 
            (2) wave planning data, and (3) resource details.
        </p>
        <p>
            It creates detailed team structures and resource allocation plans, providing 
            five key outputs: an executive summary, team structure evaluation, resource 
            summary, wave-based planning, and role-based resource allocation. The focus 
            is on two team structure models (Hub-and-Spoke and Wave-Based), with 
            justification for the recommended approach.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

def develop_resource_planning(migration_strategy):
    """
    Develop resource planning based on migration strategy and resource data.
    
    Args:
        migration_strategy: Migration strategy document content as string
    """
    pattern = r"\|(.*?)\|[\r\n]"
    wave_planning_data = re.findall(pattern, migration_strategy)
    if not wave_planning_data:
        wave_planning_data = ""

    resource_details = read_csv_file("resource_profile")
    if resource_details is None or resource_details.empty:
        st.error(
            "Resource profile data is empty. Please check the resource_profile_template.csv file and add resource data."
        )
        return
    with st.expander("Resource Profile", expanded=True):
        st.markdown("**Available Resource Profile Data**")
        st.dataframe(resource_details)
    resource_prompt = get_resource_planning_prompt(
        migration_strategy, wave_planning_data, resource_details
    )
    resource_planning_data = invoke_bedrock_model_with_reasoning(resource_prompt)
    if resource_planning_data:
        # Enhanced results section using CSS classes
        st.markdown(
            """
        <div class="results-section">
            <h3>Resource Planning Results</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.session_state["resource_planning_data"] = resource_planning_data["response"]
        with st.expander("Resource Planning Strategy", expanded=True):
            st.markdown("**Team Structure & Resource Allocation Plan**")
            st.markdown(st.session_state["resource_planning_data"])
            print("*" * 80)
            print(resource_planning_data["reasoning"])
            st.download_button(
                label="Download Resource Planning Strategy",
                data=st.session_state["resource_planning_data"],
                file_name="aws_resource_planning_data.md",
                mime="text/markdown",
            )


if __name__ == "__main__":
    # Load external CSS
    load_css()

    page_details()


    migration_strategy = st.file_uploader(
        "Upload migration strategy document with wave planning"
    )

    if st.button("Generate Resource Planning", type="primary"):
        if not migration_strategy:
            st.error("Please upload a migration strategy document.")
        else:
            # Validate file size
            is_valid, error_msg = validate_file_size(migration_strategy)
            if not is_valid:
                st.error(f"File validation error: {error_msg}")
            else:
                with st.spinner(
                    "The resource planning is being developed. "
                    "This may take a few minutes."
                ):
                    develop_resource_planning(
                        migration_strategy.getvalue().decode("utf-8")
                    )
