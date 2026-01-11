"""Learning pathway development module for AWS migration training."""

import pandas as pd
import streamlit as st

from prompt_library.learning_pathway.learning_pathway_prompt import (
    get_learning_pathway_prompt,
)
from utils.bedrock_client import invoke_bedrock_model_with_reasoning
from utils.config import load_css
from utils.file_handler import validate_file_size


# Initialize session state
if "processed_results" not in st.session_state:
    st.session_state.processed_results = []

# Load external CSS
load_css()


def update_training_pathway(md_content, training_data_df):
    """Update training pathway with links from training data."""
    table_rows = []
    for line in md_content.split("\n"):
        if line.strip().startswith("|") and line.strip().endswith("|"):
            cells = [cell.strip() for cell in line.strip().split("|")[1:-1]]
            if cells and not all(
                "-" in c and c.replace("-", "").strip() == "" for c in cells
            ):
                table_rows.append(cells)

    training_pathway_df = pd.DataFrame(
        table_rows[1:], columns=[col.strip() for col in table_rows[0]]
    )

    training_data_df.columns = training_data_df.columns.str.strip()
    training_pathway_df.columns = training_pathway_df.columns.str.strip()

    # Merge DataFrames
    training_pathway_df = training_pathway_df.merge(
        training_data_df[["Course Id", "training_link"]].copy(),
        on="Course Id",
        how="left",
    )

    training_pathway_df["training_link"] = training_pathway_df[
        "training_link"
    ].apply(lambda x: f"[Training Link]({x})" if pd.notna(x) else "")
    # Create new table
    new_table = "| " + " | ".join(training_pathway_df.columns) + " |\n"
    new_table += "|" + "|".join(["---"] * len(training_pathway_df.columns)) + "|\n"
    for _, row in training_pathway_df.iterrows():
        new_table += "| " + " | ".join(str(v) for v in row) + " |\n"

    # Replace old table with new one
    table_start = md_content.find("| Course Id")
    table_end = md_content.find("\n\n", table_start)
    if table_end == -1:  # If no double newline found
        table_end = len(md_content)
    md_content = md_content[:table_start] + new_table + md_content[table_end:]

    return md_content


def main():
    """Main function for learning pathway page."""
    # Enhanced page header using CSS classes
    st.markdown(
        """
    <div class="page-header">
        <h1>Learning Pathway Development</h1>
        <p>Create personalized training and skill development plans</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Description section using CSS classes
    st.markdown(
        """
    <div class="info-card">
        <p>
            Generate customized learning pathways based on your team's roles, 
            experience levels, and available training resources. 
            Upload your training catalog and specify target personas to receive 
            tailored recommendations for AWS migration and modernization skills.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # File uploads
    col1, col2 = st.columns(2)
    with col1:
        training_data = st.file_uploader("Upload Training Catalog (CSV)", type=["csv"])
    with col2:
        st.write("")  # Empty space for alignment

    # Configuration inputs
    col1, col2 = st.columns(2)
    with col1:
        target_role = st.selectbox(
            "Target Role",
            options=[
                "",
                "Solution Architect",
                "Software Developer",
                "Delivery Manager",
                "Alliance Lead",
                "Sales and Marketing",
            ],
            help="Select the primary role for this learning pathway",
        )

    with col2:
        target_experience = st.selectbox(
            "Experience Level",
            options=["", "Junior Level", "Senior Level", "Principal Level"],
            help="Select the experience level of the target audience",
        )

    # Learning duration input
    learning_duration = st.text_input(
        "Learning Duration",
        placeholder="e.g., 3 months, 6 weeks",
        help="Specify the timeframe for completing the learning pathway",
    )

    st.divider()

    # Validation and processing
    if st.button("Generate Learning Pathway", type="primary"):
        # Input validation
        if not training_data:
            st.error("Please upload a training catalog CSV file.")
        elif not target_role:
            st.error("Please select a target role.")
        elif not target_experience:
            st.error("Please select an experience level.")
        else:
            # Validate file size
            is_valid, error_msg = validate_file_size(training_data)
            if not is_valid:
                st.error(f"File validation error: {error_msg}")
                return
            # Enhanced expander for training data using CSS classes
            st.markdown(
                """
            <div class="results-section">
                <h3>Data Preview</h3>
            </div>
            """,
                unsafe_allow_html=True,
            )

            with st.expander("Training Catalog", expanded=True):
                training_data_df = pd.read_csv(
                    training_data, sep=",", quotechar='"', encoding="utf-8"
                )
                st.markdown(
                    f"**Training Catalog Overview** - {len(training_data_df)} courses available"
                )
                st.dataframe(training_data_df, 
                )

            with st.spinner("Generating personalized learning pathway..."):
                try:
                    # Generate learning pathway
                    prompt = get_learning_pathway_prompt(
                        training_data_df,
                        [target_role],
                        [target_experience],
                        learning_duration,
                    )
                    training_pathway = invoke_bedrock_model_with_reasoning(prompt)

                    if training_pathway:
                        # Update pathway with training links
                        training_pathway = update_training_pathway(
                            training_pathway, training_data_df
                        )

                        # Store in session state
                        st.session_state.processed_results = training_pathway

                except ValueError as ve:
                    st.error(f"An error occurred while processing: {str(ve)}")
                except Exception as e:
                    st.error(f"Unexpected error occurred while processing: {str(e)}")

    # Results section
    if (
        hasattr(st.session_state, "processed_results")
        and st.session_state.processed_results
    ):
        st.markdown(
            """
        <div class="results-section">
            <h3>Learning Pathway Results</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        with st.expander("Personalized Learning Pathway", expanded=True):
            st.markdown("**Customized Training Recommendations**")
            st.markdown(st.session_state.processed_results)

            st.download_button(
                label="Download Learning Pathway",
                data=st.session_state.processed_results,
                file_name=(
                    f"learning_pathway_"
                    f"{target_role.lower().replace(' ', '_') if target_role else 'general'}_"
                    f"{target_experience.lower().replace(' ', '_') if target_experience else 'general'}"
                    f".md"
                ),
                mime="text/markdown",
            )


if __name__ == "__main__":
    main()
