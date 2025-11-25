import os
import pandas as pd
from datetime import datetime
import json
import boto3
from strands import Agent, tool
from strands.models import BedrockModel

from config import input_folder_dir_path, model_id_claude3_7,model_temperature


# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id=model_id_claude3_7,
    temperature=model_temperature
)


def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

def excel_to_json(filename, create_file=False, max_rows_per_sheet=3000):
    """
    Convert Excel to JSON with row limits to prevent context overflow.
    Limits each sheet to max_rows_per_sheet to stay within model context limits.
    """
    try:
        # Get input folder path from config.py and join with filename  directory and construct full path
        full_path = os.path.join(input_folder_dir_path, filename)
        
        # Read Excel file
        excel_file = pd.read_excel(full_path, sheet_name=None, engine='openpyxl')
        
        # Convert to JSON-compatible dictionary
        json_data = {}
        for sheet_name, dataframe in excel_file.items():
            # Limit rows to prevent context overflow
            original_rows = len(dataframe)
            if original_rows > max_rows_per_sheet:
                print(f"WARNING: Sheet '{sheet_name}' has {original_rows} rows. Limited to {max_rows_per_sheet} rows to prevent context overflow.")
                dataframe = dataframe.head(max_rows_per_sheet)
            
            # Convert datetime columns to string format
            for column in dataframe.select_dtypes(include=['datetime64']).columns:
                dataframe[column] = dataframe[column].dt.strftime('%Y-%m-%d %H:%M:%S')
            # Handle NaN values and convert to records
            json_data[sheet_name] = dataframe.fillna('').to_dict(orient='records')
        
        # Create JSON filename
        if create_file == True:
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_full_path = os.path.join(input_folder_dir_path, json_filename)
        
            # Save JSON data to file with custom serialization
            with open(json_full_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, 
                        default=datetime_handler,
                        indent=4, 
                        ensure_ascii=False)
        return json_data
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None, None



@tool(name="it_analysis", description="Read CSV file from the target folder")
def it_analysis(filename):
    json_data = excel_to_json(filename)
    return json_data

# system_message = """
#     Use tool inventory_analysis to perform inventory analysis
#     As an AWS migration expert, conduct a comprehensive analysis of the provided IT inventory with emphasis on cost optimisation, performance metrics, disaster recovery capabilities, and strategic planning.

#     Asset Distribution
#     -Total asset count
#     -Asset categories breakdown

#     Technical Environment Analysis
#         1 Infrastructure Layer
#         - Server infrastructure
#         - Storage systems
#         - Network components
#         - Security infrastructure
#     2 Application Landscape
#         - Application inventory
#         - Technology stacks
#         - Version distribution
#         - Support status
#     3 Database Systems
#         - Database types and versions
#         - Data volumes
#         - Growth patterns
#         - Backup strategies
#     4 Operating Systems
#         - OS distribution
#         - Version analysis
#         - Support status
#         - Patch levels
#     Dependency Analysis
#     1 Application Dependencies
#         - Application-to-application mapping
#         - Integration points
#         - API relationships
#         - Service dependencies
#     2 Data Dependencies
#         - Data flow mapping
#         - Master data relationships
#         - Shared data repositories
#         - Data synchronisation requirements
#     3 Infrastructure Dependencies
#         - Hardware dependencies
#         - Network dependencies
#         - Storage dependencies
#         - Security dependencies
#     4 Critical Path Analysis
#         - Single points of failure
#         - Dependency chains
#         - Impact assessment
#         - Risk evaluation
        
#         **REMINDER: Base all analysis strictly on the provided inventory data. Do not introduce external cost estimates, market pricing, or assumed financial figures. For DR analysis, only report on disaster recovery information that is explicitly documented in the inventory.**
        
#         Format your response in markdown with clear headings, bullet points, and tables where appropriate. 
#     """
# agent = Agent(model=bedrock_model,system_prompt= system_message,tools=[it_analysis])

# question = "Conduct a comprehensive analysis of the provided IT inventory for the provided file input/it-infrastructure-inventory.xlsx"

# result = agent(question)
# print(result.message)



# filename = 'input/it-infrastructure-inventory.xlsx'
# json_data = excel_to_json(filename) 
# print(json_data)
   