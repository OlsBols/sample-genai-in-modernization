"""
Multi-stage business case generator
Generates business case in sections to maximize quality and detail
"""
import os
from strands import Agent
from strands.models import BedrockModel
from config import model_id_claude3_7, model_temperature, MAX_TOKENS_BUSINESS_CASE, output_folder_dir_path

def create_section_agent(section_prompt):
    """Create an agent for generating a specific section"""
    model = BedrockModel(
        model_id=model_id_claude3_7,
        temperature=model_temperature,
        max_tokens=MAX_TOKENS_BUSINESS_CASE
    )
    return Agent(model=model, system_prompt=section_prompt)

# Section prompts
EXECUTIVE_SUMMARY_PROMPT = """
Generate a comprehensive Executive Summary for the AWS migration business case.

**Input**: You will receive analysis from multiple agents covering current state, costs, strategy, and migration plan.

**Generate**:
1. Project Overview (use EXACT customer name and project details from PROJECT CONTEXT)
2. Current State Highlights with ACTUAL NUMBERS (e.g., "2,027 VMs, 7,581 vCPUs, 40,189 GB RAM")
3. Recommended Approach (based on ACTUAL migration strategy analysis)
4. Key Financial Metrics with ACTUAL VALUES - ensure these match the Cost Analysis section exactly:
   - On-Premises 3-Year TCO: $X (explain calculation basis)
   - AWS 3-Year TCO with NURI: $Y
   - Total Savings: $Z
   - Break-even: Month X
5. Expected Benefits (based on ACTUAL findings)
6. Critical Success Factors
7. Timeline Overview (use ACTUAL timeline from migration plan)

**Format**: Markdown, 400-500 words MAX, include key metrics table with ACTUAL numbers
**Tone**: Executive-level, strategic, business-focused
**CRITICAL**: 
- Stay under 500 words. Complete the section fully within this limit.
- Use ACTUAL NUMBERS from the analysis - NO placeholders
- Ensure financial metrics are CONSISTENT with Cost Analysis section
- Extract real values from the provided analysis text
- Reference the EXACT customer name from project context
"""

CURRENT_STATE_PROMPT = """
Generate a concise Current State Analysis section.

**Input**: Analysis from current_state_analysis, IT inventory, RVTools, ATX, and MRA agents.

**Generate** (very concise):
1. IT Infrastructure Overview with ACTUAL NUMBERS (e.g., "2,027 VMs, 7,581 vCPUs, 40,189 GB RAM, 376.3 TB storage")
2. Key Challenges (from ACTUAL analysis findings)
3. Technical Debt (from ACTUAL assessment data)
4. Organizational Readiness (from ACTUAL MRA findings)

**Format**: Markdown, 400-500 words MAX, include 1 summary table with ACTUAL numbers
**Tone**: Technical but accessible, data-driven
**CRITICAL**: 
- Stay under 500 words. Complete the section fully within this limit.
- Use ACTUAL NUMBERS from the analysis - NO placeholders like [total VM count] or [X VMs]
- Extract real values from the provided analysis text (look for numbers like "2,027 VMs" or "7,581 vCPUs")
- NO generic or placeholder data
"""

MIGRATION_STRATEGY_PROMPT = """
Generate a concise Migration Strategy section.

**Input**: Analysis from agent_migration_strategy covering 6Rs recommendations.

**Generate** (very concise):
1. Recommended Approach (1 paragraph)
2. 6Rs Distribution (well-formatted table with headers)
3. Wave Planning (brief, 2-3 sentences)
4. Quick Wins (bullet points, 3-5 items)

**Format**: Markdown with proper formatting:
- Use proper table syntax with alignment
- Clear section headers (###)
- Bullet points with consistent formatting
- 400-500 words MAX

**Tone**: Strategic, practical, actionable
**CRITICAL**: Stay under 500 words. Use proper markdown formatting for tables and lists.
"""

COST_ANALYSIS_PROMPT = """
Generate a concise Cost Analysis and TCO section.

**Input**: Analysis from agent_aws_cost_arr covering AWS costs and TCO.

**Generate** (very concise):
1. On-Premises TCO Calculation Methodology (1 paragraph explaining how on-prem costs were calculated: hardware depreciation, data center facilities, power/cooling, IT staff salaries, software licenses, maintenance)
2. Current On-Premises vs AWS Costs Comparison (table with Year 1, 2, 3)
3. 18-Month Migration Cost Ramp (table showing gradual AWS cost increase as workloads migrate, and on-prem cost decrease)
4. 3-Year TCO using 3-Year No Upfront RI pricing (summary)
5. Cost Optimization opportunities (bullet points)
6. Break-Even Analysis (1 paragraph)

**CRITICAL REQUIREMENTS FOR DETERMINISTIC CALCULATIONS**:
- Use "3-Year No Upfront RI" or "3-Year NURI" (NURI = No Upfront Reserved Instance)
- Use the EXACT cost calculations from the cost analysis provided - DO NOT recalculate
- Ensure ALL cost figures are CONSISTENT throughout the section (don't show $6.2M in one place and $516K in another)
- If cost analysis shows "Year 1 AWS: $X", use that EXACT figure - don't round or estimate
- On-premises costs should be HIGHER than AWS costs
- Show 18-month migration ramp: Month 1-6, 7-12, 13-18 with gradual AWS increase and on-prem decrease
- Use actual VM counts and specs from the analysis (e.g., 2,027 VMs)
- Include cost breakdown by service (Compute, Storage, Database, Networking)
- Show calculation basis: "Based on 2,027 VMs with average cost of $X per VM"

**Format**: Markdown with proper formatting:
- Use proper table syntax with alignment (| Column | Column |)
- Clear section headers (###)
- Well-formatted tables with borders
- 500-600 words MAX

**Tone**: Financial, analytical, data-driven showing AWS cost advantage
**CRITICAL**: Stay under 600 words. Ensure cost consistency and proper table formatting.
"""

MIGRATION_ROADMAP_PROMPT = """
Generate a concise Migration Roadmap section.

**Input**: Analysis from agent_migration_plan covering MAP methodology.

**Generate** (very concise):
1. Phased Approach (table with phases)
2. Timeline (table)
3. Key Milestones (bullet points)
4. Success Criteria (brief)

**Format**: Markdown, 400-500 words MAX, include timeline table
**Tone**: Practical, detailed, project-focused
**CRITICAL**: Stay under 500 words. Complete the section fully within this limit.
"""

BENEFITS_RISKS_PROMPT = """
Generate a concise Benefits and Risks section.

**Input**: All previous agent analyses.

**Generate** (very concise):
1. Key Benefits (bullet points, 5-7 items)
2. Main Risks (bullet points, 5-7 items)
3. Mitigation Strategies (bullet points, 3-5 items)

**Format**: Markdown with proper formatting:
- Use clear section headers (###)
- Consistent bullet point formatting
- Optional: summary table at the end
- 300-400 words MAX

**Tone**: Balanced, realistic, comprehensive
**CRITICAL**: Stay under 400 words. Use proper markdown formatting.
"""

RECOMMENDATIONS_PROMPT = """
Generate a concise Recommendations and Next Steps section.

**Input**: All previous analyses and recommendations.

**Generate** (very concise):
1. Top 3 Recommendations (based on ACTUAL analysis provided)
2. Immediate Actions (bullet points - do NOT recommend assessments that were already completed)
3. 90-Day Plan (table with specific FUTURE dates)

**CRITICAL REQUIREMENTS**:
- Do NOT recommend conducting MRA if MRA analysis was already provided
- Do NOT recommend RVTools assessment if RVTools data was already analyzed
- Focus on NEXT steps, not repeating assessments already done
- Use FUTURE dates starting from TODAY (November 25, 2025):
  * Week 1-4: November 25 - December 22, 2025
  * Week 5-8: December 23, 2025 - January 19, 2026
  * Week 9-12: January 20 - February 16, 2026
- Format dates as "Dec 2025" or "Jan 2026" for readability
- NO past dates (2023-2024)

**Format**: Markdown, 300-400 words MAX, include action items table with FUTURE dates
**Tone**: Actionable, clear, prioritized, forward-looking
**CRITICAL**: Stay under 400 words. Use dates starting from November 2025.
"""

def generate_multi_stage_business_case(agent_results, project_context):
    """
    Generate business case in multiple stages for maximum quality
    
    Args:
        agent_results: Dictionary of results from all agents
        project_context: Project information and context
    
    Returns:
        Complete business case document
    """
    print("="*80)
    print("MULTI-STAGE BUSINESS CASE GENERATION")
    print("="*80)
    
    sections = {}
    
    # Prepare context for all sections
    # Extract actual results from NodeResult objects
    def get_result_text(node_id):
        if node_id in agent_results:
            result = agent_results[node_id].result
            if result:
                result_text = str(result)
                # Extract key metrics from the beginning (usually has summary)
                # Take first 8000 chars to ensure we capture the important numbers
                return result_text[:8000]
        return 'N/A'
    
    # Build comprehensive context with actual analysis results
    context = f"""
{project_context}

**ANALYSIS RESULTS FROM PREVIOUS AGENTS:**

### Current State Analysis:
{get_result_text('current_state_analysis')}

### Cost Analysis:
{get_result_text('agent_aws_cost_arr')}

### Migration Strategy:
{get_result_text('agent_migration_strategy')}

### Migration Plan:
{get_result_text('agent_migration_plan')}

**CRITICAL INSTRUCTIONS:**
- Use ONLY the ACTUAL NUMBERS and data from the analysis results above
- Extract and use REAL values like "2,027 VMs" or "$1.8M" - NOT placeholders like [total VM count] or [$X]
- Look for specific metrics in the analysis text and use those exact numbers
- Do NOT make up generic examples or use placeholder data
- Ensure all recommendations align with the project context and actual findings
"""
    
    # Generate each section
    section_configs = [
        ('executive_summary', EXECUTIVE_SUMMARY_PROMPT, 'Executive Summary'),
        ('current_state', CURRENT_STATE_PROMPT, 'Current State Analysis'),
        ('migration_strategy', MIGRATION_STRATEGY_PROMPT, 'Migration Strategy'),
        ('cost_analysis', COST_ANALYSIS_PROMPT, 'Cost Analysis and TCO'),
        ('migration_roadmap', MIGRATION_ROADMAP_PROMPT, 'Migration Roadmap'),
        ('benefits_risks', BENEFITS_RISKS_PROMPT, 'Benefits and Risks'),
        ('recommendations', RECOMMENDATIONS_PROMPT, 'Recommendations and Next Steps')
    ]
    
    for section_key, prompt, section_name in section_configs:
        print(f"\nGenerating: {section_name}...")
        try:
            agent = create_section_agent(prompt)
            
            # Create task with context and agent results
            task = f"{context}\n\nGenerate the {section_name} section based on the available analysis."
            
            result = agent(task)
            
            # Extract text content from the result
            # result.message is a dict with 'role' and 'content' keys
            # content is a list of dicts with 'text' key
            if hasattr(result, 'message') and isinstance(result.message, dict):
                content_list = result.message.get('content', [])
                if content_list and isinstance(content_list, list):
                    content = content_list[0].get('text', '') if content_list else ''
                else:
                    content = str(result.message)
            else:
                content = str(result.message) if result.message else ""
            
            # Check if content was truncated
            if content and ("[Continued in next part...]" in content or content.endswith("...")):
                print(f"⚠️  {section_name} may be truncated - consider reducing detail or increasing max_tokens")
            
            sections[section_key] = content
            print(f"✓ {section_name} generated ({len(content)} chars)")
            
        except Exception as e:
            print(f"✗ Error generating {section_name}: {str(e)}")
            sections[section_key] = f"# {section_name}\n\n*Section generation failed: {str(e)}*"
    
    # Combine all sections
    business_case = combine_sections(sections, project_context)
    
    return business_case

def combine_sections(sections, project_context):
    """Combine all sections into final business case document"""
    
    # Extract project info
    project_info = {}
    for line in project_context.split('\n'):
        if 'Project Name:' in line:
            project_info['name'] = line.split(':', 1)[1].strip()
        elif 'Customer Name:' in line:
            project_info['customer'] = line.split(':', 1)[1].strip()
        elif 'Target AWS Region:' in line:
            project_info['region'] = line.split(':', 1)[1].strip()
    
    # Build final document
    document = f"""# AWS Migration Business Case
## {project_info.get('customer', 'Customer')} - {project_info.get('name', 'Migration Project')}

**Target Region:** {project_info.get('region', 'N/A')}  
**Generated:** {os.popen('date').read().strip()}

---

"""
    
    # Add table of contents (plain text, no links)
    document += """## Table of Contents

1. Executive Summary
2. Current State Analysis
3. Migration Strategy
4. Cost Analysis and TCO
5. Migration Roadmap
6. Benefits and Risks
7. Recommendations and Next Steps

---

"""
    
    # Add each section
    section_order = [
        ('executive_summary', 'Executive Summary'),
        ('current_state', 'Current State Analysis'),
        ('migration_strategy', 'Migration Strategy'),
        ('cost_analysis', 'Cost Analysis and TCO'),
        ('migration_roadmap', 'Migration Roadmap'),
        ('benefits_risks', 'Benefits and Risks'),
        ('recommendations', 'Recommendations and Next Steps')
    ]
    
    for section_key, section_title in section_order:
        content = sections.get(section_key, f'*{section_title} not available*')
        document += f"\n## {section_title}\n\n{content}\n\n---\n"
    
    # Add footer
    document += f"""
## Document Information

**Generated by:** AWS Migration Business Case Generator  
**Generation Method:** Multi-Stage AI Analysis  
**Model:** {model_id_claude3_7}  
**Date:** {os.popen('date').read().strip()}

---

*This business case was generated using AI-powered analysis of your infrastructure data, assessment reports, and migration readiness evaluation. All recommendations should be validated with AWS solutions architects and your technical teams.*
"""
    
    return document

if __name__ == "__main__":
    print("Multi-stage business case generator module loaded")
    print(f"Using model: {model_id_claude3_7}")
    print(f"Max tokens per section: {MAX_TOKENS_BUSINESS_CASE}")
