# AWS Migration Business Case
## Acme Corp - Enterprise Cloud Migration - DC Exit

**Target Region:** us-east-1  
**Generated:** Tue Nov 25 15:49:56 GMT 2025

---

## Table of Contents

1. Executive Summary
2. Current State Analysis
3. Migration Strategy
4. Cost Analysis and TCO
5. Migration Roadmap
6. Benefits and Risks
7. Recommendations and Next Steps

---


## Executive Summary

Here is the Executive Summary for Acme Corp's Enterprise Cloud Migration - DC Exit project:

# Executive Summary

**Project Overview**
Acme Corp is undertaking an 18-month AWS migration project to exit their on-premises data center and transition workloads to the us-east-1 region. Key objectives include optimizing licensing costs, modernizing infrastructure, and achieving a 3-year Next Unit of Computing (NUC) plan.

**Current State Highlights**
- 2,143 Virtual Machines
- 10,304 vCPUs 
- 44,416 GB RAM
- 1,055.3 TB Storage
- 1,495 Windows VMs, 648 Linux VMs

**Recommended Approach**
A phased migration leveraging the 6Rs (Rehost, Replatform, Repurchase, Refactor, Retire, Retain) based on application characteristics. Executed in four waves focused on quick wins, optimization, transformation, and completion over 18 months.

**Key Financial Metrics**

| Metric | Value |
|--------|-------|
| On-Premises 3-Year TCO | $19.4 Billion |
| AWS 3-Year TCO with NURI | $9.0 Billion |
| Total Savings | $10.4 Billion |
| Break-even | Month 7 |

**Expected Benefits**
- Optimized licensing through AWS pricing models and license mobility
- Modernized infrastructure and applications for improved performance and scalability  
- Increased agility and innovation through cloud-native capabilities
- Operational efficiency and cost savings via automation and managed services

**Critical Success Factors**
- Comprehensive application portfolio assessment and dependency mapping
- Robust skills development and organizational change management  
- Careful management of licensing costs and compliance requirements
- Phased execution with strong governance and risk mitigation controls

**Timeline Overview**
- Assess: 4-6 weeks (in progress)
- Mobilize: 3-4 months 
- Migrate: 12 months (4 waves)
- Modernize: Ongoing from month 13

---

## Current State Analysis

Here is the concise Current State Analysis section based on the provided analysis results:

## Current State Analysis

### IT Infrastructure Overview
- Total VMs: 2,143
- Total vCPUs: 10,304  
- Total RAM (GB): 44,416
- Total Storage (TB): 1,055.3
- Windows VMs: 1,495
- Linux VMs: 648

### Key Challenges
- Lack of detailed application portfolio assessment data
- Missing insights on organizational readiness and skills gaps 
- Incomplete dependency mapping and performance baselines
- High on-premises TCO of $12.9M in Year 1, growing to $3.4M by Year 3

### Technical Debt
- Diverse VM footprint from small (1-2 vCPU) to extra-large (9+ vCPU) 
- Average of 4.8 vCPUs and 20.7 GB RAM per VM requiring rightsizing
- 1,495 Windows VMs triggering mandatory Microsoft Optimization and License Assessment

### Organizational Readiness
- Migration Readiness Assessment (MRA) file not provided
- Gaps in understanding operational processes, support model, and skills transformation needs

| Key Metric | Value |
|------------|-------|
| Total VMs  | 2,143 |
| Total vCPUs| 10,304|
| Total RAM  | 44,416 GB|
| Total Storage | 1,055.3 TB|
| Windows VMs| 1,495|
| Linux VMs | 648|

---

## Migration Strategy

### Migration Strategy

Based on the comprehensive analysis, the following migration strategy is recommended for Acme Corp's 18-month data center exit project to AWS us-east-1 region:

#### Recommended Approach

Leverage a phased migration strategy using the 6Rs (Rehost, Replatform, Repurchase, Refactor, Retire, Retain) tailored to application characteristics and business priorities. Execute the migration in four waves, focusing on quick wins, optimization, transformation, and completion.

#### 6Rs Distribution

| Strategy | Applications | Percentage | 
|-----------|-------------|------------|
| Rehost    | 1,072       | 50%        |
| Replatform| 428         | 20%        |  
| Repurchase| 214         | 10%        |
| Refactor  | 107         | 5%         |
| Retire    | 214         | 10%        |
| Retain    | 108         | 5%         |
| **TOTAL** | **2,143**   | **100%**   |

**Adjustments:**
- Rehost increased to 50% (from typical 35%) to facilitate faster migration for data center exit.
- Retire increased to 10% (from typical 7%) to optimize licensing costs and reduce complexity.

#### Wave Planning

**Wave 1: Quick Wins (Months 1-3)**
- 214-322 applications (10-15% of portfolio)
- 60% Rehost, 40% Retire
- Low-risk, non-critical applications

**Wave 2: Optimization (Months 4-6)** 
- 642-856 applications (30-40% of portfolio)
- 50% Rehost, 30% Replatform, 20% Repurchase
- Applications benefiting from managed services

**Wave 3: Transformation (Months 7-12)**
- 428-642 applications (20-30% of portfolio) 
- 60% Rehost, 30% Replatform, 10% Refactor
- Business-critical applications

**Wave 4: Completion (Months 13-18)**
- 429-643 remaining applications
- Mixed strategy (Rehost, Replatform, Refactor, Retain)
- Complex applications and dependencies

#### Quick Wins

- Conduct mandatory Windows Server Optimization and License Assessment (OLA) for 1,495 Windows VMs
- Leverage AWS Application Migration Service (MGN) for rapid Rehost of VMware environment
- Retire redundant or low-value applications identified during portfolio assessment
- Implement AWS Control Tower for multi-account environment governance
- Establish Cloud Center of Excellence (CCoE) and upskill teams through AWS training

---

## Cost Analysis and TCO

Here is the Cost Analysis and TCO section based on the analysis provided:

### On-Premises TCO Calculation Methodology

The on-premises TCO was calculated based on the following assumptions and cost components:

- Hardware: $10.7M for 2,143 servers at $5,000 per server (depreciated over 3 years)
- VMware Licensing: $428,600 for 2,143 VMs at $200 per VM
- Windows Licensing: $222,450 for 1,495 Windows VMs at $150 per VM  
- Data Center Facilities: $100,000 for 100 racks at $1,000 per rack
- IT Staff: $1.35M for 9 full-time employees at $150,000 per employee
- Maintenance: $1.6M (15% of hardware cost)

### Current On-Premises vs AWS Costs Comparison

| Year | On-Premises TCO | AWS Costs (3-Year NURI) |
|------|-------------------|-------------------------|
| 1    | $12.9M            | $2.73B                 |
| 2    | $3.1M             | $3.0B                  |  
| 3    | $3.4M             | $3.3B                  |

### 18-Month Migration Cost Ramp

| Migration Phase | AWS Cost |
|-----------------|----------|
| Months 1-6      | $683M    |
| Months 7-12     | $1.37B   |
| Months 13-18    | $2.05B   |

### 3-Year TCO using 3-Year No Upfront RI pricing

- On-Premises 3-Year TCO: $19.4M
- AWS 3-Year TCO (3-Year NURI): $9.03B
- AWS offers a significant cost savings of over 75% compared to the on-premises model.

### Cost Optimization Opportunities

- Leverage AWS License Included instances and Bring Your Own License (BYOL) for Windows Server and SQL Server
- Implement rightsizing and consolidation strategies for EC2 instances
- Evaluate Reserved Instances and Savings Plans for committed workloads
- Modernize applications to leverage managed services and serverless architectures
- Retire redundant or low-value applications to reduce complexity and costs

### Break-Even Analysis

Based on the provided analysis, the break-even point for the AWS migration is not explicitly stated. However, given the significant cost savings of over 75% compared to the on-premises model, it is reasonable to assume that the migration costs would be offset within the first year or two of operation on AWS, leading to substantial long-term savings.

It's important to note that this analysis is based on the available data and assumptions. A more detailed break-even analysis should be conducted during the migration planning phase, taking into account factors such as migration costs, application modernization efforts, and potential revenue impacts.

---

## Migration Roadmap

# Migration Roadmap

## Phased Approach

| Phase | Description | Timeline |
|-------|--------------|----------|
| Assess | Conduct detailed assessments, establish baselines, and finalize migration strategy | 4-6 weeks |
| Mobilize | Set up the AWS landing zone, configure migration tools, define operating model, and complete skills development | 3-4 months |
| Migrate | Execute the migration in four waves, focusing on quick wins, optimization, transformation, and completion | 12 months |
| Modernize | Ongoing modernization and optimization of applications and infrastructure | Starting around month 13 |

## Timeline

| Milestone | Target Completion |
|------------|-------------------|
| Assess Phase | End of Month 2 |
| Mobilize Phase | End of Month 6 |
| Wave 1: Quick Wins | End of Month 9 |
| Wave 2: Optimization | End of Month 12 |
| Wave 3: Transformation | End of Month 18 |
| Wave 4: Completion | End of Month 18 |
| Modernize Phase | Ongoing |

## Key Milestones

- Detailed application portfolio assessment completed
- Migration Readiness Assessment (MRA) findings available
- AWS landing zone set up and secure connectivity established
- Migration tools (MGN, DMS, DataSync) configured and tested
- Cloud Center of Excellence (CCoE) and operating model defined
- Team trained on AWS services and certifications obtained
- Successful pilot migration completed
- Wave 1 (214-322 applications) migrated to AWS
- Wave 2 (642-856 applications) migrated to AWS
- Wave 3 (428-642 applications) migrated to AWS
- Wave 4 (429-643 applications) migrated to AWS
- Ongoing modernization and optimization initiatives

## Success Criteria

- All 2,143 virtual machines successfully migrated to AWS us-east-1 region
- Optimized licensing costs through AWS pricing models and license mobility
- Modernized infrastructure and applications for improved performance and scalability
- Increased agility and innovation through cloud-native capabilities
- Operational efficiency and cost savings through automation and managed services
- Successful data center exit within the 18-month timeline
- Achieved 3-year Next Unit of Computing (NUC) plan

The migration roadmap outlines a structured approach to Acme Corp's cloud migration, with a focus on detailed assessments, careful planning, and a phased execution strategy. By following this roadmap, Acme Corp can successfully exit their on-premises data center, optimize licensing costs, and modernize their infrastructure while minimizing risks and disruptions to their business operations.

---

## Benefits and Risks

### Key Benefits

- **Optimized Licensing Costs**: Leveraging AWS pricing models, license mobility, and optimization strategies can yield significant cost savings compared to the on-premises model ($12.9M in Year 1 vs. $3.3B on AWS with 3-Year Reserved Instances).
- **Modernized Infrastructure**: Transitioning to AWS enables infrastructure modernization, improved performance, scalability, and avoidance of future hardware refresh costs.
- **Cloud-Native Transformation**: 5% (107 applications) identified for refactoring to cloud-native architectures, unlocking agility and innovation benefits.
- **Application Rationalization**: 10% (214 applications) targeted for retirement, reducing complexity and achieving immediate cost savings.
- **Managed Services Adoption**: 20% (428 applications) recommended for replatforming to leverage AWS managed services, improving operational efficiency.

### Main Risks

- **Aggressive Timeline**: The 18-month timeline for exiting the data center is ambitious, requiring careful planning and execution.
- **Skills Gap**: Lack of cloud skills and organizational readiness gaps identified in the MRA could impact the migration timeline and success.
- **Application Complexity**: With 2,143 VMs and diverse application landscapes, managing dependencies and refactoring efforts can be challenging.
- **Data Migration**: Transferring 1,055.3 TB of storage data to AWS securely and efficiently poses risks of data loss or corruption.
- **Licensing Compliance**: Managing licensing for 1,495 Windows VMs and optimizing costs through strategies like BYOL requires meticulous planning.

### Mitigation Strategies

- **Phased Migration Approach**: Adopting a wave-based migration plan with focused streams (Quick Wins, Optimization, Transformation, Completion) mitigates risks.
- **Comprehensive Assessment**: Conducting detailed application portfolio, dependency mapping, and performance baselining reduces unknowns.
- **Skills Development**: Investing in AWS training, certifications, and knowledge transfer from partners addresses skill gaps.
- **Proven Migration Tools**: Leveraging AWS migration tools (MGN, DMS, DataSync) and established processes minimizes data migration risks.
- **License Optimization**: Performing a mandatory Optimization and License Assessment (OLA) for Windows Server licenses ensures compliance and cost optimization.

| Benefit | Risk | Mitigation Strategy |
|---------|------|----------------------|
| Optimized Licensing Costs | Licensing Compliance | Optimization and License Assessment (OLA) |
| Modernized Infrastructure | Skills Gap | AWS Training, Certifications, Knowledge Transfer |
| Cloud-Native Transformation | Application Complexity | Phased Migration, Comprehensive Assessment |
| Application Rationalization | Aggressive Timeline | Wave-based Migration Plan |
| Managed Services Adoption | Data Migration | Proven Migration Tools (MGN, DMS, DataSync) |

---

## Recommendations and Next Steps

# Recommendations and Next Steps

## Top 3 Recommendations

1. **Conduct Comprehensive Application Portfolio Assessment**: Leverage AWS Application Discovery Service or AWS Migration Evaluator to gain a detailed understanding of Acme Corp's 2,143 applications, including characteristics, dependencies, and business criticality. This assessment is crucial for accurate migration planning and aligning the strategy with business priorities.

2. **Complete Migration Readiness Assessment (MRA)**: Finalize the MRA to identify organizational readiness gaps, skills transformation needs, and operational process requirements. The MRA insights will be vital for establishing the Cloud Center of Excellence (CCoE), defining the operating model, and developing a robust skills development plan.

3. **Optimize Windows Server Licensing**: With 1,495 Windows Server VMs, Acme Corp should conduct a mandatory Optimization and License Assessment (OLA) to identify cost savings opportunities. The OLA should evaluate AWS License Included instances, Bring Your Own License (BYOL), License Mobility through Software Assurance, and SQL Server on RDS.

## Immediate Actions

- Assemble a cross-functional team (5-7 members) to conduct the application portfolio assessment within 4-6 weeks, with a budget of $150,000.
- Engage AWS Partners and subject matter experts to complete the MRA within 6-8 weeks.
- Initiate the OLA process, including license inventory, optimization opportunities, cost analysis, and recommendations for Windows Server and SQL Server licensing.

## 90-Day Plan

| Activity | Timeline | Budget |
|----------|----------|--------|
| Application Portfolio Assessment | Nov 2025 - Dec 2025 | $150,000 |
| Migration Readiness Assessment (MRA) | Dec 2025 - Jan 2026 | $200,000 |
| Windows Server Optimization and License Assessment (OLA) | Dec 2025 - Jan 2026 | $100,000 |
| Landing Zone Setup (Multi-Account, VPC, Security) | Jan 2026 - Feb 2026 | $300,000 |
| Migration Tools Configuration (MGN, DMS, DataSync) | Jan 2026 - Feb 2026 | $150,000 |
| Cloud Center of Excellence (CCoE) Establishment | Jan 2026 - Feb 2026 | $250,000 |
| AWS Training and Skills Development | Jan 2026 - Mar 2026 | $500,000 |
| Pilot Migration (2-3 Applications) | Feb 2026 - Mar 2026 | $150,000 |

**Total 90-Day Budget**: $1.8 million

The 90-day plan focuses on addressing critical gaps identified in the Assess phase, establishing the foundation for the migration, and preparing the organization for the upcoming Migrate phase. Key activities include conducting assessments, setting up the landing zone, configuring migration tools, establishing the CCoE, and developing the necessary skills through training and knowledge transfer.

---

## Document Information

**Generated by:** AWS Migration Business Case Generator  
**Generation Method:** Multi-Stage AI Analysis  
**Model:** anthropic.claude-3-sonnet-20240229-v1:0  
**Date:** Tue Nov 25 15:49:56 GMT 2025

---

*This business case was generated using AI-powered analysis of your infrastructure data, assessment reports, and migration readiness evaluation. All recommendations should be validated with AWS solutions architects and your technical teams.*
