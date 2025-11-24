# Viewing Agent Execution Logs

## Log Locations

### 1. **Real-time Backend Logs**
View in the terminal where you started the backend:
```bash
cd agentic-ai-business-case/ui/backend
python app.py
```
This shows:
- API requests
- File uploads
- Agent execution start/stop
- Errors and warnings

### 2. **Agent Execution Logs (Detailed)**
Logs are automatically saved to: `output/logs/agent_execution_YYYYMMDD_HHMMSS.log`

Each log file contains:
- Project information
- Agent execution order
- Individual node performance
- Token usage
- Execution times
- Errors and status

## Viewing Logs

### Option 1: Using the Log Viewer Script

```bash
cd agentic-ai-business-case/agents

# View latest log (live tail)
./view_logs.sh

# Or explicitly
./view_logs.sh latest

# View full content of latest log
./view_logs.sh all

# List all available logs
./view_logs.sh list

# View specific log file
./view_logs.sh agent_execution_20241124_143022.log
```

### Option 2: Manual Commands

```bash
# View latest log (live tail)
tail -f output/logs/agent_execution_*.log

# View full latest log
cat $(ls -t output/logs/*.log | head -1)

# List all logs
ls -lht output/logs/

# View specific log
cat output/logs/agent_execution_20241124_143022.log
```

### Option 3: During Execution

Watch the backend terminal in real-time as agents execute. You'll see:
```
================================================================================
STARTING AGENT WORKFLOW
================================================================================
Project: Enterprise Cloud Migration 2024
Customer: Acme Corporation
Region: us-east-1
================================================================================

Executing agent graph...
[Agent execution progress...]
Agent graph execution completed

================================================================================
FINAL BUSINESS CASE GENERATION
================================================================================
Business case generated successfully
Business case saved to: output/aws_business_case.md
```

## Log Contents

Each log file includes:

1. **Project Context**
   - Project name
   - Customer name
   - Target AWS region
   - Project description

2. **Execution Details**
   - Agent execution order
   - Individual node execution times
   - Status of each agent

3. **Performance Metrics**
   - Total nodes executed
   - Total execution time
   - Token usage statistics

4. **Output Location**
   - Path to generated business case file

## Troubleshooting

### No logs appearing?
- Check if `output/logs/` directory exists
- Verify backend is running
- Check file permissions

### Want more detailed logs?
Edit `agents/setup_logging.py` and change:
```python
level=logging.INFO  # Change to logging.DEBUG for more detail
```

### View logs from UI?
The backend terminal shows real-time progress. Keep it visible while generating business cases.
