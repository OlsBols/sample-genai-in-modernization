import os
import pandas as pd
import glob
from strands import Agent, tool
from strands.models import BedrockModel

from config import input_folder_dir_path, model_id_claude3_7,model_temperature


# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id=model_id_claude3_7,
    temperature=model_temperature
)

def read_csv_from_current_dir(filename):
    full_path = os.path.join(input_folder_dir_path, filename)
    if filename.endswith('.csv'):
        return pd.read_csv(full_path)
    elif filename.endswith(('.xlsx', '.xls')):
        return pd.read_excel(full_path)
    else:
        raise ValueError(f"Unsupported file format: {filename}")

@tool(name="rv_tool_analysis", description="Read RVTools CSV or Excel files from the target folder. Can handle single file or multiple files (e.g., vInfo, vCPU, vMemory, vDisk). Provide filename or pattern like 'rvtool*.csv' to read multiple files.")
def rv_tool_analysis(filename_or_pattern):
    """
    Read RVTools files. Can handle:
    - Single file: 'rvtool.csv' or 'rvtool-vInfo.xlsx'
    - Multiple files with pattern: 'rvtool*.csv' or 'rvtool*.xlsx'
    - Specific file: exact filename
    
    Returns a dictionary of DataFrames if multiple files, or single DataFrame if one file.
    """
    # Check if pattern contains wildcard
    if '*' in filename_or_pattern:
        # Find all matching files
        pattern_path = os.path.join(input_folder_dir_path, filename_or_pattern)
        matching_files = glob.glob(pattern_path)
        
        if not matching_files:
            raise FileNotFoundError(f"No files found matching pattern: {filename_or_pattern}")
        
        # Read all matching files
        dataframes = {}
        for file_path in matching_files:
            filename = os.path.basename(file_path)
            # Extract a meaningful key from filename (e.g., 'vInfo' from 'rvtool-vInfo.csv')
            key = filename.replace('rvtool-', '').replace('rvtool_', '').rsplit('.', 1)[0]
            
            if file_path.endswith('.csv'):
                dataframes[key] = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                dataframes[key] = pd.read_excel(file_path)
        
        return dataframes
    else:
        # Single file
        return read_csv_from_current_dir(filename_or_pattern)

# system_message = """
#     Use tool inventory_analysis to perform inventory analysis
#     As an AWS migration expert, conduct a comprehensive analysis of the provided IT inventory with emphasis on cost optimisation, performance metrics, disaster recovery capabilities, and strategic planning.

#         **IMPORTANT: Do not assume, estimate, or calculate any costs, prices, or financial figures unless explicitly provided in the inventory data. Only analyse and report on cost-related information that is directly available in the provided dataset.**

#         IT Inventory: Ensure mathematical operations like addition, subtraction, multiplication, and division are correct for Compute, Storage and Database provided in the inventory.
       
#         Perform a thorough analysis and provide your response in the following structured order:

#         ## (1) Inventory Insight & Cost Verification
#         - **Asset Categorisation**: Identify and categorise by Compute, Storage, Database, Networking, Security, Monitoring, DevOps, AI, ML
#         - **Purchase Price Verification**: 
#             - Check first if purchase prices, acquisition dates, and depreciation schedules are available. If available, then only review and validate purchase prices, acquisition dates, and depreciation schedules
#         - **Cost Categorisation**: 
#             - Check first if costs are available for assets. If available, then only break down costs by asset type with detailed cost allocation
#         - **Service Level Agreements**: 
#             - Check first if any SLAs, performance guarantees, and associated penalty clauses are available. If available, then only review existing SLAs, performance guarantees, and associated penalty clauses

#         ## (2) Capacity & Performance Analysis
#         - **Utilisation Metrics**: CPU usage, memory usage, storage usage, and network bandwidth patterns
#         - **Critical Capacity Issues**: Identify systems operating above 80% capacity with immediate action requirements
#         - **Performance Trends**: Analyse utilisation patterns, peak usage times, and growth trajectories
#         - **Underutilised Resources**: Highlight assets with consistently low utilisation rates

#         ## (3) Disaster Recovery & Business Continuity Analysis
#         - **Storage Systems Assessment**: 
#             - Analyse storage infrastructure (SAN, NAS, local storage) with capacity, performance metrics, and backup capabilities
#             - Identify storage dependencies and single points of failure
#         - **Recovery Requirements (RTO/RPO)**:
#             - Check if RTO (Recovery Time Objective) and RPO (Recovery Point Objective) requirements are documented
#             - If available, analyse business impact classifications and acceptable downtime windows
#             - Assess data loss tolerance requirements per application/system
#         - **Backup Strategies Analysis**:
#             - Review backup frequency schedules and retention policies if documented
#             - Analyse backup testing procedures and success rates if available
#             - Identify gaps in backup coverage or untested backup systems
#         - **Replication Mechanisms**:
#             - Identify existing replication setups (real-time vs. batch processing)
#             - Document synchronous vs. asynchronous replication methods if present
#             - Analyse replication targets and geographic distribution
#         - **Current DR Capabilities**:
#             - Assess existing disaster recovery sites and their capacity
#             - Review DR testing history and procedures if documented
#             - Identify critical systems without adequate DR protection

#         ## (4) Risk Assessment & End-of-Life Planning
#         - **End-of-Life Identification**: List all hardware approaching end-of-life within 12 months
#         - **Security Vulnerabilities**: Identify unsupported or obsolete systems posing security risks
#         - **Business Continuity Impact**: Assess potential service disruption risks and DR readiness gaps
#         - **Single Points of Failure**: Highlight critical systems without redundancy or DR protection

#         ## (5) Cost Optimisation Opportunities
#         - **Licence Consolidation Savings**: Check if any licence details are available. If licence details are available, then only identify potential software licence optimisation and consolidation opportunities for Microsoft and Oracle
#         - **Immediate Cost Reduction**: Identify quick wins for cost reduction (redundant systems, over-provisioned resources)
#         - **DR Cost Efficiency**: Analyse DR infrastructure costs and identify optimisation opportunities if cost data is available

#         ## (6) Patterns, Anomalies & Dependencies
#         - **Usage Patterns**: Identify trends, seasonal variations, and anomalous behaviour
#         - **Asset Dependencies**: Map critical relationships and dependencies between systems
#         - **Technology Stack Analysis**: Highlight integration points and potential single points of failure
#         - **DR Dependencies**: Analyse cross-system dependencies that impact disaster recovery strategies

#         ## (7) Strategic Recommendations & Key Findings
#         - **Executive Summary**: Data-driven insights based solely on available data
#         - **DR Readiness Assessment**: Overall disaster recovery maturity and gaps
#         - **Migration Priorities**: Systems requiring immediate attention for DR improvement
        
#         **REMINDER: Base all analysis strictly on the provided inventory data. Do not introduce external cost estimates, market pricing, or assumed financial figures. For DR analysis, only report on disaster recovery information that is explicitly documented in the inventory.**
        
#         Format your response in markdown with clear headings, bullet points, and tables where appropriate. 
#     """
# agent = Agent(model=bedrock_model,system_prompt= system_message,tools=[rv_tool_analysis])

# question = "Conduct a comprehensive analysis of the provided IT inventory with emphasis on cost optimisation, performance metrics, disaster recovery capabilities for the provided file input/rvtool.csv"

# result = agent(question)
# print(result.message)


# if __name__ == "__main__":
   
#     filename = 'input/rvtool.csv'
#     df = rv_tool_analysis(filename) 
#     print(df)