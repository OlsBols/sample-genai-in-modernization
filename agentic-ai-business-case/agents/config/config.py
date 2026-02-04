import os
from botocore.config import Config

# Get the directory where this config file is located (agents/config/)
_config_dir = os.path.dirname(os.path.abspath(__file__))

# Set paths relative to the project root (two levels up: agents/config/ -> agents/ -> project root)
_project_root = os.path.dirname(os.path.dirname(_config_dir))

# Input and output directories (relative paths)
# In production (ECS), use /tmp directories set by backend
# In development, use project directories
if os.environ.get('FLASK_ENV') == 'production':
    input_folder_dir_path = '/tmp/input/'
    output_folder_dir_path = '/tmp/output/'
else:
    input_folder_dir_path = os.path.join(_project_root, "input") + "/"
    output_folder_dir_path = os.path.join(_project_root, "output") + "/"

# S3 Configuration for case file storage
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', None)
S3_ENABLED = S3_BUCKET_NAME is not None
S3_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# ===== BEDROCK RETRY CONFIGURATION =====
# Production-ready retry configuration for handling transient errors
BEDROCK_RETRY_CONFIG = Config(
    retries={
        'max_attempts': 5,  # Retry up to 5 times
        'mode': 'adaptive'  # Adaptive retry mode (recommended for production)
        # 'mode': 'standard'  # Alternative: standard exponential backoff
    },
    connect_timeout=10,   # Connection timeout in seconds
    read_timeout=300,     # Read timeout in seconds (5 minutes for long responses)
)

# Retryable error codes (handled automatically by boto3 with above config):
# - modelStreamErrorException: Temporary Bedrock processing error
# - serviceUnavailableException: Bedrock service temporarily unavailable  
# - throttlingException: Rate limit exceeded
# - InternalServerException: AWS internal error

#Bedrock Model Configuration

# Option 1: Claude 3 Sonnet (4096 max tokens) - Works with on-demand, STABLE
# model_id_claude3_7="anthropic.claude-3-sonnet-20240229-v1:0"
# max_tokens_default = 4096

# Option 2: Claude 3.5 Sonnet with Cross-Region Inference (8192 max tokens)
# Requires model access enabled in Bedrock Console - see CLAUDE_35_SETUP.md
# TEMPORARILY DISABLED: Service unavailable errors
# model_id_claude3_7="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
# max_tokens_default = 8192

# Option 1: Claude 3.5 Sonnet v2 with Cross-Region Inference (8192 max tokens) - RECOMMENDED for guardrails
model_id_claude3_7="us.anthropic.claude-3-5-sonnet-20241022-v2:0"  # Cross-region inference profile
max_tokens_default = 8192

# Alternative models:
# model_id_claude3_7="anthropic.claude-3-sonnet-20240229-v1:0"  # Claude 3 (4096 tokens)
# model_id_claude3_7="anthropic.claude-3-haiku-20240307-v1:0"  # Faster, cheaper (4096 tokens)

model_id_nova_ite="us.amazon.nova-lite-v1:0"
model_temperature=0.3

# Multi-stage generation settings
ENABLE_MULTI_STAGE = True  # Generate business case in multiple stages
MAX_TOKENS_BUSINESS_CASE = max_tokens_default  # Will use 8192 if Claude 3.5

# Data limits to prevent context window overflow and max_tokens errors
# Reduced significantly to prevent agent output from exceeding token limits
MAX_ROWS_RVTOOLS = 2500  # Max VMs to analyze from RVTools (increased to 2500 to capture all VMs in typical datasets)
MAX_ROWS_IT_INVENTORY = 1500  # Max rows per sheet in IT inventory (reduced from 3000)
MAX_ROWS_PORTFOLIO = 1000  # Max applications in portfolio (reduced from 2000)

# ============================================================================
# DETERMINISTIC PRICING CONFIGURATION
# ============================================================================
# Control whether to use deterministic pricing calculator or LLM-based estimation

# Enable/disable deterministic pricing
USE_DETERMINISTIC_PRICING = True  # Default: ON for consistent, accurate pricing

# AWS Pricing Calculator Settings (only used if USE_DETERMINISTIC_PRICING = True)
PRICING_CONFIG = {
    # Try to use AWS Price List API for real-time pricing
    # If False or API unavailable, uses fallback pricing
    'use_aws_pricing_api': True,  # Default: ON for real-time AWS pricing
    
    # Default AWS region for pricing calculations
    # Can be overridden per calculation
    'default_region': 'us-east-1',
    
    # Pricing model to use
    # Options: '3yr_compute_sp', '3yr_ec2_sp', '3yr_no_upfront', '1yr_no_upfront', 'on_demand'
    # '3yr_compute_sp' = 3-Year Compute Savings Plan (recommended, most flexible, typically cheapest)
    # '3yr_ec2_sp' = 3-Year EC2 Instance Savings Plan (less flexible, typically more expensive than Compute SP)
    # '3yr_no_upfront' = 3-Year Reserved Instance No Upfront
    'pricing_model': '3yr_compute_sp',
    
    # Storage pricing (EBS gp3 per GB-month)
    'storage_rate_per_gb': 0.08,  # us-east-1 base rate
    
    # Data transfer estimate (as percentage of compute cost)
    'data_transfer_percentage': 0.05,  # 5% of compute cost
    
    # Enable caching for pricing lookups (improves performance)
    'enable_caching': True,
    
    # Show detailed pricing breakdown in logs
    'verbose_logging': True,
    
    # Prefer AWS Graviton (ARM) instances for Linux workloads (20% cheaper)
    # Only applies to Linux VMs, Windows will use x86
    'prefer_graviton': False,  # Set to True to prefer Graviton instances
    
    # Instance generation preference
    # Options: 'latest' (7th gen), 'newer' (6th gen), 'current' (5th gen), 'cost_optimized' (mix)
    'generation_preference': 'newer',  # Recommended: 'newer' for best price/performance
}

# ============================================================================
# RIGHT-SIZING CONFIGURATION
# ============================================================================
# Apply right-sizing based on actual utilization (if available in RVTools)
# These assumptions align with AWS Transform for VMware (ATX) methodology

RIGHT_SIZING_CONFIG = {
    # Enable right-sizing based on utilization data
    'enable_right_sizing': True,  # Default: ON for cost optimization
    
    # CPU right-sizing: Use peak utilization
    # ATX Assumption: 25% peak CPU utilization
    'cpu_sizing_method': 'peak',  # Options: 'peak', 'average', 'p95' (95th percentile)
    'cpu_peak_utilization_percent': 25,  # ATX standard: 25% peak CPU utilization
    'cpu_headroom_percentage': 0,  # No additional headroom (already in 25% assumption)
    
    # Memory right-sizing: Use peak utilization
    # ATX Assumption: 60% peak memory utilization
    'memory_sizing_method': 'peak',  # Options: 'peak', 'average', 'p95'
    'memory_peak_utilization_percent': 60,  # ATX standard: 60% peak memory utilization
    'memory_headroom_percentage': 0,  # No additional headroom (already in 60% assumption)
    
    # Storage right-sizing: Use actual used storage vs provisioned
    # ATX Assumption: 50% storage utilization if missing data
    'storage_sizing_method': 'used',  # Options: 'used', 'provisioned'
    'storage_utilization_percent': 50,  # ATX standard: 50% storage utilization
    'storage_headroom_percentage': 0,  # No additional headroom (already in 50% assumption)
    
    # Default provisioned storage if missing data
    # ATX Assumption: 500 GiB default provisioned storage
    'default_provisioned_storage_gib': 500,  # Default storage per VM if data missing
    
    # Minimum instance sizes (prevent over-optimization)
    'min_vcpu': 2,  # Minimum 2 vCPUs
    'min_memory_gb': 4,  # Minimum 4 GB RAM
    
    # Right-sizing aggressiveness
    # Options: 'conservative' (more headroom), 'moderate', 'aggressive' (less headroom)
    'aggressiveness': 'moderate',
}

# ============================================================================
# TCO COMPARISON CONFIGURATION
# ============================================================================
# Control whether to include on-premises TCO comparison in business case

TCO_COMPARISON_CONFIG = {
    # Enable on-premises TCO comparison
    # If False, business case will focus on AWS costs and business value only
    'enable_tco_comparison': False,  # Set to True to include TCO comparison
    
    # On-premises cost assumptions (used if enable_tco_comparison = True)
    'on_prem_costs': {
        'hardware_per_server_per_year': 5000,  # Hardware depreciation + refresh
        'vmware_license_per_vm_per_year': 200,  # VMware licensing
        'windows_license_per_vm_per_year': 150,  # Windows licensing
        'datacenter_per_rack_per_year': 1000,  # Power, cooling, space
        'it_staff_per_fte_per_year': 150000,  # IT staff cost
        'vms_per_fte': 100,  # Assume 1 FTE per 100 VMs
        'maintenance_percentage': 15,  # 15% of hardware cost
    },
    
    # TCO comparison display options
    'show_tco_only_if_aws_cheaper': True,  # Only show TCO if AWS < On-Prem
    'tco_analysis_years': 3,  # 3-year TCO comparison
}

# ============================================================================
# EKS (ELASTIC KUBERNETES SERVICE) CONFIGURATION
# ============================================================================
# Control whether to include EKS as a migration target option
#
# WHEN TO ENABLE EKS:
# EKS becomes cost-effective at scale due to fixed costs (~$555/month for control plane + networking).
# RECOMMENDED: 50+ small VMs (2-4 vCPU) for cost parity, 100+ VMs for 10-25% savings vs EC2.
# Below 40 VMs, EKS costs 1.5-3x more than EC2 but may be justified for strategic modernization benefits
# (faster deployments, better scalability, DevOps transformation). Fixed costs are amortized across more
# workloads at scale, making per-VM costs decrease significantly (e.g., $55/VM at 10 VMs vs $5.55/VM at 100 VMs).
#

# Enable/disable EKS analysis
ENABLE_EKS_ANALYSIS = True  # Default: ON for EKS migration option

# RECOMMENDATION LOGIC (for future enhancement):
# The system recommends EC2 vs EKS based on a 4-tier decision tree:
# 1. If EKS costs LESS than EC2: Recommend EKS (cost + modernization benefits)
# 2. If EKS costs 0-20% MORE: Recommend EKS (strategic value justifies premium)
# 3. If EKS costs 20-50% MORE: Recommend EC2 with EKS consideration (cost-sensitive)
# 4. If EKS costs 50%+ MORE: Recommend EC2 only (EKS not economically viable)
# This logic is implemented in aws_business_case.py and can be tuned by adjusting thresholds.
#
# RECOMMENDATION THRESHOLDS (configurable):
EKS_RECOMMENDATION_THRESHOLDS = {
    'tier2_max_premium': 0.20,  # 20% - Max premium for recommending EKS (strategic value)
    'tier3_max_premium': 0.50,  # 50% - Max premium for considering EKS as alternative
    # Tier 1: EKS < EC2 (negative premium) → Always recommend EKS
    # Tier 2: EKS 0-20% more → Recommend EKS (strategic value justifies premium)
    # Tier 3: EKS 20-50% more → Recommend EC2, mention EKS as alternative
    # Tier 4: EKS 50%+ more → Recommend EC2 only (EKS not viable)
}
# To adjust thresholds:
# - Increase tier2_max_premium (e.g., 0.30 = 30%) to be more aggressive with EKS
# - Decrease tier2_max_premium (e.g., 0.10 = 10%) to be more conservative
# - Adjust tier3_max_premium to change when EKS is no longer mentioned


# EKS Configuration Settings
EKS_CONFIG = {
    # ===== STRATEGY CONFIGURATION =====
    'enabled': True,  # Master switch for EKS analysis
    'strategy': 'hybrid',  # Options: 'hybrid', 'all-eks', 'disabled'
    'vcpu_threshold': 4,  # VMs with < X vCPU go to EKS (hybrid mode only)
    
    # ===== CONSOLIDATION RATIOS =====
    # Linux containers (efficient, small images)
    'linux_consolidation_ratios': {
        'small': 3.5,    # < 4 vCPU (high consolidation)
        'medium': 2.5,   # 4-8 vCPU
        'large': 1.75,   # 8-16 vCPU
        'xlarge': 1.25   # > 16 vCPU (minimal consolidation)
    },
    
    # Windows containers (less efficient, large images)
    'windows_consolidation_ratios': {
        'small': 2.0,    # < 4 vCPU (43% less efficient than Linux)
        'medium': 1.5,   # 4-8 vCPU
        'large': 1.25,   # 8-16 vCPU
        'xlarge': 1.1    # > 16 vCPU
    },
    
    # ===== CLUSTER CONFIGURATION =====
    'num_clusters': 2,  # Production + Non-production
    'prod_vm_percentage': 0.70,  # 70% of VMs are production
    'nonprod_vm_percentage': 0.30,  # 30% are dev/test
    'nonprod_uptime_percentage': 0.40,  # Dev/test runs 40% of time (8hrs/day, 5 days/week)
    # NOT YET IMPLEMENTED - Reserved for future enhancement
    # Currently uses single cluster cost model, multi-cluster and uptime optimization not implemented
    
    # ===== HIGH AVAILABILITY =====
    'production_azs': 3,  # Production spans 3 AZs
    'dev_azs': 1,  # Dev can be single AZ
    'min_nodes_per_az': 1,  # Minimum 1 node per AZ
    # NOT YET IMPLEMENTED - Reserved for future enhancement
    # Currently uses simplified HA model, per-AZ node distribution not implemented
    
    # ===== GRAVITON CONFIGURATION =====
    'enable_graviton': True,  # Enable AWS Graviton (ARM-based) instances
    # Benefits: 20% cost savings, 40% better price/performance
    # Limitations: Linux only, some apps may need recompilation
    # When disabled: Uses only x86 instances (Intel/AMD)
    
    # ===== WORKER NODE PREFERENCES =====
    # 35+ instance types across 5 generations
    'worker_node_preferences': [
        # Latest generation (m7i/c7i/r7i) - Best price/performance
        'm7i.large', 'm7i.xlarge', 'm7i.2xlarge', 'm7i.4xlarge', 'm7i.8xlarge', 'm7i.12xlarge', 'm7i.16xlarge',
        'c7i.large', 'c7i.xlarge', 'c7i.2xlarge', 'c7i.4xlarge', 'c7i.8xlarge', 'c7i.12xlarge', 'c7i.16xlarge',
        'r7i.large', 'r7i.xlarge', 'r7i.2xlarge', 'r7i.4xlarge', 'r7i.8xlarge', 'r7i.12xlarge', 'r7i.16xlarge',
        
        # Newer generation (m6i/c6i/r6i) - Proven, widely available
        'm6i.large', 'm6i.xlarge', 'm6i.2xlarge', 'm6i.4xlarge', 'm6i.8xlarge', 'm6i.12xlarge', 'm6i.16xlarge',
        'c6i.large', 'c6i.xlarge', 'c6i.2xlarge', 'c6i.4xlarge', 'c6i.8xlarge', 'c6i.12xlarge', 'c6i.16xlarge',
        'r6i.large', 'r6i.xlarge', 'r6i.2xlarge', 'r6i.4xlarge', 'r6i.8xlarge', 'r6i.12xlarge', 'r6i.16xlarge',
        
        # AMD (m6a/c6a/r6a) - 10% cheaper than Intel
        'm6a.large', 'm6a.xlarge', 'm6a.2xlarge', 'm6a.4xlarge', 'm6a.8xlarge', 'm6a.12xlarge', 'm6a.16xlarge',
        'c6a.large', 'c6a.xlarge', 'c6a.2xlarge', 'c6a.4xlarge', 'c6a.8xlarge', 'c6a.12xlarge', 'c6a.16xlarge',
        'r6a.large', 'r6a.xlarge', 'r6a.2xlarge', 'r6a.4xlarge', 'r6a.8xlarge', 'r6a.12xlarge', 'r6a.16xlarge',
        
        # Graviton (m7g/c7g/r7g) - 20% cheaper, Linux only
        'm7g.large', 'm7g.xlarge', 'm7g.2xlarge', 'm7g.4xlarge', 'm7g.8xlarge', 'm7g.12xlarge', 'm7g.16xlarge',
        'c7g.large', 'c7g.xlarge', 'c7g.2xlarge', 'c7g.4xlarge', 'c7g.8xlarge', 'c7g.12xlarge', 'c7g.16xlarge',
        'r7g.large', 'r7g.xlarge', 'r7g.2xlarge', 'r7g.4xlarge', 'r7g.8xlarge', 'r7g.12xlarge', 'r7g.16xlarge',
        
        # Current generation (m5/c5/r5) - Fallback
        'm5.large', 'm5.xlarge', 'm5.2xlarge', 'm5.4xlarge', 'm5.8xlarge', 'm5.12xlarge', 'm5.16xlarge',
        'c5.large', 'c5.xlarge', 'c5.2xlarge', 'c5.4xlarge', 'c5.9xlarge', 'c5.12xlarge', 'c5.18xlarge',
        'r5.large', 'r5.xlarge', 'r5.2xlarge', 'r5.4xlarge', 'r5.8xlarge', 'r5.12xlarge', 'r5.16xlarge',
    ],
    
    # ===== SPOT INSTANCE CONFIGURATION =====
    'spot_enabled': True,  # Enable Spot instances for cost savings
    'spot_percentage': 0.30,  # 30% Spot (burst capacity)
    'on_demand_percentage': 0.40,  # 40% On-Demand (baseline)
    'reserved_percentage': 0.30,  # 30% Reserved/Savings Plan (baseline)
    'spot_diversification_min_types': 4,  # Use at least 4 instance types
    'spot_discount': 0.70,  # 70% discount vs On-Demand
    # NOTE: Capacity mix percentages ARE IMPLEMENTED and configurable
    # spot_diversification_min_types is NOT YET IMPLEMENTED - Reserved for future enhancement
    
    # ===== COST ASSUMPTIONS (INDUSTRY STANDARD) =====
    'eks_control_plane_hourly': 0.10,  # $0.10/hour per cluster
    'overhead_factor': 1.15,  # 15% overhead for Kubernetes system pods
    'cross_az_data_transfer_pct': 0.15,  # 15% of traffic crosses AZs
    'cross_az_rate_per_gb': 0.01,  # $0.01/GB between AZs
    # NOT YET IMPLEMENTED - Reserved for future enhancement
    # Cross-AZ data transfer costs not yet calculated in pricing model
    
    # ===== STORAGE CONFIGURATION =====
    'worker_node_root_volume_gb': 100,  # OS + container runtime
    'container_image_cache_gb_per_node': 50,  # Cached container images
    'stateful_app_percentage': 0.30,  # 30% of apps need persistent storage
    'snapshot_retention_days': 30,
    'snapshot_rate_per_gb_month': 0.05,
    'ecr_image_storage_gb_per_app': 2,  # Container images in ECR
    'ecr_rate_per_gb_month': 0.10,
    # NOT YET IMPLEMENTED - Reserved for future enhancement
    # Snapshot and ECR costs not yet included in pricing model
    
    # ===== NETWORKING CONFIGURATION =====
    # NOTE: Networking now uses simplified 10% of compute cost model
    # The detailed ALB/NAT pricing below is NOT YET IMPLEMENTED - Reserved for future enhancement
    'alb_per_cluster': 2,  # Application Load Balancers per cluster
    'alb_fixed_cost_per_month': 16.20,
    'alb_lcu_cost_per_hour': 0.008,
    'avg_lcu_per_alb': 5,  # Average Load Balancer Capacity Units
    'nat_gateway_per_az': 1,
    'nat_gateway_cost_per_month': 32.40,
    'nat_gateway_data_processing_per_gb': 0.045,
    'internet_egress_pct_of_compute': 0.05,  # 5% of compute traffic to internet
    'internet_egress_rate_per_gb': 0.09,  # First 10 TB
    
    # ===== MONITORING CONFIGURATION =====
    'cloudwatch_enabled': True,
    'cloudwatch_log_ingestion_gb_per_node_per_day': 2,
    'cloudwatch_ingestion_rate_per_gb': 0.50,
    'cloudwatch_storage_rate_per_gb_month': 0.03,
    'metrics_retention_days': 30,
    
    # ===== SECURITY CONFIGURATION =====
    'secrets_per_app': 3,  # DB password, API keys, certificates
    'secrets_manager_cost_per_secret_month': 0.40,
    'guardduty_enabled': True,
    'guardduty_cost_per_cluster_month': 75,
    # NOT YET IMPLEMENTED - Reserved for future enhancement
    # Secrets Manager and GuardDuty costs not yet included in pricing model
    
    # ===== BACKUP & DR CONFIGURATION =====
    'backup_enabled': True,
    'backup_compression_ratio': 0.5,  # 50% compression
    's3_standard_rate_per_gb_month': 0.023,
    'dr_enabled': False,  # Multi-region DR
    'dr_cluster_size_percentage': 0.50,  # DR cluster is 50% of prod
    # NOT YET IMPLEMENTED - Reserved for future enhancement
    # Backup and DR costs not yet included in pricing model
    
    # ===== OPTIMIZATION CONFIGURATION =====
    # These settings control EKS cost optimization over time
    # NOT YET IMPLEMENTED - Reserved for future enhancement
    'rightsizing_enabled': True,  # Enable automatic rightsizing recommendations
    'rightsizing_savings_year2': 0.25,  # Expected 25% savings in Year 2 after 6 months of optimization
    'optimization_timeline_months': 6,  # Time to achieve full optimization (6 months)
    'enable_cluster_autoscaler': True,  # Enable Kubernetes Cluster Autoscaler for dynamic scaling
    'min_nodes_percentage': 0.60,  # Minimum nodes = 60% of baseline (scale down limit)
    'max_nodes_percentage': 1.50,  # Maximum nodes = 150% of baseline (scale up limit)
    
    # EXPLANATION:
    # - rightsizing_enabled: When True, system will recommend optimized instance types after monitoring actual usage
    # - rightsizing_savings_year2: Expected cost reduction in Year 2 after rightsizing (25% = $100 becomes $75)
    # - optimization_timeline_months: How long it takes to collect data and optimize (typically 6 months)
    # - enable_cluster_autoscaler: Kubernetes feature that automatically adds/removes nodes based on demand
    # - min_nodes_percentage: Prevents scaling below 60% of baseline (maintains minimum capacity)
    # - max_nodes_percentage: Prevents scaling above 150% of baseline (controls maximum cost)
    # 
    # EXAMPLE: If baseline is 10 nodes:
    #   - Minimum: 6 nodes (60% × 10)
    #   - Maximum: 15 nodes (150% × 10)
    #   - Autoscaler adjusts between 6-15 nodes based on actual workload demand
    
    # ===== EXCLUSION PATTERNS (HYBRID STRATEGY) =====
    # VMs matching these patterns won't be containerized in hybrid mode
    'exclude_patterns': [
        'sql', 'oracle', 'db', 'database',  # Databases (consider RDS)
        'active.?directory', 'ad.?server',  # Active Directory
        'exchange', 'sharepoint',  # Microsoft workloads
        'sap', 'peoplesoft', 'siebel',  # Enterprise apps
        'legacy', 'mainframe'  # Legacy applications
    ],
    
    # ===== WORKLOAD DETECTION =====
    'auto_detect_workload_type': True,  # Auto-select c/m/r family
    'prefer_graviton': True,  # Prefer Graviton for Linux workloads (20% savings)
    'memory_ratio_compute_threshold': 3,  # < 3 GB/vCPU = compute-optimized
    'memory_ratio_memory_threshold': 6,  # > 6 GB/vCPU = memory-optimized
}


# ============================================================================
# AWS BACKUP CONFIGURATION
# ============================================================================
# AWS Backup costs for EC2 and RDS instances
# Pricing: https://aws.amazon.com/backup/pricing/

BACKUP_CONFIG = {
    # ===== ENABLE/DISABLE =====
    'enabled': True,  # Include backup costs in ARR calculations
    
    # ===== BACKUP SERVICE =====
    'service': 'aws_backup',  # AWS Backup (managed service)
    # Alternative: 'ebs_snapshots' (manual snapshots) - not yet implemented
    
    # ===== RETENTION POLICY (3-2-1 Strategy) =====
    # Production environment (stricter retention)
    'production': {
        # Daily backups with 1 week retention
        'daily_retention_days': 7,  # Keep daily backups for 7 days
        'daily_frequency': 'daily',  # Run daily
        
        # Weekly backups with 2 weeks retention
        'weekly_retention_weeks': 2,  # Keep weekly backups for 2 weeks (14 days)
        'weekly_frequency': 'weekly',  # Run weekly (Sunday)
        
        # Monthly backups with 1 year retention
        'monthly_retention_months': 12,  # Keep monthly backups for 12 months (1 year)
        'monthly_frequency': 'monthly',  # Run monthly (1st of month)
    },
    
    # Pre-production/Development environment (lighter retention)
    'pre_production': {
        # Daily backups with shorter retention
        'daily_retention_days': 3,  # Keep daily backups for 3 days only
        'daily_frequency': 'daily',  # Run daily
        
        # Weekly backups with 1 week retention
        'weekly_retention_weeks': 1,  # Keep weekly backups for 1 week (7 days)
        'weekly_frequency': 'weekly',  # Run weekly (Sunday)
        
        # No monthly backups for pre-prod
        'monthly_retention_months': 0,  # No monthly backups
        'monthly_frequency': None,  # Disabled
    },
    
    # ===== ENVIRONMENT DISTRIBUTION =====
    # Percentage of VMs in each environment (if not detected from data)
    'default_prod_percentage': 0.70,  # 70% production
    'default_preprod_percentage': 0.30,  # 30% pre-production/dev/test
    
    # ===== ENVIRONMENT DETECTION =====
    # How to detect environment from VM/server names
    'environment_detection': {
        'enabled': True,  # Try to detect environment from names
        'prod_patterns': ['prod', 'production', 'prd', 'live'],
        'preprod_patterns': ['dev', 'test', 'uat', 'staging', 'qa', 'preprod', 'pre-prod', 'nonprod', 'non-prod'],
        'case_sensitive': False,  # Ignore case when matching
    },
    
    # ===== BACKUP SCOPE =====
    'backup_percentage': 100,  # Percentage of VMs/RDS to backup (default: 100% = all)
    'backup_ec2': True,  # Backup EC2 instances
    'backup_rds': True,  # Backup RDS instances
    'backup_ebs': True,  # Backup EBS volumes (included with EC2)
    'backup_eks': True,  # Backup EKS persistent volumes (EBS-backed)
    
    # ===== EKS BACKUP CONFIGURATION =====
    # EKS uses EBS-backed persistent volumes (PVs) for stateful workloads
    'eks_stateful_percentage': 0.30,  # 30% of EKS workloads need persistent storage
    'eks_avg_storage_per_workload_gb': 100,  # Average PV size per stateful workload
    'eks_snapshot_frequency': 'daily',  # Snapshot frequency for EKS PVs
    
    # ===== AWS PRICING API CONFIGURATION =====
    'use_pricing_api': True,  # Use AWS Price List API for real-time rates
    'pricing_api_fallback': True,  # Fall back to hardcoded rates if API fails
    
    # Fallback rates (us-east-1) - used if API unavailable
    # These are updated as of January 2026
    'fallback_rates': {
        'backup_storage_per_gb_month': 0.05,  # AWS Backup warm storage
        'backup_cold_storage_per_gb_month': 0.01,  # AWS Backup cold storage
        's3_glacier_instant_per_gb_month': 0.004,  # S3 Glacier Instant Retrieval
        's3_glacier_flexible_per_gb_month': 0.0036,  # S3 Glacier Flexible Retrieval
        's3_glacier_deep_per_gb_month': 0.00099,  # S3 Glacier Deep Archive
        'restore_per_gb': 0.02,  # Restore cost (not included in ARR)
    },
    
    # Regional pricing multipliers (relative to us-east-1)
    # Used as fallback if API doesn't return pricing for a region
    'regional_multipliers': {
        'us-east-1': 1.0,
        'us-east-2': 1.0,
        'us-west-1': 1.05,
        'us-west-2': 1.0,
        'eu-west-1': 1.05,
        'eu-west-2': 1.05,
        'eu-west-3': 1.05,
        'eu-central-1': 1.05,
        'eu-north-1': 1.0,
        'ap-southeast-1': 1.10,
        'ap-southeast-2': 1.10,
        'ap-northeast-1': 1.10,
        'ap-northeast-2': 1.10,
        'ap-northeast-3': 1.10,
        'ap-south-1': 1.08,
        'ap-east-1': 1.12,
        'sa-east-1': 1.15,
        'ca-central-1': 1.02,
        'me-south-1': 1.12,
        'af-south-1': 1.15,
    },
    
    # ===== STORAGE TIER OPTIMIZATION =====
    # Automatically move backups to cheaper storage tiers based on age
    'enable_storage_tiering': True,  # Enable intelligent tiering
    
    # Warm storage (AWS Backup) - Recent backups, fast restore
    'warm_storage_days': 7,  # Keep in warm storage for 7 days
    'warm_storage_service': 'aws_backup',  # AWS Backup warm storage
    
    # Cold storage (AWS Backup Cold) - Older backups, slower restore
    'cold_storage_days': 30,  # Move to cold after 30 days
    'cold_storage_service': 'aws_backup_cold',  # AWS Backup cold storage
    
    # Archive storage (S3 Glacier) - Long-term retention, cheapest
    'archive_storage_days': 90,  # Move to archive after 90 days
    'archive_storage_service': 's3_glacier_flexible',  # S3 Glacier Flexible Retrieval
    # Options: 's3_glacier_instant', 's3_glacier_flexible', 's3_glacier_deep'
    
    # Deep archive (S3 Glacier Deep Archive) - Compliance/regulatory, rarely accessed
    'deep_archive_enabled': False,  # Enable for compliance requirements
    'deep_archive_days': 365,  # Move to deep archive after 1 year
    'deep_archive_service': 's3_glacier_deep',  # S3 Glacier Deep Archive
    
    # ===== STORAGE TIER STRATEGY BY BACKUP TYPE =====
    'tier_strategy': {
        # Daily backups: Warm → Cold → Archive
        'daily': {
            'warm_days': 7,  # First 7 days in warm storage
            'cold_days': 0,  # No cold storage (go straight to archive)
            'archive_days': 7,  # After 7 days, move to archive until retention expires
        },
        # Weekly backups: Warm → Archive
        'weekly': {
            'warm_days': 7,  # First 7 days in warm storage
            'cold_days': 0,  # No cold storage
            'archive_days': 7,  # After 7 days, move to archive
        },
        # Monthly backups: Warm → Archive → Deep Archive
        'monthly': {
            'warm_days': 30,  # First 30 days in warm storage
            'cold_days': 0,  # No cold storage
            'archive_days': 60,  # After 30 days, move to archive
            'deep_archive_days': 180,  # After 6 months, move to deep archive
        },
    },
    
    # ===== AWS BACKUP PRICING (us-east-1) =====
    # Varies by region - these are us-east-1 rates
    # See: https://aws.amazon.com/backup/pricing/
    'backup_storage_per_gb_month': 0.05,  # $0.05/GB-month for warm storage
    'cold_storage_per_gb_month': 0.01,  # $0.01/GB-month for cold storage (not used)
    'restore_per_gb': 0.02,  # $0.02/GB for restore (not included in ARR)
    
    # ===== STORAGE OPTIMIZATION =====
    # AWS EBS Snapshot Capabilities:
    # ✅ Compression: AWS automatically compresses snapshots (30-50% reduction)
    # ✅ Incremental: AWS only stores changed blocks (3-20% of full backup per day)
    # ❌ Deduplication: AWS does NOT provide automatic cross-volume deduplication
    
    'compression_ratio': 0.7,  # 30% compression (AWS automatic, conservative estimate)
    
    # IMPORTANT: AWS EBS snapshots do NOT provide automatic cross-volume deduplication
    # Setting to 1.0 (no deduplication) because:
    # - AWS does NOT deduplicate across volumes (each volume chain is independent)
    # - Incremental efficiency is already captured in 'incremental_ratio'
    # - Block-level references are part of incremental snapshot mechanism
    # - Using both deduplication_ratio < 1.0 AND incremental_ratio would double-count savings
    # 
    # Previous values:
    # - 0.5 (50% dedup) - Too optimistic, assumed enterprise backup features
    # - 0.8 (20% dedup) - Still optimistic, double-counted incremental benefits
    # 
    # See: BACKUP_COST_DEDUPLICATION_CLARIFICATION.md for detailed analysis
    'deduplication_ratio': 1.0,  # No deduplication (AWS doesn't provide this feature)
    
    'incremental_backup': True,  # Use incremental backups (only changed blocks)
    'incremental_ratio': 0.2,  # Incremental backups are 20% of full backup size (conservative)
    
    # ===== BACKUP GROWTH =====
    'data_growth_rate_monthly': 0.02,  # 2% monthly data growth
    'backup_growth_factor': 1.0,  # No additional growth factor (already in incremental)
    
    # ===== CALCULATION METHOD =====
    # Method 1: Simple (storage × retention days × rate)
    # Method 2: Detailed (daily + weekly + monthly with incremental)
    'calculation_method': 'detailed',  # Use detailed calculation with retention tiers
    
    # ===== REGIONAL PRICING MULTIPLIERS =====
    # Adjust for different regions (us-east-1 = 1.0 baseline)
    'regional_multipliers': {
        'us-east-1': 1.0,
        'us-east-2': 1.0,
        'us-west-1': 1.05,
        'us-west-2': 1.0,
        'eu-west-1': 1.1,
        'eu-central-1': 1.15,
        'ap-southeast-1': 1.15,
        'ap-northeast-1': 1.2,
    },
}


# ============================================================================
# BEDROCK GUARDRAILS CONFIGURATION
# ============================================================================

BEDROCK_GUARDRAIL_CONFIG = {
    'enabled': True,  # Guardrails enabled
    'guardrail_identifier': 'xkx1nmap9jyv',  # Will be populated by setup script
    'guardrail_version': 'DRAFT',  # Or specific version number
    'region': 'us-east-1',  # Guardrail region (must match Bedrock region)
    
    # Guardrail behavior
    'trace': True,  # Log guardrail interventions
    'fail_on_block': False,  # If True, raise exception when content blocked
    
    # Development mode (bypass guardrails for testing)
    'dev_mode': False,  # Guardrails ACTIVE with Claude 3.5 Sonnet (8192 tokens)
}

# Note: Run ./setup_bedrock_guardrail.sh to create and configure guardrails
# This will automatically update the guardrail_identifier and guardrail_version
