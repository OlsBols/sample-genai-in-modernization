import os
from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent import GraphBuilder
from strands.multiagent.graph import GraphState
from strands.multiagent.base import Status

from config import model_id_claude3_7,model_temperature, output_folder_dir_path
from inventory_analysis import it_analysis
from rv_tool_analysis import rv_tool_analysis
from atx_analysis import read_excel_file, read_pdf_file, read_pptx_file
from mra_analysis import read_docx_file, read_markdown_file
from migration_strategy import read_migration_strategy_framework, read_portfolio_assessment
from migration_plan import read_migration_plan_framework
from project_context import get_project_context, get_project_info_dict
from setup_logging import setup_logging
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

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id=model_id_claude3_7,
    temperature=model_temperature
)

agent_it_analysis = Agent(model=bedrock_model,system_prompt= system_message_it_analysis,tools=[it_analysis])
agent_rv_tool_analysis = Agent(model=bedrock_model,system_prompt= system_message_rv_tool_analysis,tools=[rv_tool_analysis])
agent_atx_analysis = Agent(model=bedrock_model,system_prompt= system_message_atx_analysis,tools=[read_excel_file, read_pdf_file, read_pptx_file])
agent_mra_analysis = Agent(model=bedrock_model,system_prompt= system_message_mra_analysis,tools=[read_docx_file, read_markdown_file])
agent_migration_strategy = Agent(model=bedrock_model,system_prompt= system_message_migration_strategy,tools=[read_migration_strategy_framework, read_portfolio_assessment])
agent_migration_plan = Agent(model=bedrock_model,system_prompt= system_message_migration_plan,tools=[read_migration_plan_framework])
agent_aws_cost_arr = Agent(model=bedrock_model,system_prompt= system_message_aws_arr_cost,tools=[it_analysis,rv_tool_analysis])
current_state_analysis = Agent(model=bedrock_model,system_prompt= system_message_current_state_analysis,tools=[it_analysis,rv_tool_analysis])
aws_business_case = Agent(model=bedrock_model,system_prompt= system_message_aws_business_case)


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

builder.set_execution_timeout(1800)  # 30 minute timeout for entire workflow
builder.set_node_timeout(600)  # 10 minute timeout per node

# Build the graph
graph = builder.build()

# Get project context
project_context = get_project_context()
project_info = get_project_info_dict()

input_files1 = "input/it-infrastructure-inventory.xlsx"
input_files2 = "input/rvtool*.csv"  # Pattern to match multiple RVTools files
input_files3_excel = "input/atx_analysis.xlsx"
input_files3_pdf = "input/atx_report.pdf"
input_files3_pptx = "input/atx_business_case.pptx"
input_files4_mra = "input/aws-customer-migration-readiness-assessment.md"
input_files5_strategy = "input/aws-migration-strategy-6rs-framework.md"

agent_task = f"""Create a comprehensive business case to migrate on-premises IT workload to AWS.

{project_context}

    **Input Data Sources:**
        1. IT Infrastructure Inventory: {input_files1}
        2. RVTool Assessment Data: {input_files2} (multiple files may be available including vInfo, vCPU, vMemory, vDisk, etc.)
        3. AWS Transform for VMware (ATX) Assessment:
           - VMware Environment Data: {input_files3_excel}
           - Technical Assessment Report: {input_files3_pdf}
           - Business Case Presentation: {input_files3_pptx}
        4. Migration Readiness Assessment (MRA): {input_files4_mra}
        5. Migration Strategy Framework (6Rs): {input_files5_strategy}
   """

logger.info("="*80)
logger.info("STARTING AGENT WORKFLOW")
logger.info("="*80)
logger.info(f"Project: {project_info.get('projectName', 'N/A')}")
logger.info(f"Customer: {project_info.get('customerName', 'N/A')}")
logger.info(f"Region: {project_info.get('awsRegion', 'N/A')}")
logger.info(f"Description: {project_info.get('projectDescription', 'N/A')[:100]}...")
logger.info("="*80)

logger.info("Executing agent graph...")
result = graph(agent_task)
logger.info("Agent graph execution completed")

logger.info("="*80)
logger.info("FINAL BUSINESS CASE GENERATION")
logger.info("="*80)

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

