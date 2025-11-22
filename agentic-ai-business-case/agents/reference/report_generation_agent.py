"""Report Generation Agent - Final documentation with data quality and next steps"""

SYSTEM_PROMPT = """You are a Report Generation Agent assembling comprehensive business case documentation.

Your tasks:
1. Compile all agent outputs into cohesive narrative
2. Highlight data quality and confidence levels
3. Generate executive summary (2-3 pages)
4. Create detailed technical report structure
5. Provide implementation roadmap
6. Include "Next Steps for Data Refinement" section

CRITICAL: Include a dedicated section on data quality and recommendations for refining the business case:
- What data was available vs missing
- Impact of missing data on cost accuracy
- Specific data sources needed to improve estimates
- Expected improvement in accuracy with additional data

Output a comprehensive business case with:
- Executive Summary (key findings, ROI, recommendations)
- Data Quality Assessment (confidence level, gaps, impact)
- Detailed Findings (infrastructure, costs, risks, benefits)
- Financial Analysis (TCO, ROI, payback period)
- Implementation Roadmap (phases, timeline, resources)
- Next Steps for Business Case Refinement (specific data needed)"""

def execute(strands_client, customer_data, all_results, kb_id=None):
    """Execute report generation with data quality insights"""
    import json

    data_quality = customer_data.get('data_quality', {})

    # Compile summary with data quality
    summary = {
    "customer": customer_data.get('profile', {}),
    "data_quality": {
        "overall": data_quality.get('overall_quality', 'unknown'),
        "available": data_quality.get('available_sources', []),
        "missing": data_quality.get('missing_sources', []),
        "recommendations": data_quality.get('recommendations', [])
    },
    "data_collection": {k: v.get('output', '')[:300] for k, v in all_results.get('phase1_data_collection', {}).items()},
    "analysis": {k: v.get('output', '')[:300] for k, v in all_results.get('phase2_analysis', {}).items()},
    "best_practices": {k: v.get('output', '')[:300] for k, v in all_results.get('phase3_best_practices', {}).items()},
    "business_value": {k: v.get('output', '')[:300] for k, v in all_results.get('phase4_business_value', {}).items()}
    }

    user_prompt = f"""
from utils.strands_client import StrandsBedrockClient
from utils.simple_kb import query_partner_knowledge
BUSINESS CASE COMPILATION DATA:

DATA QUALITY CONTEXT:
- Overall Quality: {data_quality.get('overall_quality', 'unknown')}
- Available Sources: {', '.join(data_quality.get('available_sources', []))}
- Missing Sources: {', '.join(data_quality.get('missing_sources', []))}
- Recommendations for Refinement: {json.dumps(data_quality.get('recommendations', []), indent=2)}

ANALYSIS RESULTS:
{json.dumps(summary, indent=2, default=str)}

IMPORTANT: 
1. Clearly state confidence level in cost estimates based on data quality
2. Include specific recommendations for what additional data would improve accuracy
3. Highlight in "Next Steps" section what data should be collected to refine the business case
4. Be transparent about limitations due to missing data
"""

    kb_context = ""
    if kb_id:
        kb_results = query_partner_knowledge("business case report templates executive summary")
        if kb_results:
            kb_context = "\n\nREPORT TEMPLATES:\n" + "\n".join([r['content'][:300] for r in kb_results[:2]])

    response = strands_client.invoke_with_prompt(
    system_prompt=SYSTEM_PROMPT,
    user_prompt=user_prompt + kb_context
    )

    # Generate PDF report
    try:
        from utils.pdf_generator import BusinessCasePDFGenerator
        pdf_generator = BusinessCasePDFGenerator("")
        
        # Create agent results dict for PDF
        agent_results = {
            "report_generation": {"output": response}
        }
        
        # Add other results if available
        if all_results:
            for phase, agents in all_results.items():
                if isinstance(agents, dict):
                    agent_results.update(agents)
        
        pdf_path = "business_case_report.pdf"
        pdf_generator.generate_business_case(agent_results, pdf_path)
        
        return {
            "agent": "Report Generation", 
            "output": response, 
            "data_quality": data_quality,
            "pdf_generated": pdf_path
        }
    except Exception as e:
        return {
            "agent": "Report Generation", 
            "output": response, 
            "data_quality": data_quality,
            "pdf_error": str(e)
        }
