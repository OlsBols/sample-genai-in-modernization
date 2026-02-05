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
  ProgressBar,
  Box,
  ColumnLayout,
  Tabs,
  Toggle,
  Spinner
} from '@cloudscape-design/components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getApiUrl } from '../../utils/apiConfig.js';

// Default scope - pre-filled so user can use immediately
const DEFAULT_SCOPE = `Migration and Modernization Goals:
- Migrate on-premises infrastructure to AWS cloud
- Modernize legacy applications for cloud-native architecture  
- Improve scalability, reliability, and cost efficiency
- Implement DevOps practices and automation
- Enhance disaster recovery and business continuity capabilities`;

// Default prompt template
const DEFAULT_PROMPT = `As an AWS migration expert, conduct a comprehensive analysis of the provided IT inventory with emphasis on cost optimisation, performance metrics, disaster recovery capabilities, and strategic planning.

**IMPORTANT: Do not assume, estimate, or calculate any costs, prices, or financial figures unless explicitly provided in the inventory data.**

Perform analysis in the following structured order:

## (1) Inventory Insight & Cost Verification
- Asset Categorisation: Identify and categorise by Compute, Storage, Database, Networking, Security, Monitoring, DevOps, AI, ML
- Purchase Price Verification: Review and validate purchase prices, acquisition dates, and depreciation schedules if available
- Cost Categorisation: Break down costs by asset type with detailed cost allocation if available

## (2) Capacity & Performance Analysis
- Utilisation Metrics: CPU usage, memory usage, storage usage, and network bandwidth patterns
- Critical Capacity Issues: Identify systems operating above 80% capacity
- Performance Trends: Analyse utilisation patterns, peak usage times, and growth trajectories

## (3) Disaster Recovery & Business Continuity Analysis
- Storage Systems Assessment: Analyse storage infrastructure with capacity, performance metrics, and backup capabilities
- Recovery Requirements (RTO/RPO): Analyse business impact classifications and acceptable downtime windows
- Backup Strategies Analysis: Review backup frequency schedules and retention policies

## (4) Risk Assessment & End-of-Life Planning
- End-of-Life Identification: List all hardware approaching end-of-life within 12 months
- Security Vulnerabilities: Identify unsupported or obsolete systems
- Business Continuity Impact: Assess potential service disruption risks

## (5) Cost Optimisation Opportunities
- Licence Consolidation Savings: Identify potential software licence optimisation opportunities
- Immediate Cost Reduction: Identify quick wins for cost reduction
- DR Cost Efficiency: Analyse DR infrastructure costs

## (6) Patterns, Anomalies & Dependencies
- Usage Patterns: Identify trends, seasonal variations, and anomalous behaviour
- Asset Dependencies: Map critical relationships and dependencies between systems

## (7) Strategic Recommendations & Key Findings
- Executive Summary: Data-driven insights based solely on available data
- DR Readiness Assessment: Overall disaster recovery maturity and gaps
- Migration Priorities: Systems requiring immediate attention

Format your response in markdown with clear headings, bullet points, and tables where appropriate.`;

function ModernizationOpportunity() {
  const [inventoryFile, setInventoryFile] = useState([]);
  const [architectureFile, setArchitectureFile] = useState([]);
  const [scope, setScope] = useState(DEFAULT_SCOPE); // Pre-filled with default
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [inventoryAnalysis, setInventoryAnalysis] = useState(null);
  const [architectureAnalysis, setArchitectureAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [inventoryData, setInventoryData] = useState(null);
  const [activeTabId, setActiveTabId] = useState('upload');
  
  // Prompt customization
  const [customPrompt, setCustomPrompt] = useState(DEFAULT_PROMPT);
  const [useCustomPrompt, setUseCustomPrompt] = useState(false);
  
  // Load saved custom prompt from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('map_custom_prompt_inventory');
    if (saved) {
      setCustomPrompt(saved);
      setUseCustomPrompt(true);
    }
  }, []);
  
  // Save custom prompt
  const saveCustomPrompt = () => {
    localStorage.setItem('map_custom_prompt_inventory', customPrompt);
    alert('✓ Custom prompt saved successfully!');
  };
  
  // Reset to default
  const resetPrompt = () => {
    if (confirm('Reset prompt to default? This cannot be undone.')) {
      setCustomPrompt(DEFAULT_PROMPT);
      setUseCustomPrompt(false);
      localStorage.removeItem('map_custom_prompt_inventory');
      alert('✓ Prompt reset to default!');
    }
  };

  const handleAnalyzeInventory = async () => {
    if (inventoryFile.length === 0) {
      setError('Please upload an IT inventory CSV file');
      return;
    }
    if (!scope.trim()) {
      setError('Please provide modernization scope details');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Step 1: Analyze inventory
      const formData = new FormData();
      formData.append('file', inventoryFile[0]);
      
      // Send custom prompt if enabled
      if (useCustomPrompt && customPrompt.trim()) {
        formData.append('custom_prompt', customPrompt);
      }

      const inventoryResponse = await fetch(getApiUrl('/map/modernization/analyze-inventory'), {
        method: 'POST',
        body: formData
      });

      const inventoryResult = await inventoryResponse.json();
      
      if (!inventoryResult.success) {
        throw new Error(inventoryResult.message);
      }

      setInventoryAnalysis(inventoryResult.analysis);
      setInventoryData(inventoryResult);

      // Step 2: Analyze architecture if provided
      if (architectureFile.length > 0) {
        const archFormData = new FormData();
        archFormData.append('file', architectureFile[0]);

        const archResponse = await fetch(getApiUrl('/map/modernization/analyze-architecture'), {
          method: 'POST',
          body: archFormData
        });

        const archResult = await archResponse.json();
        
        if (archResult.success) {
          setArchitectureAnalysis(archResult.analysis);
        }
      }

      setActiveTabId('results');
    } catch (err) {
      setError(err.message || 'Failed to analyze inventory');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRecommendations = async () => {
    if (!inventoryData) {
      setError('Please analyze inventory first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Read CSV data for recommendations
      const reader = new FileReader();
      reader.onload = async (e) => {
        const text = e.target.result;
        const rows = text.split('\n').map(row => row.split(','));
        const headers = rows[0];
        const data = rows.slice(1).map(row => {
          const obj = {};
          headers.forEach((header, i) => {
            obj[header] = row[i];
          });
          return obj;
        });

        const response = await fetch(getApiUrl('/map/modernization/recommend-pathways'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            inventoryData: data,
            scope: scope,
            architectureDescription: architectureAnalysis
          })
        });

        const result = await response.json();
        
        if (!result.success) {
          throw new Error(result.message);
        }

        setRecommendations(result.recommendations);
        setLoading(false);
      };

      reader.readAsText(inventoryFile[0]);
    } catch (err) {
      setError(err.message || 'Failed to generate recommendations');
      setLoading(false);
    }
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
            description="Using On-Premises Discovery Data"
          >
            Identify Modernization Opportunity
          </Header>
        }
      >
        <SpaceBetween size="m">
          <Alert type="info">
            Upload your IT inventory CSV file and optionally an architecture diagram. 
            The scope and prompt are pre-filled with defaults - you can use them as-is or customize them.
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
                    <ColumnLayout columns={2}>
                      <FormField
                        label="IT Inventory (CSV)"
                        description="Upload your IT infrastructure inventory"
                      >
                        <FileUpload
                          value={inventoryFile}
                          onChange={({ detail }) => setInventoryFile(detail.value)}
                          accept=".csv"
                          constraintText="CSV files only"
                        />
                      </FormField>

                      <FormField
                        label="On-Premises Architecture (Optional)"
                        description="Upload architecture diagram for enhanced analysis"
                      >
                        <FileUpload
                          value={architectureFile}
                          onChange={({ detail }) => setArchitectureFile(detail.value)}
                          accept=".jpg,.jpeg,.png"
                          constraintText="Image files only (JPG, PNG)"
                        />
                      </FormField>
                    </ColumnLayout>

                    <FormField
                      label="Modernization Scope"
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
                            Analyzing inventory data... This may take a few minutes.
                          </Box>
                        </SpaceBetween>
                      </Box>
                    )}

                    <Box textAlign="center">
                      <SpaceBetween direction="horizontal" size="xs">
                        <Button
                          variant="primary"
                          onClick={handleAnalyzeInventory}
                          disabled={loading || inventoryFile.length === 0}
                        >
                          Analyze Inventory
                        </Button>
                      </SpaceBetween>
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
                          <li>Add specific focus areas relevant to your organization (e.g., HIPAA compliance, PCI-DSS)</li>
                          <li>Include industry-specific requirements or regulations</li>
                          <li>Emphasize particular cost optimization strategies</li>
                          <li>Add custom reporting formats or specific metrics to track</li>
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
                label: 'Analysis Results',
                disabled: !inventoryAnalysis,
                content: (
                  <SpaceBetween size="l">
                    {inventoryAnalysis && (
                      <ExpandableSection
                        headerText="Inventory Analysis"
                        variant="container"
                        defaultExpanded
                      >
                        <SpaceBetween size="m">
                          <Box variant="p">
                            <strong>Comprehensive IT Infrastructure Analysis</strong>
                          </Box>
                          <div className="markdown-content">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {inventoryAnalysis}
                            </ReactMarkdown>
                          </div>
                          <Button
                            onClick={() => downloadMarkdown(inventoryAnalysis, 'inventory_analysis.md')}
                          >
                            Download Analysis Report
                          </Button>
                        </SpaceBetween>
                      </ExpandableSection>
                    )}

                    {architectureAnalysis && (
                      <ExpandableSection
                        headerText="Architecture Analysis"
                        variant="container"
                        defaultExpanded
                      >
                        <SpaceBetween size="m">
                          <Box variant="p">
                            <strong>On-Premises Architecture Assessment</strong>
                          </Box>
                          <div className="markdown-content">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {architectureAnalysis}
                            </ReactMarkdown>
                          </div>
                          <Button
                            onClick={() => downloadMarkdown(architectureAnalysis, 'onprem_architecture.md')}
                          >
                            Download Architecture Report
                          </Button>
                        </SpaceBetween>
                      </ExpandableSection>
                    )}

                    {!recommendations && (
                      <Box textAlign="center">
                        <Button
                          variant="primary"
                          onClick={handleGenerateRecommendations}
                          disabled={loading}
                        >
                          Provide Modernization Recommendations
                        </Button>
                      </Box>
                    )}

                    {recommendations && (
                      <ExpandableSection
                        headerText="Modernization Recommendations"
                        variant="container"
                        defaultExpanded
                      >
                        <SpaceBetween size="m">
                          <Box variant="p">
                            <strong>AWS Modernization Pathway Recommendations</strong>
                          </Box>
                          <div className="markdown-content">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {recommendations}
                            </ReactMarkdown>
                          </div>
                          <Button
                            onClick={() => downloadMarkdown(recommendations, 'aws_modernization_approach.md')}
                          >
                            Download Modernization Strategy
                          </Button>
                        </SpaceBetween>
                      </ExpandableSection>
                    )}
                  </SpaceBetween>
                )
              }
            ]}
          />
        </SpaceBetween>
      </Container>
    </SpaceBetween>
  );
}

export default ModernizationOpportunity;
