import os
from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent import GraphBuilder
from strands.multiagent.graph import GraphState
from strands.multiagent.base import Status

from config import model_id_claude3_7, model_temperature, output_folder_dir_path, ENABLE_MULTI_STAGE, MAX_TOKENS_BUSINESS_CASE
from inventory_analysis import it_analysis
from rv_tool_analysis import rv_tool_analysis
from atx_analysis import read_excel_file, read_pdf_file, read_pptx_file
from mra_analysis import read_docx_file, read_markdown_file, read_pdf_file
from migration_strategy import read_migration_strategy_framework, read_portfolio_assessment
from migration_plan import read_migration_plan_framework
from pricing_tools import calculate_exact_aws_arr, compare_pricing_models, get_vm_cost_breakdown
from project_context import get_project_context, get_project_info_dict
from setup_logging import setup_logging
from multi_stage_business_case import generate_multi_stage_business_case
from appendix_content import get_appendix
from prompt_library.agent_prompts import (
    system_message_aws_arr_cost, 
    system_message_rv_tool_analysis, 
    system_message_it_analysis,
    system_message_aws_business_case,
    system_message_current_state_analysis,
    system_message_atx_analysis,
    system_message_mra_analysis,
    system_message_migration_strategy,
    system_message_migration_plan )

# Setup logging
logger, log_file = setup_logging()
logger.info("="*80)
logger.info("AWS BUSINESS CASE GENERATOR - STARTING")
logger.info("="*80)

# Create a BedrockModel with max_tokens limit to prevent overflow
# Add slight temperature variation to break caching
import random
temp_variation = model_temperature + (random.random() * 0.02 - 0.01)  # ±0.01 variation
bedrock_model = BedrockModel(
    model_id=model_id_claude3_7,
    temperature=temp_variation,  # Slight variation to break cache
    max_tokens=MAX_TOKENS_BUSINESS_CASE  # Use configured max tokens (8192)
)

# Create model for cost calculations with lower temperature for consistency
# Use reduced max_tokens (3000) to force concise output and prevent MaxTokensReachedException
bedrock_model_cost = BedrockModel(
    model_id=model_id_claude3_7,
    temperature=0.1,  # Lower temperature for more deterministic cost calculations
    max_tokens=3000  # Reduced from 4096 to force concise, focused output
)

# Create separate model for business case with configured max tokens
bedrock_model_business_case = BedrockModel(
    model_id=model_id_claude3_7,
    temperature=model_temperature,
    max_tokens=MAX_TOKENS_BUSINESS_CASE  # 4096 for Claude 3, 8192 for Claude 3.5
)

agent_it_analysis = Agent(model=bedrock_model,system_prompt= system_message_it_analysis,tools=[it_analysis])
agent_rv_tool_analysis = Agent(model=bedrock_model,system_prompt= system_message_rv_tool_analysis,tools=[rv_tool_analysis])
agent_atx_analysis = Agent(model=bedrock_model,system_prompt= system_message_atx_analysis,tools=[read_excel_file, read_pdf_file, read_pptx_file])
agent_mra_analysis = Agent(model=bedrock_model,system_prompt= system_message_mra_analysis,tools=[read_docx_file, read_markdown_file, read_pdf_file])
agent_migration_strategy = Agent(model=bedrock_model,system_prompt= system_message_migration_strategy,tools=[read_migration_strategy_framework, read_portfolio_assessment])
agent_migration_plan = Agent(model=bedrock_model,system_prompt= system_message_migration_plan,tools=[read_migration_plan_framework])
agent_aws_cost_arr = Agent(model=bedrock_model_cost,system_prompt= system_message_aws_arr_cost,tools=[it_analysis,rv_tool_analysis,calculate_exact_aws_arr,compare_pricing_models,get_vm_cost_breakdown])  # Use lower temperature for deterministic costs with pricing tools
current_state_analysis = Agent(model=bedrock_model,system_prompt= system_message_current_state_analysis,tools=[it_analysis,rv_tool_analysis])
aws_business_case = Agent(model=bedrock_model_business_case,system_prompt= system_message_aws_business_case)  # Use higher token limit


# Define conditional edge functions using the factory pattern
def all_dependencies_complete(required_nodes: list[str]):
    """Factory function to create AND condition for multiple dependencies."""
    def check_all_complete(state: GraphState) -> bool:
        return all(
            node_id in state.results and state.results[node_id].status == Status.COMPLETED
            for node_id in required_nodes
        )
    return check_all_complete

# Build the graph
builder = GraphBuilder()

# Add all nodes
builder.add_node(agent_it_analysis, "agent_it_analysis")
builder.add_node(agent_rv_tool_analysis, "agent_rv_tool_analysis")
builder.add_node(agent_atx_analysis, "agent_atx_analysis")
builder.add_node(agent_mra_analysis, "agent_mra_analysis")
builder.add_node(current_state_analysis, "current_state_analysis")
builder.add_node(agent_aws_cost_arr, "agent_aws_cost_arr")
builder.add_node(agent_migration_strategy, "agent_migration_strategy")
builder.add_node(agent_migration_plan, "agent_migration_plan")

# Only add aws_business_case node if NOT using multi-stage generation
if not ENABLE_MULTI_STAGE:
    builder.add_node(aws_business_case, "aws_business_case")

# (1) current_state_analysis executes ONLY when ALL four analysis agents complete
condition_for_current_state = all_dependencies_complete(["agent_it_analysis", "agent_rv_tool_analysis", "agent_atx_analysis", "agent_mra_analysis"])
builder.add_edge("agent_it_analysis", "current_state_analysis", condition=condition_for_current_state)
builder.add_edge("agent_rv_tool_analysis", "current_state_analysis", condition=condition_for_current_state)
builder.add_edge("agent_atx_analysis", "current_state_analysis", condition=condition_for_current_state)
builder.add_edge("agent_mra_analysis", "current_state_analysis", condition=condition_for_current_state)

# (2) agent_aws_cost_arr executes ONLY when ALL four analysis agents complete
condition_for_cost_arr = all_dependencies_complete(["agent_it_analysis", "agent_rv_tool_analysis", "agent_atx_analysis", "agent_mra_analysis"])
builder.add_edge("agent_it_analysis", "agent_aws_cost_arr", condition=condition_for_cost_arr)
builder.add_edge("agent_rv_tool_analysis", "agent_aws_cost_arr", condition=condition_for_cost_arr)
builder.add_edge("agent_atx_analysis", "agent_aws_cost_arr", condition=condition_for_cost_arr)
builder.add_edge("agent_mra_analysis", "agent_aws_cost_arr", condition=condition_for_cost_arr)

# (3) agent_migration_strategy executes ONLY when ALL four analysis agents complete
condition_for_migration_strategy = all_dependencies_complete(["agent_it_analysis", "agent_rv_tool_analysis", "agent_atx_analysis", "agent_mra_analysis"])
builder.add_edge("agent_it_analysis", "agent_migration_strategy", condition=condition_for_migration_strategy)
builder.add_edge("agent_rv_tool_analysis", "agent_migration_strategy", condition=condition_for_migration_strategy)
builder.add_edge("agent_atx_analysis", "agent_migration_strategy", condition=condition_for_migration_strategy)
builder.add_edge("agent_mra_analysis", "agent_migration_strategy", condition=condition_for_migration_strategy)

# (4) agent_migration_plan executes ONLY when ALL three intermediate agents complete
condition_for_migration_plan = all_dependencies_complete(["current_state_analysis", "agent_aws_cost_arr", "agent_migration_strategy"])
builder.add_edge("current_state_analysis", "agent_migration_plan", condition=condition_for_migration_plan)
builder.add_edge("agent_aws_cost_arr", "agent_migration_plan", condition=condition_for_migration_plan)
builder.add_edge("agent_migration_strategy", "agent_migration_plan", condition=condition_for_migration_plan)

# (5) aws_business_case executes ONLY when ALL four intermediate agents complete
# Skip if multi-stage is enabled (we'll generate business case separately)
if not ENABLE_MULTI_STAGE:
    condition_for_business_case = all_dependencies_complete(["current_state_analysis", "agent_aws_cost_arr", "agent_migration_strategy", "agent_migration_plan"])
    builder.add_edge("current_state_analysis", "aws_business_case", condition=condition_for_business_case)
    builder.add_edge("agent_aws_cost_arr", "aws_business_case", condition=condition_for_business_case)
    builder.add_edge("agent_migration_strategy", "aws_business_case", condition=condition_for_business_case)
    builder.add_edge("agent_migration_plan", "aws_business_case", condition=condition_for_business_case)


# Set entry points (the nodes that start first - they run in parallel)
builder.set_entry_point("agent_it_analysis")
builder.set_entry_point("agent_rv_tool_analysis")
builder.set_entry_point("agent_atx_analysis")
builder.set_entry_point("agent_mra_analysis")

logger.info(f"Multi-stage generation: {'ENABLED' if ENABLE_MULTI_STAGE else 'DISABLED'}")
if ENABLE_MULTI_STAGE:
    logger.info("Single-stage aws_business_case agent will be skipped")

builder.set_execution_timeout(1800)  # 30 minute timeout for entire workflow
builder.set_node_timeout(600)  # 10 minute timeout per node

# Build the graph
# Note: When ENABLE_MULTI_STAGE=True, the aws_business_case agent result is not used
# Multi-stage generation happens after the graph completes
graph = builder.build()

# Get project context
project_context = get_project_context()
project_info = get_project_info_dict()

# Get uploaded filenames from project_info if available, otherwise use patterns
uploaded_files = project_info.get('uploadedFiles', {})
case_id = project_info.get('caseId', '')

# Use case-specific paths if case ID exists
if case_id:
    input_base = f"input/{case_id}/"
    logger.info(f"Using case-specific input directory: {input_base}")
else:
    input_base = "input/"
    logger.info("Using base input directory (no case ID)")

input_files1 = f"{input_base}{uploaded_files.get('itInventory', 'it-infrastructure-inventory.xlsx')}" if 'itInventory' in uploaded_files else f"{input_base}it-infrastructure-inventory.xlsx"
input_files2 = f"{input_base}{uploaded_files['rvTool'][0]}" if 'rvTool' in uploaded_files and uploaded_files['rvTool'] else f"{input_base}rvtool*.xlsx"
input_files3_excel = f"{input_base}{uploaded_files.get('atxExcel', 'atx_analysis.xlsx')}" if 'atxExcel' in uploaded_files else f"{input_base}atx_analysis.xlsx"
input_files3_pdf = f"{input_base}atx_report.pdf"
input_files3_pptx = f"{input_base}atx_business_case.pptx"
input_files4_mra = f"{input_base}aws-customer-migration-readiness-assessment.md"
input_files5_strategy = f"{input_base}aws-migration-strategy-6rs-framework.md"

logger.info(f"RVTools path: {input_files2}")

# Pre-read MRA file if it exists (Option 1: Direct Python call)
mra_content = None
mra_status = "Not Available"
try:
    from mra_analysis import find_mra_file, read_pdf_file, read_docx_file, read_markdown_file
    
    mra_file = find_mra_file()
    if mra_file:
        logger.info(f"MRA file found: {mra_file}")
        
        # Read the file based on extension
        if mra_file.endswith('.pdf'):
            mra_content = read_pdf_file(mra_file)
        elif mra_file.endswith('.docx') or mra_file.endswith('.doc'):
            mra_content = read_docx_file(mra_file)
        elif mra_file.endswith('.md'):
            mra_content = read_markdown_file(mra_file)
        
        if mra_content and len(mra_content) > 1000:
            mra_status = "Available"
            logger.info(f"MRA content loaded: {len(mra_content)} characters")
        else:
            logger.warning(f"MRA file found but content is minimal: {len(mra_content) if mra_content else 0} characters")
    else:
        logger.info("No MRA file found in input directory")
except Exception as e:
    logger.error(f"Error reading MRA file: {e}")
    import traceback
    logger.error(traceback.format_exc())

import time
import uuid
import random
import pandas as pd
generation_id = int(time.time())
cache_buster = str(uuid.uuid4())[:8]  # Short unique ID
session_id = str(uuid.uuid4())  # Full UUID for session uniqueness
random_seed = random.randint(10000, 99999)  # Random number to break cache

# PRE-COMPUTE RVTOOLS SUMMARY IN PYTHON (bypasses LLM extraction and caching issues)
def get_rvtools_summary_precomputed(rvtools_path):
    """Pre-compute RVTools summary to avoid LLM extraction issues"""
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(rvtools_path)
        logger.info(f"Pre-computing RVTools summary from: {abs_path}")
        
        # Check if file exists
        if not os.path.exists(abs_path):
            logger.error(f"File does not exist: {abs_path}")
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"Directory contents: {os.listdir(os.path.dirname(abs_path)) if os.path.exists(os.path.dirname(abs_path)) else 'Directory not found'}")
            return None
        
        df = pd.read_excel(abs_path, sheet_name='vInfo')
        logger.info(f"✓ Loaded {len(df)} VMs from RVTools")
        
        # Filter to powered-on VMs only (powered-off VMs not included in migration)
        if 'Powerstate' in df.columns:
            df_powered_on = df[df['Powerstate'] == 'poweredOn']
            logger.info(f"✓ Filtered to {len(df_powered_on)} powered-on VMs")
        elif 'Power state' in df.columns:
            df_powered_on = df[df['Power state'] == 'poweredOn']
            logger.info(f"✓ Filtered to {len(df_powered_on)} powered-on VMs")
        else:
            df_powered_on = df
            logger.info("✓ No Powerstate column - using all VMs")
        
        # Calculate summary using the same logic as rv_tool_analysis
        from rv_tool_analysis import generate_vm_summary
        summary = generate_vm_summary(df_powered_on)
        
        logger.info(f"✓✓✓ PRE-COMPUTED SUMMARY SUCCESS ✓✓✓")
        logger.info(f"    Total VMs: {summary['total_vms']}")
        logger.info(f"    Total vCPUs: {summary['total_vcpus']}")
        logger.info(f"    Total RAM (GB): {summary['total_memory_gb']:.1f}")
        logger.info(f"    Total Storage (TB): {summary['total_storage_tb']:.1f}")
        logger.info(f"    Windows VMs: {summary.get('windows_vms', 0)}")
        logger.info(f"    Linux VMs: {summary.get('linux_vms', 0)}")
        return summary
    except Exception as e:
        logger.error(f"✗ Error pre-computing RVTools summary: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# Get pre-computed RVTools summary
# Use the actual RVTools file path from uploaded files or pattern
if 'rvTool' in uploaded_files and uploaded_files['rvTool']:
    rvtools_filename = uploaded_files['rvTool'][0]
else:
    rvtools_filename = "RVTools_Export.xlsx"

# Build absolute path - need to go up one level from agents/ directory
script_dir = os.path.dirname(os.path.abspath(__file__))  # agents/
project_root = os.path.dirname(script_dir)  # project root
rvtools_path = os.path.join(project_root, input_base, rvtools_filename)
logger.info(f"RVTools absolute path: {rvtools_path}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Script directory: {script_dir}")
logger.info(f"Project root: {project_root}")

rvtools_summary = get_rvtools_summary_precomputed(rvtools_path)

if rvtools_summary:
    rvtools_data_section = f"""
**═══════════════════════════════════════════════════════════════**
**PRE-COMPUTED RVTOOLS SUMMARY** (MANDATORY - Use these exact numbers)
**═══════════════════════════════════════════════════════════════**

These numbers were calculated directly from the RVTools file in Python.
DO NOT call rv_tool_analysis tool. DO NOT extract numbers from anywhere else.
USE ONLY THESE PRE-COMPUTED VALUES:

- **Total VMs for Migration**: {rvtools_summary['total_vms']}
- **Total vCPUs**: {rvtools_summary['total_vcpus']}
- **Total Memory (GB)**: {rvtools_summary['total_memory_gb']:.1f}
- **Total Storage (TB)**: {rvtools_summary['total_storage_tb']:.1f}
- **Windows VMs**: {rvtools_summary.get('windows_vms', 0)}
- **Linux VMs**: {rvtools_summary.get('linux_vms', 0)} (includes {rvtools_summary.get('other_vms', 0)} "Other" VMs treated as Linux)

**NOTE**: "Other" VMs are treated as Linux for pricing and reporting purposes.

**CRITICAL INSTRUCTIONS FOR ALL AGENTS**:
1. Use ONLY the numbers above in your analysis
2. Do NOT call rv_tool_analysis tool
3. Do NOT extract numbers from tool outputs
4. Do NOT use cached or remembered numbers
5. Copy these exact numbers into your response
6. **FOR ALL SECTIONS**: When reporting OS distribution, use EXACTLY these counts:
   - Windows VMs: {rvtools_summary.get('windows_vms', 0)}
   - Linux VMs: {rvtools_summary.get('linux_vms', 0)}
   - These counts MUST be consistent across ALL sections (Current State, Cost Analysis, etc.)

**═══════════════════════════════════════════════════════════════**
"""
    logger.info("✓ RVTools pre-computed summary added to task")
else:
    rvtools_data_section = """
**RVTools Summary**: Not available - file could not be read
"""
    logger.warning("⚠ RVTools summary could not be pre-computed")

# Build agent task with MRA content if available
# Truncate MRA to 10000 chars to prevent token overflow
mra_section = f"""
    **MRA STATUS**: {mra_status}
    
    {'**MRA CONTENT PROVIDED** - MRA file available for analysis' if mra_content else '**MRA NOT AVAILABLE** - Recommend conducting MRA as next step.'}
    
    {f'--- MRA SUMMARY (first 10000 chars) ---\\n{mra_content[:10000]}\\n--- END MRA SUMMARY ---' if mra_content else ''}
    """ if mra_content else "**MRA STATUS**: Not Available"

# Extract timeline from project description
import re
def extract_timeline_months(description):
    """Extract migration timeline in months from project description"""
    if not description:
        return None
    # Look for patterns like "18 months", "24 months", "within 18 months", "next 18 months"
    patterns = [
        r'within\s+(?:the\s+)?(?:next\s+)?(\d+)\s+months',
        r'(?:next|in)\s+(\d+)\s+months',
        r'(\d+)[-\s]month',
    ]
    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None

timeline_months = extract_timeline_months(project_info.get('projectDescription', ''))
timeline_note = f"\n**⚠️ MIGRATION TIMELINE REQUIREMENT: {timeline_months} MONTHS ⚠️**\n**ALL migration phases, waves, and timelines MUST fit within {timeline_months} months total.**\n**DO NOT exceed {timeline_months} months under any circumstances.**\n" if timeline_months else ""

logger.info(f"Extracted timeline: {timeline_months} months" if timeline_months else "No timeline found in project description")

# Cache busting: Add unique session identifier
cache_breaking_prefix = f"[SESSION:{session_id[:8]}|GEN:{generation_id}|SEED:{random_seed}] "

agent_task = f"""{cache_breaking_prefix}Create a comprehensive business case to migrate on-premises IT workload to AWS.

{project_context}
{timeline_note}

    {rvtools_data_section}
    
    **Input Data Sources:**
        1. IT Infrastructure Inventory: {input_files1}
        2. RVTool Assessment Data: {input_files2} (summary pre-computed above)
        3. AWS Transform for VMware (ATX) Assessment:
           - VMware Environment Data: {input_files3_excel}
           - Technical Assessment Report: {input_files3_pdf}
           - Business Case Presentation: {input_files3_pptx}
        4. Migration Readiness Assessment (MRA): {input_files4_mra}
        5. Migration Strategy Framework (6Rs): {input_files5_strategy}
        
    {mra_section}
        
    **CRITICAL**: Use the PRE-COMPUTED RVTOOLS SUMMARY numbers provided above.
   """

logger.info("="*80)
logger.info("STARTING AGENT WORKFLOW")
logger.info("="*80)
logger.info(f"Project: {project_info.get('projectName', 'N/A')}")
logger.info(f"Customer: {project_info.get('customerName', 'N/A')}")
logger.info(f"Region: {project_info.get('awsRegion', 'N/A')}")
logger.info(f"Description: {project_info.get('projectDescription', 'N/A')}")
logger.info("="*80)

logger.info("Executing agent graph...")
result = graph(agent_task)
logger.info("Agent graph execution completed")

logger.info("="*80)
logger.info("FINAL BUSINESS CASE GENERATION")
logger.info("="*80)

# Check if multi-stage generation is enabled
if ENABLE_MULTI_STAGE:
    logger.info("Using MULTI-STAGE generation for comprehensive business case")
    try:
        # Add timeline requirement to project context for multi-stage generation
        project_context_with_timeline = project_context
        if timeline_months:
            project_context_with_timeline = f"""{project_context}

**⚠️ CRITICAL - MIGRATION TIMELINE REQUIREMENT: {timeline_months} MONTHS ⚠️**
**ALL migration phases, waves, and timelines MUST fit within {timeline_months} months total.**
**DO NOT exceed {timeline_months} months under any circumstances.**
**Example for {timeline_months} months: Phase 1 (Months 1-{timeline_months//3}) + Phase 2 (Months {timeline_months//3+1}-{timeline_months*2//3}) + Phase 3 (Months {timeline_months*2//3+1}-{timeline_months}) = {timeline_months} months**
"""
        
        # Generate business case in multiple stages
        final_result_text = generate_multi_stage_business_case(result.results, project_context_with_timeline)
        logger.info(f"Multi-stage business case generated ({len(final_result_text)} characters)")
        
        file_path = os.path.join(output_folder_dir_path, 'aws_business_case.md')
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(final_result_text)
        logger.info(f"Business case saved to: {file_path}")
        
    except Exception as e:
        logger.error(f"Multi-stage generation failed: {str(e)}")
        logger.info("Falling back to single-stage generation")
        
        if "aws_business_case" in result.results:
            final_result = result.results["aws_business_case"].result
            final_result_text = str(final_result)
            file_path = os.path.join(output_folder_dir_path, 'aws_business_case.md')
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("# AWS Business Case Report\n\n")
                file.write(f"Generated on: {result.execution_order[-1].execution_time}ms execution time\n\n")
                file.write("---\n\n")
                file.write(final_result_text)
            logger.info(f"Business case saved to: {file_path}")
else:
    logger.info("Using SINGLE-STAGE generation")
    if "aws_business_case" in result.results:
        final_result = result.results["aws_business_case"].result
        logger.info("Business case generated successfully")
        
        final_result_text = str(final_result)
        file_path = os.path.join(output_folder_dir_path, 'aws_business_case.md')
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("# AWS Business Case Report\n\n")
            file.write(f"Generated on: {result.execution_order[-1].execution_time}ms execution time\n\n")
            file.write("---\n\n")
            file.write(final_result_text)
            file.write("\n\n---\n\n")
            file.write(get_appendix())
        logger.info(f"Business case saved to: {file_path}")
    else:
        logger.error("Business case not found in results")

logger.info("="*60)
logger.info(f"Status: {result.status}")
logger.info(f"Execution order: {[node.node_id for node in result.execution_order]}")
logger.info("="*60)

# Display overall performance
logger.info("=== Graph Performance ===")
logger.info(f"Total Nodes Executed: {result.completed_nodes}/{result.total_nodes}")
logger.info(f"Total Execution Time: {result.execution_time}ms")
logger.info(f"Token Usage: {result.accumulated_usage}")

# Display individual node performance
logger.info("=== Individual Node Performance ===")
for node in result.execution_order:
    logger.info(f"- {node.node_id}: {node.execution_time}ms")
    if hasattr(node, 'status'):
        logger.info(f"  Status: {node.status}")

logger.info("="*80)
logger.info(f"Log file saved to: {log_file}")
logger.info("="*80)

