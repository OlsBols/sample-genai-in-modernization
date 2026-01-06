# Setup Guide

## One-Click Setup

The `setup.sh` script automates the entire installation process.

### What It Does

1. **Prerequisites Check** - Verifies Python 3.8+, Node.js 16+, npm, AWS CLI
2. **AWS Credentials** - Validates AWS credentials are configured
3. **Virtual Environments** - Creates main and UI backend venvs
4. **Dependencies** - Installs Python and Node.js dependencies
5. **AWS Services** - Creates DynamoDB table and S3 bucket (optional)
6. **Directories** - Creates `input/` and `output/logs/` directories
7. **Scripts** - Creates `start-all.sh` and `stop-all.sh` convenience scripts

### Usage

```bash
# 1. Configure AWS credentials (choose one method)

# RECOMMENDED: AWS SSO (for organizations)
aws configure sso
aws sso login --profile <your-profile>
export AWS_PROFILE=<your-profile>

# OR: AWS CLI profile (for IAM users)
aws configure

# OR: Environment variables (for quick testing)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# 2. (Optional) Set S3 bucket for file storage
export S3_BUCKET_NAME=your-bucket-name

# 3. Run setup script
./setup.sh

# 4. Start application
./start-all.sh
```

Access at: `http://localhost:3000`

### What Gets Created

```
project/
├── venv/                    # Main Python virtual environment
├── input/                   # Directory for input files
├── output/                  # Directory for generated business cases
│   └── logs/               # Execution logs
├── ui/
│   ├── backend/
│   │   └── venv/           # UI backend virtual environment
│   └── node_modules/       # UI frontend dependencies
├── start-all.sh            # Start script (created by setup)
└── stop-all.sh             # Stop script (created by setup)
```

### AWS Resources Created

**DynamoDB Table**
- **Name**: `BusinessCases`
- **Primary Key**: `caseId` (String)
- **Purpose**: Stores business case metadata and content
- **Billing**: On-demand (pay per request)

**S3 Bucket** (Optional)
- **Name**: Value of `S3_BUCKET_NAME` environment variable
- **Purpose**: Stores uploaded assessment files
- **Structure**: `s3://bucket-name/{caseId}/filename`

## IAM Permissions

### Required Permissions (Core Functionality)

The application requires access to the following AWS services:

**1. Amazon Bedrock** - AI model access for business case generation
```json
{
  "Sid": "BedrockRequired",
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "bedrock:InvokeModelWithResponseStream"
  ],
  "Resource": [
    "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
    "arn:aws:bedrock:*::foundation-model/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
  ]
}
```

**2. AWS Pricing API** - Real-time pricing data for EC2, RDS, EKS
```json
{
  "Sid": "PricingAPIRequired",
  "Effect": "Allow",
  "Action": [
    "pricing:GetProducts"
  ],
  "Resource": "*"
}
```

### Optional Permissions (Enhanced Features)

**3. DynamoDB** - Case persistence and history (optional)
```json
{
  "Sid": "DynamoDBOptional",
  "Effect": "Allow",
  "Action": [
    "dynamodb:CreateTable",
    "dynamodb:DescribeTable",
    "dynamodb:PutItem",
    "dynamodb:GetItem",
    "dynamodb:UpdateItem",
    "dynamodb:DeleteItem",
    "dynamodb:Query",
    "dynamodb:Scan"
  ],
  "Resource": "arn:aws:dynamodb:*:*:table/BusinessCases"
}
```

**4. Amazon S3** - File storage for uploaded assessments (optional)
```json
{
  "Sid": "S3Optional",
  "Effect": "Allow",
  "Action": [
    "s3:CreateBucket",
    "s3:PutObject",
    "s3:GetObject",
    "s3:DeleteObject",
    "s3:ListBucket",
    "s3:PutBucketVersioning",
    "s3:PutBucketPublicAccessBlock",
    "s3:PutBucketEncryption",
    "s3:PutBucketLifecycleConfiguration",
    "s3:PutBucketTagging"
  ],
  "Resource": [
    "arn:aws:s3:::your-bucket-name",
    "arn:aws:s3:::your-bucket-name/*"
  ]
}
```

**5. Bedrock Guardrails** - PII protection and content filtering (optional)
```json
{
  "Sid": "BedrockGuardrailsOptional",
  "Effect": "Allow",
  "Action": [
    "bedrock:CreateGuardrail",
    "bedrock:GetGuardrail",
    "bedrock:ApplyGuardrail"
  ],
  "Resource": "*"
}
```

### Complete IAM Policy

For convenience, here's a complete policy with all permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockRequired",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
        "arn:aws:bedrock:*::foundation-model/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
      ]
    },
    {
      "Sid": "PricingAPIRequired",
      "Effect": "Allow",
      "Action": [
        "pricing:GetProducts"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DynamoDBOptional",
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable",
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/BusinessCases"
    },
    {
      "Sid": "S3Optional",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:PutBucketVersioning",
        "s3:PutBucketPublicAccessBlock",
        "s3:PutBucketEncryption",
        "s3:PutBucketLifecycleConfiguration",
        "s3:PutBucketTagging"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    },
    {
      "Sid": "BedrockGuardrailsOptional",
      "Effect": "Allow",
      "Action": [
        "bedrock:CreateGuardrail",
        "bedrock:GetGuardrail",
        "bedrock:ApplyGuardrail"
      ],
      "Resource": "*"
    }
  ]
}
```

### How to Apply IAM Policy

**For IAM Users:**
1. Go to IAM Console → Users → Select your user
2. Add permissions → Attach policies directly → Create policy
3. Paste the JSON policy above
4. Name it `AWSMigrationBusinessCaseGeneratorPolicy`
5. Attach to your user

**For IAM Roles (EC2/ECS/Lambda):**
1. Go to IAM Console → Roles → Select your role
2. Add permissions → Create inline policy
3. Paste the JSON policy above
4. Name it `AWSMigrationBusinessCaseGeneratorPolicy`

**Minimum Required:**
- Bedrock access (Claude 3 Sonnet)
- Pricing API access

**Optional but Recommended:**
- DynamoDB (for case persistence)
- S3 (for file storage)
- Bedrock Guardrails (for production deployments)

## Troubleshooting

### "Python 3 is not installed"
```bash
# macOS
brew install python3

# Ubuntu
sudo apt-get install python3
```

### "Node.js is not installed"
```bash
# macOS
brew install node

# Ubuntu
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### "AWS credentials are not configured"
```bash
# Option 1: AWS CLI
aws configure

# Option 2: AWS SSO
aws sso login --profile <profile>

# Option 3: Environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### "'BedrockRuntime' object has no attribute 'converse_stream'"
```bash
# boto3/botocore is too old (requires >= 1.34.90)
source venv/bin/activate
python3 -m pip install --upgrade boto3 botocore

# Verify version
python3 -c "import boto3; print(boto3.__version__)"
```

### "DynamoDB table already exists"
- This is normal if you've run setup before
- The script will continue without error
- To recreate: Delete table in AWS Console first

### "Permission denied: ./setup.sh"
```bash
chmod +x setup.sh
./setup.sh
```

### Script fails partway through
- Check error message for specific issue
- Fix the issue (e.g., install missing dependency)
- Re-run `./setup.sh` - it will skip completed steps

## Manual Cleanup

If you need to start fresh:

```bash
# Remove virtual environments
rm -rf venv/
rm -rf ui/backend/venv/
rm -rf ui/node_modules/

# Remove generated scripts
rm -f start-all.sh stop-all.sh

# Remove AWS resources (optional)
aws dynamodb delete-table --table-name BusinessCases
aws s3 rb s3://$S3_BUCKET_NAME --force

# Then re-run setup
./setup.sh
```

## Input Files

### Required Files

1. **Migration Readiness Assessment** (Markdown, Word, or PDF)
   - Organizational readiness evaluation
   - Skills assessment
   - Change management readiness
   - **Required for all business cases**
   - **Formats**: .md, .docx, .doc, .pdf

2. **At least ONE infrastructure file**:
   - RVTools Export, OR
   - IT Infrastructure Inventory, OR
   - ATX Assessment files

### Infrastructure Files (Choose One)

**1. RVTools Export** (Excel or CSV)
- vInfo sheet with VM inventory
- Columns: VM name, CPUs, Memory, Storage, OS, Powerstate
- Recommended: 2,000-2,500 VMs max for optimal performance
- **Tip**: For large exports, upload vInfo file only to prevent timeouts

**2. IT Infrastructure Inventory** (Excel)
- Server inventory (Servers sheet)
- Database inventory (Databases sheet)
- **Application dependencies** (Application dependency sheet) - **NEW**: For wave planning
- **Server mappings** (Server to application sheet) - **NEW**: For wave planning
- **Database mappings** (Database to application sheet) - **NEW**: For wave planning

**Features**:
- **EC2/RDS Pricing**: Calculates costs from Servers and Databases sheets
- **EKS Analysis**: Uses actual server specs for container migration (not estimates)
- **Wave Planning**: Generates dependency-based migration waves when dependency sheets provided

**Dependency Sheets** (Optional but Recommended):
- `Application dependency` - App-to-app dependencies with criticality
- `Server to application` - Server hosting mappings
- `Database to application` - Database dependencies
- `Server communication` - Network dependencies (optional)

**When dependency sheets provided**: Business case includes detailed wave plan with applications grouped by dependencies  
**When dependency sheets missing**: Business case shows high-level phases with note about dependency mapping

**3. ATX Assessment** (Excel, PDF, PowerPoint)
- VMware environment analysis from AWS Transform for VMware
- Cost projections
- Technical recommendations
- Can upload all three formats for comprehensive analysis

### Optional Files

**4. Application Portfolio** (CSV or Excel)
- Detailed application characteristics
- Dependencies and business criticality
- If not provided, industry-standard assumptions are used
- Used for more accurate 7Rs recommendations

## Configuration

## Project Structure

The codebase is organized into functional modules for maintainability:

```
agents/
├── core/           # Business case generation orchestration
├── analysis/       # Data analysis modules (RVTools, IT Inventory, ATX, MRA)
├── pricing/        # AWS pricing calculations and cost analysis
├── strategy/       # Migration strategy and planning
├── export/         # Excel export and reporting
├── config/         # Configuration management
├── utils/          # Utility functions and helpers
└── prompt_library/ # Agent prompts and templates
```

### Model Settings (`agents/config/config.py`)

```python
# Model selection
model_id_claude3_7 = "anthropic.claude-3-sonnet-20240229-v1:0"
max_tokens_default = 8192

# Temperature (lower = more deterministic)
model_temperature = 0.3  # General agents
# Cost agent uses 0.1 for consistency

# Pricing model (default: 3-Year Compute Savings Plan)
pricing_model = '3yr_compute_sp'  # ~9% cheaper than 3yr_no_upfront
# Options: '3yr_compute_sp', '3yr_ec2_sp', '3yr_no_upfront', 'on_demand'

# Data limits
MAX_ROWS_RVTOOLS = 2500  # Max VMs to analyze
MAX_ROWS_IT_INVENTORY = 1500
MAX_ROWS_PORTFOLIO = 1000

# Multi-stage generation (recommended)
ENABLE_MULTI_STAGE = True
```

### EKS Configuration (`agents/config/config.py`)

```python
# EKS Configuration
EKS_CONFIG = {
    'enabled': True,  # Enable/disable EKS analysis
    'strategy': 'hybrid',  # 'hybrid', 'all-eks', or 'disabled'
    'enable_graviton': True,  # Enable AWS Graviton (ARM) for 20% savings
    'consolidation_ratios': {
        'linux': {'small': 3.5, 'medium': 2.5, 'large': 1.75, 'xlarge': 1.25},
        'windows': {'small': 2.0, 'medium': 1.5, 'large': 1.25, 'xlarge': 1.1}
    },
    'worker_nodes': [
        # 35+ instance types across 5 generations
        # Includes Graviton (m7g, c7g, r7g) if enabled
        'm7i.xlarge', 'm7i.2xlarge', 'm7i.4xlarge', ...
    ],
    'spot_instance_config': {
        'spot_percentage': 30,
        'on_demand_percentage': 40,
        'reserved_percentage': 30
    }
}

# EKS Recommendation Thresholds (Python-based decision tree)
EKS_RECOMMENDATION_THRESHOLDS = {
    'tier2_max_premium': 0.20,  # Recommend EKS up to 20% premium
    'tier3_max_premium': 0.50,  # Mention EKS up to 50% premium
}
```

### AWS Backup Configuration (`agents/config/config.py`)

```python
# AWS Backup Configuration
BACKUP_CONFIG = {
    'enabled': True,  # Enable/disable backup cost calculations
    'enable_storage_tiering': True,  # Intelligent tiering for cost savings
    'deep_archive_enabled': False,  # Enable S3 Glacier Deep Archive tier
    
    # Production retention policy
    'production': {
        'daily_retention_days': 7,
        'weekly_retention_weeks': 2,
        'monthly_retention_months': 12
    },
    
    # Pre-production retention policy
    'pre_production': {
        'daily_retention_days': 3,
        'weekly_retention_weeks': 1,
        'monthly_retention_months': 0
    },
    
    # Storage optimization
    'compression_ratio': 0.7,  # 70% compression
    'deduplication_ratio': 0.5,  # 50% deduplication
    'incremental_ratio': 0.2,  # 20% incremental backup size
    
    # EKS backup configuration
    'backup_eks': True,  # Enable EKS persistent volume backups
    'eks_stateful_percentage': 0.30,  # 30% of workloads are stateful
    'eks_avg_storage_per_workload_gb': 100,
    
    # Environment detection
    'environment_detection': {
        'enabled': True,
        'prod_patterns': ['prod', 'production', 'prd'],
        'preprod_patterns': ['dev', 'test', 'uat', 'staging', 'qa', 'development']
    },
    
    # Pricing
    'use_pricing_api': True,  # Use AWS Pricing API for real-time rates
    'fallback_rates': {
        'backup_storage_per_gb_month': 0.05,
        's3_glacier_flexible_per_gb_month': 0.0036,
        's3_glacier_deep_per_gb_month': 0.00099
    }
}
```

**Backup Cost Features**:
- **Automatic Integration**: Backup costs automatically included in all calculations
- **Environment Detection**: Automatically detects production vs pre-production from VM names
- **Intelligent Tiering**: Warm → Archive → Deep Archive (up to 85% savings)
- **EKS Support**: Includes persistent volume backups for stateful workloads
- **Real-Time Pricing**: Uses AWS Pricing API with regional multipliers

**Disable Backup Costs**:
```python
BACKUP_CONFIG = {
    'enabled': False,  # Disable backup cost calculations
    ...
}
```

**Customize Retention**:
```python
# Example: Longer production retention
'production': {
    'daily_retention_days': 14,  # 2 weeks instead of 7 days
    'weekly_retention_weeks': 4,  # 1 month instead of 2 weeks
    'monthly_retention_months': 24  # 2 years instead of 1 year
}
```

### AWS Credentials

The system uses boto3's default credential chain and supports multiple authentication methods.

**Method 1: AWS SSO (Recommended for Organizations)**
```bash
# One-time setup
aws configure sso

# Daily login (session expires after 8-12 hours)
aws sso login --profile <your-profile>
export AWS_PROFILE=<your-profile>

# Verify
aws sts get-caller-identity
```

**Method 2: AWS CLI Profile (Recommended for IAM Users)**
```bash
# One-time setup
aws configure

# Verify
aws sts get-caller-identity

# No re-login needed (credentials don't expire)
```

**Method 3: Environment Variables (Quick Testing)**
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# Verify
aws sts get-caller-identity
```

**Method 4: IAM Role (EC2/ECS/Lambda)**
```bash
# No configuration needed!
# Credentials are automatic when running on AWS infrastructure
```

### S3 Storage (Optional)

```bash
export S3_BUCKET_NAME=your-bucket-name
cd ui/backend
source venv/bin/activate
python3 setup_s3.py
```

### Bedrock Guardrails (Optional - Recommended for Production)

Guardrails provide PII protection, hallucination prevention, and content filtering.

**Setup**:
```bash
# Run guardrail setup script
./setup_bedrock_guardrail.sh

# This will:
# 1. Create Bedrock Guardrail with policies
# 2. Update agents/config/config.py with guardrail ID
# 3. Enable guardrails automatically
```

**What Guardrails Do**:
- ✅ **PII Protection**: Anonymize emails, names, IPs, phone numbers
- ✅ **Data Security**: Block SSN, credit cards, passwords
- ✅ **Hallucination Prevention**: Ensure AI uses actual data (contextual grounding)
- ✅ **Content Filtering**: Block inappropriate content
- ✅ **Topic Filtering**: Block off-topic requests (financial advice, legal advice)

**Cost Impact**:
- Overhead: ~51% increase (~$0.06 per business case)
- Worth it for: Production, GDPR/HIPAA compliance, enterprise customers

**To Disable** (for development):
```python
# Edit agents/config/config.py
BEDROCK_GUARDRAIL_CONFIG = {
    'enabled': False,  # Disable guardrails
    # OR
    'dev_mode': True,  # Bypass guardrails in development
}
```

**For detailed information on Bedrock Guardrails setup, refer to the setup script: `./setup_bedrock_guardrail.sh`**

## Next Steps After Setup

1. **Start the application**: `./start-all.sh`
2. **Access UI**: Open http://localhost:3000
3. **Upload files**: Use the UI to upload assessment files
4. **Generate business case**: Follow the 4-step wizard
5. **Edit and export**: Customize the generated business case

## Environment Variables

### Required
- `AWS_ACCESS_KEY_ID` - AWS access key (or use aws configure)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (or use aws configure)
- `AWS_DEFAULT_REGION` - AWS region (default: us-east-1)

### Optional
- `S3_BUCKET_NAME` - S3 bucket for file storage (enables S3 features)

## Benefits of One-Click Setup

- ✅ **Saves Time**: 10+ manual commands → 1 script
- ✅ **Prevents Errors**: Automated checks and validation
- ✅ **Consistent**: Same setup for all users
- ✅ **Idempotent**: Safe to run multiple times
- ✅ **Informative**: Clear progress and error messages
- ✅ **Complete**: Sets up everything including AWS resources

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify AWS credentials: `aws sts get-caller-identity`
3. Check Python version: `python3 --version`
4. Check Node version: `node --version`
5. Review setup script output for error messages
6. Check logs in `output/logs/` directory

## Related Documentation

- `README.md` - Project overview and quick start
- `SYSTEM_ARCHITECTURE.md` - Technical architecture and data flow
- `BEDROCK_GUARDRAILS_GUIDE.md` - Guardrails setup and configuration
- `EKS_PRICING_DESIGN.md` - EKS pricing design and recommendation logic
