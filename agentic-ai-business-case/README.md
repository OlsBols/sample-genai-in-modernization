# AWS Migration Business Case Generator

## Overview

An **AI-powered multi-agent system** that automatically generates comprehensive AWS migration business cases by analyzing infrastructure data, organizational readiness, and producing detailed migration strategies, cost projections, and phase-specific execution plans.

**Key Benefit**: Reduces business case development time from **weeks to hours** while maintaining professional quality and industry-standard frameworks.

---

## 🎯 What This Does

This system analyzes your infrastructure and organizational data to automatically generate:

✅ **Current State Analysis** - Comprehensive infrastructure and organizational assessment  
✅ **AWS Cost Projections** - 3-year TCO with multiple pricing models (On-Demand, RI, Savings Plans)  
✅ **Migration Strategy** - Application categorization using AWS 6Rs framework  
✅ **Migration Plan** - Phase-by-phase roadmap (Assess, Mobilize, Migrate, Modernize)  
✅ **Business Case Document** - Executive-ready comprehensive proposal  

---

## 🏗️ Architecture

**9 AI Agents** working in parallel and sequence:

```
Phase 1 (Parallel):
├── IT Inventory Analysis
├── RVTool VMware Analysis
├── ATX VMware Analysis
└── MRA Organizational Readiness

Phase 2 (Parallel):
├── Current State Synthesis
├── AWS Cost Analysis
└── Migration Strategy (6Rs)

Phase 3:
└── Migration Plan (MAP Phases)

Phase 4:
└── Business Case Generation
```

**Total Runtime**: 6-10 minutes  
**Output**: Professional business case document

---

## 📁 Project Structure

```
agentic-ai-business-case/
├── README.md                           # This file
├── EXECUTIVE_SUMMARY.md                # Detailed value proposition for AWS Partners
├── QUICK_START.md                      # Quick start guide
├── CLEANUP_SUMMARY.md                  # Architecture cleanup documentation
│
├── input/                              # Input files and framework documents
│   ├── Test-Data-Set-Demo-Excel-V2.xlsx                    # Sample IT inventory
│   ├── rvtool.csv                                          # Sample RVTool data
│   ├── analysis.xlsx                                       # Sample ATX data
│   ├── report.pdf                                          # Sample ATX report
│   ├── business_case.pptx                                  # Sample ATX presentation
│   ├── aws-customer-migration-readiness-assessment.md      # Sample MRA
│   ├── aws-migration-strategy-6rs-framework.md             # 6Rs framework reference
│   └── aws-migration-plan-framework.md                     # MAP framework reference
│
├── output/                             # Generated business case documents
│   └── aws_business_case.md            # Sample generated business case
│
├── agents/                             # AI agent implementations
│   ├── aws_business_case.py            # Main orchestrator (RUN THIS)
│   ├── inventory_analysis.py           # IT inventory agent
│   ├── rv_tool_analysis.py             # RVTool agent
│   ├── atx_analysis.py                 # ATX agent
│   ├── mra_analysis.py                 # MRA agent
│   ├── migration_strategy.py           # Migration strategy agent
│   ├── migration_plan.py               # Migration plan agent
│   ├── config.py                       # Configuration
│   ├── prompt_library/                 # Centralized prompts
│   ├── WORKFLOW.md                     # Workflow documentation
│   └── COMPLETE_AGENT_ARCHITECTURE.md  # Architecture details
│
├── test/                               # Test scripts
│   ├── README.md                       # Test documentation
│   ├── test_atx_data.py               # Test ATX data extraction
│   ├── test_mra_data.py               # Test MRA data extraction
│   └── test_migration_strategy_data.py # Test migration strategy
│
└── business-case-agents/
    └── requirements.txt                # Python dependencies
```

---

## 📥 Input Files Explained

### Required Input Files (Place in `input/` folder)

| File | Purpose | Description | Agent |
|------|---------|-------------|-------|
| **Test-Data-Set-Demo-Excel-V2.xlsx** | IT Infrastructure Inventory | General IT asset inventory with servers, storage, databases, applications | IT Inventory Analysis |
| **rvtool.csv** | RVTool VMware Assessment | VMware environment data exported from RVTool | RVTool VMware Analysis |
| **analysis.xlsx** | ATX VMware Environment Data | AWS Transform for VMware assessment - environment data | ATX VMware Analysis |
| **report.pdf** | ATX Technical Assessment | AWS Transform for VMware - detailed technical report | ATX VMware Analysis |
| **business_case.pptx** | ATX Business Case Presentation | AWS Transform for VMware - executive presentation | ATX VMware Analysis |
| **aws-customer-migration-readiness-assessment.md** | Migration Readiness Assessment | Organizational readiness evaluation (MRA) | MRA Analysis |

### Framework Reference Files (Already in `input/` folder)

| File | Purpose | Used By |
|------|---------|---------|
| **aws-migration-strategy-6rs-framework.md** | 6Rs migration strategy guidance with ranges (30-40/10-20/10-20/5-10/5-10/5-10) | Migration Strategy Agent |
| **aws-migration-plan-framework.md** | MAP methodology (Assess, Mobilize, Migrate, Modernize) | Migration Plan Agent |

---

## 🚀 Quick Start

### Prerequisites

1. **AWS Account** with Bedrock access
2. **Python 3.x** installed
3. **AWS Credentials** configured with Bedrock permissions

### Installation

#### Core Agent Dependencies

```bash
# 1. Install agent dependencies (required for business case generation)
cd agentic-ai-business-case/agents
pip install -r requirements.txt
```

**Required Packages:**
- `strands-agents` - AWS Bedrock agent framework
- `strands-agents-tools` - Agent tools and utilities
- `boto3>=1.34.0` - AWS SDK for Python
- `botocore>=1.34.0` - AWS SDK core
- `pyyaml>=6.0` - YAML parsing
- `pandas>=2.0.0` - Data analysis
- `python-dotenv>=1.0.0` - Environment variables
- `requests>=2.31.0` - HTTP library
- `openpyxl>=3.1.0` - Excel file handling
- `python-pptx>=0.6.23` - PowerPoint file handling
- `reportlab>=4.0.0` - PDF generation
- `PyPDF2>=3.0.0` - PDF file handling

#### UI Dependencies (Optional)

If using the web UI:

```bash
# Backend dependencies
cd agentic-ai-business-case/ui/backend
pip install -r requirements.txt

# Frontend dependencies
cd agentic-ai-business-case/ui
npm install
```

#### AWS Credentials

```bash
# Option 1: AWS CLI (recommended)
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Configuration

Edit `agents/config.py` to set your paths:

```python
input_folder_dir_path = "/path/to/agentic-ai-business-case/"
output_folder_dir_path = "/path/to/agentic-ai-business-case/output/"
```

### Run the Business Case Generator

```bash
cd agentic-ai-business-case/agents
python aws_business_case.py
```

**Expected Runtime**: 6-10 minutes  
**Output Location**: `output/aws_business_case.md`

---

## 📊 Sample Files

### Input Samples
Sample input files are provided in the `input/` folder:
- ✅ IT inventory (Excel)
- ✅ RVTool VMware data (CSV)
- ✅ ATX assessment outputs (Excel, PDF, PowerPoint)
- ✅ MRA organizational readiness (Markdown)

### Output Sample
A sample generated business case is available in `output/aws_business_case.md` showing:
- Current state analysis
- AWS cost projections
- Migration strategy with 6Rs categorization
- Migration plan with MAP phases
- Risk assessment and success metrics

---

## 🎓 Key Features

### 1. Comprehensive Data Integration
- Analyzes multiple data sources simultaneously
- Cross-validates findings across assessments
- Provides unified, consistent recommendations

### 2. Intelligent Decision-Making
- **Windows Server OLA**: Automatically flags when >20 servers (30-50% savings opportunity)
- **Phase Readiness**: Determines if further assessment needed or ready to proceed
- **Context-Aware**: Adapts recommendations based on customer situation

### 3. Industry-Standard Frameworks
- **6Rs Migration Strategy**: Rehost, Replatform, Repurchase, Refactor, Retire, Retain
- **Flexible Ranges**: 30-40% / 10-20% / 10-20% / 5-10% / 5-10% / 5-10%
- **MAP Methodology**: Assess, Mobilize, Migrate, Modernize phases

### 4. Professional Output
- Executive-ready business case document
- Comprehensive cost analysis with multiple pricing models
- Detailed migration roadmap with timelines
- Risk assessment and mitigation strategies

---

## 📖 Documentation

### Essential Reading

1. **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Detailed value proposition, ROI analysis, use cases for AWS Partners
2. **[QUICK_START.md](QUICK_START.md)** - Quick start guide with troubleshooting
3. **[agents/WORKFLOW.md](agents/WORKFLOW.md)** - Complete workflow and agent architecture
4. **[agents/COMPLETE_AGENT_ARCHITECTURE.md](agents/COMPLETE_AGENT_ARCHITECTURE.md)** - Technical architecture details
5. **[test/README.md](test/README.md)** - Testing guide for individual agents

### Framework Documents

- **[input/aws-migration-strategy-6rs-framework.md](input/aws-migration-strategy-6rs-framework.md)** - Complete 6Rs framework with ranges and guidance
- **[input/aws-migration-plan-framework.md](input/aws-migration-plan-framework.md)** - Complete MAP methodology framework

---

## 🧪 Testing

Test individual agents before running the full orchestration:

```bash
cd test

# Test data extraction (no AWS credentials needed)
python test_atx_data.py
python test_mra_data.py
python test_migration_strategy_data.py
python test_migration_plan_data.py

# Test full agents (requires AWS credentials)
python test_atx_agent.py
python test_mra_agent.py
python test_migration_strategy_agent.py
python test_migration_plan_agent.py
```

---

## 🔧 Customization

### For Customer-Specific Needs

1. **Edit Framework Files** (no code changes needed):
   - `input/aws-migration-strategy-6rs-framework.md` - Adjust 6Rs ranges and guidance
   - `input/aws-migration-plan-framework.md` - Customize MAP phases and activities

2. **Update Configuration**:
   - `agents/config.py` - Set paths and model parameters

3. **Customize Prompts** (optional):
   - `agents/prompt_library/agent_prompts.py` - Adjust agent prompts

---

## 💼 Value for AWS Partners

### Time Savings: **85-90%**
- Traditional: 5-8 weeks
- AI-Powered: 1-2 days

### Cost Savings: **$400K-700K annually**
- Reduce consultant time by 200-280 hours per business case

### Revenue Impact: **$2M-5M additional wins**
- 20-30% higher win rates with data-driven proposals
- Handle 5-10x more opportunities with same team

**See [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) for complete ROI analysis**

---

## 🎯 Use Cases

1. **Pre-Sales / Opportunity Qualification** - Quickly assess and generate preliminary business case
2. **Migration Assessment Services** - Deliver comprehensive assessment reports
3. **Competency Validation** - Demonstrate systematic migration approach for AWS Partner audits
4. **Customer Workshops** - Generate baseline analysis for strategy discussions
5. **Proposal Development** - Create comprehensive RFP responses with detailed estimates

---

## 🔍 What Gets Analyzed

### Infrastructure Analysis
- ✅ Server inventory (physical, virtual, cloud)
- ✅ VMware environment (vCPUs, memory, storage, VMs)
- ✅ Database systems and versions
- ✅ Storage systems and capacity
- ✅ Network architecture
- ✅ Application dependencies

### Organizational Readiness
- ✅ Business readiness and sponsorship
- ✅ Skills and capabilities
- ✅ Process maturity
- ✅ Technology platform readiness
- ✅ Security and compliance
- ✅ Operations readiness
- ✅ Financial readiness

### Cost Analysis
- ✅ Current on-premises TCO
- ✅ AWS cost projections (On-Demand, RI, Savings Plans)
- ✅ 3-year TCO comparison
- ✅ Cost optimization opportunities
- ✅ Windows Server license optimization (if >20 servers)

### Migration Strategy
- ✅ Application categorization by 6Rs
- ✅ Wave planning (4 waves over 12-18 months)
- ✅ Timeline and resource estimates
- ✅ Risk assessment

### Migration Plan
- ✅ Assess phase readiness and gaps
- ✅ Mobilize phase activities and timeline
- ✅ Migrate phase wave-by-wave plan
- ✅ Modernize phase roadmap

---

## 📈 Success Metrics

The generated business case includes:

- **Migration Success Metrics**: Applications migrated, velocity, downtime, budget
- **Business Outcome Metrics**: Cost savings %, performance improvement, availability
- **Financial Metrics**: TCO reduction, ROI timeline, OpEx vs CapEx shift

---

## 🛠️ Troubleshooting

### Common Issues

**1. AWS Credentials Error**
```bash
# Configure credentials
aws configure
# OR
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

**2. Module Not Found**
```bash
pip install -r business-case-agents/requirements.txt
```

**3. File Not Found**
- Ensure all input files are in the `input/` folder
- Update paths in `agents/config.py`

**4. Bedrock Access**
- Ensure AWS account has Bedrock enabled
- Verify Claude 3.7 Sonnet model access
- Check permissions for us-east-1 region

---

## 📚 Documentation

### Essential Documentation
- **[README.md](README.md)** - This file, main project documentation
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project layout and architecture
- **[ui/README.md](ui/README.md)** - Web UI documentation
- **[ui/QUICK_REFERENCE.md](ui/QUICK_REFERENCE.md)** - Quick start for UI features

### Optional Storage Setup
- **[ui/DYNAMODB_SETUP.md](ui/DYNAMODB_SETUP.md)** - DynamoDB persistence setup
- **[ui/S3_STORAGE_SETUP.md](ui/S3_STORAGE_SETUP.md)** - S3 file storage setup

### Input Framework Files
- `input/aws-migration-strategy-6rs-framework.md` - 6Rs framework guidance
- `input/aws-migration-plan-framework.md` - MAP phases guidance
- `input/aws-customer-migration-readiness-assessment.md` - MRA template

---

## 🤝 Support

For questions or issues:
1. Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture
2. Check [ui/README.md](ui/README.md) for UI-specific help
3. Review sample output in `output/aws_business_case.md`
4. Verify AWS credentials and Bedrock access

---

## 📝 License

This project is designed for AWS Partners working on Migration and Modernization Competency.

---

## 🚀 Getting Started Checklist

### Command Line Usage
- [ ] Install agent dependencies: `pip install -r agents/requirements.txt`
- [ ] Configure AWS credentials with Bedrock access
- [ ] Update paths in `agents/config.py`
- [ ] Place input files in `input/` folder
- [ ] Run `python agents/aws_business_case.py`
- [ ] Review output in `output/aws_business_case.md`

### Web UI Usage
- [ ] Install agent dependencies: `pip install -r agents/requirements.txt`
- [ ] Install UI dependencies: `pip install -r ui/backend/requirements.txt` and `npm install`
- [ ] Configure AWS credentials
- [ ] Start backend: `python ui/backend/app.py`
- [ ] Start frontend: `npm start` (in ui/ directory)
- [ ] Access UI at http://localhost:3000

---

**Ready to generate your AWS migration business case in minutes instead of weeks!** 🎉
