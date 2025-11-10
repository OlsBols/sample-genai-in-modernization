# Deployment

**Primary Setup Script**: `simple_s3_kb.py`

## Files

- `simple_s3_kb.py` - Main setup script (S3 + Claude)
- `kb_config.json` - Generated configuration file

## Usage

```bash
# Setup simple S3 knowledge base
python3 deployment/simple_s3_kb.py

# Test knowledge retrieval
python3 test_simple_kb.py

# Generate business case
python3 agents/orchestrator.py --customer-data ../AnyCustomer_data
```

## What Gets Created

1. S3 bucket with partner data
2. Simple document retrieval system
3. Direct Claude integration (no vector database)

## Benefits

- **Simple**: No complex vector database setup
- **Fast**: Immediate setup, no ingestion wait time
- **Cost-effective**: Only S3 storage + Claude API calls
- **Reliable**: No OpenSearch mapping issues

Knowledge retrieval uses `utils/simple_kb.py` for direct S3 + Claude queries.
