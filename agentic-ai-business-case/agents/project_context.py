"""
Utility to read and provide project context to all agents
"""
import os
import json
from config import input_folder_dir_path

def get_project_context():
    """
    Read project information from the input folder.
    Returns a formatted string with project context.
    """
    project_info_file = os.path.join(input_folder_dir_path, 'input', 'project_info.json')
    
    if not os.path.exists(project_info_file):
        return ""
    
    try:
        with open(project_info_file, 'r', encoding='utf-8') as f:
            project_info = json.load(f)
        
        context = f"""
**PROJECT CONTEXT:**
- Project Name: {project_info.get('projectName', 'N/A')}
- Customer Name: {project_info.get('customerName', 'N/A')}
- Target AWS Region: {project_info.get('awsRegion', 'N/A')}
- Project Description: {project_info.get('projectDescription', 'N/A')}

**IMPORTANT: All analysis, recommendations, and outputs must align with the project description and objectives stated above.**
"""
        return context
    except Exception as e:
        print(f"Warning: Could not read project context: {str(e)}")
        return ""

def get_project_info_dict():
    """
    Read project information and return as dictionary.
    Includes uploaded filenames if available.
    """
    project_info_file = os.path.join(input_folder_dir_path, 'input', 'project_info.json')
    
    if not os.path.exists(project_info_file):
        return {}
    
    try:
        with open(project_info_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not read project info: {str(e)}")
        return {}
