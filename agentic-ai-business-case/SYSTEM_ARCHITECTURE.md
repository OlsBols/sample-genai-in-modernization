# Business Case Generator - System Architecture

## Overview

This document describes the complete flow of how the AWS Migration Business Case Generator works, from UI request to final document generation.

---

## 📊 Complete Business Case Generation Flow

### 1. UI REQUEST (Frontend → Backend)

**File**: `ui/backend/app.py`

```
User clicks "Generate Business Case" in UI
    ↓
POST /api/generate-business-case
    ↓
Receives: {
    projectName, customerName, region,
    projectDescription, files (RVTools, MRA, etc.)
}
    ↓
Saves files to: input/case-{caseId}/
    ↓
Calls: run_business_case_generation()
```

---

### 2. MAIN ORCHESTRATOR

**File**: `agents/aws_business_case.py`

This is the **main entry point** that orchestrates everything:

```python
run_business_case_generation()
    ↓
1. Pre-compute RVTools summary (filters to 51 powered-on VMs)
2. Read MRA PDF content
3. Build agent graph with dependencies
4. Execute agent graph (parallel where possible)
5. Generate multi-stage business case
6. Save to output/aws_business_case.md
```

---

### 3. AGENT GRAPH EXECUTION (Parallel Processing)

**File**: `agents/aws_business_case.py` (graph builder)

**Execution Order** (with dependencies):

```
PHASE 1 - Initial Analysis (Run in Parallel):
├── agent_it_analysis        → IT inventory analysis
├── agent_rv_tool_analysis   → RVTools VMware analysis (filters to 51 VMs)
├── agent_atx_analysis        → ATX assessment analysis
└── agent_mra_analysis        → MRA readiness analysis

PHASE 2 - Synthesis (Wait for Phase 1):
├── current_state_analysis    → Synthesizes all Phase 1 results
├── agent_migration_strategy  → 7Rs strategy recommendations
└── agent_aws_cost_arr        → Cost calculations (calls pricing tools)

PHASE 3 - Planning (Wait for Phase 2):
└── agent_migration_plan      → Roadmap and timeline

PHASE 4 - Final Document (Wait for Phase 3):
└── Multi-stage business case generation
```

---

### 4. INDIVIDUAL AGENT FILES & THEIR ROLES

#### Analysis Agents:

**1. `agents/rv_tool_analysis.py`**
- Reads RVTools Excel/CSV files
- **Filters to powered-on VMs only** (e.g., 51 out of 212 total)
- Generates VM summary statistics
- Tool: `rv_tool_analysis()`
- **Critical**: Filtering happens here to exclude powered-off VMs

**2. `agents/mra_analysis.py`**
- Reads MRA PDF documents
- Extracts migration readiness findings
- Tool: `read_file_from_input_dir()`

**3. `agents/atx_analysis.py`**
- Reads ATX assessment files (Excel, PDF, PowerPoint)
- Tools: `read_excel_file()`, `read_pdf_file()`, `read_pptx_file()`

**4. `agents/it_analysis.py`**
- Reads IT inventory files
- Tool: `inventory_analysis()`

#### Cost Analysis:

**5. `agents/aws_arr_cost.py`**
- Main cost analysis agent
- Uses prompts from `agents/prompt_library/agent_prompts.py`
- Calls pricing tools from `agents/pricing_tools.py`

**6. `agents/pricing_tools.py`**
- Tool: `calculate_exact_aws_arr()` - Main pricing calculator
- Calls `rv_tool_analysis()` to get filtered VM data
- Uses `agents/aws_pricing_calculator.py` for calculations
- Generates Excel export via `agents/excel_export.py`

**7. `agents/aws_pricing_calculator.py`**
- Class: `AWSPricingCalculator`
- Method: `calculate_arr_from_dataframe()`
- Calculates costs for each VM
- Returns aggregated results with breakdowns

**8. `agents/excel_export.py`**
- Function: `export_vm_to_ec2_mapping()`
- Creates: `output/vm_to_ec2_mapping.xlsx`
- Contains VM-to-EC2 instance mapping with costs

#### Strategy & Planning:

**9. `agents/migration_strategy.py`**
- 7Rs distribution (Rehost, Replatform, Refactor, etc.)
- Wave planning recommendations

**10. `agents/migration_plan.py`**
- Roadmap generation
- Timeline creation with milestones

---

### 5. MULTI-STAGE BUSINESS CASE GENERATION

**File**: `agents/multi_stage_business_case.py`

```python
generate_multi_stage_business_case(agent_results, project_context)
    ↓
For each section:
    1. Executive Summary
    2. Current State Analysis
    3. Migration Strategy
    4. Cost Analysis
    5. Migration Roadmap
    6. Benefits and Risks
    7. Recommendations
    8. Appendix (from agents/appendix_content.py)
    ↓
Each section:
    - Creates dedicated agent with section-specific prompt
    - Passes all previous agent results as context
    - Generates section content
    - Combines into final document
```

**Section Prompts** (all in `agents/multi_stage_business_case.py`):
- `EXECUTIVE_SUMMARY_PROMPT`
- `CURRENT_STATE_PROMPT`
- `MIGRATION_STRATEGY_PROMPT`
- `COST_ANALYSIS_PROMPT` (dynamic based on TCO config)
- `MIGRATION_ROADMAP_PROMPT`
- `BENEFITS_RISKS_PROMPT`
- `RECOMMENDATIONS_PROMPT`

---

### 6. SUPPORTING FILES

**Configuration:**
- **`agents/config.py`** - System configuration (regions, pricing models, TCO settings)

**Utilities:**
- **`agents/project_context.py`** - Helper functions for case-specific file paths
- **`agents/prompt_library/agent_prompts.py`** - All individual agent prompts
- **`agents/appendix_content.py`** - AWS partner programs content

---

### 7. OUTPUT FILES

```
output/
├── aws_business_case.md          ← Final business case document
├── vm_to_ec2_mapping.xlsx        ← Excel export with VM→EC2 mapping
└── logs/
    └── agent_execution_*.log     ← Execution logs with timestamps
```

---

## 🔄 Simplified Flow Diagram

```
UI (React)
    ↓
ui/backend/app.py (Flask)
    ↓
agents/aws_business_case.py (Main Orchestrator)
    ↓
┌─────────────────────────────────────────┐
│  AGENT GRAPH (Parallel Execution)      │
├─────────────────────────────────────────┤
│  Phase 1: Analysis Agents               │
│  ├─ rv_tool_analysis.py (filters 51 VMs)│
│  ├─ mra_analysis.py                     │
│  ├─ atx_analysis.py                     │
│  └─ it_analysis.py                      │
│                                          │
│  Phase 2: Synthesis                     │
│  ├─ current_state_analysis              │
│  ├─ migration_strategy.py               │
│  └─ aws_arr_cost.py                     │
│      └─ pricing_tools.py                │
│          └─ aws_pricing_calculator.py   │
│              └─ excel_export.py         │
│                                          │
│  Phase 3: Planning                      │
│  └─ migration_plan.py                   │
└─────────────────────────────────────────┘
    ↓
multi_stage_business_case.py
    ↓
Generates 7 sections sequentially
    ↓
output/aws_business_case.md
```

---

## 🎯 Key Points

### Entry Point
- **UI**: `ui/backend/app.py` receives POST request
- **Main Orchestrator**: `agents/aws_business_case.py` coordinates everything

### Parallel Execution
- Phase 1 agents run simultaneously for efficiency
- Dependencies ensure proper data flow between phases

### VM Filtering
- Happens in `rv_tool_analysis.py`
- Filters to powered-on VMs only (e.g., 51 out of 212 total)
- Critical for accurate cost calculations

### Cost Calculation Flow
```
pricing_tools.py
    ↓ calls
rv_tool_analysis() (gets filtered 51 VMs)
    ↓ passes to
aws_pricing_calculator.py
    ↓ calculates costs
excel_export.py (generates Excel)
```

### Final Assembly
- `multi_stage_business_case.py` generates each section
- Each section has dedicated agent with specific prompt
- All sections receive context from previous agent results

### Prompt Storage
- Individual agent prompts: `agents/prompt_library/agent_prompts.py`
- Section prompts: `agents/multi_stage_business_case.py`

---

## 📝 Data Flow Example

### Example: 51 VMs Migration

```
1. User uploads RVTools file (212 total VMs)
   ↓
2. rv_tool_analysis.py filters to 51 powered-on VMs
   ↓
3. Pre-computed summary: 51 VMs, 213 vCPUs, 686 GB RAM, 11.3 TB storage
   ↓
4. pricing_tools.py calculates costs for 51 VMs
   ↓
5. aws_pricing_calculator.py: $5,941.43/month for 51 VMs
   ↓
6. Excel export: 51 rows (one per VM)
   ↓
7. current_state_analysis: Uses 51 VMs in summary
   ↓
8. Executive Summary: Shows 51 VMs, $5,941.43/month
   ↓
9. Cost Analysis: Shows 51 VMs, $5,941.43/month (consistent!)
   ↓
10. Final business case: All sections show 51 VMs consistently
```

---

## 🔧 Configuration

### Key Configuration Files

**`agents/config.py`**:
- `USE_DETERMINISTIC_PRICING` - Enable/disable pricing tools
- `TCO_COMPARISON_CONFIG` - TCO comparison settings
- `model_id_claude3_7` - AI model selection
- `MAX_TOKENS_BUSINESS_CASE` - Output token limits

### TCO Configuration

```python
TCO_COMPARISON_CONFIG = {
    'enable_tco_comparison': False,  # Set to True to enable
    'on_prem_costs': {
        'hardware_per_server_per_year': 5000,
        'vmware_license_per_vm_per_year': 200,
        # ... more settings
    }
}
```

---

## 🧪 Testing Individual Components

### Test RVTools Analysis
```bash
python test_rvtools_only.py
```

### Test VM Count Extraction
```bash
python test_vm_count_extraction.py
```

### Test Pricing Calculator
```python
from agents.pricing_tools import calculate_exact_aws_arr
result = calculate_exact_aws_arr('RVTools_Export.xlsx', 'us-east-1')
```

---

## 📊 Performance Characteristics

### Parallel Execution Benefits
- Phase 1: 4 agents run simultaneously (~30-40 seconds)
- Phase 2: 3 agents run simultaneously (~40-50 seconds)
- Phase 3: 1 agent (~25-30 seconds)
- Phase 4: 7 sections generated sequentially (~2-3 minutes)

**Total Time**: ~3-4 minutes for complete business case

### Token Usage
- Individual agents: 2,000-8,000 tokens per agent
- Section generation: 400-600 words per section
- Total document: ~5,000-8,000 words

---

## 🔒 Critical Validation Rules

### VM Count Consistency
- All sections must show same VM count (e.g., 51 VMs)
- Powered-on VMs only (powered-off excluded)
- Instance distribution must sum to total VM count

### Financial Consistency
- Executive Summary costs must match Cost Analysis
- All cost figures from same source (pricing tool)
- No estimation or recalculation allowed

### Data Accuracy
- Use actual numbers from analysis (no placeholders)
- No approximations (e.g., "51 VMs" not "approximately 50")
- No meta-commentary in output

---

## 📚 Related Documentation

- `SETUP_GUIDE.md` - Installation and setup
- `PRICING_CONFIGURATION_GUIDE.md` - Pricing configuration
- `EXCEL_EXPORT_DOCUMENTATION.md` - Excel export details
- `README.md` - Project overview

---

**Last Updated**: December 5, 2025
**Version**: 1.0
