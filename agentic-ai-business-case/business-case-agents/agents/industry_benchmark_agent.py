"""Industry Benchmark Agent - Industry-specific insights"""
from utils.strands_client import StrandsBedrockClient
from utils.simple_kb import query_partner_knowledge

SYSTEM_PROMPT = """You are an Industry Benchmarking Agent providing industry-specific cloud adoption insights.

Your tasks:
1. Identify industry vertical and company size
2. Provide cloud adoption benchmarks
3. Compare against industry peers
4. Estimate typical migration timelines

Output a benchmark report with:
- Industry context
- Peer comparisons
- Adoption patterns
- Timeline benchmarks"""

def execute(strands_client, customer_data, kb_id=None):
    """Execute industry benchmark agent"""
    import json
    
    profile = json.dumps(customer_data.get('profile', {}), indent=2)
    user_prompt = f"Company Profile:\n{profile}"
    
    kb_context = ""
    if kb_id:
        kb_results = query_partner_knowledge("retail industry cloud adoption benchmarks")
        if kb_results:
            kb_context = "\n\nIndustry Benchmarks:\n" + "\n".join([r['content'][:300] for r in kb_results[:2]])
    
    response = strands_client.invoke_with_prompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt + kb_context
    )
    
    return {"agent": "Industry Benchmark", "output": response}
