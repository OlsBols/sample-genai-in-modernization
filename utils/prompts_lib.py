"""
Prompts library module containing various prompt templates for AWS migration analysis.

This module provides standardised prompt templates for different aspects of AWS migration
including resource planning, migration patterns, inventory analysis, modernisation pathways,
and architecture review.
"""


def get_resource_planning_prompt(
    migration_strategy, wave_planning_data, resource_details
):
    """
    Generate a comprehensive AWS migration resource planning prompt.

    Args:
        migration_strategy (str): The migration strategy details
        wave_planning_data (str): Wave planning information
        resource_details (str): Available resource details

    Returns:
        str: Formatted resource planning prompt
    """
    resource_prompt = f"""
        As an AWS migration expert, please develop comprehensive AWS migration resource planning using the following inputs:

        **INPUT PARAMETERS:**
        - Migration Strategy: {migration_strategy}
        - Wave Planning Data: {wave_planning_data}
        - Resource Details: {resource_details}


        **Executive Summary**
        - High-level summary of migration complexity and wave structure
        - Key considerations and narrative of effort estimation methodology
        - Overview of recommended team structure approach

        **Resource summary**
        • Recommended Team Structure

        **Planning for recommended team structure** 
        **Justification and Rationale**

        """
    return resource_prompt


def get_migration_patterns_prompt(services_summary, scope_text):
    """
    Generate a migration patterns analysis prompt.

    Args:
        services_summary (str): Summary of AWS services
        scope_text (str): Additional scope information

    Returns:
        str: Formatted migration patterns prompt
    """
    prompt = f"""
        As an AWS migration expert, please develope an AWS migration strategy 
        based on the following AWS calculator data: {services_summary} and
        Additional scope information{scope_text if scope_text else ""}
        
        1. Analyse the calculator data focusing on cost optimisation and performance as key drivers.
        2. Create a migration wave planning for the final strategy with in a table format:
        3. Answer the following questions:
           (1) Predict the month where partner will achieve the first 50,000 USD($) milestone in cumulative spend.
        
        Format your response in markdown to make it readable and structured. 
        """
    return prompt


def get_invventory_analysis_prompt(inventory_csv):
    """
    Generate an inventory analysis prompt.

    Args:
        inventory_csv (str): CSV data containing IT inventory information

    Returns:
        str: Formatted inventory analysis prompt
    """
    prompt = f"""
        As an AWS migration expert, conduct a comprehensive analysis of the provided IT inventory with emphasis on cost optimisation, performance metrics, and strategic planning.

        {inventory_csv}

        Perform a thorough analysis and provide your response in the following structured order:

        ## (1) Inventory Insight & Cost Verification
        ## (2) Capacity & Performance Analysis
        ## (3) Cost Optimisation Opportunities

        **REMINDER: Base all analysis strictly on the provided inventory data. Do not introduce external cost estimates, market pricing, or assumed financial figures.**
        
        Format your response in markdown with clear headings, bullet points, and tables where appropriate. 
        """
    return prompt


def get_modernization_pathways_prompt(
    inventory_csv, architecture_description, scope_text
):
    """
    Generate a modernisation pathways analysis prompt.

    Args:
        inventory_csv (str): CSV data containing IT inventory information
        architecture_description (str): Target architecture description
        scope_text (str): Modernisation scope information

    Returns:
        str: Formatted modernisation pathways prompt
    """
    prompt = f"""
        As an AWS migration expert, analyse the provided IT inventory, 
        modernisation scope and target architecture analysis to develop an AWS modernisation strategy 
        with implementation approach.
        Focus on cost optimisation and performance as key drivers.Always use USD($) as currency.
        
        IT Inventory:
        {inventory_csv}

        Modernisation Scope:
        {scope_text}
        
        {
        "Target Architecture Analysis:" + architecture_description
        if architecture_description
        else "No target architecture provided."
    }
        
        To develop an AWS modernisation strategy with implementation approach: 
        (a) Use the following modernisation pathways and recommend AWS services for each applicable pathway:
        
        1. Move to Cloud Native: API Gateway, Lambda, EventBridge, Step Functions, SQS, SNS, Amazon MQ, AppSync, Cognito, Amplify, X-Ray, Migration Hub Refactor Spaces, CognitoSync
        2. Move to Containers: EKS, ECS, ECR, Fargate, App Runner
        3. Move to Open Source: RDS (MySQL, Postgres, MariaDB), Aurora, Linux containers on ECS/EKS/Fargate, Lambda
        4. Move to Managed Databases: RDS (MySQL, Postgres, MariaDB), Aurora, DocumentDB, KeySpaces, ElastiCache, MemoryDB, DMS, DynamoDB Accelerator (DAX), Neptune,KeySpaces, Timestream and MemoryDB
        5. Move to Managed Analytics: Lake Formation, Kinesis, EMR, Redshift, MSK, Athena, Glue, QuickSight, OpenSearch, Kendra, MWAA, Appflow, HealthLake
        6. Move to Modern DevOps: CloudFormation, Config, CodeBuild, CodeDeploy, CodePipeline, CodeGuru, Amplify, X-Ray, CodeArtifact, CodeCatalyst, Prometheus, DeviceFarm, DevOpsGuru
        7. Move to AI: Amazon Bedrock, Q Developer, Sagemaker, A2I, Forecast, Lex, Polly, Transcribe, Personalize, Comprehend, Textract, Rekognition, Comprehend Medical, Translate
        8. Additional AWS Services Assessment -Identify any additional AWS services required other the modernisation pathways
        
        """
    return prompt


def get_onprem_architecture_prompt():
    """
    Generate a on premises architecture analysis prompt.

    Returns:
        str: Formatted on premises architecture analysis  prompt
    """
    prompt_template = """
        You are an expert IT Enterprise Architect with experience in reviewing enterprise architecture diagrams. Your expertise spans infrastructure, applications, data, security, operational, monitoring and network architecture across on-premises and hybrid environments.
        **Your Role:**
            - Conduct thorough, systematic reviews of architecture diagrams
            - Be thorough but concise in analysis
        **Output Format:**
            - Executive Summary 
            - Detailed analysis and findings based on checklist 

    """
    return prompt_template
