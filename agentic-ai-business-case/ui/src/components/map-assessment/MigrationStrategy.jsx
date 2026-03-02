import React, { useState, useEffect } from 'react';
import {
  Container,
  Header,
  SpaceBetween,
  FormField,
  FileUpload,
  Textarea,
  Button,
  Alert,
  ExpandableSection,
  Box,
  Tabs,
  Toggle,
  Spinner
} from '@cloudscape-design/components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getApiUrl } from '../../utils/apiConfig.js';
import { useMapAssessment } from '../../contexts/MapAssessmentContext.jsx';

// Default scope - pre-filled so user can use immediately
const DEFAULT_SCOPE = `Migration Goals:
- Migrate workloads to AWS cloud infrastructure
- Optimize costs and improve operational efficiency
- Implement best practices for cloud architecture
- Establish migration waves and timelines
- Minimize business disruption during migration`;

// Default prompt template
const DEFAULT_PROMPT = `As an AWS migration expert, analyze the provided AWS Calculator data and generate a comprehensive migration strategy with detailed planning.

Perform analysis in the following structured order:

## (1) Migration Overview & Scope
- Total workloads and services to be migrated
- Migration complexity assessment
- Key dependencies and constraints
- Timeline and phasing recommendations

## (2) Migration Patterns & Strategies
- 7R Strategy Analysis (Rehost, Replatform, Refactor, Repurchase, Retire, Retain, Relocate)
- Recommended approach for each workload category
- Rationale for each migration pattern
- Risk assessment for each strategy

## (3) Wave Planning & Sequencing
- Migration wave structure and grouping
- Dependencies and prerequisites for each wave
- Recommended sequence and timeline
- Quick wins and pilot candidates

## (4) Cost Analysis & Optimization
- Current vs. projected AWS costs
- Cost optimization opportunities
- Reserved Instance and Savings Plan recommendations
- TCO comparison and ROI projections

## (5) Technical Requirements
- Infrastructure prerequisites
- Network and connectivity requirements
- Security and compliance considerations
- Backup and disaster recovery planning

## (6) Risk Mitigation & Contingency
- Identified risks and mitigation strategies
- Rollback procedures
- Testing and validation approach
- Success criteria and KPIs

## (7) Resource & Timeline Planning
- Required team structure and skills
- Estimated effort and duration
- Key milestones and deliverables
- Training and enablement needs

Format your response in markdown with clear headings, bullet points, and tables where appropriate.`;

function MigrationStrategy() {
  const { 
    migrationStrategyData, 
    setMigrationStrategyData, 
    resetMigrationStrategy 
  } = useMapAssessment();
  
  const [calculatorFile, setCalculatorFile] = useState([]);
  const [scope, setScope] = useState(DEFAULT_SCOPE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [strategy, setStrategy] = useState(migrationStrategyData.strategy || null);
  const [recordsProcessed, setRecordsProcessed] = useState(0);
  const [activeTabId, setActiveTabId] = useState('upload');
  
  // Prompt customization
  const [customPrompt, setCustomPrompt] = useState(DEFAULT_PROMPT);
  const [useCustomPrompt, setUseCustomPrompt] = useState(false);
  
  // Load existing data from context on mount
  useEffect(() => {
    if (migrationStrategyData.strategy) {
      setStrategy(migrationStrategyData.strategy);
      setActiveTabId('results');
    }
  }, []);
  
  // Load saved custom prompt from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('map_custom_prompt_migration');
    if (saved) {
      setCustomPrompt(saved);
      setUseCustomPrompt(true);
    }
  }, []);
  
  // Save custom prompt
  const saveCustomPrompt = () => {
    localStorage.setItem('map_custom_prompt_migration', customPrompt);
    alert('✓ Custom prompt saved successfully!');
  };
  
  // Reset to default
  const resetPrompt = () => {
    if (confirm('Reset prompt to default? This cannot be undone.')) {
      setCustomPrompt(DEFAULT_PROMPT);
      setUseCustomPrompt(false);
      localStorage.removeItem('map_custom_prompt_migration');
      alert('✓ Prompt reset to default!');
    }
  };

  const handleGenerateStrategy = async () => {
    if (calculatorFile.length === 0) {
      setError('Please upload an AWS Calculator CSV file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', calculatorFile[0]);
      formData.append('scope', scope);
      
      // Send custom prompt if enabled
      if (useCustomPrompt && customPrompt.trim()) {
        formData.append('custom_prompt', customPrompt);
      }

      const response = await fetch(getApiUrl('/map/migration-strategy/generate'), {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message);
      }

      setStrategy(result.strategy);
      setRecordsProcessed(result.recordsProcessed);
      // Save to context
      setMigrationStrategyData({ strategy: result.strategy });
      // Switch to results tab to show the generated strategy
      setActiveTabId('results');
    } catch (err) {
      setError(err.message || 'Failed to generate migration strategy');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStrategy(null);
    setRecordsProcessed(0);
    setCalculatorFile([]);
    setScope(DEFAULT_SCOPE);
    setActiveTabId('upload');
    resetMigrationStrategy();
  };

  const downloadMarkdown = (content, filename) => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <SpaceBetween size="l">
      <Container
        header={
          <Header
            variant="h1"
            description="From AWS Calculator Data"
            actions={
              <Button onClick={handleReset} disabled={!strategy}>
                Reset
              </Button>
            }
          >
            Develop Migration Patterns and Planning
          </Header>
        }
      >
        <SpaceBetween size="m">
          <Alert type="info">
            Upload your AWS Calculator CSV export to generate an optimized migration 
            strategy with comprehensive planning and cost analysis. The scope and prompt 
            are pre-filled with defaults - you can use them as-is or customize them.
          </Alert>

          <Tabs
            activeTabId={activeTabId}
            onChange={({ detail }) => setActiveTabId(detail.activeTabId)}
            tabs={[
              {
                id: 'upload',
                label: 'Upload & Configure',
                content: (
                  <SpaceBetween size="l">
                    <FormField
                      label="AWS Calculator CSV"
                      description="Upload your AWS Calculator export file"
                    >
                      <FileUpload
                        value={calculatorFile}
                        onChange={({ detail }) => setCalculatorFile(detail.value)}
                        accept=".csv"
                        constraintText="CSV files only"
                      />
                    </FormField>

                    <FormField
                      label="Migration Scope"
                      description="Pre-filled with default goals - edit as needed or use as-is"
                    >
                      <Textarea
                        value={scope}
                        onChange={({ detail }) => setScope(detail.value)}
                        rows={6}
                      />
                    </FormField>

                    {error && (
                      <Alert
                        type="error"
                        dismissible
                        onDismiss={() => setError(null)}
                      >
                        {error}
                      </Alert>
                    )}

                    {loading && (
                      <Box textAlign="center" padding="l">
                        <SpaceBetween size="m" alignItems="center">
                          <Spinner size="large" />
                          <Box variant="p" color="text-body-secondary">
                            Generating migration strategy... This may take a few minutes.
                          </Box>
                        </SpaceBetween>
                      </Box>
                    )}

                    <Box textAlign="center">
                      <Button
                        variant="primary"
                        onClick={handleGenerateStrategy}
                        disabled={loading || calculatorFile.length === 0}
                      >
                        Generate Migration Strategy
                      </Button>
                    </Box>
                  </SpaceBetween>
                )
              },
              {
                id: 'prompt',
                label: 'Customize Prompt',
                content: (
                  <SpaceBetween size="l">
                    <Alert type="info">
                      The default analysis prompt is shown below. Toggle "Use Custom Prompt" to modify it for your specific needs.
                      Your custom prompt will be saved and used for future analyses.
                    </Alert>

                    <FormField>
                      <Toggle
                        checked={useCustomPrompt}
                        onChange={({ detail }) => setUseCustomPrompt(detail.checked)}
                      >
                        <Box variant="strong">Use Custom Prompt</Box>
                      </Toggle>
                    </FormField>

                    <FormField
                      label="Analysis Prompt"
                      description={useCustomPrompt ? "Edit the prompt below to customize the analysis" : "Default prompt (toggle above to edit)"}
                    >
                      <Textarea
                        value={customPrompt}
                        onChange={({ detail }) => setCustomPrompt(detail.value)}
                        rows={25}
                        disabled={!useCustomPrompt}
                      />
                    </FormField>

                    <SpaceBetween direction="horizontal" size="xs">
                      <Button
                        variant="primary"
                        onClick={saveCustomPrompt}
                        disabled={!useCustomPrompt}
                      >
                        Save Custom Prompt
                      </Button>
                      <Button
                        onClick={resetPrompt}
                      >
                        Reset to Default
                      </Button>
                    </SpaceBetween>

                    <ExpandableSection
                      headerText="Prompt Customization Tips"
                      variant="default"
                    >
                      <SpaceBetween size="s">
                        <Box variant="p">
                          <strong>Tips for customizing the prompt:</strong>
                        </Box>
                        <ul>
                          <li>Add specific migration patterns relevant to your workloads</li>
                          <li>Include industry-specific compliance requirements</li>
                          <li>Emphasize particular cost optimization strategies</li>
                          <li>Add custom wave planning criteria</li>
                          <li>Include specific AWS services you want to evaluate</li>
                          <li>Adjust the level of detail for each analysis section</li>
                        </ul>
                      </SpaceBetween>
                    </ExpandableSection>
                  </SpaceBetween>
                )
              },
              {
                id: 'results',
                label: 'Strategy Results',
                disabled: !strategy,
                content: strategy && (
                  <ExpandableSection
                    headerText="Migration Strategy Results"
                    variant="container"
                    defaultExpanded
                  >
                    <SpaceBetween size="m">
                      <Box variant="p">
                        <strong>AWS Migration Strategy & Planning</strong>
                        {recordsProcessed > 0 && (
                          <Box variant="small" color="text-status-info">
                            {recordsProcessed} records processed
                          </Box>
                        )}
                      </Box>
                      <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {strategy}
                        </ReactMarkdown>
                      </div>
                      <Button
                        onClick={() => downloadMarkdown(strategy, 'aws_migration_strategy_with_plan.md')}
                      >
                        Download Migration Strategy
                      </Button>
                    </SpaceBetween>
                  </ExpandableSection>
                )
              }
            ]}
          />
        </SpaceBetween>
      </Container>
    </SpaceBetween>
  );
}

export default MigrationStrategy;
