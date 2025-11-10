"""Modernization Scenario Agent - Migration pathways using ALL available data"""

from utils.strands_client import StrandsBedrockClient
from utils.simple_kb import query_partner_knowledge

SYSTEM_PROMPT = """You are a Modernization Scenario Agent generating migration pathway options.

Your tasks:
1. Analyze complete application portfolio and dependencies
2. Generate multiple migration scenarios (rehost, replatform, refactor)
3. Consider application dependencies and database relationships
4. Calculate effort, timeline, cost, and risk for each scenario
5. Provide phased migration recommendations

Output a scenario matrix with:
- Migration strategies for each application tier
- Effort estimates (person-hours)
- Timeline projections (months)
- Risk assessments (high/medium/low)
- Dependency-aware sequencing
- Recommended migration waves"""

def execute(strands_client, customer_data, phase1_results, kb_id=None):
    """Execute modernization scenario analysis using comprehensive data"""
    
    scope = customer_data.get('scope', '')[:2000]
    infra = customer_data.get('infrastructure', {})
    strategy_docs = customer_data.get('strategy', {})
    infra_summary = phase1_results.get('data_ingestion', {}).get('output', '')[:1000]
    
    # Build comprehensive context
    data_summary = f"""
SCOPE AND APPLICATION PORTFOLIO:
{scope}

INFRASTRUCTURE ANALYSIS:
{infra_summary}
"""
    
    # Add dependency information if available
    if 'dependencies' in infra:
        data_summary += f"""
APPLICATION DEPENDENCIES:
- Dependency mapping data available
- Application-to-database relationships documented
- Infrastructure dependencies mapped
"""
    
    # Add strategy context
    if 'migration-modernization-drivers' in strategy_docs or '2-migration-modernization-drivers' in strategy_docs:
        driver_doc = strategy_docs.get('2-migration-modernization-drivers', strategy_docs.get('migration-modernization-drivers', ''))
        data_summary += f"\n\nMIGRATION DRIVERS:\n{driver_doc[:1000]}"
    
    # Add readiness assessment if available
    if 'aws-migration-readiness-assessment' in strategy_docs or '5-aws-migration-readiness-assessment' in strategy_docs:
        mra_doc = strategy_docs.get('5-aws-migration-readiness-assessment', strategy_docs.get('aws-migration-readiness-assessment', ''))
        data_summary += f"\n\nREADINESS ASSESSMENT:\n{mra_doc[:1000]}"
    
    user_prompt = data_summary
    
    # Query KB for complexity scoring
    kb_context = ""
    if kb_id:
        kb_results = query_partner_knowledge("migration complexity scoring matrix 7Rs rehost replatform refactor")
        if kb_results:
            kb_context = "\n\nPARTNER MIGRATION METHODOLOGIES:\n" + "\n".join([r['content'][:400] for r in kb_results[:3]])
    
    response = strands_client.invoke_with_prompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt + kb_context
    )
    
    return {"agent": "Modernization Scenario", "output": response}
