# Learning Pathway Prompt

## Description
The `learning_pathway_prompt.py` module provides a specialised prompt generation function for creating comprehensive AWS migration and modernisation training pathways. This module generates detailed prompts that instruct AI models to design role-specific, experience-tailored learning programmes aligned with the AWS Migration Acceleration Programme (MAP) and current industry best practices. The training data is sourced from a structured CSV template that categorises courses into business and technical tracks.

## Primary Purpose
- Generate customised AWS training pathway recommendations based on role, experience level, and time constraints
- Create structured learning programmes for AWS migration and modernisation initiatives using predefined course catalogue
- Provide practical, role-relevant competencies for AWS migration projects
- Support organisational upskilling and capability development for AWS adoption using standardised training templates

## Key Features
- **Role-Specific Customisation**: Tailors training pathways to specific job roles and responsibilities
- **Experience Level Adaptation**: Adjusts content complexity based on learner's current experience level
- **Duration Management**: Ensures training programmes fit within specified time constraints and weekly hour limits (maximum 40 hours per week)
- **Progressive Learning Structure**: Builds expertise systematically from foundational to advanced concepts
- **Practical Focus**: Emphasises hands-on, real-world migration scenarios and use cases
- **Dual Perspective Integration**: Combines technical and business viewpoints where appropriate
- **Structured Output Format**: Generates standardised table format with detailed rationale
- **Template-Based Training Data**: Uses structured CSV format from `sampledata/sample-training-template.csv` for consistent course information

## Input Parameters

### Function: `get_learning_pathway_prompt(training_data, target_role, target_experience, learning_duration)`

- **Parameter**: `training_data`
  - **Type**: String/Object (CSV-based)
  - **Required**: Yes
  - **Description**: Comprehensive training course data sourced from `sampledata/sample-training-template.csv` with mandatory structure including course IDs, titles, training links, and detailed descriptions
  - **Template Structure**: 
    - `Course Id`: Unique identifier following pattern (BA-XXX, BM-XXX, BMM-XXX)
    - `title`: Training course name
    - `training_link`: URL(s) to course resources (AWS Skill Builder, documentation, workshops)
    - `details`: Comprehensive course description and learning objectives
- **Parameter**: `target_role`
  - **Type**: String
  - **Required**: Yes
  - **Description**: Specific job role or position for which the training pathway is being designed

- **Parameter**: `target_experience`
  - **Type**: String
  - **Required**: Yes
  - **Description**: Current experience level of the target learner

- **Parameter**: `learning_duration`
  - **Type**: String/Number
  - **Required**: Yes
  - **Description**: Maximum allowable duration for the complete training pathway
  - **Example**: "40 hours", "2 weeks", "1 month"
  - **Constraint**: Total weekly training must not exceed 40 hours

## Expected Output Structure

The function returns a comprehensive prompt that instructs the AI to generate:

### 1. Training Pathway Table
A structured table with the following mandatory format:
```markdown
| Course Id | Training Name | Description | Duration (minutes) |
|-----------|---------------|-------------|-------------------|
| [ID]      | [Title]       | [Summary]   | [Time]           |
```

**Table Components**:
- **Course Id**: Exact identifier from the CSV template (BA-001, BM-005, BMM-003, etc.)
- **Training Name**: Exact course title from the `title` column in the template
- **Description**: Concise course summary from the `details` column
- **Duration**: Time allocation in minutes for each training module

### 2. Detailed Rationale Section
Comprehensive analysis covering:

- **Total Duration Analysis**: Complete time investment expressed in hours with breakdown
- **Role-Specific Justification**: Explanation of why specific trainings align with the target role's responsibilities
- **Experience Level Alignment**: Assessment of how the pathway matches the learner's current skill level
- **Expected Outcomes**: Detailed skills and competencies gained upon pathway completion

### 3. Key Requirements Integration
- Latest AWS services and features coverage from template courses
- Industry best practices incorporation through structured course progression
- Real-world migration scenarios alignment with MAP through practical workshops
- Technical and business perspective balance via categorisation
- Practical, hands-on learning emphasis through workshop-based courses

## Usage Context

### AWS Migration and Modernisation Projects
- Designing training programmes for migration teams using standardised course catalogue
- Upskilling existing staff for cloud adoption initiatives with proven training paths
- Creating role-specific learning paths for different team members based on template structure
- Supporting organisational change management during cloud transformation

### Learning and Development Programmes
- Professional development planning with structured progression paths
- Skills gap analysis and remediation using comprehensive course categories

### Integration Points
- Works with training management systems using CSV-based course data
- Can be integrated into HR and L&D workflows with structured course identifiers
- Supports migration project planning and resource allocation through role-specific pathways

### Example Usage
```python
from learning_pathway_prompt import get_learning_pathway_prompt

# Load training data from CSV template
import pandas as pd
training_data = pd.read_csv('sampledata/sample-training-template.csv')

# Generate training pathway for a Solutions Architect
target_role = "Solutions Architect"
target_experience = "Intermediate"
learning_duration = "40 hours"

pathway_prompt = get_learning_pathway_prompt(
    training_data, 
    target_role, 
    target_experience, 
    learning_duration
)

# The prompt will generate pathways using courses like:
# BA-001: Migration Readiness Assessment
# BM-005: AWS Well Architected
# BMM-001: AWS Application Migration Service
```

## Related Files
- `pages/04_learning_pathway.py` - UI implementation for learning pathway generation
- `sampledata/sample-training-template.csv` - **Mandatory training course data template** with structured course information
- `utils/` - Supporting utilities for CSV processing and pathway generation

## Constraints and Considerations
- **Weekly Hour Limit**: Ensures training programmes remain under 40 hours per week
- **Duration Compliance**: Total pathway duration must not exceed specified learning_duration
- **Progressive Structure**: Maintains logical skill progression from BA (assessment) → BM (migration) → BMM (modernisation)
- **Role Relevance**: Focuses on practical competencies directly applicable to the target role
- **Template Dependency**: Requires valid CSV template structure for proper course selection and pathway generation