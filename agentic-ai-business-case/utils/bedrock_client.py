import boto3
import json
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


from .config import (
    get_aws_region,
    get_model_config,
    BEDROCK_CONFIG,
)

# Haiku 4.5 model ID for fast, lightweight analysis tasks
# Try cross-region first, fall back to direct model ID
HAIKU_MODEL_IDS = [
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "anthropic.claude-haiku-4-5-20251001-v1:0",
]


def _create_bedrock_client():
    """Create and return AWS Bedrock runtime client"""
    config = Config(**BEDROCK_CONFIG)
    return boto3.client("bedrock-runtime", region_name=get_aws_region(), config=config)


def _clean_response(text):
    """Clean HTML artifacts from model responses for markdown rendering"""
    import re
    if text:
        text = re.sub(r'<br\s*/?>', '\n', text)
    return text


def invoke_bedrock_model_without_reasoning(text_content):
    try:
        client = _create_bedrock_client()
        model_config = get_model_config("claude_3_7")

        # Use provided parameters or defaults from config
        max_tokens = model_config["max_tokens"]
        # Prepare the request body
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": text_content}],
        }

        # Make the API call
        response = client.invoke_model(
            modelId=model_config["model_id"], body=json.dumps(body)
        )

        # Parse response
        response_content = json.loads(response["body"].read())
        return _clean_response(response_content["content"][0]["text"])

    except (BotoCoreError, ClientError, Exception) as e:
        import logging
        error_msg = f"ERROR: Can't invoke '{model_config.get('model_id', 'unknown')}'. max_tokens={model_config.get('max_tokens')}. Reason: {e}"
        logging.error(error_msg)
        print(error_msg)
        return None


def invoke_bedrock_model_with_reasoning(prompt: str):
    """
    Invoke Bedrock model using configuration settings from config.py.
    Falls back to non-reasoning mode if the model doesn't support extended thinking.

    Args:
        prompt (str): The user prompt for the model

    Returns:
        dict: Dictionary containing both reasoning and response text
    """
    try:
        client = _create_bedrock_client()
        model_config = get_model_config("claude_3_7")

        # Create the message with the user's prompt
        conversation = [
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ]

        # Only enable reasoning for models that support it (Claude 3.7+)
        model_id = model_config["model_id"]
        supports_reasoning = "claude-3-7" in model_id or "claude-4" in model_id

        if supports_reasoning:
            # Configure reasoning parameters with specified token budget
            reasoning_config = {
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": model_config.get("reasoning_budget", 2000),
                }
            }

            response = client.converse(
                modelId=model_id,
                messages=conversation,
                additionalModelRequestFields=reasoning_config,
            )
        else:
            # Use converse without reasoning for models that don't support it
            response = client.converse(
                modelId=model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": model_config.get("max_tokens", 8192)},
            )

        # Extract the list of content blocks from the model's response
        content_blocks = response["output"]["message"]["content"]

        reasoning = None
        text = None

        # Process each content block to find reasoning and response text
        for block in content_blocks:
            if "reasoningContent" in block:
                reasoning = block["reasoningContent"]["reasoningText"]["text"]
            if "text" in block:
                text = _clean_response(block["text"])

        return {
            "reasoning": reasoning,
            "response": text if text else "No text response received from the model.",
            "success": True,
        }

    except (BotoCoreError, ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_config['model_id']}'. Reason: {e}")
        return {"reasoning": None, "response": None, "success": False, "error": str(e)}


def invoke_bedrock_model_for_image_analysis(onprem_image, prompt, image_type):
    try:
        client = _create_bedrock_client()
        model_config = get_model_config("claude_3_7")

        # Use provided parameters or defaults from config
        max_tokens = model_config["max_tokens"]
        image_format = image_type

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image_format,
                                "data": onprem_image,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        }

        response = client.invoke_model(
            modelId=model_config["model_id"], body=json.dumps(body)
        )

        response_content = json.loads(response["body"].read())
        return _clean_response(response_content["content"][0]["text"])

    except (BotoCoreError, ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_config['model_id']}'. Reason: {e}")
        return None


def invoke_bedrock_model_claude_3_5(prompt):
    """
    Invoke Bedrock Claude 3.5 Sonnet model with a prompt

    Args:
        prompt (str): The user prompt for the model

    Returns:
        str: The model's response text, or None if an error occurs
    """
    print(prompt)
    try:
        client = _create_bedrock_client()
        model_config = get_model_config("claude_3_5")

        # Prepare the request body
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": model_config["max_tokens"],
            "messages": [{"role": "user", "content": prompt}],
        }

        # Make the API call
        response = client.invoke_model(
            modelId=model_config["model_id"], body=json.dumps(body)
        )

        # Parse response
        response_content = json.loads(response["body"].read())
        return _clean_response(response_content["content"][0]["text"])

    except (BotoCoreError, ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_config['model_id']}'. Reason: {e}")
        return None


def invoke_bedrock_haiku(text_content, max_tokens=8192):
    """
    Invoke Claude Haiku 4.5 for fast, lightweight analysis tasks.
    Significantly faster than Sonnet for structured analysis like gap identification.
    Tries cross-region inference first, then direct model ID.

    Args:
        text_content: The prompt text
        max_tokens: Max output tokens (default 8192)

    Returns:
        str: The model's response text, or None if an error occurs
    """
    import logging
    client = _create_bedrock_client()

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": text_content}],
    }

    last_error = None
    for model_id in HAIKU_MODEL_IDS:
        try:
            response = client.invoke_model(
                modelId=model_id, body=json.dumps(body)
            )
            response_content = json.loads(response["body"].read())
            return _clean_response(response_content["content"][0]["text"])
        except (BotoCoreError, ClientError, Exception) as e:
            last_error = e
            logging.warning(f"Haiku model '{model_id}' failed: {e}. Trying next...")
            continue

    # All Haiku attempts failed — fall back to default Sonnet model
    logging.warning(f"All Haiku models failed. Falling back to default model. Last error: {last_error}")
    try:
        model_config = get_model_config("claude_3_7")
        body["max_tokens"] = model_config["max_tokens"]
        response = client.invoke_model(
            modelId=model_config["model_id"], body=json.dumps(body)
        )
        response_content = json.loads(response["body"].read())
        return _clean_response(response_content["content"][0]["text"])
    except (BotoCoreError, ClientError, Exception) as e:
        logging.error(f"Fallback model also failed: {e}")
        return None
