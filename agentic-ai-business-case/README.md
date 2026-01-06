# AWS Migration Business Case Generator

**Version 1.0** | Production Ready

AI-powered tool that generates comprehensive AWS migration business cases using multi-agent analysis of your infrastructure data.

## Key Features

✅ **Real-Time AWS Pricing** - AWS Price List API for EC2, RDS, EKS (all pricing models)  
✅ **Three Input Types** - RVTools, IT Infrastructure Inventory, or ATX assessments  
✅ **Dependency-Based Wave Planning** - Intelligent migration waves from IT Inventory dependencies  
✅ **EKS Container Analysis** - Python-based recommendation engine with 4-tier decision tree  
✅ **IT Inventory EKS Support** - Uses actual server specs for accurate EKS categorization  
✅ **AWS Backup Cost Analysis** - Intelligent tiering with prod/pre-prod differentiation (up to 85% savings)  
✅ **Bedrock Guardrails** - PII protection, hallucination prevention (optional)  
✅ **Excel Exports** - Detailed cost breakdowns with VM/server-level mapping and backup costs  
✅ **Smart Agent Selection** - Only runs agents for available input files

## Generated Outputs

### Business Case Document
Comprehensive markdown document with 7 sections:
1. **Executive Summary** - High-level overview, costs, and recommendation
2. **Current State Analysis** - Infrastructure inventory and assessment
3. **Migration Strategy** - 7Rs distribution and approach
4. **Cost Analysis** - Detailed AWS costs with pricing breakdowns
5. **Migration Roadmap** - Timeline, phases, and wave planning
6. **Benefits & Risks** - Business value and risk mitigation
7. **Recommendations** - Next steps and action items
8. **Appendix** - Technical details and AWS programs

### Excel Exports

**For RVTools Input:**
- **VM to EC2 Mapping** (`vm_to_ec2_mapping.xlsx`)
  - VM inventory with recommended EC2 instances
  - Per-VM cost breakdown (compute, storage, backup)
  - Instance type recommendations with pricing
  - Summary sheet with total costs
  - Backup Summary sheet (when backup costs enabled)

**For IT Infrastructure Inventory Input:**
- **IT Inventory Pricing** (`it_inventory_aws_pricing_*.xlsx`)
  - **Pricing Comparison** - Option 1 (EC2 Instance SP + RDS 3yr) vs Option 2 (Compute SP + RDS 1yr)
  - **EC2 Details** - Server-by-server breakdown with right-sizing and instance recommendations (both options)
  - **RDS Details** - Database-by-database breakdown with engine mapping and pricing (both options)
  - **EC2 Comparison** - Side-by-side EC2 pricing comparison
  - **RDS Comparison** - Side-by-side RDS pricing comparison with upfront fees
  - **Summary Sheets** - Aggregated costs by instance type
  - **Backup Summary** - Production/pre-production breakdown with storage tiering savings (when enabled)

**EKS Migration Analysis** (`eks_migration_analysis.xlsx`) - When EKS enabled
- **Migration Strategy Summary** - Executive overview with recommendation
- **EKS VM Categorization** - VMs by OS and size (Linux/Windows, Small/Medium/Large/XLarge)
- **EKS Cluster Design** - Worker node configuration and sizing
- **EC2 vs EKS Comparison** - Cost comparison across options
- **EKS ROI Analysis** - Financial justification and benefits

## Quick Start

```bash
# 1. Configure AWS credentials
aws configure

# 2. (Optional) Set S3 bucket for file storage
export S3_BUCKET_NAME=your-bucket-name

# 3. Run setup (one-time)
./setup.sh

# 4. (Optional) Enable guardrails for production
./setup_bedrock_guardrail.sh

# 5. Start application
./start-all.sh
```

Access at: `http://localhost:3000`

**Prerequisites**: Python 3.8+, Node.js 16+, AWS account with Bedrock access

**Detailed setup**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)

### Bedrock Guardrails (Optional)

Production-grade content safety and compliance:

```bash
./setup_bedrock_guardrail.sh
```

**Protections**: PII anonymization, hallucination prevention, content filtering  
**Cost**: ~$0.06 per business case  
**Use case**: Production deployments, GDPR/HIPAA compliance

### Basic Usage

```bash
./start-all.sh   # Start application
./stop-all.sh    # Stop application
```

**Command-line mode:**
```bash
source venv/bin/activate
python agents/core/aws_business_case.py
```

## Core Capabilities

**Analysis**
- Multi-agent system (9 specialized agents) with parallel execution
- Smart agent selection (only runs agents for available input files)
- Pre-computed infrastructure summaries (deterministic, no LLM caching issues)
- MRA integration for organizational readiness assessment
- **Dependency-based wave planning** from IT Infrastructure Inventory
- **IT Inventory EKS analysis** using actual server specifications
- **AWS Backup cost analysis** with intelligent storage tiering and environment detection

**EKS Container Migration** (✅ Production Ready)
- **Python-based recommendation engine** - Deterministic 4-tier decision tree
- **Tier 1**: EKS cheaper → Recommend EKS
- **Tier 2**: EKS 0-20% premium → Recommend EKS (strategic value)
- **Tier 3**: EKS 20-50% premium → Recommend EC2 (mention EKS)
- **Tier 4**: EKS 50%+ premium → Recommend EC2 only
- OS-aware VM categorization, consolidation ratios (2-3.5x Linux, 1.1-2x Windows)
- 35+ worker node types (Intel, AMD, Graviton), Spot instance strategy (30/40/30 mix)
- Excel export with 5 tabs (Strategy, Categorization, Cluster Design, Cost Comparison, ROI)

**AWS Backup Cost Analysis** (✅ Production Ready)
- **Intelligent storage tiering** - Warm → Archive → Deep Archive (up to 85% savings)
- **Environment differentiation** - Production vs pre-production retention policies
- **Automatic detection** - From VM names, folders, clusters
- **EKS persistent volumes** - Backup costs for stateful workloads
- **Real-time pricing** - AWS Pricing API with regional multipliers
- **Excel integration** - Backup cost column and detailed Backup Summary sheet

**Security & Compliance** (Optional)
- Bedrock Guardrails: PII anonymization, hallucination prevention, content filtering
- GDPR/HIPAA compliance ready
- Cost: ~$0.06 per business case (~51% overhead)

**Output**
- Comprehensive business case (7 sections + appendix)
- Excel exports with detailed cost breakdowns
- Editable markdown in UI
- DynamoDB persistence with version tracking
- S3 storage for uploaded documents (optional)

## Cost Estimation

### AWS Bedrock Costs (Claude 3 Sonnet)

- **Input**: $0.003 per 1K tokens
- **Output**: $0.015 per 1K tokens

**Example** (2,027 VMs - Large Dataset):
```
Input:  150,000 tokens × $0.003 = $0.45
Output:  25,000 tokens × $0.015 = $0.38
Total: ~$0.83 per business case
```

### Monthly Cost Examples

| Usage | Business Cases | Bedrock | DynamoDB | S3 | Total |
|-------|---------------|---------|----------|----|----|
| Light | 10/month | $10 | $0.01 | $0.05 | ~$10/month |
| Medium | 50/month | $50 | $0.02 | $0.12 | ~$50/month |
| Heavy | 200/month | $200 | $0.05 | $0.50 | ~$200/month |

### Cost Optimization

- Use Claude 3 Sonnet (not 3.5) for standard cases
- Filter RVTools to powered-on VMs only (already implemented)
- Limit MAX_ROWS_RVTOOLS in config.py (default: 2,500)
- Reuse saved cases instead of regenerating

## Input Data Requirements

**Required**: Migration Readiness Assessment (Markdown, Word, or PDF)

**Choose ONE infrastructure input**:
1. **RVTools Export** (Excel/CSV) - VMware environment, most comprehensive
2. **IT Infrastructure Inventory** (Excel) - Servers + Databases + Dependencies
3. **ATX Assessment** (Excel/PDF/PowerPoint) - AWS Transform for VMware

**Optional**: Application Portfolio (CSV/Excel) - For accurate 7Rs recommendations

**IT Infrastructure Inventory Features**:
- **EC2/RDS Pricing**: Calculates costs from Servers and Databases sheets
- **EKS Analysis**: Uses actual server specs for container migration recommendations
- **Wave Planning**: Generates dependency-based migration waves from dependency sheets

**Details**: See [SETUP_GUIDE.md](SETUP_GUIDE.md#input-files)

## Architecture

### Multi-Agent System (9 Agents)

```
Input Data Sources
  RVTools | IT Inventory | ATX | MRA
         ↓
Phase 1: Analysis (Parallel, Auto-Selected)
  ├─ RVTools Analysis (if file exists)
  ├─ IT Inventory Analysis (if file exists)
  ├─ ATX Analysis (if file exists)
  └─ MRA Analysis (if file exists)
         ↓
Phase 2: Synthesis (Wait for Phase 1)
  ├─ Current State Analysis
  ├─ Cost Analysis (calls pricing tools)
  └─ Migration Strategy
         ↓
Phase 3: Planning (Wait for Phase 2)
  └─ Migration Plan (with dependency-based wave planning)
         ↓
Phase 4: Multi-Stage Business Case
  ├─ Executive Summary
  ├─ Current State
  ├─ Migration Strategy
  ├─ Cost Analysis
  ├─ Migration Roadmap
  ├─ Benefits & Risks
  ├─ Recommendations
  └─ Appendix
```

**Key Features**:
- Smart agent selection (only runs agents for available files)
- Parallel execution (Phase 1 agents run simultaneously)
- Conditional edges (Phase 2 waits for all active Phase 1 agents)
- Multi-stage generation (7 sections + appendix)

**Details**: See [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)

## Project Structure

```
agents/
├── core/           # Business case generation orchestration
├── analysis/       # Data analysis (RVTools, IT Inventory, ATX, MRA)
├── pricing/        # AWS pricing calculations and cost analysis
├── strategy/       # Migration strategy and planning
├── export/         # Excel export and reporting
├── config/         # Configuration management
├── utils/          # Utility functions and helpers
└── prompt_library/ # Agent prompts and templates
```

## Configuration

**Key settings** (`agents/config/config.py`):

```python
# Model
model_id_claude3_7 = "anthropic.claude-3-sonnet-20240229-v1:0"
model_temperature = 0.3  # General agents (0.1 for cost calculations)

# Pricing
pricing_model = '3yr_compute_sp'  # 3-Year Compute Savings Plan (default)
# Options: '3yr_compute_sp', '3yr_ec2_sp', '3yr_no_upfront', 'on_demand'

# Data limits
MAX_ROWS_RVTOOLS = 2500  # Max VMs to analyze

# EKS Configuration
EKS_CONFIG = {
    'enabled': True,
    'strategy': 'hybrid',  # 'hybrid', 'all-eks', or 'disabled'
    'enable_graviton': True,  # AWS Graviton (ARM) for 20% savings
}

# EKS Recommendation Thresholds (Python-based decision tree)
EKS_RECOMMENDATION_THRESHOLDS = {
    'tier2_max_premium': 0.20,  # Recommend EKS up to 20% premium
    'tier3_max_premium': 0.50,  # Mention EKS up to 50% premium
}

# AWS Backup Configuration
BACKUP_CONFIG = {
    'enabled': True,  # Enable/disable backup cost calculations
    'enable_storage_tiering': True,  # Intelligent tiering for cost savings
    'production': {
        'daily_retention_days': 7,
        'weekly_retention_weeks': 2,
        'monthly_retention_months': 12
    },
    'pre_production': {
        'daily_retention_days': 3,
        'weekly_retention_weeks': 1,
        'monthly_retention_months': 0
    },
}

# Guardrails (optional)
BEDROCK_GUARDRAIL_CONFIG = {
    'enabled': True,  # Set to False to disable
    'guardrail_identifier': 'xkx1nmap9jyv',  # Auto-populated by setup script
}
```

**Full configuration guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md#configuration)

## Troubleshooting

**Quick fixes**:
- AWS credentials: `aws sts get-caller-identity`
- Restart: `./stop-all.sh && ./start-all.sh`
- Check logs: `output/logs/agent_execution_*.log`
- Re-run setup: `./setup.sh` (safe to re-run)

**Common issues**:
- boto3 version: `pip install --upgrade boto3 botocore` (requires >= 1.34.90)
- AWS SSO expired: `aws sso login --profile <profile>`
- Port in use: Check if services already running

**Comprehensive troubleshooting**: [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting)

## Documentation

- `SETUP_GUIDE.md` - Installation and configuration
- `SYSTEM_ARCHITECTURE.md` - Technical architecture and data flow

## EKS Container Migration (Production Ready)

**Python-Based Recommendation Engine**
- Deterministic 4-tier decision tree (no LLM guessing)
- Configurable thresholds in `agents/config/config.py`
- Tier 1: EKS cheaper → Recommend EKS
- Tier 2: EKS 0-20% premium → Recommend EKS (strategic value)
- Tier 3: EKS 20-50% premium → Recommend EC2 (mention EKS)
- Tier 4: EKS 50%+ premium → Recommend EC2 only

**Features**
- OS-aware VM categorization (Linux/Windows, Small/Medium/Large/XLarge)
- Consolidation ratios: 2-3.5x Linux, 1.1-2x Windows
- 35+ worker node types (Intel, AMD, Graviton)
- Spot instance strategy (30% Spot, 40% On-Demand, 30% Reserved)
- MRA-based strategy recommendations
- Excel export with 5 professional tabs

**Configuration** (`agents/config/config.py`):
```python
EKS_CONFIG = {
    'enabled': True,
    'strategy': 'hybrid',  # 'hybrid', 'all-eks', or 'disabled'
    'enable_graviton': True,  # 20% cost savings for Linux
}

EKS_RECOMMENDATION_THRESHOLDS = {
    'tier2_max_premium': 0.20,  # Recommend EKS up to 20% premium
    'tier3_max_premium': 0.50,  # Mention EKS up to 50% premium
}
```

## Dependency-Based Wave Planning (NEW)

**Intelligent Migration Waves from IT Infrastructure Inventory**

**What It Does**:
- Analyzes application dependencies from IT Inventory
- Generates migration waves based on dependency chains
- Wave 1: Independent applications (no dependencies)
- Wave 2+: Applications grouped by dependencies

**Required IT Inventory Sheets**:
- `Applications` - Application list with IDs and criticality
- `Application dependency` - App-to-app dependencies
- `Server to application` - Server hosting mappings
- `Database to application` - Database dependencies

**Output**:
```
Wave 1 (Months 1-3): 12 independent apps, 79 servers
Wave 2 (Months 4-6): 2 dependent apps, 20 servers
```

**Benefits**:
- Data-driven wave assignments (not generic phases)
- Risk reduction (independent apps migrated first)
- Server-specific assignments with actual names
- Transparent when dependencies unavailable

**Configuration**: Automatic when IT Inventory has dependency sheets

## IT Infrastructure Inventory EKS Support (NEW)

**Accurate EKS Analysis Using Actual Server Specs**

**What It Does**:
- Reads actual server specifications from IT Inventory Servers sheet
- Uses real vCPU, RAM, OS per server for EKS categorization
- Applies same EKS rules as RVTools (OS-aware, size-based)

**Before**: Synthetic servers with estimated sizes  
**After**: Actual server specs for accurate analysis

**Example**:
```
Input (IT Inventory):
- WebServer-01: 4 vCPU, 16 GB, Red Hat Linux
- AppServer-02: 2 vCPU, 8 GB, Ubuntu
- DBServer-03: 8 vCPU, 32 GB, Windows Server

Output:
- WebServer-01 → EKS (Linux, suitable size)
- AppServer-02 → EKS (Linux, small)
- DBServer-03 → EC2 (Windows, large)
```

**Benefits**:
- Accurate EKS categorization per server
- Real server names in recommendations
- Precise cluster sizing
- Better cost estimates

**Configuration**: Automatic when IT Inventory uploaded

## AWS Backup Cost Analysis (Production Ready)

**Intelligent Backup Cost Calculation with Storage Tiering**

**What It Does**:
- Calculates AWS Backup costs for all VMs/servers
- Differentiates production vs pre-production environments
- Applies intelligent storage tiering for cost optimization
- Includes EKS persistent volume backups

**Key Features**:

**1. Environment Detection**
- Automatic detection from VM names: `prod`, `production`, `prd` → Production
- Pre-production patterns: `dev`, `test`, `uat`, `staging`, `qa`
- Folder/cluster analysis for environment classification
- Default: Production (safer for cost estimation)

**2. Retention Policies**
```
Production:
- Daily backups: 7 days retention
- Weekly backups: 2 weeks retention
- Monthly backups: 1 year retention

Pre-Production:
- Daily backups: 3 days retention
- Weekly backups: 1 week retention
- Monthly backups: None
```

**3. Intelligent Storage Tiering**
- **Warm** (AWS Backup): Days 1-7, $0.05/GB-month
- **Archive** (S3 Glacier Flexible): Days 8-90, $0.0036/GB-month
- **Deep Archive** (S3 Glacier Deep): Days 90+, $0.00099/GB-month
- **Savings**: Up to 85% vs keeping all backups in warm storage

**4. Compression & Deduplication**
- Compression: 70% (configurable)
- Deduplication: 50% (configurable)
- Combined: ~65% storage reduction

**5. EKS Support**
- Persistent volume backups for stateful workloads
- 30% stateful workload assumption (configurable)
- 100GB average storage per workload (configurable)

**Example Output**:
```
Total Monthly Cost (Compute/Storage): $485.72
Total Monthly Backup Cost: $132.09
Total Monthly Cost (with Backup): $617.81

Backup Breakdown:
- Production VMs: 2 VMs, $97.50/month
- Pre-Production VMs: 1 VM, $34.59/month
- Storage Tiering Savings: $19.65 (17.5%)
- Retention: Daily (7d), Weekly (2w), Monthly (1yr)
```

**Excel Export Integration**:
- "Backup Monthly Cost ($)" column in VM to EC2 Mapping
- Cost breakdown in Summary sheet
- NEW: Backup Summary sheet with detailed breakdown
  - Overall backup costs with tiering savings
  - Production environment details
  - Pre-production environment details
  - Retention policy breakdown
  - Storage tier breakdown (warm/archive/deep)

**Configuration** (`agents/config/config.py`):
```python
BACKUP_CONFIG = {
    'enabled': True,  # Enable/disable backup costs
    'enable_storage_tiering': True,  # Intelligent tiering
    'production': {
        'daily_retention_days': 7,
        'weekly_retention_weeks': 2,
        'monthly_retention_months': 12
    },
    'pre_production': {
        'daily_retention_days': 3,
        'weekly_retention_weeks': 1,
        'monthly_retention_months': 0
    },
    'compression_ratio': 0.7,  # 70% compression
    'deduplication_ratio': 0.5,  # 50% deduplication
    'backup_eks': True,  # Enable EKS backups
}
```

**Cost Example** (100 VMs, 500GB average storage):
```
Without Tiering: $875/month
With Tiering: $172.50/month
Savings: $702.50/month (80%)
```

## Version Information

**Current Version**: 1.0 (Production Ready)  
**Release Date**: January 2026  
**Python**: 3.8+  
**Node.js**: 16+  
**AWS Services**: Bedrock (Claude 3 Sonnet), DynamoDB (optional), S3 (optional)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review `SETUP_GUIDE.md` for setup issues
3. Review `SYSTEM_ARCHITECTURE.md` for technical details
4. Check AWS Bedrock console for errors
5. Verify AWS credentials: `aws sts get-caller-identity`
6. Check logs in `output/logs/` directory

## License

MIT License - See LICENSE file for details
