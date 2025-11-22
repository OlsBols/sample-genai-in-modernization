"""GenAI Opportunity Agent - AI/ML use cases"""
from utils.strands_client import StrandsBedrockClient

SYSTEM_PROMPT = """You are a GenAI Opportunity Agent identifying AI/ML value creation opportunities.

Your tasks:
1. Analyze business processes for AI opportunities
2. Identify retail-specific use cases (personalization, supply chain, inventory)
3. Calculate ROI projections
4. Create implementation roadmaps

Output an AI opportunity assessment with:
- Use case identification
- ROI projections
- Implementation priorities
- Roadmap recommendations"""

def execute(strands_client, customer_data, kb_id=None):
    """Execute GenAI opportunity agent"""
    import json
    
    profile = customer_data.get('profile', {})
    strategy_docs = customer_data.get('strategy', {})
    scope = customer_data.get('scope', '')[:1000]
    
    # Extract business context from strategy documents
    business_context = ""
    for doc_name, content in strategy_docs.items():
        business_context += f"{doc_name}: {content[:500]}\n\n"
    
    user_prompt = f"""Industry: {profile.get('industry', 'Unknown')}
Company Profile: {json.dumps(profile, indent=2)}

Business Context:
{business_context}

Scope:
{scope}

Please identify GenAI opportunities for this organization."""
    
    response = strands_client.invoke_with_prompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt
    )
    
    return {"agent": "GenAI Opportunity", "output": response}
