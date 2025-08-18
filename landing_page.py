"""
This page provides information about core features of the demo.
"""

import streamlit as st

for key in st.session_state.keys():
    del st.session_state[key]

# Title and Introduction
st.title("Gen AI: Art of Possibility for AWS MAP Assessment")
# Content on the right side
st.markdown("""
    This demo illustrates the application of Generative AI during the MAP assessment phase, following the completion of on-premises discovery. It showcases capabilities that enhance migration planning, cost optimisation, identification of modernisation opportunities, and resource planning, processes which were previously both time-consuming and complex.
    - This demo can analyse infrastructure data to generate strategic recommendations, predict MAP funding milestones, and create comprehensive migration wave plans.
    - AWS partners can leverage these GenAI capabilities across three progressive implementation levels—from direct model usage to fully automated solutions—creating a transformative approach to cloud migration assessment.
    """)
st.image(
    "sampledata/landing_page_image.jpeg",
    caption="Generative AI in AWS MAP Assessment Phase",
)
st.header("Key features:")
st.markdown("""
- **Modernisation Opportunity Analysis**: GenAI analyses architecture and on-premises infrastructure data to identify modernisation pathways with corresponding AWS cost projections.
- **Migration Strategy Development**: Creates data-driven migration patterns, wave planning with cumulative spend forecasts, and $50k milestone predictions to accelerate migration.
- **Resource Planning**: Resource planning is based on three key inputs: migration strategy, wave planning data, and resource details. It creates detailed team structures and resource allocation plans, providing five key outputs: an executive summary, team structure evaluation, resource summary, wave-based planning, and role-based resource allocation. The focus is on two team structure models (Hub-and-Spoke and Wave-Based), with justification for the recommended approach.

""")

st.warning(
    """ 💡 Remember, while our GenAI is a whiz at insights, it might occasionally daydream—so always double-check its predictions!"""
)
