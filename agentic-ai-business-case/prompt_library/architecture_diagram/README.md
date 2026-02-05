# Architecture Diagram Prompt

## Description
The `architecture_diagram_prompt.py` module provides a specialized prompt generation function for creating AWS architecture diagrams in Draw.io XML format. This module is designed to generate comprehensive prompts that instruct AI models to create valid, well-structured Draw.io XML files representing AWS cloud architectures.

## Primary Purpose
- Generate detailed prompts for AI-powered creation of AWS architecture diagrams
- Ensure consistent Draw.io XML formatting and AWS styling standards
- Provide comprehensive guidelines for proper AWS service representation
- Enable automated generation of professional-quality architecture diagrams

## Key Features
- **XML Structure Compliance**: Ensures proper Draw.io XML formatting with correct headers, encoding, and tag structure
- **AWS Resource Icon Styling**: Implements standardized AWS resource icon patterns with proper gradients, colors, and connection points
- **Multi-line Label Support**: Supports descriptive service labels with line breaks for better readability
- **Layer Separation**: Enforces clear architectural layer separation with color coding
- **Connection Point Management**: Includes comprehensive connection points for flexible edge attachment
- **Production-Ready Guidelines**: Incorporates monitoring, security, and scaling considerations

## Input Parameters

### Function: `get_architecture_diagram_prompt(description)`
- **Parameter**: `description` (string)
  - **Type**: String
  - **Required**: Yes
  - **Description**: A textual description of the AWS architecture to be diagrammed
  - **Example**: "Serverless web application with API Gateway, Lambda functions, and DynamoDB"

## Expected Output Structure
The function returns a comprehensive prompt string that includes:

1. **System Prompt Section**:
   - XML formatting rules and requirements
   - AWS styling guidelines
   - Resource icon pattern specifications
   - Basic XML structure template

2. **Generated XML Requirements**:
   - Well-formed Draw.io XML structure
   - AWS resource icon styling
   - Layer separation and color coding
   - Multi-line service descriptions
   - Proper element positioning and spacing

## Usage Context
This module is typically used in applications that:
- Generate AWS architecture documentation automatically
- Create visual representations of system architecture
- Support during migration planning and modernization efforts
- Provide architectural guidance and best practices
- Enable rapid prototyping of AWS solutions

### Integration Points
- Works with AI models capable of generating Draw.io XML
- Can be integrated into web applications (like Streamlit apps)


### Example Usage
```python
from architecture_diagram_prompt import get_architecture_diagram_prompt

# Generate prompt for a serverless architecture
description = "Three-tier web application with load balancer, auto-scaling EC2 instances, and RDS database"
prompt = get_architecture_diagram_prompt(description)

# The prompt can then be sent to an AI model to generate the Draw.io XML
```

## Related Files
- `pages/06_architecture_diagram.py` - Likely contains the UI implementation for architecture diagram generation
- `utils/` - May contain supporting utilities for file handling and processing