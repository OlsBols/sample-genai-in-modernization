#!/usr/bin/env python3
"""
AWS CDK Stack for Business Case Generator - Simple Deployment (No OIDC/Domain/Certificate)

Architecture:
- ALB with HTTP/HTTPS (self-signed cert)
- ECS Fargate service (Flask serves both frontend and API)
- S3 buckets for file storage
- DynamoDB for case metadata
- No custom domain, no OIDC authentication
"""

from aws_cdk import (
    App, Stack, Duration, RemovalPolicy,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_logs as logs,
    aws_ecr_assets as ecr_assets,
)
from constructs import Construct
import os

class BusinessCaseGeneratorSimpleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # ====================================================================
        # VPC
        # ====================================================================
        vpc = ec2.Vpc(
            self, "VPC",
            max_azs=2,
            nat_gateways=1,  # Cost optimization
        )
        
        # ====================================================================
        # S3 Buckets
        # ====================================================================
        input_bucket = s3.Bucket(
            self, "InputBucket",
            bucket_name=f"business-case-input-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.RETAIN,
            auto_delete_objects=False,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )
        
        output_bucket = s3.Bucket(
            self, "OutputBucket",
            bucket_name=f"business-case-output-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.RETAIN,
            auto_delete_objects=False,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )
        
        # ====================================================================
        # DynamoDB Table
        # ====================================================================
        table = dynamodb.Table(
            self, "CasesTable",
            table_name="business-case-cases",
            partition_key=dynamodb.Attribute(
                name="caseId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
        )
        
        # Add GSI for user queries
        table.add_global_secondary_index(
            index_name="UserIdIndex",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt",
                type=dynamodb.AttributeType.STRING
            ),
        )
        
        # ====================================================================
        # ECS Cluster
        # ====================================================================
        cluster = ecs.Cluster(
            self, "Cluster",
            cluster_name="business-case-cluster",
            vpc=vpc,
            container_insights=True,
        )
        
        # ====================================================================
        # Task Definition
        # ====================================================================
        task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef",
            memory_limit_mib=2048,
            cpu=1024,
        )
        
        # Grant permissions
        input_bucket.grant_read_write(task_definition.task_role)
        output_bucket.grant_read_write(task_definition.task_role)
        table.grant_read_write_data(task_definition.task_role)
        
        # Grant Bedrock permissions
        task_definition.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=[
                    "arn:aws:bedrock:*:*:foundation-model/*",
                    "arn:aws:bedrock:*:*:inference-profile/*",
                ],
            )
        )
        
        # Grant AWS Pricing API permissions
        task_definition.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "pricing:GetProducts",
                    "pricing:DescribeServices",
                    "pricing:GetAttributeValues",
                ],
                resources=["*"],
            )
        )
        
        # Grant Savings Plans API permissions
        task_definition.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "savingsplans:DescribeSavingsPlansOfferingRates",
                    "savingsplans:DescribeSavingsPlansOfferings",
                ],
                resources=["*"],
            )
        )
        
        # Build and add container
        container = task_definition.add_container(
            "AppContainer",
            image=ecs.ContainerImage.from_asset(
                directory=os.path.join(os.path.dirname(__file__), "../.."),
                file="infrastructure/Dockerfile",
                platform=ecr_assets.Platform.LINUX_AMD64,
                build_args={
                    "BUILDKIT_INLINE_CACHE": "1",
                },
            ),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="business-case",
                log_retention=logs.RetentionDays.ONE_WEEK,
            ),
            environment={
                "FLASK_ENV": "production",
                "AWS_REGION": self.region,
                "S3_INPUT_BUCKET": input_bucket.bucket_name,
                "S3_OUTPUT_BUCKET": output_bucket.bucket_name,
                "DYNAMODB_TABLE_NAME": table.table_name,
                "AUTO_SAVE_TO_DYNAMODB": "true",
            },
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health')\" || exit 1"],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(10),
                retries=3,
                start_period=Duration.seconds(60),
            ),
        )
        
        container.add_port_mappings(
            ecs.PortMapping(container_port=8080, protocol=ecs.Protocol.TCP)
        )
        
        # ====================================================================
        # Application Load Balancer (Simple - No OIDC)
        # ====================================================================
        
        # Create ALB
        alb = elbv2.ApplicationLoadBalancer(
            self, "ALB",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name="business-case-alb",
            idle_timeout=Duration.seconds(600),
        )
        
        # Create target group
        target_group = elbv2.ApplicationTargetGroup(
            self, "TargetGroup",
            vpc=vpc,
            port=8080,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(
                path="/api/health",
                interval=Duration.seconds(30),
                timeout=Duration.seconds(10),
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
            ),
            deregistration_delay=Duration.seconds(30),
        )
        
        # Create ECS service
        service = ecs.FargateService(
            self, "Service",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            service_name="business-case-service",
            assign_public_ip=False,
            health_check_grace_period=Duration.seconds(60),
        )
        
        # Attach service to target group
        service.attach_to_application_target_group(target_group)
        
        # HTTP Listener (no authentication)
        listener = alb.add_listener(
            "HttpListener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_action=elbv2.ListenerAction.forward([target_group]),
        )
        
        # ====================================================================
        # Outputs
        # ====================================================================
        from aws_cdk import CfnOutput
        
        CfnOutput(
            self, "LoadBalancerDNSOutput",
            value=alb.load_balancer_dns_name,
            description="Application URL (HTTP)"
        )
        CfnOutput(
            self, "ApplicationURLOutput",
            value=f"http://{alb.load_balancer_dns_name}",
            description="Access the application at this URL"
        )
        CfnOutput(self, "InputBucketOutput", value=input_bucket.bucket_name)
        CfnOutput(self, "OutputBucketOutput", value=output_bucket.bucket_name)
        CfnOutput(self, "DynamoDBTableOutput", value=table.table_name)

# ============================================================================
# App
# ============================================================================
app = App()

BusinessCaseGeneratorSimpleStack(
    app, "BusinessCaseGeneratorSimpleStack",
    env={
        "account": os.environ.get("CDK_DEFAULT_ACCOUNT"),
        "region": os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
    },
)

app.synth()
