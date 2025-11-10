"""Data Ingestion Agent - Infrastructure mapping with data quality assessment"""

from utils.strands_client import StrandsBedrockClient

SYSTEM_PROMPT = """You are a Data Ingestion Agent analyzing AWS Transform assessment output and customer data.

Your tasks:
1. Process AWS Transform assessment report with ready ARR calculations
2. Extract infrastructure inventory from Transform output
3. Analyze application portfolio and dependencies from Transform data
4. Assess migration readiness and complexity from Transform recommendations
5. Validate data completeness for business case generation

Output a structured analysis with:
- AWS Transform Assessment Summary (ARR, migration waves, recommendations)
- Application Portfolio Analysis from Transform data
- Infrastructure Summary from Transform inventory
- Migration Complexity Assessment from Transform output
- Data Quality and Completeness for business case"""

def execute(strands_client, customer_data, kb_id=None):
    """Execute data ingestion with quality assessment"""
    import json
    import pandas as pd
    
    infra = customer_data.get('infrastructure', {})
    scope = customer_data.get('scope', '')[:1000]
    data_quality = customer_data.get('data_quality', {})
    
    # Build comprehensive data summary focusing on AWS Transform
    data_summary = f"""
AWS TRANSFORM ASSESSMENT STATUS:
"""
    
    # Check for AWS Transform assessment data first
    transform_data = {}
    for key, value in infra.items():
        if 'transform' in key.lower():
            transform_data[key] = value
            if isinstance(value, pd.DataFrame):
                data_summary += f"\n✓ {key}: {len(value)} records with ARR calculations"
            else:
                data_summary += f"\n✓ {key}: Available with ready ARR data"
    
    if transform_data:
        data_summary += "\n\n✅ AWS Transform assessment available - ARR calculations ready to use"
    else:
        data_summary += "\n\n⚠️ No AWS Transform assessment found - will use alternative data sources"
    
    data_summary += f"""

SCOPE OVERVIEW:
{scope}

SUPPORTING DATA SOURCES:
"""
    
    # RVTool CSV data
    if 'rvtool_csv' in infra:
        df = infra['rvtool_csv']
        data_summary += f"""
✓ RVTool CSV Available:
  - Servers: {len(df)}
  - Total vCPUs: {df['CPU Cores'].sum() if 'CPU Cores' in df.columns else 'N/A'}
  - Total Memory (GB): {round(df['Memory (MB)'].sum() / 1024, 2) if 'Memory (MB)' in df.columns else 'N/A'}
  - Total Storage (TB): {round(df['Provisioned Storage (GB)'].sum() / 1024, 2) if 'Provisioned Storage (GB)' in df.columns else 'N/A'}
  - OS Distribution: {df['Operating System'].value_counts().to_dict() if 'Operating System' in df.columns else 'N/A'}
  - Environments: {df['Environment'].value_counts().to_dict() if 'Environment' in df.columns else 'N/A'}
"""
    
    # RVTool Excel (detailed)
    if 'rvtool_excel' in infra:
        sheets = infra['rvtool_excel']
        data_summary += f"""
✓ Detailed RVTools Excel Available:
  - Sheets: {list(sheets.keys())}
  - Comprehensive VM, storage, network data available
"""
    
    # AWS Calculator
    if 'aws_calculator' in infra:
        df = infra['aws_calculator']
        data_summary += f"""
✓ AWS Calculator Data Available:
  - Configurations: {len(df)}
  - Can use for cost validation
"""
    
    # Dependencies
    if 'dependencies' in infra:
        sheets = infra['dependencies']
        data_summary += f"""
✓ Application Dependency Data Available:
  - Sheets: {list(sheets.keys())}
  - Application-infrastructure relationships documented
"""
    
    # Analytics
    if 'analytics' in infra:
        data_summary += f"""
✓ Analytics Migration Data Available:
  - OpenSearch/Analytics workload assessment included
"""
    
    # Add recommendations from data quality
    if data_quality.get('recommendations'):
        data_summary += f"""

DATA GAP RECOMMENDATIONS:
{chr(10).join(['- ' + rec for rec in data_quality.get('recommendations', [])])}
"""
    
    user_prompt = data_summary
    
    # Query KB for mapping methodologies
    kb_context = ""
    if kb_id:
        kb_results = bedrock_client.query_knowledge_base(kb_id, "infrastructure mapping AWS services EC2 RDS sizing")
        if kb_results:
            kb_context = "\n\nPARTNER MAPPING METHODOLOGIES:\n" + "\n".join([r['content'][:400] for r in kb_results[:3]])
    
    response = strands_client.invoke_with_prompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt + kb_context
    )
    
    return {"agent": "Data Ingestion", "output": response, "data_quality": data_quality}
