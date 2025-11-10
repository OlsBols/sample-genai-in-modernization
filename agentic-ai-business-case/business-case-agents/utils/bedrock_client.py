import boto3
import json
from typing import Dict, Any

class BedrockClient:
    """Client for invoking Claude via Bedrock Runtime"""
    
    def __init__(self, region: str = 'us-east-1', model_id: str = 'anthropic.claude-3-5-sonnet-20240620-v1:0'):
        self.region = region
        self.model_id = model_id
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=region)
    
    def invoke_with_prompt(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        """Invoke Claude with system and user prompts"""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        })
        
        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def query_knowledge_base(self, kb_id: str, query: str, max_results: int = 5) -> list:
        """Query Bedrock Knowledge Base for partner data"""
        try:
            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {'numberOfResults': max_results}
                }
            )
            return [
                {
                    'content': result['content']['text'],
                    'score': result.get('score', 0)
                }
                for result in response['retrievalResults']
            ]
        except Exception as e:
            print(f"Warning: Could not query knowledge base: {e}")
            return []
