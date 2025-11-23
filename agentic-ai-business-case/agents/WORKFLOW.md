# AWS Business Case Agent Workflow

## Agent Graph Structure

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    ENTRY POINTS (Run in Parallel)                        │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │agent_it_     │  │agent_rv_tool_│  │agent_atx_    │  │agent_mra_  │ │
│  │  analysis    │  │  analysis    │  │  analysis    │  │  analysis  │ │
│  │(IT Inventory)│  │(RVTool VMware│  │(ATX VMware)  │  │(MRA Report)│ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
│         │                 │                  │                │        │
│         └─────────────────┼──────────────────┼────────────────┘        │
│                           │                  │                         │
└───────────────────────────┼──────────────────┼─────────────────────────┘
                            │                  │
              ┌─────────────┴──────────────────┴─────────────┐
              │                                               │
              ▼                                               ▼
┌─────────────┴──────────┐  ┌──────────────────┐  ┌─────────┴──────────┐
│ current_state_         │  │ agent_aws_cost_  │  │ agent_migration_   │
│    analysis            │  │      arr         │  │    strategy        │
│ (Synthesize all 4)     │  │ (AWS Cost)       │  │ (6Rs Strategy)     │
└────────────┬───────────┘  └────────┬─────────┘  └──────────┬─────────┘
             │                       │                        │
             └───────────────────────┼────────────────────────┘
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

3. **agent_atx_analysis**
   - Input: 
     - `analysis.xlsx` (VMware environment data)
     - `report.pdf` (Technical assessment report)
     - `business_case.pptx` (Executive presentation)
   - Tools: `read_excel_file`, `read_pdf_file`, `read_pptx_file`
   - Purpose: Analyze AWS Transform for VMware (ATX) assessment outputs

4. **agent_mra_analysis** ⭐ NEW
   - Input: `aws-customer-migration-readiness-assessment.md`
   - Tools: `read_docx_file`, `read_markdown_file`
   - Purpose: Analyze Migration Readiness Assessment (MRA) for organizational readiness

### Intermediate Agents (Wait for all 4 entry agents)

5. **current_state_analysis**
   - Dependencies: agent_it_analysis + agent_rv_tool_analysis + agent_atx_analysis + agent_mra_analysis
   - Purpose: Synthesize all four analyses into comprehensive current state (technical + organizational)
   - Tools: `it_analysis`, `rv_tool_analysis`

6. **agent_aws_cost_arr**
   - Dependencies: agent_it_analysis + agent_rv_tool_analysis + agent_atx_analysis + agent_mra_analysis
   - Purpose: Calculate AWS costs and ARR projections
   - Tools: `it_analysis`, `rv_tool_analysis`

7. **agent_migration_strategy**
   - Dependencies: agent_it_analysis + agent_rv_tool_analysis + agent_atx_analysis + agent_mra_analysis
   - Input: `aws-migration-strategy-6rs-framework.md` (reference)
   - Tools: `read_migration_strategy_framework`, `read_portfolio_assessment`
   - Purpose: Recommend migration strategy using AWS 6Rs framework
   - Special: Checks for >20 Windows Servers (triggers OLA requirement)

8. **agent_migration_plan** ⭐ NEW
   - Dependencies: current_state_analysis + agent_aws_cost_arr + agent_migration_strategy
   - Input: `aws-migration-plan-framework.md` (reference)
   - Tools: `read_migration_plan_framework`
   - Purpose: Create comprehensive migration plan (Assess, Mobilize, Migrate, Modernize)
   - Special: Determines if further assessment needed or ready to proceed

### Final Agent

9. **aws_business_case**
   - Dependencies: current_state_analysis + agent_aws_cost_arr + agent_migration_strategy + agent_migration_plan
   - Purpose: Generate final comprehensive business case
   - Output: `output/aws_business_case.md`

## Execution Flow

1. **Phase 1**: Four agents run in parallel
   - IT inventory analysis
   - RVTool VMware analysis
   - ATX VMware analysis
   - MRA organizational readiness analysis

2. **Phase 2**: After all four complete (run in parallel)
   - Current state synthesis (technical + organizational)
   - AWS cost calculation and ARR projections
   - Migration strategy recommendation (6Rs framework)

3. **Phase 3**: After Phase 2 completes
   - Migration plan creation (Assess, Mobilize, Migrate, Modernize phases)

4. **Phase 4**: After Phase 3 completes
   - Final business case generation

## Configuration

- **Model**: Claude 3.7 Sonnet (`us.anthropic.claude-3-7-sonnet-20250219-v1:0`)
- **Temperature**: 0.3
- **Execution Timeout**: 600 seconds (10 minutes)
- **Node Timeout**: 180 seconds (3 minutes per node)

## Input Files

```
input/
├── Test-Data-Set-Demo-Excel-V2.xlsx                    # IT Infrastructure Inventory
├── rvtool.csv                                          # RVTool VMware Assessment
├── analysis.xlsx                                       # ATX VMware Environment Data
├── report.pdf                                          # ATX Technical Assessment Report
├── business_case.pptx                                  # ATX Business Case Presentation
├── aws-customer-migration-readiness-assessment.md      # MRA Organizational Readiness
├── aws-migration-strategy-6rs-framework.md             # Migration Strategy Reference (6Rs)
└── aws-migration-plan-framework.md                     # Migration Plan Framework (MAP)
```

## Output

```
output/
└── aws_business_case.md               # Final Business Case Report
```


---

## Migration Strategy Agent Details

### AWS 6Rs Framework
The migration strategy agent uses the industry-standard AWS 6Rs framework:

1. **Rehost** (Lift and Shift) - 20-30% savings
2. **Replatform** (Lift, Tinker, and Shift) - 30-40% savings
3. **Repurchase** (Drop and Shop) - Move to SaaS
4. **Refactor** (Re-architect) - 40-60% savings (long-term)
5. **Retire** - 100% savings for decommissioned apps
6. **Retain** (Revisit) - Keep in current environment

### Windows Server Optimization
**Special Rule**: If >20 Windows Servers are detected:
- **MANDATORY**: Optimization and License Assessment (OLA) required
- Analyzes Windows Server and SQL Server licensing
- Evaluates BYOL vs. License Included options
- Identifies consolidation opportunities
- **Expected Savings**: 30-50% through license optimization

### Data Source Priority
1. **Application Portfolio Assessment** (if available) - Most accurate
2. **Infrastructure Analysis** (IT + RVTool + ATX) - Good baseline
3. **Industry Standard Framework** (fallback) - General guidance

### Key Outputs
- Application categorization by 6Rs strategy
- Migration wave plan (4 waves over 12-18 months)
- Timeline and effort estimates
- Cost savings projections
- Risk assessment and mitigation
- OLA recommendation (if applicable)

### Important Notes
- **Customer-specific strategy is always preferred**
- Agent clearly states when using industry-standard assumptions
- Recommends conducting detailed portfolio assessment
- Emphasizes that actual strategy depends on business priorities
