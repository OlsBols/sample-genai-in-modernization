# AWS Business Case Agent Workflow

## Agent Graph Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRY POINTS (Run in Parallel)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ agent_it_analysis│  │agent_rv_tool_    │  │agent_atx_    │ │
│  │                  │  │    analysis      │  │  analysis    │ │
│  │ (IT Inventory)   │  │ (RVTool VMware)  │  │ (ATX VMware) │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘ │
│           │                     │                    │         │
│           └─────────────────────┼────────────────────┘         │
│                                 │                              │
└─────────────────────────────────┼──────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
        ┌───────────────────────┐   ┌──────────────────────┐
        │ current_state_        │   │ agent_aws_cost_arr   │
        │    analysis           │   │                      │
        │ (Synthesize all 3)    │   │ (AWS Cost Analysis)  │
        └───────────┬───────────┘   └──────────┬───────────┘
                    │                           │
                    └───────────┬───────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  aws_business_case    │
                    │                       │
                    │ (Final Business Case) │
                    └───────────────────────┘
```

## Agent Details

### Entry Point Agents (Run in Parallel)

1. **agent_it_analysis**
   - Input: `Test-Data-Set-Demo-Excel-V2.xlsx`
   - Tool: `it_analysis`
   - Purpose: Analyze general IT infrastructure inventory

2. **agent_rv_tool_analysis**
   - Input: `rvtool.csv`
   - Tool: `rv_tool_analysis`
   - Purpose: Analyze RVTool VMware assessment data

3. **agent_atx_analysis** ⭐ NEW
   - Input: 
     - `analysis.xlsx` (VMware environment data)
     - `report.pdf` (Technical assessment report)
     - `business_case.pptx` (Executive presentation)
   - Tools: `read_excel_file`, `read_pdf_file`, `read_pptx_file`
   - Purpose: Analyze AWS Transform for VMware (ATX) assessment outputs

### Intermediate Agents (Wait for all 3 entry agents)

4. **current_state_analysis**
   - Dependencies: agent_it_analysis + agent_rv_tool_analysis + agent_atx_analysis
   - Purpose: Synthesize all three analyses into comprehensive current state
   - Tools: `it_analysis`, `rv_tool_analysis`

5. **agent_aws_cost_arr**
   - Dependencies: agent_it_analysis + agent_rv_tool_analysis + agent_atx_analysis
   - Purpose: Calculate AWS costs and ARR projections
   - Tools: `it_analysis`, `rv_tool_analysis`

### Final Agent

6. **aws_business_case**
   - Dependencies: current_state_analysis + agent_aws_cost_arr
   - Purpose: Generate final comprehensive business case
   - Output: `output/aws_business_case.md`

## Execution Flow

1. **Phase 1**: Three agents run in parallel
   - IT inventory analysis
   - RVTool VMware analysis
   - ATX VMware analysis

2. **Phase 2**: After all three complete
   - Current state synthesis
   - AWS cost calculation
   (These two run in parallel)

3. **Phase 3**: After Phase 2 completes
   - Final business case generation

## Configuration

- **Model**: Claude 3.7 Sonnet (`us.anthropic.claude-3-7-sonnet-20250219-v1:0`)
- **Temperature**: 0.3
- **Execution Timeout**: 600 seconds (10 minutes)
- **Node Timeout**: 180 seconds (3 minutes per node)

## Input Files

```
input/
├── Test-Data-Set-Demo-Excel-V2.xlsx  # IT Infrastructure Inventory
├── rvtool.csv                         # RVTool VMware Assessment
├── analysis.xlsx                      # ATX VMware Environment Data
├── report.pdf                         # ATX Technical Assessment Report
└── business_case.pptx                 # ATX Business Case Presentation
```

## Output

```
output/
└── aws_business_case.md               # Final Business Case Report
```
