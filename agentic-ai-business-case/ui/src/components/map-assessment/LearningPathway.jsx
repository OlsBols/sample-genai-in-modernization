import React, { useState, useEffect } from 'react';
import {
  Container,
  Header,
  SpaceBetween,
  FormField,
  FileUpload,
  Input,
  Select,
  Button,
  Alert,
  ExpandableSection,
  Box,
  ColumnLayout,
  Tabs,
  Toggle,
  Textarea,
  Spinner
} from '@cloudscape-design/components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getApiUrl } from '../../utils/apiConfig.js';
import { useMapAssessment } from '../../contexts/MapAssessmentContext.jsx';

// Default input - pre-filled so user can use immediately
const DEFAULT_INPUT = {
  targetRole: 'Cloud Solutions Architect',
  duration: '3 months'
};

// Default prompt template
const DEFAULT_PROMPT = `As an AWS training and enablement expert, analyze the provided training catalog and generate a personalized learning pathway for the specified role and experience level.

Perform analysis in the following structured order:

## (1) Role Requirements Analysis
- Key responsibilities and skills for the target role
- Required AWS services and technologies
- Industry best practices and standards
- Certification requirements and recommendations

## (2) Skills Gap Assessment
- Current skill level evaluation
- Required competencies for target role
- Priority areas for development
- Learning objectives and outcomes

## (3) Learning Pathway Structure
- Foundational courses and prerequisites
- Core technical training modules
- Advanced and specialized topics
- Hands-on labs and practical exercises

## (4) Course Recommendations
- Recommended courses from training catalog
- Course sequence and dependencies
- Estimated duration for each course
- Learning format (classroom, online, self-paced)

## (5) Certification Roadmap
- Relevant AWS certifications
- Certification preparation strategy
- Exam prerequisites and requirements
- Study resources and practice tests

## (6) Hands-On Practice Plan
- Lab exercises and projects
- Real-world scenarios and use cases
- Sandbox environment recommendations
- Portfolio building activities

## (7) Timeline and Milestones
- Week-by-week learning schedule
- Key milestones and checkpoints
- Progress tracking recommendations
- Completion criteria and assessment

## (8) Additional Resources
- Documentation and reference materials
- Community resources and forums
- Mentorship and support options
- Continuous learning recommendations

Format your response in markdown with clear headings, bullet points, and tables where appropriate.`;

function LearningPathway() {
  const { 
    learningPathwayData, 
    setLearningPathwayData, 
    resetLearningPathway 
  } = useMapAssessment();
  
  const [trainingFile, setTrainingFile] = useState([]);
  const [targetRole, setTargetRole] = useState(DEFAULT_INPUT.targetRole);
  const [experienceLevel, setExperienceLevel] = useState({ label: 'Intermediate', value: 'intermediate' });
  const [duration, setDuration] = useState(DEFAULT_INPUT.duration);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [learningPathway, setLearningPathway] = useState(learningPathwayData.pathway || null);
  const [activeTabId, setActiveTabId] = useState('upload');
  
  // Prompt customization
  const [customPrompt, setCustomPrompt] = useState(DEFAULT_PROMPT);
  const [useCustomPrompt, setUseCustomPrompt] = useState(false);
  
  // Load existing data from context on mount
  useEffect(() => {
    if (learningPathwayData.pathway) {
      setLearningPathway(learningPathwayData.pathway);
      setActiveTabId('results');
    }
  }, []);
  
  // Load saved custom prompt from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('map_custom_prompt_learning');
    if (saved) {
      setCustomPrompt(saved);
      setUseCustomPrompt(true);
    }
  }, []);
  
  // Save custom prompt
  const saveCustomPrompt = () => {
    localStorage.setItem('map_custom_prompt_learning', customPrompt);
    alert('✓ Custom prompt saved successfully!');
  };
  
  // Reset to default
  const resetPrompt = () => {
    if (confirm('Reset prompt to default? This cannot be undone.')) {
      setCustomPrompt(DEFAULT_PROMPT);
      setUseCustomPrompt(false);
      localStorage.removeItem('map_custom_prompt_learning');
      alert('✓ Prompt reset to default!');
    }
  };

  const experienceLevels = [
    { label: 'Beginner', value: 'beginner' },
    { label: 'Intermediate', value: 'intermediate' },
    { label: 'Advanced', value: 'advanced' }
  ];

  const handleGeneratePathway = async () => {
    if (trainingFile.length === 0) {
      setError('Please upload a training data CSV file');
      return;
    }
    if (!targetRole.trim()) {
      setError('Please specify a target role');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', trainingFile[0]);
      formData.append('targetRole', targetRole);
      formData.append('experienceLevel', experienceLevel.value);
      formData.append('duration', duration);
      
      // Send custom prompt if enabled
      if (useCustomPrompt && customPrompt.trim()) {
        formData.append('custom_prompt', customPrompt);
      }

      const response = await fetch(getApiUrl('/map/learning-pathway/generate'), {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message);
      }

      setLearningPathway(result.learningPathway);
      // Save to context
      setLearningPathwayData({ pathway: result.learningPathway });
      // Switch to results tab to show the generated pathway
      setActiveTabId('results');
    } catch (err) {
      setError(err.message || 'Failed to generate learning pathway');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setLearningPathway(null);
    setTrainingFile([]);
    setTargetRole(DEFAULT_INPUT.targetRole);
    setExperienceLevel({ label: 'Intermediate', value: 'intermediate' });
    setDuration(DEFAULT_INPUT.duration);
    setActiveTabId('upload');
    resetLearningPathway();
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
            description="Personalized AWS Training Recommendations"
            actions={
              <Button onClick={handleReset} disabled={!learningPathway}>
                Reset
              </Button>
            }
          >
            Learning Pathway Development
          </Header>
        }
      >
        <SpaceBetween size="m">
          <Alert type="info">
            Generate personalized learning pathways for your AWS migration team. 
            Upload training data and specify role requirements to receive customized 
            course recommendations and duration analysis. Default values are pre-filled.
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
                      label="Training Data (CSV)"
                      description="Upload your training catalog or course data"
                    >
                      <FileUpload
                        value={trainingFile}
                        onChange={({ detail }) => setTrainingFile(detail.value)}
                        accept=".csv"
                        constraintText="CSV files only"
                      />
                    </FormField>

                    <ColumnLayout columns={3}>
                      <FormField
                        label="Target Role"
                        description="Pre-filled with default - edit as needed"
                      >
                        <Input
                          value={targetRole}
                          onChange={({ detail }) => setTargetRole(detail.value)}
                          placeholder="e.g., Cloud Architect, DevOps Engineer"
                        />
                      </FormField>

                      <FormField
                        label="Experience Level"
                        description="Current experience level"
                      >
                        <Select
                          selectedOption={experienceLevel}
                          onChange={({ detail }) => setExperienceLevel(detail.selectedOption)}
                          options={experienceLevels}
                        />
                      </FormField>

                      <FormField
                        label="Duration"
                        description="Pre-filled with default - edit as needed"
                      >
                        <Input
                          value={duration}
                          onChange={({ detail }) => setDuration(detail.value)}
                          placeholder="e.g., 3 months, 6 weeks"
                        />
                      </FormField>
                    </ColumnLayout>

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
                            Generating personalized learning pathway... This may take a few minutes.
                          </Box>
                        </SpaceBetween>
                      </Box>
                    )}

                    <Box textAlign="center">
                      <Button
                        variant="primary"
                        onClick={handleGeneratePathway}
                        disabled={loading || trainingFile.length === 0 || !targetRole.trim()}
                      >
                        Generate Learning Pathway
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
                          <li>Add specific certifications required for your organization</li>
                          <li>Include industry-specific training requirements</li>
                          <li>Emphasize particular AWS services or technologies</li>
                          <li>Add custom learning formats or delivery methods</li>
                          <li>Include specific skill assessment criteria</li>
                          <li>Adjust the level of detail for each learning section</li>
                        </ul>
                      </SpaceBetween>
                    </ExpandableSection>
                  </SpaceBetween>
                )
              },
              {
                id: 'results',
                label: 'Pathway Results',
                disabled: !learningPathway,
                content: learningPathway && (
                  <ExpandableSection
                    headerText="Learning Pathway Results"
                    variant="container"
                    defaultExpanded
                  >
                    <SpaceBetween size="m">
                      <Box variant="p">
                        <strong>Personalized AWS Training Pathway</strong>
                      </Box>
                      <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {learningPathway}
                        </ReactMarkdown>
                      </div>
                      <Button
                        onClick={() => downloadMarkdown(learningPathway, 'learning_pathway.md')}
                      >
                        Download Learning Pathway
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

export default LearningPathway;
