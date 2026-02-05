# Prompt Library

This prompt library provides a comprehensive collection of specialized prompt templates designed to automate and enhance migration and modernization activities under the AWS Migration Acceleration Program (MAP).


## Prompt Inventory

| Category | Prompt Name | Function | Location | Input Types | Primary Output |
|----------|-------------|----------|----------|-------------|----------------|
| **Architecture Diagram** | Architecture Diagram | `get_architecture_diagram_prompt()` | `architecture_diagram/architecture_diagram_prompt.py` | Architecture description text | Draw.io XML format AWS architecture diagrams with proper styling and structure |
| **Business Case Validation** | Business Case Validation | `get_business_case_validation_prompt()` | `business_case_validation/business_case_validation_prompt.py` | Business case data | Business case analysis and validation recommendations |
| **Learning Pathway** | Learning Pathway | `get_learning_pathway_prompt()` | `learning_pathway/learning_pathway_prompt.py` | Training data CSV, target role, experience level, duration | Customized training pathways with course recommendations and duration analysis |
| **Migration Patterns** | Migration Patterns | `get_migration_patterns_prompt()` | `migration_patterns/migration_patterns_prompt.py` | AWS Calculator CSV, scope text | 3 migration patterns, wave planning, MAP milestone predictions |
| **Modernization Opportunity** | Inventory Analysis | `get_inventory_analysis_prompt()` | `modernization_opportunity/inventory_analysis_prompt.py` | CSV inventory data | Asset categorization, performance analysis, DR assessment, risk evaluation |
| **Modernization Opportunity** | Modernization Pathways | `get_modernization_pathways_prompt()` | `modernization_opportunity/modernization_pathways_prompt.py` | CSV inventory, architecture description, scope text | 8 modernization pathways with AWS service recommendations and cost estimates |
| **Modernization Opportunity** | On-Premises Architecture | `get_onprem_architecture_prompt()` | `modernization_opportunity/onprem_architecture_prompt.py` | Architecture diagrams (JPG, JPEG, PNG) | Infrastructure component analysis, security controls, integration patterns |
| **Resource Planning** | Resource Planning | `get_resource_planning_prompt()` | `resource_planning/resource_planning_prompt.py` | Migration strategy, wave planning, resource profiles | Team structure evaluation, resource allocation, cost projections |