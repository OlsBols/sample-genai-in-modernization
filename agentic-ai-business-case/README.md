# AWS Migration Business Case Generator

An AI-powered tool that generates comprehensive AWS migration business cases using multi-agent analysis of your infrastructure data.

## Features

- **Multi-Agent Analysis**: 9 specialized AI agents analyze different aspects of your migration
- **Smart Agent Selection**: Automatically selects agents based on uploaded files
- **Comprehensive Business Case**: Executive summary, current state, costs, strategy, roadmap, benefits/risks
- **Multiple Data Sources**: RVTools, IT inventory, ATX assessments, MRA reports
- **Cost Analysis**: TCO comparison with validation, 3-year projections, migration cost ramp
- **Editable Output**: Edit generated markdown directly in the UI
- **Save & Load**: DynamoDB integration for case persistence with version tracking
- **S3 Storage**: Optional file storage for uploaded documents

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (for UI)
- AWS Account with Bedrock access
- AWS credentials configured

### Installation

```bash
# Install Python dependencies
cd agentic-ai-business-case
pip install -r requirements.txt

# Install UI dependencies
cd ui
npm install
```

### Configuration

1. **AWS Credentials**:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

2. **Bedrock Model Access**:
   - Claude 3 Sonnet is enabled by default in AWS Bedrock

3. **Optional - DynamoDB** (for saving cases):
```bash
cd ui/backend
python setup_dynamodb.py
```

4. **Optional - S3** (for file persistence):
```bash
export S3_BUCKET_NAME=your-bucket-name
python setup_s3.py
```

### Running the Application

**Option 1: UI (Recommended)**
```bash
# Use the convenient start script
cd agentic-ai-business-case/ui
./start.sh

# Or manually:
# Terminal 1: Start backend
cd agentic-ai-business-case/ui/backend
python app.py

# Terminal 2: Start frontend
cd agentic-ai-business-case/ui
npm start
```

Access at: `http://localhost:3000`

**UI Workflow**:
1. Enter project information
2. Upload assessment files (agents auto-selected based on files)
3. Review & generate business case
4. Edit, save, and export results

**Option 2: Command Line**
```bash
cd agentic-ai-business-case
python agents/aws_business_case.py
```

## Cost Estimation

### AWS Bedrock Costs

The tool uses Amazon Bedrock with Claude 3 Sonnet. Costs vary by input size:

### Pricing Model (Claude 3 Sonnet)

- **Input**: $0.003 per 1K tokens
- **Output**: $0.015 per 1K tokens

**Example Calculation (2,027 VMs - Large Dataset)**:
```
Input:  150,000 tokens × $0.003 = $0.45
Output:  25,000 tokens × $0.015 = $0.38
Total: $0.83 per business case
```

### Claude 3.5 Sonnet (Optional Upgrade)

- **Input**: $0.003 per 1K tokens
- **Output**: $0.015 per 1K tokens
- **Max Tokens**: 8,192 (vs 4,096 for Claude 3)
- **Cost**: ~10-20% higher due to more detailed output
- **Benefit**: Better quality, more comprehensive analysis

### Additional AWS Costs

#### DynamoDB (Optional)
- **Storage**: $0.25 per GB-month
- **Typical**: 100 saved cases = ~50 MB = $0.01/month
- **Reads/Writes**: On-demand pricing, negligible for typical usage

#### S3 (Optional)
- **Storage**: $0.023 per GB-month
- **Typical**: 100 cases × 50 MB = 5 GB = $0.12/month
- **Requests**: ~$0.01/month for typical usage

### Monthly Cost Examples

#### Light Usage (10 business cases/month)
- **Bedrock**: 10 × $1.00 = $10.00
- **DynamoDB**: $0.01
- **S3**: $0.05
- **Total**: ~$10/month

#### Medium Usage (50 business cases/month)
- **Bedrock**: 50 × $1.00 = $50.00
- **DynamoDB**: $0.02
- **S3**: $0.12
- **Total**: ~$50/month

#### Heavy Usage (200 business cases/month)
- **Bedrock**: 200 × $1.00 = $200.00
- **DynamoDB**: $0.05
- **S3**: $0.50
- **Total**: ~$200/month

### Cost Optimization Tips

1. **Use Claude 3 Sonnet** (not 3.5) for standard cases
2. **Filter RVTools data** to powered-on VMs only (already implemented)
3. **Limit MAX_ROWS_RVTOOLS** in config.py (default: 2,500)
4. **Reuse saved cases** instead of regenerating
5. **Use lower temperature** for cost calculations (already set to 0.1)

### Cost Monitoring

Monitor your Bedrock usage:
```bash
# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name InvocationCount \
  --dimensions Name=ModelId,Value=anthropic.claude-3-sonnet-20240229-v1:0 \
  --start-time 2025-11-01T00:00:00Z \
  --end-time 2025-11-30T23:59:59Z \
  --period 86400 \
  --statistics Sum
```

Set up billing alerts:
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name bedrock-cost-alert \
  --alarm-description "Alert when Bedrock costs exceed $100" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold
```

## Input Data Requirements

### Required Files

1. **Migration Readiness Assessment** (Markdown or Word)
   - Organizational readiness evaluation
   - Skills assessment
   - Change management readiness
   - **Required for all business cases**

2. **At least ONE infrastructure file**:
   - RVTools Export, OR
   - IT Infrastructure Inventory, OR
   - ATX Assessment files

### Infrastructure Files (Choose One or More)

1. **RVTools Export** (Excel or CSV)
   - vInfo sheet with VM inventory (prioritized for large datasets)
   - Columns: VM name, CPUs, Memory, Storage, OS, Powerstate
   - Recommended: 2,000-2,500 VMs max for optimal performance
   - **Tip**: For large exports, upload vInfo file only to prevent timeouts

2. **IT Infrastructure Inventory** (Excel)
   - Server inventory
   - Application portfolio
   - Database inventory

3. **ATX Assessment** (Excel, PDF, PowerPoint)
   - VMware environment analysis from AWS Transform for VMware
   - Cost projections
   - Technical recommendations
   - Can upload all three formats for comprehensive analysis

### Optional Files

4. **Application Portfolio** (CSV or Excel)
   - Detailed application characteristics
   - Dependencies and business criticality
   - If not provided, industry-standard assumptions are used

## Architecture

### Multi-Agent System (9 Agents)

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Data Sources                        │
│  RVTools │ IT Inventory │ ATX │ MRA │ Frameworks             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │   Phase 1: Analysis     │
        │  (Parallel Execution)   │
        │  Auto-selected based    │
        │  on uploaded files      │
        └────────────┬────────────┘
                     │
    ┌────────────────┼────────────────┬────────────┐
    │                │                │            │
┌───▼───┐      ┌────▼────┐      ┌───▼────┐  ┌───▼───┐
│  RV   │      │   IT    │      │  ATX   │  │  MRA  │
│ Tools │      │Inventory│      │Analysis│  │       │
└───┬───┘      └────┬────┘      └───┬────┘  └───┬───┘
    │               │                │           │
    └───────────────┼────────────────┴───────────┘
                    │
        ┌───────────▼───────────┐
        │  Phase 2: Synthesis   │
        │ (Conditional Edges)   │
        │  Always runs          │
        └───────────┬───────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────┐    ┌────▼────┐    ┌────▼────┐
│Current │    │  Cost   │    │Migration│
│ State  │    │Analysis │    │Strategy │
└───┬────┘    └────┬────┘    └────┬────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
        ┌──────────▼──────────┐
        │ Phase 3: Planning   │
        │  Always runs        │
        └──────────┬──────────┘
                   │
            ┌──────▼──────┐
            │  Migration  │
            │    Plan     │
            └──────┬──────┘
                   │
        ┌──────────▼──────────────┐
        │ Phase 4: Multi-Stage    │
        │   Business Case Gen     │
        │  Always runs            │
        └──────────┬──────────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┐
    │              │              │              │
┌───▼───┐    ┌────▼────┐    ┌───▼────┐    ┌───▼────┐
│Exec   │    │Current  │    │  Cost  │    │Strategy│
│Summary│    │ State   │    │Analysis│    │        │
└───────┘    └─────────┘    └────────┘    └────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┐
    │              │              │              │
┌───▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
│Roadmap │   │Benefits │   │  Recs   │   │Appendix │
│        │   │ & Risks │   │         │   │         │
└────────┘   └─────────┘   └─────────┘   └─────────┘
```

### Key Features

- **Smart Agent Selection**: Phase 1 agents auto-selected based on uploaded files
- **Parallel Execution**: Phase 1 agents run simultaneously for speed
- **Conditional Edges**: Phase 2 waits for all Phase 1 agents to complete
- **Multi-Stage Generation**: 7 sections + appendix generated independently
- **Token Optimization**: Each section gets full token budget (8,192 tokens)
- **Deprecated Services Check**: All agents verify services are not deprecated
- **TCO Validation**: Only shows on-prem comparison if AWS demonstrates savings
- **Relative Timeframes**: Uses Week 1-2, Month 1-3 instead of specific dates

## Configuration

### Model Settings (agents/config.py)

```python
# Model selection
model_id_claude3_7 = "anthropic.claude-3-sonnet-20240229-v1:0"
max_tokens_default = 8192  # Increased for Claude 3.5

# Temperature (lower = more deterministic)
model_temperature = 0.3  # General agents
# Cost agent uses 0.1 for consistency

# Data limits
MAX_ROWS_RVTOOLS = 2500  # Max VMs to analyze
MAX_ROWS_IT_INVENTORY = 1500
MAX_ROWS_PORTFOLIO = 1000

# Multi-stage generation (recommended)
ENABLE_MULTI_STAGE = True
```

### Cost Calculation Formulas

The tool uses standardized formulas for consistency. Recommended to use AWS Pricing calculator, AWS Transform, Migration Evaluator or Migration Portfolio Assessment.

**On-Premises TCO**:
- Hardware: $5,000 per server/year
- VMware licensing: $200 per VM/year
- Windows licensing: $150 per Windows VM/year
- Data center: $1,000 per rack/year
- IT staff: $150,000 per FTE/year (1 FTE per 100 VMs)
- Maintenance: 15% of hardware cost

**AWS Costs (3-Year NURI)**:
- Small VM (1-2 vCPU): $200-300/month
- Medium VM (3-4 vCPU): $400-600/month
- Large VM (5-8 vCPU): $800-1,200/month
- XLarge VM (9+ vCPU): $1,500-2,500/month
- Storage: $0.10 per GB-month

### Deprecated Services Prevention

The tool automatically avoids recommending deprecated AWS services:
- References: `agents/reference/aws_deprecated_services.md`
- Checks against AWS lifecycle page: https://aws.amazon.com/products/lifecycle/
- Examples avoided: Migration Hub, CodeGuru Reviewer, Cognito Sync, etc.
- Recommends current alternatives: MGN, Amazon Q Developer, AppSync, etc.

### Appendix Content

Every business case includes an appendix with AWS Partner Programs:
- MAP (Migration Acceleration Program)
- OLA (Optimization and Licensing Assessment)
- ISV Workload Migration Program
- VMware Migration Programs
- POC Program
- Additional migration resources

## Troubleshooting

### Common Issues

**1. "RVTools data not available"**
- Ensure file is uploaded through UI
- Check file is in `input/` directory
- Verify file matches pattern `rvtool*.xlsx`
- For large datasets, upload vInfo file only

**2. "AWS credentials expired"**
- Refresh AWS credentials: `aws sso login --profile <profile>`
- Or regenerate temporary credentials
- Verify: `aws sts get-caller-identity`

**3. Cost calculations vary between runs**
- This is expected due to AI nature
- Variation should be within ±10% with temperature=0.1
- Use saved cases for consistency
- TCO validation ensures AWS shows savings or focuses on business value

**4. Token limit exceeded**
- Reduce MAX_ROWS_RVTOOLS in config.py
- Filter RVTools to powered-on VMs only
- Upload vInfo file only for large datasets
- Multi-stage generation helps (ENABLE_MULTI_STAGE=True)

**5. Slow generation (>15 minutes)**
- Check dataset size (>2,500 VMs?)
- Verify AWS region latency
- Consider reducing data limits
- Ensure RVTools vInfo prioritization is working

**6. Deprecated services in output**
- Should not happen - agents check against lifecycle page
- If found, update `agents/reference/aws_deprecated_services.md`
- Report issue for prompt strengthening