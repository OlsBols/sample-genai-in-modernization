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

// Default input - pre-filled so user can use immediately
const DEFAULT_INPUT = `Migration Strategy Context:
- 6-month migration timeline with 3 waves
- Focus on lift-and-shift for initial wave
- Modernization in subsequent waves
- 24/7 support required during migration

Wave Planning Context:
- Wave 1: Non-critical applications (Month 1-2)
- Wave 2: Business applications (Month 3-4)
- Wave 3: Critical systems (Month 5-6)`;

// Default prompt template
const DEFAULT_PROMPT = `As an AWS migration resource planning expert, analyze the provided resource profile data and generate a comprehensive team structure and resource allocation plan.

Perform analysis in the following structured order:

## (1) Resource Requirements Analysis
- Required roles and skill sets for migration
- Team size recommendations by phase
- Skills gap analysis
- Training and certification needs

## (2) Team Structure & Organization
- Recommended organizational structure
- Roles and responsibilities matrix
- Reporting relationships
- Communication and escalation paths

## (3) Resource Allocation by Phase
- Pre-migration phase staffing
- Migration execution phase staffing
- Post-migration support staffing
- Ramp-up and ramp-down planning

## (4) Cost Projections & Budget
- Labor cost estimates by role
- Training and certification costs
- Contractor vs. FTE analysis
- Total resource budget projection

## (5) Skills Development Plan
- Required AWS certifications
- Training curriculum recommendations
- Hands-on lab and practice requirements
- Knowledge transfer strategy

## (6) Resource Timeline & Milestones
- Resource onboarding schedule
- Key milestone dependencies
- Peak resource utilization periods
- Resource release planning

## (7) Risk Mitigation & Contingency
- Resource availability risks
- Skills shortage mitigation
- Backup resource planning
- Vendor and partner engagement strategy

Format your response in markdown with clear headings, bullet points, and tables where appropriate.`;

function ResourcePlanning() {
  const { 
    resourcePlanningData, 
    setResourcePlanningData, 
    resetResourcePlanning 
  } = useMapAssessment();
  
  const [resourceFile, setResourceFile] = useState([]);
  const [migrationStrategy, setMigrationStrategy] = useState(DEFAULT_INPUT);
  const [wavePlanning, setWavePlanning] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resourcePlan, setResourcePlan] = useState(resourcePlanningData.plan || null);
  const [activeTabId, setActiveTabId] = useState('upload');
  
  // Prompt customization
  const [customPrompt, setCustomPrompt] = useState(DEFAULT_PROMPT);
  const [useCustomPrompt, setUseCustomPrompt] = useState(false);
  
  // Load existing data from context on mount
  useEffect(() => {
    if (resourcePlanningData.plan) {
      setResourcePlan(resourcePlanningData.plan);
      setActiveTabId('results');
    }
  }, []);
  
  // Load saved custom prompt from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('map_custom_prompt_resource');
    if (saved) {
      setCustomPrompt(saved);
      setUseCustomPrompt(true);
    }
  }, []);
  
  // Save custom prompt
  const saveCustomPrompt = () => {
    localStorage.setItem('map_custom_prompt_resource', customPrompt);
    alert('✓ Custom prompt saved successfully!');
  };
  
  // Reset to default
  const resetPrompt = () => {
    if (confirm('Reset prompt to default? This cannot be undone.')) {
      setCustomPrompt(DEFAULT_PROMPT);
      setUseCustomPrompt(false);
      localStorage.removeItem('map_custom_prompt_resource');
      alert('✓ Prompt reset to default!');
    }
  };

  const handleGeneratePlan = async () => {
    if (resourceFile.length === 0) {
      setError('Please upload a resource profile CSV file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', resourceFile[0]);
      formData.append('migrationStrategy', migrationStrategy);
      formData.append('wavePlanning', wavePlanning);
      
      // Send custom prompt if enabled
      if (useCustomPrompt && customPrompt.trim()) {
        formData.append('custom_prompt', customPrompt);
      }

      const response = await fetch(getApiUrl('/map/resource-planning/generate'), {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message);
      }

      setResourcePlan(result.resourcePlan);
      // Save to context
      setResourcePlanningData({ plan: result.resourcePlan });
      // Switch to results tab to show the generated plan
      setActiveTabId('results');
    } catch (err) {
      setError(err.message || 'Failed to generate resource plan');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResourcePlan(null);
    setResourceFile([]);
    setMigrationStrategy(DEFAULT_INPUT);
    setWavePlanning('');
    setActiveTabId('upload');
    resetResourcePlanning();
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
            description="Team Structure and Resource Allocation"
            actions={
              <Button onClick={handleReset} disabled={!resourcePlan}>
                Reset
              </Button>
            }
          >
            Resource Planning
          </Header>
        }
      >
        <SpaceBetween size="m">
          <Alert type="info">
            Upload your resource profile to generate team structure recommendations, 
            resource allocation plans, and cost projections for your migration project.
            The context fields are pre-filled with defaults - you can use them as-is or customize them.
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
                      label="Resource Profile (CSV)"
                      description="Upload your resource profile template"
                    >
                      <FileUpload
                        value={resourceFile}
                        onChange={({ detail }) => setResourceFile(detail.value)}
                        accept=".csv"
                        constraintText="CSV files only"
                      />
                    </FormField>

                    <FormField
                      label="Migration Strategy Context"
                      description="Pre-filled with default context - edit as needed or use as-is"
                    >
                      <Textarea
                        value={migrationStrategy}
                        onChange={({ detail }) => setMigrationStrategy(detail.value)}
                        rows={6}
                      />
                    </FormField>

                    <FormField
                      label="Wave Planning (Optional)"
                      description="Provide additional wave planning details"
                    >
                      <Textarea
                        value={wavePlanning}
                        onChange={({ detail }) => setWavePlanning(detail.value)}
                        placeholder="Enter wave planning details..."
                        rows={4}
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
                            Generating resource plan... This may take a few minutes.
                          </Box>
                        </SpaceBetween>
                      </Box>
                    )}

                    <Box textAlign="center">
                      <Button
                        variant="primary"
                        onClick={handleGeneratePlan}
                        disabled={loading || resourceFile.length === 0}
                      >
                        Generate Resource Plan
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
                          <li>Add specific roles required for your organization</li>
                          <li>Include regional or location-specific requirements</li>
                          <li>Emphasize particular skill sets or certifications</li>
                          <li>Add custom cost models or budget constraints</li>
                          <li>Include specific team structure preferences</li>
                          <li>Adjust the level of detail for each planning section</li>
                        </ul>
                      </SpaceBetween>
                    </ExpandableSection>
                  </SpaceBetween>
                )
              },
              {
                id: 'results',
                label: 'Planning Results',
                disabled: !resourcePlan,
                content: resourcePlan && (
                  <ExpandableSection
                    headerText="Resource Planning Results"
                    variant="container"
                    defaultExpanded
                  >
                    <SpaceBetween size="m">
                      <Box variant="p">
                        <strong>Team Structure & Resource Allocation Plan</strong>
                      </Box>
                      <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {resourcePlan}
                        </ReactMarkdown>
                      </div>
                      <Button
                        onClick={() => downloadMarkdown(resourcePlan, 'resource_planning.md')}
                      >
                        Download Resource Plan
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

export default ResourcePlanning;
