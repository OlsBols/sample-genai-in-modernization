# AWS Business Case Multi-Agent System

## Overview

Prompt-based multi-agent system using AWS Bedrock and Claude 3.5 Sonnet to generate comprehensive business cases for AWS migration and modernization projects.

## Quick Start

```bash
cd business-case-agents
./deploy.sh
python3 agents/orchestrator.py --customer-data ../AnyCustomer_data
```

## Project Structure

```
Business_Case_Hackathon/
├── README.md (this file)
├── AnyCustomer_data/ (example customer data)
├── AnyTech_Partner_data/ (partner knowledge base)
└── business-case-agents/ (main application)
    ├── README.md (detailed documentation)
    ├── AGENT_BREAKDOWN.md (refactoring guide)
    ├── agents/ (12 individual agent files)
    ├── deployment/ (AWS setup scripts)
    ├── utils/ (helper libraries)
    └── config/ (configuration)
```

## Key Features

- **12 Specialized Agents**: Each in its own Python file for easy refactoring
- **Prompt-Based**: Direct Claude invocation via Bedrock Runtime
- **Knowledge Base**: Reusable partner methodologies across customers
- **Scalable**: 1 partner setup → unlimited customers

## Architecture

**1 Partner → Many Customers Model**
- Partner data stored in Bedrock Knowledge Base (shared)
- Customer data processed locally (isolated)
- Each agent queries KB for context and invokes Claude directly

## Documentation

- **business-case-agents/README.md** - Complete setup and usage guide
- **business-case-agents/AGENT_BREAKDOWN.md** - Agent refactoring guide

## Cost

- Setup: ~$200-300/month (OpenSearch Serverless)
- Per business case: ~$40-60 (Claude invocations)

## Prerequisites

- AWS Account with Bedrock access
- Python 3.11+
- AWS CLI configured
- Claude 3.5 Sonnet model access enabled

## Getting Started

See `business-case-agents/README.md` for detailed instructions.
