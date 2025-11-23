# Agent Analysis Tests

This folder contains test scripts for the AWS migration analysis agents.

## Test Files

### ATX Analysis Tests

#### 1. test_atx_data.py
Tests the ATX data extraction tools without requiring AWS credentials.
- Reads analysis.xlsx and shows sheet structure
- Reads report.pdf and displays first 500 characters
- Reads business_case.pptx and displays first 500 characters

**Run:**
```bash
cd test
python test_atx_data.py
```

#### 2. test_atx_agent.py
Runs the full ATX analysis agent with AWS Bedrock.
- Requires AWS credentials configured
- Uses Claude 3.7 Sonnet model
- Provides comprehensive VMware to AWS migration analysis

**Run:**
```bash
cd test
python test_atx_agent.py
```

### MRA Analysis Tests

#### 3. test_mra_data.py
Tests the MRA data extraction tools without requiring AWS credentials.
- Reads aws-customer-migration-readiness-assessment.md
- Tests Word document reading (if .docx file available)

**Run:**
```bash
cd test
python test_mra_data.py
```

#### 4. test_mra_agent.py
Runs the full MRA analysis agent with AWS Bedrock.
- Requires AWS credentials configured
- Uses Claude 3.7 Sonnet model
- Provides comprehensive migration readiness assessment analysis

**Run:**
```bash
cd test
python test_mra_agent.py
```

## Prerequisites

**For data extraction tests (test_*_data.py):**
- No AWS credentials required
- Tests file reading functionality only

**For agent tests (test_*_agent.py):**
- AWS credentials configured (via `aws configure` or environment variables)
- Access to AWS Bedrock with Claude 3.7 Sonnet model

## AWS Credentials Setup

```bash
# Option 1: Using AWS CLI
aws configure

# Option 2: Using environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Migration Strategy Tests

#### 5. test_migration_strategy_data.py
Tests the migration strategy data extraction tools without requiring AWS credentials.
- Reads aws-migration-strategy-6rs-framework.md
- Tests portfolio assessment reading (if available)

**Run:**
```bash
cd test
python test_migration_strategy_data.py
```

#### 6. test_migration_strategy_agent.py
Runs the full migration strategy agent with AWS Bedrock.
- Requires AWS credentials configured
- Uses Claude 3.7 Sonnet model
- Provides comprehensive migration strategy using AWS 6Rs framework
- Checks for Windows Server OLA requirement (>20 servers)

**Run:**
```bash
cd test
python test_migration_strategy_agent.py
```

## Agent Overview

- **ATX Agent**: Analyzes AWS Transform for VMware assessment outputs
- **MRA Agent**: Analyzes Migration Readiness Assessment documents
- **Migration Strategy Agent**: Recommends migration approach using AWS 6Rs framework
  - Checks for >20 Windows Servers (triggers OLA requirement)
  - Uses portfolio assessment if available, otherwise industry-standard framework
  - Provides wave planning and timeline recommendations
