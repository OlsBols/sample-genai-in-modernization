"""Productivity Impact Agent - Efficiency analysis"""
from utils.strands_client import StrandsBedrockClient
from utils.simple_kb import query_partner_knowledge

SYSTEM_PROMPT = """You are a Productivity Impact Agent quantifying operational efficiency and innovation benefits using AWS Cloud Value Framework.

Your tasks:
1. Apply Cloud Value Framework methodologies
2. Calculate staff productivity gains
3. Measure innovation acceleration
4. Quantify automation benefits

Output a productivity analysis with:
- Staff productivity gains
- Cost avoidance
- Innovation metrics
- Automation benefits"""

def execute(strands_client, customer_data, kb_id=None):
    """Execute productivity impact agent"""
    scope = customer_data.get('scope', '')[:500]

    user_prompt = f"Current State:\n{scope}"

    kb_context = ""
    if kb_id:
        kb_results = query_partner_knowledge("Cloud Value Framework productivity")
        if kb_results:
            kb_context = "\n\nCVF Methodology:\n" + "\n".join([r['content'][:300] for r in kb_results[:2]])

    response = strands_client.invoke_with_prompt(
    system_prompt=SYSTEM_PROMPT,
    user_prompt=user_prompt + kb_context
    )

    return {"agent": "Productivity Impact", "output": response}
