"""Company Intelligence Agent - Business context using ALL strategy documents"""

from utils.strands_client import StrandsBedrockClient

SYSTEM_PROMPT = """You are a Company Intelligence Agent extracting business context from company information.

Your tasks:
1. Analyze company profile and ALL strategy documents
2. Identify business drivers and objectives from multiple sources
3. Extract strategic priorities and migration readiness
4. Assess organizational readiness and stakeholder alignment
5. Synthesize customer conversations and partner insights

Output a structured report with:
- Company overview (size, industry, revenue)
- Business drivers for cloud migration
- Strategic objectives and success criteria
- Key stakeholders and decision makers
- Organizational readiness assessment
- Customer pain points and expectations"""

def execute(strands_client, customer_data):
    """Execute company intelligence using ALL strategy documents"""
    import json
    
    profile = json.dumps(customer_data.get('profile', {}), indent=2)
    strategy_docs = customer_data.get('strategy', {})
    
    # Build comprehensive strategy context
    data_summary = f"""
COMPANY PROFILE:
{profile}

STRATEGY DOCUMENTS:
"""
    
    # Add all strategy documents
    doc_order = [
        '1-strategy-vision-document',
        '2-migration-modernization-drivers',
        '3-customer-insights-partner',
        '4-customer-conversations',
        '5-aws-migration-readiness-assessment'
    ]
    
    for doc_key in doc_order:
        if doc_key in strategy_docs:
            data_summary += f"\n\n{doc_key.upper()}:\n{strategy_docs[doc_key][:1500]}\n"
    
    # Add any other strategy docs not in the list
    for doc_key, doc_content in strategy_docs.items():
        if doc_key not in doc_order:
            data_summary += f"\n\n{doc_key.upper()}:\n{doc_content[:1000]}\n"
    
    user_prompt = data_summary
    
    response = strands_client.invoke_with_prompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt
    )
    
    return {"agent": "Company Intelligence", "output": response}
