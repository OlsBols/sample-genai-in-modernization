import React from 'react';
import {
  Container,
  Header,
  SpaceBetween,
  Box,
  ColumnLayout,
  Button,
  ProgressBar,
  Alert,
  StatusIndicator,
  KeyValuePairs
} from '@cloudscape-design/components';
import { generateBusinessCase } from '../services/api';

const ReviewStep = ({
  projectInfo,
  uploadedFiles,
  selectedAgents,
  generationStatus,
  setGenerationStatus,
  setBusinessCaseResult,
  setActiveStepIndex
}) => {
  
  const agentNames = {
    itInventory: 'IT Inventory Analysis',
    rvTool: 'RVTool VMware Analysis',
    atx: 'ATX VMware Analysis',
    mra: 'MRA Organizational Readiness',
    currentState: 'Current State Synthesis',
    costAnalysis: 'AWS Cost Analysis',
    migrationStrategy: 'Migration Strategy (6Rs)',
    migrationPlan: 'Migration Plan (MAP)',
    businessCase: 'Business Case Generation'
  };
  const handleGenerate = async () => {
    setGenerationStatus({
      isGenerating: true,
      progress: 0,
      currentAgent: 'Initializing...',
      completed: false,
      error: null
    });

    try {
      // Simulate progress updates
      const agents = Object.entries(selectedAgents.agents)
        .filter(([_, enabled]) => enabled)
        .map(([id, _]) => id);

      for (let i = 0; i < agents.length; i++) {
        setGenerationStatus(prev => ({
          ...prev,
          progress: ((i + 1) / agents.length) * 100,
          currentAgent: `Running ${agents[i]} agent...`
        }));
        
        // Simulate agent execution time
        await new Promise(resolve => setTimeout(resolve, 2000));
      }

      // Call the actual API
      const result = await generateBusinessCase({
        projectInfo,
        uploadedFiles,
        selectedAgents: agents
      });

      console.log('API Result:', result); // Debug log
      setBusinessCaseResult(result);
      setGenerationStatus({
        isGenerating: false,
        progress: 100,
        currentAgent: 'Completed',
        completed: true,
        error: null
      });
      
      // Auto-navigate to results step after successful generation
      setTimeout(() => {
        setActiveStepIndex(3); // Move to results step
      }, 1000);
    } catch (error) {
      setGenerationStatus({
        isGenerating: false,
        progress: 0,
        currentAgent: '',
        completed: false,
        error: error.message || 'Failed to generate business case'
      });
    }
  };

  const getFileCount = () => {
    return Object.values(uploadedFiles).filter(Boolean).length;
  };

  const getAgentCount = () => {
    return Object.values(selectedAgents.agents).filter(Boolean).length;
  };

  return (
    <Container
      header={
        <Header
          variant="h2"
          description="Review your configuration and generate the business case"
        >
          Review & Generate
        </Header>
      }
    >
      <SpaceBetween size="l">
        {!generationStatus.completed && !generationStatus.isGenerating && (
          <Alert type="info">
            Review the information below and click "Generate Business Case" to start the analysis.
          </Alert>
        )}

        <ColumnLayout columns={2} variant="text-grid">
          <SpaceBetween size="l">
            <Box>
              <Box variant="awsui-key-label">Project Information</Box>
              <KeyValuePairs
                columns={1}
                items={[
                  { label: 'Project Name', value: projectInfo.projectName || 'Not provided' },
                  { label: 'Customer Name', value: projectInfo.customerName || 'Not provided' },
                  { label: 'AWS Region', value: projectInfo.awsRegion },
                  { label: 'Description', value: projectInfo.projectDescription || 'Not provided' }
                ]}
              />
            </Box>
          </SpaceBetween>

          <SpaceBetween size="l">
            <Box>
              <Box variant="awsui-key-label">Configuration Summary</Box>
              <KeyValuePairs
                columns={1}
                items={[
                  { label: 'Files Uploaded', value: `${getFileCount()} files` },
                  { label: 'Agents Selected', value: `${getAgentCount()} agents` }
                ]}
              />
            </Box>
          </SpaceBetween>
        </ColumnLayout>

        <Box>
          <Box variant="awsui-key-label" margin={{ bottom: 's' }}>Agents That Will Run</Box>
          <Alert type="info">
            Agents are automatically selected based on your uploaded files. Phase 2, 3, and 4 agents always run to generate the complete business case.
          </Alert>
          <Box margin={{ top: 's' }}>
            <SpaceBetween size="xs">
              {Object.entries(selectedAgents.agents)
                .filter(([_, enabled]) => enabled)
                .map(([agentId, _]) => (
                  <Box key={agentId}>
                    <StatusIndicator type="success">
                      {agentNames[agentId] || agentId}
                    </StatusIndicator>
                  </Box>
                ))}
            </SpaceBetween>
          </Box>
        </Box>

        {generationStatus.isGenerating && (
          <SpaceBetween size="m">
            <Box>
              <StatusIndicator type="in-progress">
                {generationStatus.currentAgent}
              </StatusIndicator>
            </Box>
            <ProgressBar
              value={generationStatus.progress}
              label="Generation Progress"
              description="This may take 6-10 minutes depending on the number of agents selected"
              additionalInfo={`${Math.round(generationStatus.progress)}% complete`}
            />
          </SpaceBetween>
        )}

        {generationStatus.completed && (
          <Alert type="success">
            Business case generated successfully! Proceed to the Results step to view and export.
          </Alert>
        )}

        {generationStatus.error && (
          <Alert type="error">
            {generationStatus.error}
          </Alert>
        )}

        {!generationStatus.completed && (
          <Box float="right">
            <Button
              variant="primary"
              onClick={handleGenerate}
              loading={generationStatus.isGenerating}
              disabled={!projectInfo.projectName || getFileCount() === 0}
            >
              Generate Business Case
            </Button>
          </Box>
        )}
      </SpaceBetween>
    </Container>
  );
};

export default ReviewStep;
