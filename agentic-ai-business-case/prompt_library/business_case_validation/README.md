# Business Case Validation Prompt

## Description
The `business_case_validation_prompt.py` module provides a comprehensive prompt generation function for validating AWS business cases and Total Cost of Ownership (TCO) analyses. This module creates detailed evaluation criteria that help assess the completeness and accuracy of AWS migration and modernisation business cases through a structured, expert-level analysis framework.

## Primary Purpose
- Provide the comprehensive AWS business case validation
- Ensure thorough evaluation of TCO analyses and cost modelling approaches
- Provide structured assessment criteria for AWS migration financial planning
- Enable systematic review of business value propositions and cost optimisation strategies
- Support FinOps best practices and cloud financial management validation

## Key Features
- **Seven-Pillar Assessment Framework**: Comprehensive evaluation across cost estimation inputs, modelling, business value, optimisation, TCO comparison, cost management, and Cloud Value Framework
- **Structured Response Format**: Enforces markdown formatting for professional documentation
- **Comprehensive Cost Coverage**: Evaluates all cost factors including compute, storage, network, database, support, and operational expenses
- **Business Value Quantification**: Assesses both tangible and intangible benefits of AWS implementation
- **Right-sizing Validation**: Reviews instance types, pricing options, and resource optimisation strategies
- **Cloud Value Framework Alignment**: Ensures coverage of all four AWS Cloud Economics pillars
- **Automated Tool Preference**: Emphasises automated data collection over manual processes for accuracy

## Input Parameters
### Function: `get_business_case_validation_prompt()`
- **Parameters**: None
- **Return Type**: String
- **Description**: Returns a comprehensive validation prompt without requiring input parameters, as it provides a standardised assessment framework

## Expected Output Structure
The function returns a detailed prompt that instructs the AI to evaluate business cases across seven key areas:

1. **Inputs for Cost Estimation**:
   - Cost factor completeness assessment
   - On-premises infrastructure evaluation
   - Growth projections and scalability analysis
   - Performance, security, and compliance considerations
   - Network traffic and data transfer analysis
   - Data collection methodology review
   - Strategic objectives alignment
   - Migration timeline incorporation

2. **Cost Estimates and Modelling**:
   - Usage pattern scenarios validation
   - Multi-year projection assessment
   - Pricing options evaluation (On-Demand, Reserved Instances, Savings Plans)
   - TCO coverage verification
   - ROI calculation review
   - Industry-specific case study integration

3. **Business Value Analysis**:
   - Value stream mapping evaluation
   - Tangible and intangible benefits quantification
   - Scalability, reliability, and performance improvements
   - Business objectives alignment assessment
   - Industry solutions mapping

4. **Right-sizing and Pricing Optimisation**:
   - Instance type and sizing appropriateness
   - Cost-saving options consideration
   - Resource utilisation analysis
   - Zombie resource identification processes
   - Unusual VM pattern documentation

5. **TCO Comparison**:
   - On-premises vs AWS comparison
   - Infrastructure refresh cycle consideration
   - Complete cost coverage verification
   - Migration cost documentation
   - Assumptions and limitations clarity

6. **Cost Management and Optimisation Strategies**:
   - AWS cost management tools integration
   - Licence planning considerations
   - Automation efficiency potential
   - Developer productivity impact
   - Responsibility frameworks
   - Escalation processes

7. **Cloud Value Framework**:
   - Four-pillar coverage assessment (Cost Savings, Staff Productivity, Operational Resilience, Business Agility)
   - AWS Cloud Economics alignment

## Usage Context
This module is typically used in scenarios involving:

### AWS Migration and Modernisation Projects
- Validating business cases for cloud migration initiatives
- Reviewing TCO analyses before executive presentations
- Ensuring comprehensive cost modelling approaches
- Supporting migration planning and financial justification

### Financial Planning and FinOps
- Conducting thorough business case reviews
- Validating cost optimisation strategies
- Ensuring alignment with AWS Cloud Economics principles
- Supporting financial governance and accountability

### Solution Architecture Reviews
- Assessing technical and financial alignment
- Validating right-sizing and pricing strategies
- Reviewing operational efficiency considerations
- Ensuring comprehensive business value analysis

### Integration Points
- Can be integrated into migration planning workflows
- Supports executive reporting and decision-making processes

### Example Usage
```python
from business_case_validation_prompt import get_business_case_validation_prompt

# Generate validation prompt
validation_prompt = get_business_case_validation_prompt()

# The prompt can then be used with business case documentation
# to generate comprehensive validation reports
```

## Related Files
- `pages/05_business_case_review.py` - Likely contains the UI implementation for business case validation
- `utils/` - May contain supporting utilities for cost analysis and financial modelling
- AWS Cloud Economics documentation - Referenced for Cloud Value Framework validation