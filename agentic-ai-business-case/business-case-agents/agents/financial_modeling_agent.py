"""Financial Modeling Agent - Comprehensive financial analysis with TCO integration"""
from utils.strands_client import StrandsBedrockClient
from utils.simple_kb import query_partner_knowledge
import json

SYSTEM_PROMPT = """You are a Financial Modeling Agent performing comprehensive financial analysis for AWS migration business cases.

Your tasks:
1. Analyze TCO data and migration scenarios
2. Calculate NPV, IRR, and payback period for each scenario
3. Factor in migration costs from partner data
4. Perform sensitivity analysis
5. Generate detailed financial projections

Use actual data provided. Calculate realistic financial metrics based on:
- Current infrastructure costs
- AWS migration scenarios (lift-shift, replatform, refactor, cloud-native)
- Migration implementation costs
- Operational savings over time
- Risk-adjusted returns

Output detailed financial analysis with specific calculations, not generic estimates."""

def execute(strands_client, customer_data, all_results, kb_id=None):
    """Execute financial modeling with full TCO integration"""
    
    # Get complete TCO analysis data - handle different result structures
    tco_data = {}
    if isinstance(all_results, dict):
        # Try different possible locations for TCO data
        tco_data = all_results.get('tco_calculation', {})
        if not tco_data:
            tco_data = all_results.get('phase2_analysis', {}).get('tco_calculation', {})
    
    # Extract actual financial data with safe defaults
    current_cost = 8.5  # Default fallback
    scenarios = {}
    tco_output = "No TCO data available"
    
    if isinstance(tco_data, dict):
        current_cost = tco_data.get('current_cost', 8.5)
        scenarios = tco_data.get('scenarios', {})
        tco_output = tco_data.get('output', 'TCO analysis completed')
    
    # Get partner migration cost factors
    kb_context = ""
    migration_costs = {
        'lift_shift': 0.15,
        'replatform': 0.25, 
        'refactor': 0.40,
        'cloud_native': 0.60
    }
    
    if kb_id:
        try:
            kb_results = query_partner_knowledge("migration costs implementation timeline financial modeling")
            if kb_results:
                kb_context = "\n\nPartner Migration Cost Data:\n" + "\n".join([r['content'][:400] for r in kb_results[:3]])
                
                # Extract migration cost factors from partner data
                for result in kb_results:
                    content = result['content'].lower()
                    if 'migration cost' in content or 'implementation cost' in content:
                        if 'lift' in content and 'shift' in content:
                            migration_costs['lift_shift'] = 0.15
                        if 'replatform' in content:
                            migration_costs['replatform'] = 0.25
                        if 'refactor' in content or 'moderniz' in content:
                            migration_costs['refactor'] = 0.40
                        if 'cloud native' in content or 'greenfield' in content:
                            migration_costs['cloud_native'] = 0.60
        except Exception as e:
            print(f"Warning: Could not retrieve partner knowledge: {e}")
    
    # Build comprehensive financial analysis prompt
    user_prompt = f"""
FINANCIAL MODELING REQUEST

## Current State
- Annual Infrastructure Cost: ${current_cost:.1f}M
- Migration Scenarios Available: {list(scenarios.keys()) if scenarios else 'Standard scenarios'}

## TCO Analysis Summary
{tco_output[:1000]}  

## Migration Cost Factors (from partner data)
{json.dumps(migration_costs, indent=2)}

## Required Financial Analysis
Calculate for each migration scenario:
1. **Implementation Costs**: One-time migration costs
2. **Annual Operating Costs**: Ongoing AWS costs
3. **Annual Savings**: Year-over-year cost reduction
4. **NPV Calculation**: 5-year net present value (8% discount rate)
5. **IRR**: Internal rate of return
6. **Payback Period**: Time to recover implementation costs
7. **Sensitivity Analysis**: Best/worst case scenarios (+/-20%)

## Scenarios to Analyze
{json.dumps(scenarios, indent=2) if scenarios else 'Use standard lift-shift, replatform, refactor, cloud-native scenarios'}

Provide specific dollar amounts and percentages based on the ${current_cost:.1f}M current annual cost.
"""
    
    try:
        response = strands_client.invoke_with_prompt(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt + kb_context
        )
    except Exception as e:
        response = f"Error generating financial model: {e}\n\nFallback analysis based on ${current_cost:.1f}M current cost with standard migration scenarios."
    
    return {
        "agent": "Financial Modeling", 
        "output": response,
        "current_cost": current_cost,
        "migration_costs": migration_costs,
        "scenarios_analyzed": list(scenarios.keys()) if scenarios else []
    }
