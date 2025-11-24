# Project Structure

## Directory Layout

```
agentic-ai-business-case/
├── agents/                          # AI agent implementations
│   ├── aws_business_case.py        # Main orchestrator
│   ├── inventory_analysis.py       # IT inventory agent
│   ├── rv_tool_analysis.py         # RVTool VMware agent
│   ├── atx_analysis.py             # ATX VMware agent
│   ├── mra_analysis.py             # Migration readiness agent
│   ├── migration_strategy.py       # 6Rs strategy agent
│   ├── migration_plan.py           # MAP phases agent
│   ├── aws_arr_cost.py             # Cost analysis agent
│   ├── config.py                   # Configuration
│   ├── prompt_library/             # Agent prompts
│   └── requirements.txt            # Agent dependencies
│
├── input/                           # Input files and frameworks
│   ├── aws-migration-strategy-6rs-framework.md
│   ├── aws-migration-plan-framework.md
│   └── aws-customer-migration-readiness-assessment.md
│
├── output/                          # Generated business cases
│   └── aws_business_case.md
│
├── ui/                              # Web interface
│   ├── src/                        # React frontend
│   │   ├── components/             # UI components
│   │   ├── App.js                  # Main app
│   │   └── index.js                # Entry point
│   ├── backend/                    # Flask API
│   │   ├── app.py                  # API server
│   │   ├── setup_dynamodb.py       # DynamoDB setup
│   │   ├── setup_s3.py             # S3 setup
│   │   └── requirements.txt        # Backend dependencies
│   ├── public/                     # Static files
│   ├── package.json                # Frontend dependencies
│   ├── README.md                   # UI documentation
│   ├── QUICK_REFERENCE.md          # Quick start guide
│   ├── DYNAMODB_SETUP.md           # DynamoDB setup guide
│   └── S3_STORAGE_SETUP.md         # S3 setup guide
│
└── README.md                        # Main documentation
```

## Key Files

### Agent Files
- **`agents/aws_business_case.py`** - Main orchestrator that coordinates all agents
- **`agents/config.py`** - Configuration for paths and model settings
- **`agents/requirements.txt`** - Python dependencies for agents

### UI Files
- **`ui/src/App.js`** - Main React application
- **`ui/backend/app.py`** - Flask API server
- **`ui/package.json`** - Frontend dependencies
- **`ui/backend/requirements.txt`** - Backend dependencies

### Documentation Files
- **`README.md`** - Main project documentation
- **`ui/README.md`** - UI-specific documentation
- **`ui/QUICK_REFERENCE.md`** - Quick start for UI features
- **`ui/DYNAMODB_SETUP.md`** - DynamoDB persistence setup
- **`ui/S3_STORAGE_SETUP.md`** - S3 file storage setup

### Input Framework Files
- **`input/aws-migration-strategy-6rs-framework.md`** - 6Rs framework guidance
- **`input/aws-migration-plan-framework.md`** - MAP phases guidance
- **`input/aws-customer-migration-readiness-assessment.md`** - MRA template

## Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                         Web UI                               │
│  ┌──────────────┐              ┌──────────────┐            │
│  │   React      │◄────────────►│  Flask API   │            │
│  │   Frontend   │              │   Backend    │            │
│  └──────────────┘              └──────┬───────┘            │
│                                       │                      │
└───────────────────────────────────────┼──────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   ▼                   │
                    │        ┌──────────────────┐          │
                    │        │  Agent System    │          │
                    │        │  (aws_business_  │          │
                    │        │   case.py)       │          │
                    │        └────────┬─────────┘          │
                    │                 │                     │
                    │    ┌────────────┼────────────┐       │
                    │    ▼            ▼            ▼       │
                    │  Phase 1      Phase 2     Phase 3    │
                    │  Agents       Agents      Agents     │
                    └─────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              AWS Bedrock      DynamoDB           S3
              (AI Models)      (Storage)      (Files)
```

## Data Flow

1. **Input** → User uploads files via UI or places in `input/` directory
2. **Processing** → Agents analyze files using AWS Bedrock
3. **Output** → Business case generated in `output/` directory
4. **Storage** (Optional) → Saved to DynamoDB with files in S3
5. **Export** → Download as PDF or Markdown

## Dependencies

### Agent Dependencies (`agents/requirements.txt`)
- strands-agents - AWS Bedrock agent framework
- boto3 - AWS SDK
- pandas - Data analysis
- openpyxl, python-pptx, PyPDF2 - File handling

### UI Backend Dependencies (`ui/backend/requirements.txt`)
- Flask - Web framework
- Flask-CORS - CORS support
- boto3 - AWS SDK for DynamoDB/S3

### UI Frontend Dependencies (`ui/package.json`)
- React - UI framework
- @cloudscape-design/components - AWS UI components
- react-markdown - Markdown rendering
- html2pdf.js - PDF export

## Configuration

### Agent Configuration (`agents/config.py`)
```python
input_folder_dir_path = "/path/to/agentic-ai-business-case/"
output_folder_dir_path = "/path/to/agentic-ai-business-case/output/"
model_id_claude3_7 = "anthropic.claude-3-sonnet-20240229-v1:0"
```

### Environment Variables
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# Optional: DynamoDB
DYNAMODB_TABLE_NAME=aws-migration-business-cases

# Optional: S3
S3_BUCKET_NAME=aws-migration-business-cases-files
```

## Ports

- **Frontend**: http://localhost:3000 (or 3001 if 3000 is busy)
- **Backend API**: http://localhost:5000

## Output

Generated business case includes:
- Executive Summary
- Current State Analysis
- AWS Cost Projections (3-year TCO)
- Migration Strategy (6Rs categorization)
- Migration Plan (MAP phases)
- Risk Assessment
- Recommendations
