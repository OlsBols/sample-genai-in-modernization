import React, { useState, useEffect } from 'react';
import {
  Container,
  Header,
  SpaceBetween,
  FormField,
  FileUpload,
  Button,
  Alert,
  ExpandableSection,
  Box,
  Tabs,
  Toggle,
  Textarea,
  Spinner
} from '@cloudscape-design/components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getApiUrl } from '../../utils/apiConfig.js';

// Default prompt template
const DEFAULT_PROMPT = `As an AWS business case validation expert, conduct a comprehensive review and analysis of the provided business case document.

Perform analysis in the following structured order:

## (1) Executive Summary Review
- Overall business case quality assessment
- Key findings and recommendations summary
- Critical gaps or missing information
- Alignment with AWS best practices

## (2) TCO Analysis Validation
- Current infrastructure cost analysis
- Projected AWS cost calculations
- Cost assumptions and methodology review
- Savings projections and ROI validation

## (3) Migration Strategy Assessment
- Proposed migration approach evaluation
- 7R strategy application review
- Timeline and phasing analysis
- Risk assessment and mitigation plans

## (4) Technical Architecture Review
- Proposed AWS architecture evaluation
- Service selection and sizing validation
- High availability and disaster recovery design
- Security and compliance considerations

## (5) Financial Analysis
- Capital vs. operational expense comparison
- Break-even analysis
- Cash flow projections
- Financial risk assessment

## (6) Resource and Timeline Validation
- Team structure and staffing plan review
- Project timeline and milestones assessment
- Resource allocation and cost validation
- Training and enablement requirements

## (7) Risk and Compliance Review
- Identified risks and mitigation strategies
- Compliance and regulatory requirements
- Security and governance considerations
- Business continuity planning

## (8) Recommendations and Improvements
- Strengths of the current business case
- Areas requiring additional detail or clarification
- Suggested improvements and enhancements
- Next steps and action items

Format your response in markdown with clear headings, bullet points, and tables where appropriate.`;

function BusinessCaseReview() {
  const [pdfFile, setPdfFile] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validation, setValidation] = useState(null);
  const [pagesProcessed, setPagesProcessed] = useState(0);
  const [activeTabId, setActiveTabId] = useState('upload');
  
  // Prompt customization
  const [customPrompt, setCustomPrompt] = useState(DEFAULT_PROMPT);
  const [useCustomPrompt, setUseCustomPrompt] = useState(false);
  
  // Load saved custom prompt from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('map_custom_prompt_business');
    if (saved) {
      setCustomPrompt(saved);
      setUseCustomPrompt(true);
    }
  }, []);
  
  // Save custom prompt
  const saveCustomPrompt = () => {
    localStorage.setItem('map_custom_prompt_business', customPrompt);
    alert('✓ Custom prompt saved successfully!');
  };
  
  // Reset to default
  const resetPrompt = () => {
    if (confirm('Reset prompt to default? This cannot be undone.')) {
      setCustomPrompt(DEFAULT_PROMPT);
      setUseCustomPrompt(false);
      localStorage.removeItem('map_custom_prompt_business');
      alert('✓ Prompt reset to default!');
    }
  };

  const handleValidate = async () => {
    if (pdfFile.length === 0) {
      setError('Please upload a business case PDF file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', pdfFile[0]);
      
      // Send custom prompt if enabled
      if (useCustomPrompt && customPrompt.trim()) {
        formData.append('custom_prompt', customPrompt);
      }

      const response = await fetch(getApiUrl('/map/business-validation/validate'), {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message);
      }

      setValidation(result.validation);
      setPagesProcessed(result.pagesProcessed);
      // Switch to results tab to show the validation
      setActiveTabId('results');
    } catch (err) {
      setError(err.message || 'Failed to validate business case');
    } finally {
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
            description="Comprehensive TCO Analysis and Validation"
          >
            Business Case Review
          </Header>
        }
      >
        <SpaceBetween size="m">
          <Alert type="info">
            Upload your business case PDF document for comprehensive validation and analysis. 
            The system will review TCO calculations, migration strategies, and provide 
            recommendations for improvement.
          </Alert>

          <Tabs
            activeTabId={activeTabId}
            onChange={({ detail }) => setActiveTabId(detail.activeTabId)}
            tabs={[
              {
                id: 'upload',
                label: 'Upload Document',
                content: (
                  <SpaceBetween size="l">
                    <FormField
                      label="Business Case Document (PDF)"
                      description="Upload your business case PDF for validation"
                    >
                      <FileUpload
                        value={pdfFile}
                        onChange={({ detail }) => setPdfFile(detail.value)}
                        accept=".pdf"
                        constraintText="PDF files only"
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
                            Validating business case... This may take a few minutes.
                          </Box>
                        </SpaceBetween>
                      </Box>
                    )}

                    <Box textAlign="center">
                      <Button
                        variant="primary"
                        onClick={handleValidate}
                        disabled={loading || pdfFile.length === 0}
                      >
                        Validate Business Case
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
                      The default validation prompt is shown below. Toggle "Use Custom Prompt" to modify it for your specific needs.
                      Your custom prompt will be saved and used for future validations.
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
                      label="Validation Prompt"
                      description={useCustomPrompt ? "Edit the prompt below to customize the validation" : "Default prompt (toggle above to edit)"}
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
                          <li>Add specific validation criteria for your organization</li>
                          <li>Include industry-specific compliance requirements</li>
                          <li>Emphasize particular financial metrics or KPIs</li>
                          <li>Add custom risk assessment frameworks</li>
                          <li>Include specific AWS Well-Architected pillars to focus on</li>
                          <li>Adjust the level of detail for each validation section</li>
                        </ul>
                      </SpaceBetween>
                    </ExpandableSection>
                  </SpaceBetween>
                )
              },
              {
                id: 'results',
                label: 'Validation Results',
                disabled: !validation,
                content: validation && (
                  <ExpandableSection
                    headerText="Validation Results"
                    variant="container"
                    defaultExpanded
                  >
                    <SpaceBetween size="m">
                      <Box variant="p">
                        <strong>Business Case Validation & Analysis</strong>
                        {pagesProcessed > 0 && (
                          <Box variant="small" color="text-status-info">
                            {pagesProcessed} pages analyzed
                          </Box>
                        )}
                      </Box>
                      <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {validation}
                        </ReactMarkdown>
                      </div>
                      <Button
                        onClick={() => downloadMarkdown(validation, 'business_case_validation.md')}
                      >
                        Download Validation Report
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

export default BusinessCaseReview;
