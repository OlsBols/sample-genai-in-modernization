"""Risk Assessment Agent - Risk quantification"""
from utils.strands_client import StrandsBedrockClient
from utils.simple_kb import query_partner_knowledge

SYSTEM_PROMPT = """You are a Risk Assessment Agent evaluating and quantifying migration risks.

Your tasks:
1. Identify technical, business, and organizational risks
2. Quantify probability and impact scores
3. Develop mitigation strategies
4. Create risk register

Output a risk assessment with:
- Risk identification
- Probability/impact scores
- Mitigation strategies
- Risk register"""

def execute(strands_client, customer_data, kb_id=None):
    """Execute risk assessment agent"""
    scope = customer_data.get('scope', '')[:500]

    user_prompt = f"Migration Readiness: 3.2/5.0\n\nScope:\n{scope}"

    kb_context = ""
    if kb_id:
        kb_results = query_partner_knowledge("risk assessment mitigation")
        if kb_results:
            kb_context = "\n\nRisk Frameworks:\n" + "\n".join([r['content'][:300] for r in kb_results[:2]])

    response = strands_client.invoke_with_prompt(
    system_prompt=SYSTEM_PROMPT,
    user_prompt=user_prompt + kb_context
    )

    return {"agent": "Risk Assessment", "output": response}
