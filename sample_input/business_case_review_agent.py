from pathlib import Path

from strands import Agent
from strands.models.bedrock import BedrockModel
from strands_tools import file_read

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "sample_data"
PDF_PATH = str(DATA_DIR / "sample_business_case.pdf")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("\n--- Business Case Review ---\n")

    reviewer = Agent(
        system_prompt=(
            "You are a senior migration business case reviewer. "
            "Use the file_read tool to read documents, then analyse and provide feedback on: "
            "completeness, cost assumptions, risk coverage, and timeline realism. "
            "Be specific and actionable."
        ),
        model=BedrockModel(model_id="us.anthropic.claude-sonnet-4-20250514-v1:0", temperature=0.3, streaming=True),
        tools=[file_read],
        callback_handler=None,
    )

    message = f"""
    Read this business case PDF and provide a review:
    {PDF_PATH}

    Include:
    1. Executive summary of the business case
    2. Strengths of the proposal
    3. Gaps or weaknesses
    4. Recommendations for improvement
    """

    output = reviewer(message)
    print(output)

    print("\n\n--- Done ---")


if __name__ == "__main__":
    main()
