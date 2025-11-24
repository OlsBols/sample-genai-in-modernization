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
  setBusinessCaseResult
}) => {
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
                  { label: 'Agents Selected', value: `${getAgentCount()} agents` },
                  { label: 'Run Mode', value: selectedAgents.runAll ? 'All Agents' : 'Custom Selection' }
                ]}
              />
            </Box>
          </SpaceBetween>
        </ColumnLayout>

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
