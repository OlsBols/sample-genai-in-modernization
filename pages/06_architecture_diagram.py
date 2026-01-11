"""AWS Architecture Diagram Generator module for creating Draw.io XML diagrams."""

from datetime import datetime

import streamlit as st

from prompt_library.architecture_diagram.architecture_diagram_prompt import (
    get_architecture_diagram_prompt,
)
from utils.bedrock_client import invoke_bedrock_model_without_reasoning
from utils.config import load_css


def generate_drawio_xml_diagram(description: str) -> str:
    """
    Generate Draw.io XML directly using Claude 3.7 with AWS resource icon pattern styling.
    
    Args:
        description: Text description of the AWS architecture
        
    Returns:
        Generated XML content as string, empty string if generation fails
    """
    try:
        prompt = get_architecture_diagram_prompt(description)
        generated_xml = invoke_bedrock_model_without_reasoning(prompt)

        if not generated_xml:
            raise ValueError("Failed to generate XML from Bedrock model")

        # Clean any markdown formatting
        if "<?xml" not in generated_xml:
            generated_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + generated_xml

        # Remove any markdown code blocks
        generated_xml = generated_xml.replace("```xml", "").replace("```", "").strip()

        # Validate basic XML structure and AWS styling
        required_elements = [
            "<mxfile",
            "<diagram",
            "<mxGraphModel",
            "shape=mxgraph.aws4.resourceIcon",
            "gradientDirection=north",
            "strokeColor=#ffffff",
            "points=[[0,0,0]",
        ]
        if not all(element in generated_xml for element in required_elements):
            raise ValueError(
                "Generated XML is missing required Draw.io structure or AWS styling elements"
            )

        return generated_xml

    except ValueError as ve:
        st.error(f"Failed to generate diagram: {str(ve)}")
        return ""
    except (ConnectionError, TimeoutError) as ce:
        st.error(f"Network error during diagram generation: {str(ce)}")
        return ""
    except Exception as e:
        st.error(f"Unexpected error during diagram generation: {str(e)}")
        return ""


def main():
    """Main function for architecture diagram generation page."""
    # Load external CSS
    load_css()

    # Enhanced page header using CSS classes
    st.markdown(
        """
    <div class="page-header">
        <h1>AWS Architecture Diagram Generator</h1>
        <p>Generate Draw.io XML diagrams using AI</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Description section using CSS classes
    st.markdown(
        """
    <div class="info-card">
        <p>
            Describe your AWS architecture and generate a professional Draw.io XML diagram. 
            The generated diagram will include proper AWS service icons, styling, and 
            connections that you can download and edit in Draw.io.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # User input
    description = st.text_area(
        "Describe your AWS architecture:",
        height=150,
        placeholder="Example: A serverless architecture with API Gateway, Lambda, and DynamoDB...",
    )

    if st.button("Generate Diagram", type="primary"):
        if description:
            with st.spinner("Generating diagram..."):
                # Generate XML
                xml_content = generate_drawio_xml_diagram(description)

            if xml_content:  # Only show success if we have valid content
                st.markdown(
                    """
                <div class="results-section">
                    <h3>Diagram Generated Successfully</h3>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                with st.expander("Download & Usage Instructions", expanded=True):
                    st.markdown("**Generated Draw.io Diagram**")

                    # Display download button
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="Download Draw.io File",
                        data=xml_content,
                        file_name=f"aws_architecture_{timestamp}.drawio",
                        mime="application/xml",
                    )

                    st.markdown("""
                    **To view and edit this diagram:**
                    1. Download the .drawio file using the button above
                    2. Open it in [draw.io](https://app.diagrams.net/)
                    3. Or use the Draw.io Desktop application
                    4. Edit, customize, and export as needed
                    """)

                # Show the XML content in a collapsible section
                with st.expander("View Generated XML"):
                    st.code(xml_content, language="xml")
            else:
                st.markdown(
                    """
                <div class="warning-alert">
                    <p>Failed to generate diagram. Please try again with a different 
                    description or check the error message above.</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
            <div class="warning-alert">
                Please provide a description of your AWS architecture.
            </div>
            """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
