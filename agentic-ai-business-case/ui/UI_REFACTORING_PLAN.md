# UI Refactoring Plan

## Requirements

### 1. Remove Agent Selection Step
- **Current**: Step 3 "Configure Agents" allows users to select which agents to run
- **New**: Auto-select agents based on uploaded files
- **Impact**: Reduces wizard from 5 steps to 4 steps

### 2. Auto-Select Agents Based on Input Files
- After file upload, automatically determine which agents should run
- Show selected agents on the "Review & Generate" page
- Logic:
  - If `itInventory` uploaded → enable `itInventory` agent
  - If `rvTool` uploaded → enable `rvTool` agent
  - If `atxExcel`, `atxPdf`, or `atxPptx` uploaded → enable `atx` agent
  - If `mra` uploaded → enable `mra` agent
  - Always enable: `currentState`, `costAnalysis`, `migrationStrategy`, `migrationPlan`, `businessCase`

### 3. Disable Next Button During Generation
- **Current**: User can navigate away during generation
- **New**: Disable "Next" button while business case is being generated
- Only enable after generation completes

### 4. Make Markdown Editable in UI
- **Current**: Markdown is read-only in textarea
- **New**: Allow users to edit the markdown content
- Provide "Save Changes" button to update the content
- Track if content has been modified

### 5. Save Edited Version to DynamoDB
- Save edited markdown content to DynamoDB
- Update `lastUpdated` timestamp
- Maintain version history (optional enhancement)

### 6. Export Edited Version
- **PDF Export**: Export the currently displayed (possibly edited) version
- **Markdown Export**: Export the currently displayed (possibly edited) version
- Ensure exports reflect any user edits

## Implementation Steps

### Step 1: Update App.jsx
- Remove AgentConfigStep from wizard
- Add auto-selection logic after file upload
- Update step indices (3 steps instead of 5)

### Step 2: Update ReviewStep.jsx
- Add agent selection display (read-only)
- Show which agents will run based on files
- Disable navigation during generation

### Step 3: Update ResultsStep.jsx
- Make markdown textarea editable
- Add "Save Changes" button
- Track edited state
- Update save/export functions to use edited content

### Step 4: Update Backend API (app.py)
- Ensure save endpoint handles edited content
- Update DynamoDB schema if needed

## File Changes Required

1. `ui/src/App.jsx` - Remove agent config step, add auto-selection
2. `ui/src/components/ReviewStep.jsx` - Add agent display, disable navigation
3. `ui/src/components/ResultsStep.jsx` - Make editable, add save functionality
4. `ui/backend/app.py` - Verify save endpoint handles edited content

## Benefits

- **Simpler UX**: Fewer steps, less confusion
- **Smarter**: Auto-detects what to run based on inputs
- **More Flexible**: Users can edit and refine the output
- **Better Persistence**: Edited versions are saved properly
