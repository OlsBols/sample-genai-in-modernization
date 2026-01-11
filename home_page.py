import streamlit as st

from utils.config import load_css


# Clear session state
for key in st.session_state.keys():
    del st.session_state[key]

# Load external CSS
load_css()

# Main header using CSS classes
st.markdown(
    """
<div class="page-header">
    <h1>Using Gen AI - MAP Assess Phase</h1>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="info-card">
    <p>
        This demo illustrates the application of Generative AI (Gen AI) during the AWS Migration Acceleration Program (MAP) assessment phase, after the completion of on-premises discovery. It showcases capabilities that enhance migration planning, cost optimization, identification of modernization opportunities, and resource planning—processes which were previously both time-consuming and complex.
    </p>
    <ul>
        <li>This demo can analyse infrastructure data to generate strategic recommendations, predict MAP funding milestones, and create comprehensive migration wave plans with greater efficiency and insight than traditional methods.</li>
        <li>AWS partners can leverage these GenAI capabilities across three progressive implementation levels—from direct model usage to fully automated solutions—creating a transformative approach to cloud migration assessment.</li>
    </ul>
</div>
""",
    unsafe_allow_html=True,
)

# # Image section
# st.image(
#     "sampledata/Image_output.jpeg", caption="Generative AI in AWS MAP Assessment Phase"
# )

# Key features header using CSS classes
st.markdown(
    """
<h2 class="text-secondary">Key Features</h2>
""",
    unsafe_allow_html=True,
)

# Features list using CSS classes
st.markdown(
    """
<div class="results-section">
    <ul>
        <li><strong>Modernization Opportunity Analysis:</strong> Analyzes infrastructure data and identifies modernization pathways with AWS cost projections.</li>
        <li><strong>Migration Strategy Development:</strong> Creates migration patterns, wave planning, and $50k milestone predictions.</li>
        <li><strong>Resource Planning:</strong> Develops team structures and resource allocation plans.</li>
        <li><strong>Learning Pathway Development:</strong> Creates personalized training plans for AWS migration teams.</li>
        <li><strong>Business Case Review:</strong> Comprehensive TCO analysis and validation with PDF processing.</li>
        <li><strong>Architecture Diagram Generator:</strong> Generates AWS diagrams in Draw.io XML format.</li>
        <li><strong>Interactive Analysis Chat:</strong> Context-aware conversations with generated outputs and scenario exploration.</li>
    </ul>
</div>
""",
    unsafe_allow_html=True,
)

# Warning message using CSS classes
st.markdown(
    """
<div class="warning-alert">
    <p>
        - AI Accuracy Disclaimer: While GenAI provides valuable insights, it might occasionally generate inaccurate predictions. Always validate and double-check AI-generated recommendations before implementation.
    </p>
    <p>
       - This solution is explicitly designed for proof-of-concept purposes only to explore the art of possibility with Generative AI for MAP assessments. Please adhere to your company's enhanced security and compliance policies
    </p>
</div>
""",
    unsafe_allow_html=True,
)
