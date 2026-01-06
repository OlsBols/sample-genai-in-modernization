"""
Bedrock Guardrails Integration
Provides helper functions for using Bedrock with guardrails enabled
"""
import json
import logging
from typing import Dict, Any, Optional
from agents.config.config import BEDROCK_GUARDRAIL_CONFIG

logger = logging.getLogger(__name__)


def should_use_guardrails() -> bool:
    """
    Check if guardrails should be used
    
    Returns:
        bool: True if guardrails are enabled and configured
    """
    if BEDROCK_GUARDRAIL_CONFIG.get('dev_mode', False):
        logger.info("Guardrails disabled (dev_mode=True)")
        return False
    
    if not BEDROCK_GUARDRAIL_CONFIG.get('enabled', False):
        logger.info("Guardrails disabled (enabled=False)")
        return False
    
    guardrail_id = BEDROCK_GUARDRAIL_CONFIG.get('guardrail_identifier', '')
    if not guardrail_id:
        logger.warning("Guardrails enabled but guardrail_identifier not set. Run ./setup_bedrock_guardrail.sh")
        return False
    
    return True


def get_guardrail_config() -> Optional[Dict[str, str]]:
    """
    Get guardrail configuration for Bedrock API calls
    
    Returns:
        dict: Guardrail configuration or None if disabled
    """
    if not should_use_guardrails():
        return None
    
    return {
        'guardrailIdentifier': BEDROCK_GUARDRAIL_CONFIG['guardrail_identifier'],
        'guardrailVersion': BEDROCK_GUARDRAIL_CONFIG['guardrail_version']
    }


def add_guardrails_to_request(request_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add guardrail configuration to Bedrock request body
    
    Args:
        request_body: Bedrock API request body
    
    Returns:
        dict: Request body with guardrails added (if enabled)
    """
    guardrail_config = get_guardrail_config()
    
    if guardrail_config:
        request_body.update(guardrail_config)
        if BEDROCK_GUARDRAIL_CONFIG.get('trace', True):
            logger.info(f"Guardrails enabled: {guardrail_config['guardrailIdentifier']} v{guardrail_config['guardrailVersion']}")
    
    return request_body


def check_guardrail_response(response_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if guardrail intervened in the response
    
    Args:
        response_body: Bedrock API response body
    
    Returns:
        dict: Response body (unchanged)
    
    Raises:
        ValueError: If content was blocked and fail_on_block=True
    """
    if 'amazon-bedrock-guardrailAction' in response_body:
        action = response_body['amazon-bedrock-guardrailAction']
        
        if action == 'GUARDRAIL_INTERVENED':
            # Guardrail modified content (e.g., PII redaction)
            assessments = response_body.get('amazon-bedrock-guardrailAssessments', [])
            logger.warning(f"⚠️ Guardrail intervened: {len(assessments)} assessments")
            
            if BEDROCK_GUARDRAIL_CONFIG.get('trace', True):
                for assessment in assessments:
                    logger.info(f"  - {assessment.get('type', 'unknown')}: {assessment.get('action', 'unknown')}")
        
        elif action == 'BLOCKED':
            # Content was blocked
            reason = response_body.get('amazon-bedrock-guardrailReason', 'Unknown reason')
            logger.error(f"❌ Content blocked by guardrail: {reason}")
            
            if BEDROCK_GUARDRAIL_CONFIG.get('fail_on_block', False):
                raise ValueError(f"Content blocked by Bedrock Guardrail: {reason}")
            
            # Return empty response if not failing
            return {
                'content': [{
                    'text': '[Content blocked by guardrail. Please review your input and try again.]'
                }],
                'guardrail_blocked': True,
                'guardrail_reason': reason
            }
    
    return response_body


def log_guardrail_metrics(action: str, reason: str = None):
    """
    Log guardrail metrics for monitoring
    
    Args:
        action: Guardrail action (INTERVENED, BLOCKED, NONE)
        reason: Reason for intervention (optional)
    """
    try:
        import boto3
        from datetime import datetime
        
        cloudwatch = boto3.client('cloudwatch', region_name=BEDROCK_GUARDRAIL_CONFIG.get('region', 'us-east-1'))
        
        metric_data = [
            {
                'MetricName': 'GuardrailInterventions',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.utcnow(),
                'Dimensions': [
                    {'Name': 'Action', 'Value': action}
                ]
            }
        ]
        
        if reason:
            metric_data[0]['Dimensions'].append({'Name': 'Reason', 'Value': reason})
        
        cloudwatch.put_metric_data(
            Namespace='MigrationBusinessCase',
            MetricData=metric_data
        )
        
        logger.debug(f"Logged guardrail metric: {action}")
    
    except Exception as e:
        logger.debug(f"Failed to log guardrail metrics: {e}")


def get_guardrail_status() -> Dict[str, Any]:
    """
    Get current guardrail status and configuration
    
    Returns:
        dict: Guardrail status information
    """
    return {
        'enabled': BEDROCK_GUARDRAIL_CONFIG.get('enabled', False),
        'configured': bool(BEDROCK_GUARDRAIL_CONFIG.get('guardrail_identifier')),
        'guardrail_id': BEDROCK_GUARDRAIL_CONFIG.get('guardrail_identifier', 'Not configured'),
        'version': BEDROCK_GUARDRAIL_CONFIG.get('guardrail_version', 'Not configured'),
        'region': BEDROCK_GUARDRAIL_CONFIG.get('region', 'us-east-1'),
        'dev_mode': BEDROCK_GUARDRAIL_CONFIG.get('dev_mode', False),
        'active': should_use_guardrails()
    }


# Example usage for Strands library integration
def create_bedrock_model_with_guardrails(model_id: str, **kwargs):
    """
    Create a Bedrock model with guardrails enabled (for Strands library)
    
    Args:
        model_id: Bedrock model ID
        **kwargs: Additional model parameters
    
    Returns:
        BedrockModel: Model instance with guardrails
    """
    from strands.models import BedrockModel
    
    # Add guardrail configuration if enabled
    guardrail_config = get_guardrail_config()
    if guardrail_config:
        kwargs['guardrail_identifier'] = guardrail_config['guardrailIdentifier']
        kwargs['guardrail_version'] = guardrail_config['guardrailVersion']
        logger.info(f"✓ Guardrails enabled for model {model_id}")
    else:
        logger.info(f"⚠️ Guardrails disabled for model {model_id}")
    
    return BedrockModel(model_id=model_id, **kwargs)


if __name__ == '__main__':
    # Test guardrail configuration
    print("Bedrock Guardrails Status:")
    print("=" * 50)
    
    status = get_guardrail_status()
    for key, value in status.items():
        print(f"{key:15s}: {value}")
    
    print("\nGuardrail Config:")
    config = get_guardrail_config()
    if config:
        print(f"  Identifier: {config['guardrailIdentifier']}")
        print(f"  Version: {config['guardrailVersion']}")
    else:
        print("  Not configured or disabled")
    
    print("\nTo enable guardrails:")
    print("  1. Run: ./setup_bedrock_guardrail.sh")
    print("  2. Set BEDROCK_GUARDRAIL_CONFIG['enabled'] = True in config.py")
