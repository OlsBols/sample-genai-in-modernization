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
from prompt_library.agent_prompts import (
    system_message_aws_arr_cost, 
    system_message_rv_tool_analysis, 
    system_message_it_analysis,
    system_message_aws_business_case,
    system_message_current_state_analysis,
    system_message_atx_analysis )

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id=model_id_claude3_7,
    temperature=model_temperature
)

agent_it_analysis = Agent(model=bedrock_model,system_prompt= system_message_it_analysis,tools=[it_analysis])
agent_rv_tool_analysis = Agent(model=bedrock_model,system_prompt= system_message_rv_tool_analysis,tools=[rv_tool_analysis])
agent_atx_analysis = Agent(model=bedrock_model,system_prompt= system_message_atx_analysis,tools=[read_excel_file, read_pdf_file, read_pptx_file])
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
builder.add_node(current_state_analysis, "current_state_analysis")
builder.add_node(agent_aws_cost_arr, "agent_aws_cost_arr")
builder.add_node(aws_business_case, "aws_business_case")

# (1) current_state_analysis executes ONLY when ALL three analysis agents complete
condition_for_current_state = all_dependencies_complete(["agent_it_analysis", "agent_rv_tool_analysis", "agent_atx_analysis"])
builder.add_edge("agent_it_analysis", "current_state_analysis", condition=condition_for_current_state)
builder.add_edge("agent_rv_tool_analysis", "current_state_analysis", condition=condition_for_current_state)
builder.add_edge("agent_atx_analysis", "current_state_analysis", condition=condition_for_current_state)

# (2) agent_aws_cost_arr executes ONLY when ALL three analysis agents complete
condition_for_cost_arr = all_dependencies_complete(["agent_it_analysis", "agent_rv_tool_analysis", "agent_atx_analysis"])
builder.add_edge("agent_it_analysis", "agent_aws_cost_arr", condition=condition_for_cost_arr)
builder.add_edge("agent_rv_tool_analysis", "agent_aws_cost_arr", condition=condition_for_cost_arr)
builder.add_edge("agent_atx_analysis", "agent_aws_cost_arr", condition=condition_for_cost_arr)

# (3) aws_business_case executes ONLY when BOTH current_state_analysis AND agent_aws_cost_arr complete
condition_for_business_case = all_dependencies_complete(["current_state_analysis", "agent_aws_cost_arr"])
builder.add_edge("current_state_analysis", "aws_business_case", condition=condition_for_business_case)
builder.add_edge("agent_aws_cost_arr", "aws_business_case", condition=condition_for_business_case)


# Set entry points (the nodes that start first - they run in parallel)
builder.set_entry_point("agent_it_analysis")
builder.set_entry_point("agent_rv_tool_analysis")
builder.set_entry_point("agent_atx_analysis")

builder.set_execution_timeout(600)  # 10 minute timeout
builder.set_node_timeout(180)  # 3 minute timeout per node

# Build the graph
graph = builder.build()

input_files1 = "input/Test-Data-Set-Demo-Excel-V2.xlsx"
input_files2 = "input/rvtool.csv"
input_files3_excel = "input/analysis.xlsx"
input_files3_pdf = "input/report.pdf"
input_files3_pptx = "input/business_case.pptx"
agent_task = f"""Create a comprehensive business case to migrate on-premises IT workload to AWS. 
    **Input Data Sources:**
        1. IT Infrastructure Inventory: {input_files1}
        2. RVTool Assessment Data: {input_files2}
        3. AWS Transform for VMware (ATX) Assessment:
           - VMware Environment Data: {input_files3_excel}
           - Technical Assessment Report: {input_files3_pdf}
           - Business Case Presentation: {input_files3_pptx}
   """

result = graph(agent_task)

print("\n" + "="*80)
print("FINAL BUSINESS CASE")
print("="*80)
if "aws_business_case" in result.results:
    final_result = result.results["aws_business_case"].result
    print(f"\n{final_result}")
    final_result_text = str(final_result)
    file_path = os.path.join(output_folder_dir_path, 'aws_business_case.md')
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("# AWS Business Case Report\n\n")
        file.write(f"Generated on: {result.execution_order[-1].execution_time}ms execution time\n\n")
        file.write("---\n\n")
        file.write(final_result_text)

print(f"\n{'='*60}")
print(f"Status: {result.status}")
print(f"Execution order: {[node.node_id for node in result.execution_order]}")
print(f"{'='*60}")

# Display overall performance
print(f"\n=== Graph Performance ===")
print(f"Total Nodes Executed: {result.completed_nodes}/{result.total_nodes}")
print(f"Total Execution Time: {result.execution_time}ms")
print(f"Token Usage: {result.accumulated_usage}")

