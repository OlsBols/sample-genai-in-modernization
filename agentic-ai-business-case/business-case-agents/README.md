# AWS Business Case Multi-Agent System

Production-ready multi-agent system using **AWS Bedrock Claude 3.5 Sonnet** and **Strands SDK** to generate comprehensive business cases for AWS migration projects.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure AWS credentials
aws configure

# 3. Enable Bedrock model access (no longer needed for serverless model)
# Go to AWS Console → Bedrock → Model access
# Enable: Claude 3.5 Sonnet

# 4. Setup Knowledge Base (Partner Data)
python3 deployment/simple_s3_kb.py

# 5. Generate business case
python3 agents/orchestrator_strands.py --customer-data /path/to/customer/data
```

## Architecture

**Strands SDK + AWS Bedrock + S3 Knowledge Base System**

### Core Components:
- **Foundation Model**: AWS Bedrock Claude 3.5 Sonnet (`anthropic.claude-3-5-sonnet-20241022`)
- **Integration Layer**: Custom Strands SDK client for prompt engineering and context management
- **Knowledge Base**: S3-based partner data repository (no vector database required)
- **Customer Data**: Local processing (RVTools, Migration Evaluator, Portfolio Assessment, AWS Transform)
- **Agents**: 12 specialized AI agents with Strands SDK integration
- **Output**: Executive PDF reports + structured JSON data + AWS Calculator links

### Data Flow:
```
Customer Data → Strands SDK → Claude 3.5 Sonnet → AI Agents → Orchestrator → PDF Report
     ↑                                                                            ↓
S3 Knowledge Base ←→ Context Management ←→ Response Processing ←→ Result Aggregation
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Project Structure

```
business-case-agents/
├── README.md                           # This file
├── ARCHITECTURE.md                     # Detailed architecture documentation
├── requirements.txt                    # Python dependencies
├── config/
│   └── agent_config.yaml              # Agent configuration
├── deployment/
│   ├── simple_s3_kb.py                # Setup partner knowledge base
│   ├── kb_config.json                 # Generated knowledge base config
│   └── README.md                      # Deployment instructions
├── agents/
│   ├── orchestrator_strands.py        # Main orchestrator
│   ├── company_intelligence_agent.py  # Business context analysis
│   ├── data_ingestion_agent.py        # Technical assessment
│   ├── tco_calculation_agent.py       # Cost analysis
│   ├── industry_benchmark_agent.py    # Peer comparisons
│   ├── modernization_scenario_agent.py # Migration strategies
│   ├── risk_assessment_agent.py       # Risk identification
│   ├── security_framework_agent.py    # Security architecture
│   ├── productivity_impact_agent.py   # Efficiency improvements
│   ├── genai_opportunity_agent.py     # AI use case identification
│   ├── financial_modeling_agent.py    # Financial analysis
│   ├── landing_zone_agent.py          # AWS account structure
│   └── report_generation_agent.py     # Document creation
└── utils/
    ├── strands_client.py               # Strands SDK client
    ├── simple_kb.py                   # Partner knowledge retrieval
    ├── data_loader.py                 # Customer data loading
    ├── pdf_generator.py               # PDF report generation
    ├── markdown_generator.py          # Markdown documentation
    ├── aws_calculator_bulk.py         # AWS Calculator integration
    └── bedrock_client.py              # AWS Bedrock client
```

## Customer Data Support

The system supports multiple data sources:

**Standard Data:**
- RVTools Excel (infrastructure inventory)
- Dependencies mapping
- Analytics data
- Strategy documents
- Project scope

**Migration Tools Data (Enhanced):**
- Migration Evaluator PPT/data
- Migration Portfolio Assessment XLS  
- AWS Transform generated reports
- AWS Calculator exports

## Agent Capabilities

### 12 Production Agents with Strands SDK Integration:

| Agent | Input | Output | Key Features |
|-------|-------|--------|--------------|
| **Company Intelligence** | Customer data, strategy docs | Business context analysis | Context management, prompt engineering |
| **Data Ingestion** | RVTools, infrastructure data | Technical assessment | Large data processing, structured output |
| **TCO Calculation** | Current costs, AWS pricing | Cost analysis + calculator links | Financial modeling, AWS integration |
| **Industry Benchmark** | Company profile, market data | Peer comparisons | Knowledge base integration |
| **Modernization Scenario** | Application portfolio | Migration strategies | Multi-scenario analysis |
| **Risk Assessment** | Current state, migration plan | Risk identification & mitigation | Risk modeling frameworks |
| **Security Framework** | Compliance requirements | Security architecture | Compliance templates |
| **Productivity Impact** | Current processes | Efficiency improvements | Process optimization |
| **GenAI Opportunity** | Business context | AI use case identification | Innovation frameworks |
| **Financial Modeling** | TCO data, business metrics | NPV, IRR, payback analysis | Financial calculations |
| **Landing Zone** | Technical requirements | AWS account structure design | AWS best practices |
| **Report Generation** | All agent outputs | Executive PDF reports | Document generation |

## Usage

### Generate Full Business Case
```bash
python3 agents/orchestrator_strands.py --customer-data /path/to/customer/data
```

### Setup Partner Knowledge Base
```bash
python3 deployment/simple_s3_kb.py
```

## Key Features

### Enhanced TCO Calculation
- Supports Migration Evaluator data
- Supports Portfolio Assessment XLS
- Supports AWS Transform reports
- Generates AWS Calculator links
- Falls back to public AWS pricing

### Professional PDF Report Generation
- Executive-ready business case reports
- Enhanced typography and formatting
- Hierarchical document structure
- Automatic page breaks between sections
- Professional styling with proper spacing

### Partner Knowledge Integration
- Migration best practices
- Pricing models and benchmarks
- Cloud Value Framework
- Sample business cases

### Strands SDK Benefits
- Optimized prompt engineering for business analysis
- Efficient context management for large datasets
- Standardized response processing and validation
- Robust error handling and retry mechanisms
- Token-efficient Claude 3.5 Sonnet integration

## Technical Implementation

### Foundation Model
- **Model**: AWS Bedrock Claude 3.5 Sonnet (`anthropic.claude-3-5-sonnet-20241022`)
- **Region**: us-east-1
- **Configuration**: Optimized for business analysis and technical documentation

### Strands SDK Client
```python
client = StrandsBedrockClient(
    model_id="anthropic.claude-3-5-sonnet-20241022",
    region="us-east-1",
    max_tokens=4000,
    temperature=0.1
)
```

### Agent Architecture
Each agent follows a standardized pattern:
1. **Input Processing**: Customer data + knowledge base context
2. **Prompt Engineering**: Specialized prompts via Strands SDK
3. **Model Invocation**: Claude 3.5 Sonnet processing
4. **Response Processing**: Structured output formatting
5. **Error Handling**: Retry logic and validation

## Prerequisites

### AWS Setup
- AWS CLI configured with appropriate credentials
- AWS Bedrock access enabled in us-east-1 region
- Claude 3.5 Sonnet model access enabled
- S3 permissions for knowledge base storage

### Python Environment
- Python 3.8 or higher
- Required packages (see requirements.txt)

## Installation

```bash
# Clone repository
git clone <repository-url>
cd business-case-agents

# Install dependencies
pip install -r requirements.txt

# Configure AWS
aws configure

# Setup knowledge base
python3 deployment/simple_s3_kb.py
```

## Configuration

### Agent Configuration
Edit `config/agent_config.yaml` to customize agent behavior:
- Model parameters
- Prompt templates
- Output formats
- Error handling settings

### Knowledge Base Configuration
The system automatically generates `deployment/kb_config.json` during setup.

## Troubleshooting

**Claude access denied?**
- Enable Claude 3.5 Sonnet in AWS Console → Bedrock → Model access
- Check AWS credentials: `aws sts get-caller-identity`

**No partner context?**
- Check S3 bucket: `business-case-kb-us-east-1`
- Verify files uploaded in `partner-data/` prefix
- Run: `python3 deployment/simple_s3_kb.py`

**Agent execution errors?**
- Check AWS region configuration (must be us-east-1)
- Verify customer data format and structure
- Check CloudWatch logs for detailed error messages

## Cost Estimate

- **S3 Storage**: ~$1/month for partner documents
- **Per business case**: $20-40 (Claude invocations only)
- **Monthly (10 customers)**: ~$200-400
- **No vector database costs**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the GitLab repository
- Check the troubleshooting section above
- Review the architecture documentation

---

**Status: PRODUCTION READY** 🚀
