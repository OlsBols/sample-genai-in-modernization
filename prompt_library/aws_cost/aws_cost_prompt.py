def get_modernization_pathways_cost_prompt(inventory_csv, high_level_strategy):
    prompt = f"""
        As an AWS migration expert, analyse the provided IT inventory and modernisation strategy to develop an AWS cost estimation with modernisation pathway recommendations.
        Focus on cost optimisation and performance. Always use USD($) as currency. Use British English standards.
        Ensure all mathematical calculations (addition, multiplication) are correct.

        IT Inventory:
        {inventory_csv}

        Modernisation Strategy:
        {high_level_strategy}

        Use exactly these ## headings in this order:

        ## Executive Summary
        5 concise bullet points covering:
        - Portfolio overview and modernisation scope
        - Total estimated monthly AWS spend
        - Total estimated first 12 months spend
        - Top recommended modernisation pathways
        - Key cost optimisation opportunities

        ## High Level AWS Cost Summary
        Create a table with these columns. Include ALL recommended services across all pathways.
        | Group | Region | AWS Service | Monthly ($) | First 12 Months ($) | Configuration Summary |
        Group values: one of the 8 modernisation pathways below, or "Additional AWS Services".
        Region: Europe (Ireland) eu-west-1.
        Include a **Total** row at the bottom summing the Monthly and First 12 Months columns.
        Ensure the Total row values are mathematically correct — the sum of all individual rows.

        ## Modernisation Pathway Analysis
        For each applicable pathway below, use a ### sub-heading and provide:
        - Why this pathway is appropriate (2-3 bullet points)
        - Recommended AWS services with suggested configuration
        - Estimated monthly cost for this pathway

        Only include pathways that are relevant to the inventory. Use these pathway names:

        ### Move to Cloud Native
        Services: API Gateway, Lambda, EventBridge, Step Functions, SQS, SNS, Amazon MQ, AppSync, Cognito, Amplify, X-Ray, Migration Hub Refactor Spaces

        ### Move to Containers
        Services: EKS, ECS, ECR, Fargate, App Runner

        ### Move to Open Source
        Services: RDS (MySQL, Postgres, MariaDB), Aurora, Linux containers on ECS/EKS/Fargate, Lambda

        ### Move to Managed Databases
        Services: RDS, Aurora, DocumentDB, KeySpaces, ElastiCache, MemoryDB, DMS, DAX, Neptune, Timestream

        ### Move to Managed Analytics
        Services: Lake Formation, Kinesis, EMR, Redshift, MSK, Athena, Glue, QuickSight, OpenSearch, Kendra, MWAA, AppFlow, HealthLake

        ### Move to Modern DevOps
        Services: CloudFormation, Config, CodeBuild, CodeDeploy, CodePipeline, CodeGuru, CodeArtifact, CodeCatalyst, Prometheus, DevOps Guru

        ### Move to AI
        Services: Amazon Bedrock, Q Developer, SageMaker, A2I, Forecast, Lex, Polly, Transcribe, Personalize, Comprehend, Textract, Rekognition, Translate

        ### Additional AWS Services
        Monitoring, governance, security, storage, backup, and DR services not covered by the pathways above.

        Keep each pathway section concise — bullet points preferred over paragraphs.
        """
    return prompt
