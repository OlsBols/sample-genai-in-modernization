"""
Multi-stage business case generator
Generates business case in sections to maximize quality and detail
"""
import os
from strands import Agent
from strands.models import BedrockModel
from config import (
    model_id_claude3_7, 
    model_temperature, 
    MAX_TOKENS_BUSINESS_CASE, 
    output_folder_dir_path,
    TCO_COMPARISON_CONFIG
)
from appendix_content import get_appendix

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

**CRITICAL - TCO PRESENTATION RULE**:
- ONLY show cost savings metrics if AWS demonstrates lower TCO than on-premises
- If AWS costs are EQUAL or HIGHER, focus on business value and strategic benefits instead
- Do NOT show negative savings or unfavorable cost comparisons

**CRITICAL - AVOID REPETITION**:
- Keep this section HIGH-LEVEL only - detailed numbers will be in later sections
- Do NOT repeat detailed wave structures, timelines, or cost breakdowns
- Focus on KEY takeaways and strategic overview only

**Generate**:
1. Project Overview (use EXACT customer name and project details from PROJECT CONTEXT)
2. Current State Highlights - Use EXACT VM counts from analysis (e.g., "51 virtual machines" not "approximately 50")
3. Recommended Approach - STRATEGIC OVERVIEW (e.g., "phased approach over 18 months" without wave details)
4. Key Financial Metrics - SUMMARY ONLY:
   **CRITICAL - EXTRACT FROM COST ANALYSIS**:
   - Search the "Cost Analysis" section in the input for these EXACT values:
   - Total Monthly AWS Cost: Find "Total AWS Cost" or "monthly_total" in Cost Analysis
   - Total Annual Recurring Revenue (ARR): Find "total_arr" or "Annual Cost" in Cost Analysis
   - 3-Year AWS Investment: Calculate as (Monthly Cost × 36) or find "3-Year" in Cost Analysis
   - DO NOT use any other numbers - ONLY extract from the Cost Analysis section provided
   - If you see multiple cost numbers, use the ones from "agent_aws_cost_arr" or "Cost Analysis" section
   **CRITICAL**: Check TCO_ENABLED flag in context:
   - IF TCO_ENABLED=True AND AWS < On-Prem: Include "Break-even: Month X"
   - IF TCO_ENABLED=False OR AWS >= On-Prem: DO NOT include break-even, show business value instead
5. Expected Benefits - TOP 3-4 ONLY (detailed list will be in Benefits section)
6. Critical Success Factors - TOP 3 ONLY
7. Timeline Overview - HIGH-LEVEL (e.g., "18-month phased approach" without wave breakdown)

**Format**: Markdown, 400-500 words MAX, include key metrics table
**Tone**: Executive-level, strategic, business-focused
**CRITICAL**: 
- Use ACTUAL NUMBERS from analysis - NO placeholders or approximations
- Financial metrics MUST match Cost Analysis exactly (e.g., if Cost Analysis shows $5,941.43/month, use that exact number)
- VM counts must be exact (e.g., "51 VMs" not "approximately 50")
- NO meta-commentary - write only the content itself
"""

CURRENT_STATE_PROMPT = """
Generate a concise Current State Analysis section.

**Input**: Analysis from current_state_analysis, IT inventory, RVTools, ATX, and MRA agents.

**Generate** (very concise):
1. IT Infrastructure Overview with ACTUAL NUMBERS from the analysis (Total VMs, vCPUs, RAM, Storage)
2. Key Challenges (from ACTUAL analysis findings)
3. Technical Debt (from ACTUAL assessment data)
4. Organizational Readiness (from ACTUAL MRA findings)

**Format**: Markdown, 400-500 words MAX, include 1 summary table
**Tone**: Technical but accessible, data-driven
**CRITICAL**: Use ACTUAL numbers from analysis - NO placeholders, examples, or cached data. NO meta-commentary.
"""

MIGRATION_STRATEGY_PROMPT = """
Generate a concise Migration Strategy section.

**Input**: Analysis from agent_migration_strategy covering 7Rs recommendations.

**CRITICAL - TIMELINE REQUIREMENT**: 
- Check PROJECT CONTEXT for migration timeline (e.g., "18 months", "24 months")
- ALL phases and waves MUST fit within this EXACT timeline
- DO NOT exceed the specified duration
- Example for 18 months: Wave 1 (Months 1-6) + Wave 2 (Months 7-12) + Wave 3 (Months 13-18) = 18 months
- Example for 24 months: Wave 1 (Months 1-8) + Wave 2 (Months 9-16) + Wave 3 (Months 17-24) = 24 months

**CRITICAL - DEPRECATED SERVICES**: Ensure all AWS service recommendations are current and NOT deprecated. Reference: https://aws.amazon.com/products/lifecycle/

**Generate** (very concise):
1. Recommended Approach (1 paragraph) - mention the EXACT timeline from PROJECT CONTEXT
2. 7Rs Distribution (well-formatted table with actual numbers or percentages - NO "TBD" values. If exact numbers unavailable, use reasonable estimates based on VM analysis)
3. Wave Planning (brief, 2-3 sentences) - waves MUST fit within project timeline
4. Quick Wins (bullet points, 3-5 items)

**Format**: Markdown, 400-500 words MAX, proper tables and bullets
**Tone**: Strategic, practical, actionable
**CRITICAL**: NO meta-commentary - write only the content itself. RESPECT the project timeline.
"""

def get_cost_analysis_prompt():
    """Generate cost analysis prompt based on TCO config"""
    tco_enabled = TCO_COMPARISON_CONFIG.get('enable_tco_comparison', False)
    
    if tco_enabled:
        return """
Generate a concise Cost Analysis and TCO section.

**Input**: Analysis from agent_aws_cost_arr covering AWS costs and TCO.

**CRITICAL - DEPRECATED SERVICES**: Do NOT include any deprecated or end-of-life AWS services in cost analysis. Only include current, actively supported services. Reference: https://aws.amazon.com/products/lifecycle/

**CRITICAL - TCO VALIDATION RULE**:
- ONLY show on-premises TCO comparison if AWS demonstrates cost savings (AWS < On-Prem)
- If AWS costs are EQUAL or HIGHER than on-premises, SKIP the TCO comparison table
- Instead, focus on business value: agility, innovation, scalability, reduced technical debt
- Emphasize strategic advantages and operational benefits over pure cost comparison

**Generate** (very concise):
1. AWS Cost Summary (AWS services and projected costs with 3-Year NURI)
2. **IF AWS < On-Prem**: Include On-Premises TCO Calculation Methodology and comparison table
3. **IF AWS >= On-Prem**: Skip TCO comparison, focus on business value and strategic benefits
4. 18-Month Migration Cost Ramp (table showing gradual AWS cost increase as workloads migrate)
5. Cost Optimization opportunities (bullet points)
6. **IF AWS < On-Prem**: Break-Even Analysis (1 paragraph)
7. **IF AWS >= On-Prem**: Business Value Justification (agility, innovation, time-to-market, reduced operational complexity)

**CRITICAL REQUIREMENTS FOR DETERMINISTIC CALCULATIONS**:
- Use "3-Year No Upfront RI" or "3-Year NURI" (NURI = No Upfront Reserved Instance)
- Use the EXACT cost calculations from the cost analysis provided - DO NOT recalculate
- Ensure ALL cost figures are CONSISTENT throughout the section (don't show $6.2M in one place and $516K in another)
- If cost analysis shows "Year 1 AWS: $X", use that EXACT figure - don't round or estimate
- On-premises costs should be HIGHER than AWS costs
- Show 18-month migration ramp: Month 1-6, 7-12, 13-18 with gradual AWS increase and on-prem decrease
- Use actual VM counts and specs from the analysis
- Include cost breakdown by service (Compute, Storage, Database, Networking)
- Show calculation basis with actual numbers from the analysis

**CRITICAL - OS DISTRIBUTION COUNTS**:
- SEARCH for "PRE-COMPUTED RVTOOLS SUMMARY" in the context
- Use ONLY the Windows VMs and Linux VMs counts from that summary
- Example: If summary shows "Windows VMs: 781" and "Linux VMs: 1246", use EXACTLY those numbers
- These counts are consistent with pricing calculator (Other VMs are treated as Linux)

**Format**: Markdown with proper formatting:
- Use proper table syntax with alignment (| Column | Column |)
- Clear section headers (###)
- Well-formatted tables with borders
- 500-600 words MAX

**Tone**: Financial, analytical, data-driven showing AWS cost advantage
**CRITICAL**: Stay under 600 words. Ensure cost consistency and proper table formatting.
"""
    else:
        return """
Generate a concise Cost Analysis section (TCO COMPARISON DISABLED).

**Input**: Analysis from agent_aws_cost_arr covering AWS costs.

**CRITICAL - TCO DISABLED**: 
- DO NOT include on-premises cost calculations
- DO NOT show TCO comparison tables
- DO NOT show break-even analysis
- DO NOT mention cost savings vs on-premises
- DO NOT calculate or reference on-premises infrastructure costs
- Focus ONLY on AWS costs and business value

**CRITICAL - DEPRECATED SERVICES**: Do NOT include any deprecated or end-of-life AWS services in cost analysis. Only include current, actively supported services.

**Generate** (very concise):
1. AWS Cost Summary (AWS services and projected costs with 3-Year NURI)
   - Total Monthly AWS Cost
   - Total Annual AWS Cost (ARR)
   - Breakdown by service (Compute, Storage, Database, Networking)
   - Breakdown by instance type (ONLY if provided in cost analysis - DO NOT make up instance counts)
   - Cost per VM average
   
   **CRITICAL - INSTANCE DISTRIBUTION**:
   - ONLY include instance types explicitly mentioned in the cost analysis
   - Instance counts MUST sum to the total VM count (e.g., if 51 VMs total, all instance counts must sum to 51)
   - DO NOT list made-up instance types or counts
   - If instance distribution not provided, SKIP this subsection
   
   **CRITICAL - OS DISTRIBUTION**:
   - SEARCH for "PRE-COMPUTED RVTOOLS SUMMARY" in the context
   - Use ONLY the Windows VMs and Linux VMs counts from that summary
   - Windows + Linux counts MUST equal total migrating VMs from the summary
   - Example: If summary shows "Windows VMs: 781" and "Linux VMs: 1246", use EXACTLY those numbers
   - These counts are consistent with pricing calculator (Other VMs are treated as Linux)
2. 18-Month Migration Cost Ramp (table showing ONLY AWS costs ramping up as migration progresses)
   - Month 1-6: X% of workloads, $Y AWS cost
   - Month 7-12: X% of workloads, $Y AWS cost
   - Month 13-18: 100% of workloads, $Y AWS cost
   - DO NOT show on-premises cost reduction
3. Cost Optimization Opportunities (bullet points, 5-7 items)
   - Reserved Instances and Savings Plans
   - Right-sizing recommendations
   - Storage optimization
   - Spot instances for suitable workloads
4. Business Value Justification (focus on strategic benefits, NOT cost savings)
   - Agility and faster time-to-market
   - Innovation enablement (AI/ML, analytics, modern services)
   - Reduced technical debt and operational complexity
   - Global scalability and reliability
   - Security and compliance improvements

**CRITICAL REQUIREMENTS**:
- Use the EXACT cost calculations from the cost analysis provided - DO NOT recalculate
- Ensure ALL cost figures are CONSISTENT throughout the section
- Use actual VM counts and specs from the analysis
- Include cost breakdown by service (Compute, Storage, Database, Networking)
- Show calculation basis: "Based on X VMs with average cost of $Y per VM"
- DO NOT mention on-premises costs anywhere

**Format**: Markdown, 400-500 words MAX, proper tables
**Tone**: Financial, analytical, business-value focused
**CRITICAL**: NO on-premises costs. Ensure cost consistency. NO meta-commentary.
"""

COST_ANALYSIS_PROMPT = get_cost_analysis_prompt()

MIGRATION_ROADMAP_PROMPT = """
Generate a concise Migration Roadmap section.

**Input**: Analysis from agent_migration_plan covering MAP methodology.

**CRITICAL - TIMELINE REQUIREMENT**: 
- Check PROJECT CONTEXT for migration timeline (e.g., "18 months", "24 months")
- ALL phases MUST fit within this EXACT timeline
- DO NOT exceed the specified duration
- Calculate phase durations to sum to the project timeline
- Example for 18 months: Phase 1 (Months 1-6) + Phase 2 (Months 7-12) + Phase 3 (Months 13-18) = 18 months
- Example for 24 months: Phase 1 (Months 1-8) + Phase 2 (Months 9-16) + Phase 3 (Months 17-24) = 24 months

**TABLE FORMATTING**: When creating the Phased Approach table, use wider column widths for Phase and Duration columns (minimum 15-20 characters) for better readability.

**CRITICAL - TIMEFRAME FORMAT**:
- Use RELATIVE timeframes only (Week 1-2, Month 1-3, Quarter 1, etc.)
- DO NOT use specific calendar dates or months (e.g., "January 2026" or "Q1 2025")
- Use generic timeframes: "Month 1-3", "Month 4-6", "Month 7-12", etc.
- For phases: "Phase 1 (Months 1-3)", "Phase 2 (Months 4-9)", etc.
- ENSURE phase durations sum to the project timeline from PROJECT CONTEXT

**Generate** (very concise):
1. Phased Approach (table with phases and relative durations that sum to project timeline)
2. Timeline (table with relative timeframes - Month 1, Month 2, etc.)
3. Key Milestones (bullet points with relative timing)
4. Success Criteria (brief)

**Example Timeline Format for 18-month project**:
| Phase | Duration | Key Activities |
|-------|----------|----------------|
| Assess | Month 1-2 | Discovery, assessment |
| Mobilize | Month 3-5 | Landing zone, pilot planning |
| Migrate | Month 6-18 | Wave-based migration |

**Format**: Markdown, 400-500 words MAX, timeline table with relative timeframes
**Tone**: Practical, detailed, project-focused
**CRITICAL**: Use relative timeframes only (no specific dates). NO meta-commentary.
"""

BENEFITS_RISKS_PROMPT = """
Generate a concise Benefits and Risks section.

**Input**: All previous agent analyses.

**IMPORTANT**: Emphasize both financial AND strategic/operational benefits. Even if cost savings are minimal, highlight:
- Agility and faster time-to-market
- Innovation enablement (AI/ML, analytics, modern services)
- Reduced technical debt and operational complexity
- Global scalability and reliability
- Security and compliance improvements

**Generate** (very concise):
1. Key Benefits (bullet points, 5-7 items - include both cost and strategic benefits)
2. Main Risks (bullet points, 5-7 items)
3. Mitigation Strategies (bullet points, 3-5 items)

**Format**: Markdown, 300-400 words MAX, clear headers and bullets
**Tone**: Balanced, realistic, comprehensive
**CRITICAL**: NO meta-commentary - write only the content itself
"""

RECOMMENDATIONS_PROMPT = """
Generate a concise Recommendations and Next Steps section.

**Input**: All previous analyses and recommendations.

**CRITICAL - AVOID REPETITION**:
- Do NOT repeat cost savings numbers (already in Executive Summary and Cost Analysis)
- Do NOT repeat wave structures (already in Migration Roadmap)
- Do NOT repeat VM counts or infrastructure details (already in Current State)
- Focus on ACTIONABLE next steps only

**Generate** (very concise):
1. Top 3 Strategic Recommendations (NEW insights, not repeating previous sections)
2. Immediate Actions (bullet points - do NOT recommend assessments that were already completed)
3. Recommended Deep-Dive Assessments (if only basic data like RVTools was provided):
   - **AWS Migration Evaluator**: Detailed TCO analysis and right-sizing recommendations
   - **Migration Portfolio Assessment (MPA)**: Application dependency mapping and wave planning
   - **ISV Migration Tools**: Evaluate third-party solutions for enhanced migration capabilities:
     * Comprehensive cloud readiness assessments
     * Application resource management and optimization
4. 90-Day Plan (table with relative timeframes - focus on ACTIONS not metrics)

**CRITICAL REQUIREMENTS**:
- Do NOT recommend conducting MRA if MRA analysis was already provided
- Do NOT recommend RVTools assessment if RVTools data was already analyzed
- Do NOT recommend ATX assessment if ATX data was already analyzed
- If only RVTools data was provided, RECOMMEND deeper assessments (Migration Evaluator, MPA, Partner tools)
- Focus on NEXT steps, not repeating assessments already done
- Use RELATIVE timeframes (NOT specific dates):
  * Week 1-2, Week 3-4, Week 5-6, etc.
  * Month 1, Month 2, Month 3, etc.
  * Quarter 1, Quarter 2, etc.
- DO NOT use specific calendar dates (e.g., "November 25" or "Dec 2025")
- Use generic timeframes that work regardless of when the document is generated

**Example Format**:
| Timeframe | Activity | Owner |
|-----------|----------|-------|
| Week 1-2  | Finalize landing zone design | Cloud Architecture Team |
| Week 3-4  | Complete pilot wave planning | Migration Team |
| Month 2   | Execute pilot migration | Migration Team |
| Month 3   | Review and optimize | Operations Team |

**Format**: Markdown, 400-500 words MAX, action items table with relative timeframes
**Tone**: Actionable, clear, prioritized, forward-looking
**CRITICAL**: Use relative timeframes only (Week 1-2, Month 1, etc.). NO meta-commentary.
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
    
    # Determine which assessments were completed
    completed_assessments = []
    if 'agent_rv_tool_analysis' in agent_results and agent_results['agent_rv_tool_analysis'].result:
        completed_assessments.append('RVTools VMware Assessment')
    if 'agent_atx_analysis' in agent_results and agent_results['agent_atx_analysis'].result:
        completed_assessments.append('AWS Transform (ATX) Assessment')
    if 'agent_mra_analysis' in agent_results and agent_results['agent_mra_analysis'].result:
        completed_assessments.append('Migration Readiness Assessment (MRA)')
    if 'agent_it_analysis' in agent_results and agent_results['agent_it_analysis'].result:
        completed_assessments.append('IT Infrastructure Inventory Analysis')
    
    assessments_note = f"\n**ASSESSMENTS ALREADY COMPLETED**: {', '.join(completed_assessments)}\n**DO NOT recommend these assessments again.**" if completed_assessments else ""
    
    # Get TCO configuration
    tco_enabled = TCO_COMPARISON_CONFIG.get('enable_tco_comparison', False)
    tco_note = f"\n**TCO_ENABLED**: {tco_enabled}\n**CRITICAL**: {'Include on-premises TCO comparison if AWS < On-Prem' if tco_enabled else 'DO NOT include on-premises costs, TCO comparison, or break-even analysis'}"
    
    # Build comprehensive context with actual analysis results
    context = f"""
{project_context}
{tco_note}

**ANALYSIS RESULTS FROM PREVIOUS AGENTS:**

### Current State Analysis:
{get_result_text('current_state_analysis')}

### Cost Analysis:
{get_result_text('agent_aws_cost_arr')}

### Migration Strategy:
{get_result_text('agent_migration_strategy')}

### Migration Plan:
{get_result_text('agent_migration_plan')}
{assessments_note}

**CRITICAL INSTRUCTIONS:**
- Use ONLY the ACTUAL NUMBERS and data from the analysis results above
- Extract and use REAL values from the analysis - NOT placeholders like [total VM count] or [$X]
- Look for specific metrics in the analysis text and use those exact numbers
- Do NOT make up generic examples or use placeholder data
- IGNORE any example numbers you may have seen in prompts or previous responses
- Ensure all recommendations align with the project context and actual findings
- RESPECT the TCO_ENABLED flag above - if False, DO NOT include any on-premises cost calculations
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
8. Appendix: AWS Partner Programs for Migration and Modernization

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
    
    # Add appendix with AWS partner programs
    document += f"\n{get_appendix()}\n\n"
    
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
    
    # Clean up markdown code fences
    document = cleanup_markdown_fences(document)
    
    return document


def cleanup_markdown_fences(text):
    """
    Remove markdown code fence markers (```markdown, ```, etc.) from the text
    These sometimes appear in LLM output and should be removed for cleaner presentation
    """
    import re
    
    # Remove ```markdown at the start of code blocks
    text = re.sub(r'```markdown\s*\n', '', text)
    
    # Remove ``` at the end of code blocks (but preserve code blocks that are intentional)
    # Only remove standalone ``` on its own line
    text = re.sub(r'\n```\s*\n', '\n\n', text)
    
    # Remove any remaining ``` that appear at start or end of lines
    text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
    
    return text

if __name__ == "__main__":
    print("Multi-stage business case generator module loaded")
    print(f"Using model: {model_id_claude3_7}")
    print(f"Max tokens per section: {MAX_TOKENS_BUSINESS_CASE}")
