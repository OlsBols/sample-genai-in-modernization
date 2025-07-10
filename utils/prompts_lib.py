"""
Prompts library module containing various prompt templates for AWS migration analysis.

This module provides standardised prompt templates for different aspects of AWS migration
including resource planning, migration patterns, inventory analysis, modernisation pathways,
and architecture review.
"""

def get_resource_planning_prompt(migration_strategy,wave_planning_data,resource_details):
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

        **ANALYSIS FRAMEWORK:**

        **Step 1: Input Analysis**
        Analyse the provided inputs to understand:
        • Migration strategy complexity, scale, and workload volume from {migration_strategy}
        • Technology stack composition and legacy system dependencies
        • Wave structure, timeline, and application distribution from {wave_planning_data}
        • Available skills, roles, rates, and resource constraints from {resource_details}

        **Step 2: Team Structure Development**
        Develop two distinct team structures using the analysed inputs:

        **Team Structure 1: Hub-and-Spoke Model**
        - Central Centre of Excellence (CoE) with distributed execution teams
        - Centralised governance with federated delivery capabilities
        - Resource allocation based on {resource_details} and {wave_planning_data}

        **Team Structure 2: Wave-Based Approach**
        - Teams specifically aligned to migration waves from {wave_planning_data}
        - Sequential team formation based on wave requirements and {migration_strategy}

        **Step 3: Apply Structural Guidelines**
        For both team structures, implement:
        • Target utilisation rate: 85-95%
        • Team pods of 3-5 people with role specialisations from {resource_details}
        • 15-20% contingency capacity on all calculations
        • UK-specific constraints (public holidays and school holidays)
        • **Effort Estimation Standard**: Use person-days where 8 hours = 1 day and 5 days = 1 week

        **Step 4: Resource Calculations**
        Calculate team sizes using:
        • Wave volumes and timelines from {wave_planning_data}
        • Migration complexity factors from {migration_strategy}
        • Available skills and rates from {resource_details}
        • 6 R's migration strategy complexity multipliers
        • **Calculation Standard**: All effort estimations must use person-days (8 hours = 1 day, 5 days = 1 week)

        **OUTPUT REQUIREMENTS:**

        **Executive Summary**
        - High-level summary of migration complexity and wave structure
        - Key considerations and narrative of effort estimation methodology
        - Overview of recommended team structure approach

        **1. Team structure evaluation and recommendation** 
        - High-level overview of Team Structure 1: Hub-and-Spoke Model
        - High-level overview of Team Structure 2: Wave-Based Approach
        - Based on the developed team structures, compare Hub-and-Spoke Model and Wave-Based Approach and identify gaps and the most common or consistent elements across both structures including:
            • Shared roles and responsibilities
            • Common resource requirements
            • Consistent workstream dependencies
            • Similar governance mechanisms
        - Based on this analysis, synthesise a final structure; 
        and select and prioritise the most relevant skills from 
        {resource_details} based on migration complexity, cost-effectiveness and
        accelerated migration delivery. Specify, core team assignments, 
        specialist requirements and Support function involvement (when needed)

        **2. Resource summary**
        • Total Project Duration: [X months]
        • Total Effort Required: [X person-days]
        • Peak Team Size: [X people]
        • Recommended Team Structure: [Hub-and-Spoke/Wave-Based/Hybrid Recommended]

        **3. Planning for recommended team structure**
        | Wave | Description | Workloads/Apps | Duration (weeks) | Required Team Size | Key Roles |
        |------|-------------|----------------|------------------|---------------|-----------|
        | Wave 1 | | | | | |
        | Wave 2 | | | | | |
        | Wave 3 | | | | | |
        | Wave 4 | | | | | |
        | **Total** | | | | | |

        **4. Role-Based resource allocation**
        - Ensure the Role-Based resource allocation is inline with a point number (Team structure evaluation and recommendation) which the most relevant skills based on migration complexity, cost-effectiveness and accelerated migration delivery
        - Total Number of Days are the same as Total Effort Required. Ensure only relevant and required specialists are included
        **Note**: All calculations based on person-days where 8 hours = 1 day and 5 days = 1 week

        | Role | Required FTE | Number of Days | Utilisation % | Daily Rate (£) | Total Cost (£) |
        |------|-------------|----------------|---------------|----------------|----------------|
        | Senior Solutions Architect | | | | | |
        | Migration Engineer | | | | | |
        | DevOps Engineer | | | | | |
        | Cloud Infrastructure Engineer | | | | | |
        | Application Migration Specialist | | | | | |
        | Test Engineer | | | | | |
        | Project Manager | | | | | |
        | Change Manager | | | | | |
        | **Total** | | | | | |

        **5. Justification and Rationale**
        Provide detailed reasoning for:
        • **Team Sizing Rational**: How wave volumes and complexity drove team size decisions
        • **Effort Estimation Methodology**: Calculation approach using complexity factors (Rehost,Replatform, and Refactor) and person-days standard (8 hours = 1 day, 5 days = 1 week)
        • **Cost Optimisation Strategy**: How the recommended structure balances cost efficiency with delivery acceleration

        Format your response in markdown to make it readable and structured. Use British English standards. 
        **Ensure all calculated totals are consistent across tables - the sum of individual wave efforts in Table 3 must equal the total effort in Table 2, the sum of role-based person-days in Table 4 must equal the total effort in Table 2, and all cost calculations must reconcile across all tables with no discrepancies.**
        """
    return resource_prompt

def get_migration_patterns_prompt(services_summary,scope_text):
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
        Additional scope information{ scope_text if scope_text else ''}
        
        In order to develop an AWS migration strategy adhere to the following fix structure only in response. Always use USD($) as currency. Use British English standards.
        1. Analyse the calculator data focusing on cost optimisation and performance as key drivers.
        2. Generate three different patterns to modernize these workloads, 
        progressing from minimal changes to more comprehensive modernization.
        3. Compare these three approaches and identify the most common or consistent elements across all strategies.
        4. Based on this analysis, synthesise a final strategy that incorporates the most consistent aspects from all three approaches.
        5. Create a migration wave planning for the final strategy with in a table format:
           - Table header 'High Level Wave Plan'
           - Wave number and description
           - Services/workloads included in each wave
           - Estimated duration for each wave
           - Calculate the cumulative USD($) spend for each wave in a table format
        6. Answer the following questions:
           (1) Predict the month where partner will achieve the first 50,000 USD($) milestone in cumulative spend.
           (2) If the first 50,000 USD($) milestone in cumulative spend takes longer than four months, provide recommendations and strategies to accelerate migration for the first 50,000 USD($) milestone within the first three months.
           (3) Include appropriate risks and assumptions involved in the strategy to accelerate migration.
           (4) Include rational, reasoning and assumptions for the estimated duration for each wave
        
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

        **IMPORTANT: Do not assume, estimate, or calculate any costs, prices, or financial figures unless explicitly provided in the inventory data. Only analyse and report on cost-related information that is directly available in the provided dataset.**

        IT Inventory:
        {inventory_csv}

        Perform a thorough analysis and provide your response in the following structured order:

        ## (1) Inventory Insight & Cost Verification
        - **Asset Categorisation**: Identify and categorise by Compute, Storage, Database, Networking, Security, Monitoring, DevOps, AI, ML
        - **Purchase Price Verification**: 
            - Check first if purchase prices, acquisition dates, and depreciation schedules are available. If available, then only review and validate purchase prices, acquisition dates, and depreciation schedules
        - **Cost Categorisation**: 
            - Check first if costs are available for assets. If available, then only break down costs by asset type with detailed cost allocation
        - **Service Level Agreements**: 
            - Check first if any SLAs, performance guarantees, and associated penalty clauses are available. If available, then only review existing SLAs, performance guarantees, and associated penalty clauses

        ## (2) Capacity & Performance Analysis
        - **Utilisation Metrics**: CPU usage, memory usage, storage usage, and network bandwidth patterns
        - **Critical Capacity Issues**: Identify systems operating above 80% capacity with immediate action requirements
        - **Performance Trends**: Analyse utilisation patterns, peak usage times, and growth trajectories
        - **Underutilised Resources**: Highlight assets with consistently low utilisation rates

        ## (3) Risk Assessment & End-of-Life Planning
        - **End-of-Life Identification**: List all hardware approaching end-of-life within 12 months
        - **Security Vulnerabilities**: Identify unsupported or obsolete systems posing security risks
        - **Business Continuity Impact**: Assess potential service disruption risks

        ## (4) Cost Optimisation Opportunities
        - **Licence Consolidation Savings**: Check if any licence details are available. If licence details are available, then only identify potential software licence optimisation and consolidation opportunities for Microsoft and Oracle
        - **Immediate Cost Reduction**: Identify quick wins for cost reduction (redundant systems, over-provisioned resources)

        ## (5) Patterns, Anomalies & Dependencies
        - **Usage Patterns**: Identify trends, seasonal variations, and anomalous behaviour
        - **Asset Dependencies**: Map critical relationships and dependencies between systems
        - **Technology Stack Analysis**: Highlight integration points and potential single points of failure

        ## (6) Strategic Recommendations & Key Findings
        - **Executive Summary**: Data-driven insights based solely on available data
        
        **REMINDER: Base all analysis strictly on the provided inventory data. Do not introduce external cost estimates, market pricing, or assumed financial figures.**
        
        Format your response in markdown with clear headings, bullet points, and tables where appropriate. Use British English standards throughout.
        """
    return prompt

def get_modernization_pathways_prompt(inventory_csv,architecture_description,scope_text):
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
        
        {"Target Architecture Analysis:" + architecture_description if architecture_description else
         "No target architecture provided."}
        
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
        
        Format your response as Table name 'High Level AWS Cost' with the following columns:
        Mondernization Pathway or Additional AWS Services
        AWS Service Name
        Recommend Service Configuration
        Monthly cost in USD($) for AWS region Europe (Ireland) eu-west-1
        Estimate ARR (annual recurring costs) in USD($) 

        (b) For each applicable pathway:
        1. Explain why this pathway is appropriate
        2. Recommend specific AWS services based on provided IT Inventory and include suggested AWS services configuration.
        3. Provide rational bheind selecting AWS services
        4. Estimate monthly costs in USD for all recommended services (provide a estimate in the range of $1,000-$50,000)
        4. Estimate ARR (annual recurring costs) in USD($) for all recommended services (provide a estimate in the range of $1,000-$50,000) for AWS region Europe (Ireland) eu-west-1

        (c) Develop high level implementation approach

        Format your response in markdown to make it readable and structured. Use British English standards.
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
            - Follow provided checklist instructions
        **Checklist instructions:**
            - Identify Physical/virtual infrastructure and storage components 
            - Identify Network topology, Network segmentation and security zones, Load balancing and Network redundancy inclduing external connectivity and integration points 
            - Verify Security controls (firewalls, IDS/IPS) and Authentication and authorization mechanisms 
            - Review Application tiers, integration patterns and application dependencies
            - Identify deployment components and environment
            - Identify database, data flows, database integration and ETL processes
            - Identify Monitoring and alerting capabilities
            - Identify antanlytics and big data components and environment
        **Output Format:**
            - Executive Summary 
            - Detailed analysis and findings based on checklist 

    """
    return prompt_template
