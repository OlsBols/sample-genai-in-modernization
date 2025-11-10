# AWS Business Case Multi-Agent System Architecture

## System Overview

Production-ready multi-agent system using **AWS Bedrock Claude 3.5 Sonnet** and **Strands SDK** to generate comprehensive business cases for AWS migration projects.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AWS Business Case Generation System                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────────┐
│  Customer Data  │    │   Partner Data   │    │        AWS Services             │
│                 │    │                  │    │                                 │
│ • RVTools       │    │ • Best Practices │    │ • Bedrock Claude 3.5 Sonnet    │
│ • Migration     │    │ • Pricing Models │    │ • S3 Knowledge Base             │
│   Evaluator     │    │ • Benchmarks     │    │ • AWS Calculator API            │
│ • Portfolio     │    │ • Templates      │    │                                 │
│   Assessment    │    │                  │    │                                 │
│ • Transform     │    │                  │    │                                 │
└─────────────────┘    └──────────────────┘    └─────────────────────────────────┘
         │                       │                            │
         │                       │                            │
         ▼                       ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Data Processing Layer                               │
│                                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────────────┐ │
│  │  Data Loader    │  │ Knowledge Base   │  │      Strands SDK Client         │ │
│  │                 │  │                  │  │                                 │ │
│  │ • Excel Parser  │  │ • S3 Retrieval   │  │ • Prompt Engineering            │ │
│  │ • PPT Parser    │  │ • Context Mgmt   │  │ • Context Management            │ │
│  │ • JSON Parser   │  │ • Document Index │  │ • Response Processing           │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Multi-Agent Processing Layer                          │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           Agent Orchestrator                                │ │
│  │                     (orchestrator_strands.py)                              │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                         │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │              │              │              │              │              │  │
│  ▼              ▼              ▼              ▼              ▼              ▼  │
│ ┌─────────────┐┌─────────────┐┌─────────────┐┌─────────────┐┌─────────────┐┌──│─┐
│ │ Company     ││ Data        ││ TCO         ││ Industry    ││ Moderniz.   ││Risk│
│ │ Intelligence││ Ingestion   ││ Calculation ││ Benchmark   ││ Scenario    ││Asmt│
│ └─────────────┘└─────────────┘└─────────────┘└─────────────┘└─────────────┘└──┘─┘
│                                                                                 │
│ ┌─────────────┐┌─────────────┐┌─────────────┐┌─────────────┐┌─────────────┐┌──│─┐
│ │ Security    ││ Productivity││ GenAI       ││ Financial   ││ Landing     ││Rpt │
│ │ Framework   ││ Impact      ││ Opportunity ││ Modeling    ││ Zone        ││Gen │
│ └─────────────┘└─────────────┘└─────────────┘└─────────────┘└─────────────┘└──┘─┘
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Output Generation Layer                             │
│                                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────────────┐ │
│  │ PDF Generator   │  │ Markdown Gen     │  │    AWS Calculator Links         │ │
│  │                 │  │                  │  │                                 │ │
│  │ • Executive     │  │ • Structured     │  │ • TCO Estimates                 │ │
│  │   Summary       │  │   Reports        │  │ • Service Configs               │ │
│  │ • Technical     │  │ • JSON Data      │  │ • Pricing Models                │ │
│  │   Details       │  │ • Agent Results  │  │                                 │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Foundation Model
- **Model**: AWS Bedrock Claude 3.5 Sonnet (`anthropic.claude-3-5-sonnet-20241022`)
- **Region**: us-east-1
- **Configuration**: Optimized for business analysis and technical documentation

### 2. Strands SDK Integration
- **Prompt Engineering**: Specialized prompts for each agent type
- **Context Management**: Efficient handling of large customer datasets
- **Response Processing**: Standardized output formatting and validation
- **Error Handling**: Robust retry logic and error recovery

### 3. Knowledge Base (S3-based)
- **Storage**: S3 bucket with partner data
- **Content**: Migration best practices, pricing models, benchmarks
- **Access**: Direct S3 retrieval (no vector database required)

### 4. Multi-Agent System
12 specialized agents orchestrated for comprehensive business case generation:

| Agent | Purpose | Key Outputs |
|-------|---------|-------------|
| Company Intelligence | Business context analysis | Company profile, strategic objectives |
| Data Ingestion | Technical assessment | Infrastructure inventory, dependencies |
| TCO Calculation | Cost analysis | Current vs AWS costs, calculator links |
| Industry Benchmark | Peer comparisons | Market positioning, best practices |
| Modernization Scenario | Migration strategies | Application modernization paths |
| Risk Assessment | Risk identification | Risk matrix, mitigation strategies |
| Security Framework | Security architecture | Compliance mapping, security controls |
| Productivity Impact | Efficiency improvements | Process optimization, productivity gains |
| GenAI Opportunity | AI use case identification | AI/ML opportunities, implementation roadmap |
| Financial Modeling | Financial analysis | NPV, IRR, payback period calculations |
| Landing Zone | AWS account structure | Multi-account strategy, governance |
| Report Generation | Document creation | Executive PDF reports, technical documentation |

## Data Flow

```
Customer Data → Data Loader → Context Builder → Strands SDK → Claude 3.5 → Agent Processing
                                    ↑                                            ↓
                            S3 Knowledge Base ←→ Response Aggregation → PDF Report
```

## Technical Implementation

### Agent Architecture Pattern
```python
# Each agent follows standardized pattern:
1. Input Processing: Customer data + knowledge base context
2. Prompt Engineering: Specialized prompts via Strands SDK
3. Model Invocation: Claude 3.5 Sonnet processing
4. Response Processing: Structured output formatting
5. Error Handling: Retry logic and validation
```

### Strands SDK Client Configuration
```python
client = StrandsBedrockClient(
    model_id="anthropic.claude-3-5-sonnet-20241022",
    region="us-east-1",
    max_tokens=4000,
    temperature=0.1
)
```

## Deployment Architecture

### AWS Services Used
- **AWS Bedrock**: Claude 3.5 Sonnet model hosting
- **Amazon S3**: Knowledge base storage
- **AWS Calculator API**: Cost estimation integration

### Security & Compliance
- IAM roles with least privilege access
- S3 bucket encryption at rest
- VPC endpoints for secure communication
- Audit logging for all API calls

## Performance Characteristics

### Scalability
- Concurrent agent processing
- Stateless architecture
- Horizontal scaling capability

### Cost Optimization
- S3 storage: ~$1/month for partner documents
- Per business case: $20-40 (Claude invocations only)
- No vector database costs
- Pay-per-use model

### Processing Time
- Individual agent: 30-60 seconds
- Full business case: 8-12 minutes
- Parallel agent execution where possible

## Integration Points

### Input Formats Supported
- **RVTools**: Excel format infrastructure inventory
- **Migration Evaluator**: PowerPoint and data exports
- **Portfolio Assessment**: Excel spreadsheets
- **AWS Transform**: Generated reports and assessments
- **Custom Data**: JSON, CSV, text documents

### Output Formats
- **PDF Reports**: Executive-ready business case documents
- **JSON Data**: Structured agent results for integration
- **Markdown**: Human-readable technical documentation
- **AWS Calculator Links**: Direct cost estimation tools

## Monitoring & Observability

### Logging
- Agent execution logs
- Error tracking and retry attempts
- Performance metrics per agent
- Cost tracking per business case

### Quality Assurance
- Output validation for each agent
- Consistency checks across agent results
- Format validation for generated reports
- Link validation for AWS Calculator URLs
