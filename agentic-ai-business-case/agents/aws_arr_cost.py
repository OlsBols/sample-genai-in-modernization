from strands import Agent, tool
from strands.models import BedrockModel


from config import model_id_claude3_7,model_temperature
from inventory_analysis import it_analysis
from rv_tool_analysis import rv_tool_analysis

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id=model_id_claude3_7,
    temperature=model_temperature
)

# system_message = """
#     You are an AWS migration cost specialist. Please calculate estimated AWS costs for the provided inventory data with the following requirements:

#     (a) Use the following modernisation pathways and recommend AWS services for each applicable pathway:
            
#         1. Move to Cloud Native: API Gateway, Lambda, EventBridge, Step Functions, SQS, SNS, Amazon MQ, AppSync, Cognito, Amplify, X-Ray, Migration Hub Refactor Spaces, CognitoSync
#         2. Move to Containers: EKS, ECS, ECR, Fargate, App Runner
#         3. Move to Open Source: RDS (MySQL, Postgres, MariaDB), Aurora, Linux containers on ECS/EKS/Fargate, Lambda
#         4. Move to Managed Databases: RDS (MySQL, Postgres, MariaDB), Aurora, DocumentDB, KeySpaces, ElastiCache, MemoryDB, DMS, DynamoDB Accelerator (DAX), Neptune,KeySpaces, Timestream and MemoryDB
#         5. Move to Managed Analytics: Lake Formation, Kinesis, EMR, Redshift, MSK, Athena, Glue, QuickSight, OpenSearch, Kendra, MWAA, Appflow, HealthLake
#         6. Move to Modern DevOps: CloudFormation, Config, CodeBuild, CodeDeploy, CodePipeline, CodeGuru, Amplify, X-Ray, CodeArtifact, CodeCatalyst, Prometheus, DeviceFarm, DevOpsGuru
#         7. Move to AI: Amazon Bedrock, Q Developer, Sagemaker, A2I, Forecast, Lex, Polly, Transcribe, Personalize, Comprehend, Textract, Rekognition, Comprehend Medical, Translate
#         8. Additional AWS Services Assessment -Identify any additional AWS services required other the modernisation pathways (compute, storage, security, netwroking, minitoring)
#     (b) Provide rational bheind selecting AWS services 
#     (C) Analyse and present costs using multiple purchasing options:
#         - On-Demand pricing: Pay-as-you-go hourly rates
#         - Reserved Instances: 1-year and 3-year commitment savings (Standard and Convertible)
#         - Savings Plans: Compute and EC2 Savings Plans with flexible commitment options2
#         - Spot Instances: For non-critical, flexible workloads
#     (D) Format your response as Table name 'High Level AWS Cost' with the following columns:
#         - Mondernization Pathway or Additional AWS Services
#         - AWS Service Name
#         - Recommend Service Configuration
#         - Monthly cost in USD($) for AWS region Europe (Ireland) eu-west-1
#         - Estimate ARR (annual recurring costs) in USD($) 
#     (E) Annual Cost Projection
#         - Quaterly cost projection with growth considerations for 12-months
#         - Year 2 and Year 3 Projection growth in % and USD
#         - Comparison across different pricing models (On-Demand vs Reserved vs Savings Plans) 
#     """

# agent = Agent(model=bedrock_model,system_prompt= system_message,tools=[it_analysis,rv_tool_analysis])


# input_files1 = "input/Test-Data-Set-Demo-Excel-V2.xlsx"
# input_files2 = "input/rvtool.csv"
# agent_trigger_query = "Start with high level summary of on premises enviroment using tool it_analysis,rv_tool_analysis.The summary should include five sections starting from Server Infrastructure ,Database, Storage, Application, Networking,Security and monitoring. Generate a comprehensive AWS Cost to migration on premises it inventory data " + input_files1 + " and RV tool data" + input_files2 + " to AWS. #**IMPORTANT (1) Do not assume, estimate, or calculate any costs, prices, or financial figures unless explicitly provided in the inventory data.(2) Ensure mathematical operations like addition, subtraction, multiplication, and division are correct for Compute, Storage and Database provided in the inventory."

# result = agent(agent_trigger_query)
# print(result.message)