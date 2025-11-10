from strands import Agent
from strands.models import BedrockModel
import json
from typing import Dict, Any

class StrandsBedrockClient:
    """Strands SDK client for Bedrock Claude integration"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.agent = Agent()
        self.region = region
        # Use proper BedrockModel - region is set via AWS credentials/config
        self.agent.model = BedrockModel(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
        )
        
    def invoke_with_prompt(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        """Invoke Claude via Strands SDK"""
        try:
            # Set system prompt
            self.agent.system_prompt = system_prompt
            
            # Invoke with user prompt
            response = self.agent(user_prompt)
            
            # Handle different response types
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)
        except Exception as e:
            return f"Error invoking Strands: {str(e)}"
