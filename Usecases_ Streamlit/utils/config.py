# utils/config.py
"""
Configuration settings for AWS migration and modernisation tools
"""

import os
from pathlib import Path
from typing import Dict

import streamlit as st

# AWS Configuration
AWS_REGION = "us-east-1"
BEDROCK_CONFIG = {
    "read_timeout": 300,  # 5 minutes
    "connect_timeout": 60,
    "retries": {"max_attempts": 3},
}

# Model Configuration
CLAUDE_3_7_SONNET_MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
CLAUDE_3_5_SONNET_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Default Model Parameters
DEFAULT_MAX_TOKENS = 121072
DEFAULT_TEMPERATURE = 0.7
DEFAULT_REASONING_BUDGET = 2000

# Chat-specific Parameters
CHAT_TEMPERATURE = 0.3  # Lower temperature for more consistent chat responses
MEMORY_TEMPERATURE = 0.2  # Lower for memory processing consistency


# Image Processing Configuration
MAX_IMAGE_SIZE_MB = 3.75
MAX_IMAGE_DIMENSIONS = {"width": 8000, "height": 8000}

# PDF Processing Configuration
MAX_PAGES_DEFAULT = 10
PDF_DPI = 150
BASE_DPI = 72
IMAGE_FORMAT = "png"
MEDIA_TYPE = "image/png"

# File Paths Configuration
FILE_PATHS = {
    "resource_profile": "sampledata/resource_profile_template.csv",
    "architecture_diagram": "sampledata/architecture_diagram/",
}

# File Limits Configuration
FILE_LIMITS = {"max_size_mb": 10}


def get_aws_region() -> str:
    """Get AWS region from environment or default"""
    return os.getenv("AWS_REGION", AWS_REGION)


def get_model_config(model_type: str = "claude_3_7") -> Dict:
    """Get model configuration based on type"""
    if model_type == "claude_3_5":
        return {
            "model_id": CLAUDE_3_5_SONNET_MODEL_ID,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "temperature": DEFAULT_TEMPERATURE,
        }
    else:
        return {
            "model_id": CLAUDE_3_7_SONNET_MODEL_ID,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "temperature": DEFAULT_TEMPERATURE,
            "reasoning_budget": DEFAULT_REASONING_BUDGET,
        }


def get_chat_model_config() -> Dict:
    """Get model configuration specifically for chat assistant with lower temperature"""
    return {
        "model_id": CLAUDE_3_7_SONNET_MODEL_ID,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "temperature": CHAT_TEMPERATURE,  
        "reasoning_budget": DEFAULT_REASONING_BUDGET,
    }


def get_memory_model_config() -> Dict:
    """Get model configuration specifically for Mem0 memory operations with Claude 3.7 Sonnet"""
    return {
        "model_id": CLAUDE_3_7_SONNET_MODEL_ID,
        "max_tokens": 128000,  
        "temperature": MEMORY_TEMPERATURE,  
    }


def get_embedder_config_to_initialize_mem0() -> Dict:
    """Get embedder configuration for Mem0 initialization"""
    return {
        "provider": "aws_bedrock",
        "config": {
            "model": "amazon.titan-embed-text-v2:0",
        },
    }


def get_vector_store_config_initialize_mem0() -> Dict:
    """Get vector store configuration for Mem0 initialization"""
    return {
        "provider": "qdrant",
        "config": {
            "collection_name": "mem0_chat",
            "embedding_model_dims": 1024,  
            "path": "/tmp/qdrant_mem0",
            "on_disk": False,
        },
    }


def load_css():
    """Load external CSS file for Streamlit pages."""
    css_file = Path(__file__).parent / "styles.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS file not found. Using default styling.")
