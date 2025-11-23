# ATX Analysis Tests

This folder contains test scripts for the AWS Transform for VMware (ATX) analysis agent.

## Test Files

### 1. test_atx_data.py
Tests the data extraction tools without requiring AWS credentials.
- Reads analysis.xlsx and shows sheet structure
- Reads report.pdf and displays first 500 characters
- Reads business_case.pptx and displays first 500 characters

**Run:**
```bash
cd test
python test_atx_data.py
```

### 2. test_atx_agent.py
Runs the full ATX analysis agent with AWS Bedrock.
- Requires AWS credentials configured
- Uses Claude 3.7 Sonnet model
- Provides comprehensive VMware to AWS migration analysis

**Run:**
```bash
cd test
python test_atx_agent.py
```

**Prerequisites:**
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
