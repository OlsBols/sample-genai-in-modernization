"""Landing Zone Design Agent - Account architecture"""
from utils.strands_client import StrandsBedrockClient

SYSTEM_PROMPT = """You are a Landing Zone Design Agent creating multi-account governance and network architecture.

Your tasks:
1. Design AWS account strategy
2. Create network architecture for multi-location connectivity
3. Establish governance framework
4. Plan organizational units

Output a landing zone blueprint with:
- Account structure
- Network design
- Governance framework
- OU hierarchy"""

def execute(strands_client, customer_data, kb_id=None):
    """Execute landing zone design agent"""
    profile = customer_data.get('profile', {})
    strategy_docs = customer_data.get('strategy', {})
    scope = customer_data.get('scope', '')[:1000]
    
    employees = profile.get('employees', 'Unknown')
    locations = profile.get('locations', 'Unknown')
    
    # Extract business context
    business_context = ""
    for doc_name, content in strategy_docs.items():
        business_context += f"{doc_name}: {content[:300]}\n\n"

    user_prompt = f"""Organization: {employees} employees, {locations} locations

Business Context:
{business_context}

Scope:
{scope}

Design a comprehensive AWS Landing Zone for this organization."""

    response = strands_client.invoke_with_prompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt
    )

    return {"agent": "Landing Zone Design", "output": response}
