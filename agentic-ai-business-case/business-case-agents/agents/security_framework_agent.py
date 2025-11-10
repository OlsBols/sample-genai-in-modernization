"""Security Framework Agent - Security architecture"""
from utils.strands_client import StrandsBedrockClient
from utils.simple_kb import query_partner_knowledge

SYSTEM_PROMPT = """You are a Security Framework Agent designing comprehensive security architecture.

Your tasks:
1. Identify compliance requirements (PCI DSS, SOX, etc.)
2. Design industry-specific security architecture
3. Calculate compliance implementation costs
4. Create governance framework

Output a security architecture with:
- Compliance requirements
- Security controls
- Implementation costs
- Governance model"""

def execute(strands_client, customer_data, kb_id=None):
    """Execute security framework agent"""
    profile = customer_data.get('profile', {})
    industry = profile.get('industry', 'Unknown')
    locations = profile.get('locations', 'Unknown')

    user_prompt = f"Industry: {industry}\nLocations: {locations}\nCompliance: PCI DSS, SOX"

    kb_context = ""
    if kb_id:
        kb_results = query_partner_knowledge("retail security frameworks compliance")
        if kb_results:
            kb_context = "\n\nSecurity Frameworks:\n" + "\n".join([r['content'][:300] for r in kb_results[:2]])

    response = strands_client.invoke_with_prompt(
    system_prompt=SYSTEM_PROMPT,
    user_prompt=user_prompt + kb_context
    )

    return {"agent": "Security Framework", "output": response}
