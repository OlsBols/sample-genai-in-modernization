"""Common backend configuration for agents and AWS services."""

import os

# ---------------------------------------------------------------------------
# AWS Configuration
# ---------------------------------------------------------------------------
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", None)

# ---------------------------------------------------------------------------
# Model IDs
# ---------------------------------------------------------------------------
CLAUDE_SONNET_4_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"
CLAUDE_3_7_SONNET_MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
CLAUDE_3_5_SONNET_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

DEFAULT_MODEL_ID = CLAUDE_SONNET_4_MODEL_ID

# ---------------------------------------------------------------------------
# Model Parameters
# ---------------------------------------------------------------------------
DEFAULT_MAX_TOKENS = 65536
DEFAULT_TEMPERATURE = 0.7
DEFAULT_REASONING_BUDGET = 2000

# ---------------------------------------------------------------------------
# SSE / Streaming
# ---------------------------------------------------------------------------
SSE_MEDIA_TYPE = "text/event-stream"

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_aws_region() -> str:
    """Return the configured AWS region."""
    return AWS_REGION
