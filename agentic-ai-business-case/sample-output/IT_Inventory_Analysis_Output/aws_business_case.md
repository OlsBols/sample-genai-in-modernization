# AWS Migration Business Case
## ACME - InventoryAnalysis Migration

**Target Region:** us-east-1  
**Generated:** Wed 14 Jan 2026 14:54:53 GMT

---

## Table of Contents

1. Executive Summary
2. Current State Analysis
3. Migration Strategy
4. Cost Analysis and TCO
5. Migration Roadmap
6. Benefits and Risks
7. Recommendations and Next Steps
8. Appendix: AWS Partner Programs for Migration and Modernization

---


## Executive Summary

# Executive Summary

ACME's AWS migration initiative represents a strategic digital transformation program to modernize their IT infrastructure within a 12-month timeline. This comprehensive migration to AWS us-east-1 region encompasses their entire application portfolio and infrastructure estate.

## Project Overview
The migration scope covers ACME's complete infrastructure footprint, targeting a data center exit within 12 months. The project will leverage AWS's comprehensive suite of services to enable modernization while maintaining business continuity.

## Current State Highlights
- Infrastructure Estate: 200 virtual machines
  - 196 Linux servers
  - 4 Windows servers
- Compute Resources: 1,172 vCPUs, 6,503.5 GB RAM
- Storage Footprint: 5.3 TB
- Database Environment: 14 database instances
- MRA Readiness Score: 3.2/5.0

## Recommended Approach
A phased 12-month migration strategy utilizing AWS's proven migration methodology, combining rehosting for rapid migration with strategic modernization opportunities. The approach emphasizes maintaining business continuity while enabling progressive transformation.

## Key Financial Metrics
- Monthly AWS Cost: $16,694.22
- Annual AWS Cost (ARR, including backup): $200,330.66
- 3-Year Total Cost: $731,522.99 (including RDS upfront fees)
- Pricing based on 3-Year EC2 Instance Savings Plan with RDS Partial Upfront

## Expected Benefits
1. Enhanced operational efficiency through AWS managed services
2. Improved scalability and flexibility for business growth
3. Access to advanced cloud capabilities including AI/ML and analytics
4. Strengthened security posture through AWS native security services

## Critical Success Factors
1. Comprehensive skills development program for IT staff
2. Robust change management and communication strategy
3. Adherence to migration timeline milestones

## Timeline Overview
12-month phased implementation:
- Foundation & Initial Migrations (Months 1-4)
- Core Workload Migration (Months 5-8)
- Complex Workload Migration & Optimization (Months 9-12)

This migration will position ACME for improved agility, innovation, and operational excellence while providing access to AWS's extensive service portfolio for future growth and transformation.

---

## Current State Analysis

# Current State Analysis

## Infrastructure Overview

| Component | Quantity/Details |
|-----------|-----------------|
| Total VMs | 200 |
| Operating Systems | Linux: 196 (98%), Windows: 4 (2%) |
| Compute Resources | 1,172 vCPUs |
| Memory | 6,503.5 GB RAM |
| Storage | 5.3 TB |
| Databases | 14 instances |
| Environment Type | Production |

*Reference: Detailed VM-level inventory and specifications available in RVTools export and IT inventory spreadsheets*

## Key Challenges

- Significant skills gap with only 15% of staff having basic AWS knowledge, requiring comprehensive training program
- Manual deployment and operational processes lacking automation, impacting migration efficiency
- Complex database dependencies with 14 instances requiring careful migration planning
- Security framework requires enhancement to meet cloud requirements

## Technical Debt

- Legacy infrastructure predominantly running on Linux systems requiring modernization
- Manual security monitoring and deployment processes needing automation
- Limited implementation of encryption and modern security controls
- Reactive monitoring approach requiring transformation to proactive cloud-native monitoring

## Organizational Readiness

Based on MRA findings, overall cloud readiness score is 3.2/5.0 (Moderate). Organization shows strong executive sponsorship but requires significant technical upskilling. People & Process readiness (2.8/5.0) indicates need for cloud training and process modernization. Platform & Architecture score (2.5/5.0) highlights modernization requirements, while Security & Compliance (3.0/5.0) demonstrates basic controls with room for improvement.

The predominantly Linux environment (98%) presents opportunities for containerization and modernization during migration, particularly suitable for AWS EKS adoption. The limited Windows footprint minimizes licensing complexity during migration planning. The environment's compute and memory footprint suggests opportunities for right-sizing during migration, while the moderate storage requirements allow for straightforward data transfer planning within the 12-month timeline.

---

## Migration Strategy

# Migration Strategy

The recommended migration approach encompasses a 12-month accelerated timeline, leveraging a hybrid strategy combining traditional EC2 migrations with containerization opportunities. This approach prioritizes business continuity while enabling modernization where beneficial.

The AWS 7Rs framework provides a structured approach to cloud migration, categorizing workloads by transformation level—from simple lift-and-shift (Rehost) to complete modernization (Refactor/Re-architect).

| Strategy | Count | Description |
|----------|---------|-------------|
| Rehost | 80 VMs (40%) | Direct lift-and-shift to EC2 |
| Replatform | 50 VMs (25%) | Optimization and containerization |
| Refactor | 30 VMs (15%) | Modernization to cloud-native |
| Replace | 20 VMs (10%) | SaaS alternatives |
| Retire | 20 VMs (10%) | Decommission |

The migration will execute in three waves across 12 months:
- Wave 1 (Months 1-4): Foundation and initial rehost
- Wave 2 (Months 5-8): Core replatform and refactor
- Wave 3 (Months 9-12): Complex workloads and optimization

Quick Wins:
- Containerize stateless Linux applications using EKS
- Implement Auto Scaling for variable workloads
- Leverage serverless computing for event-driven processes
- Modernize CI/CD pipelines with AWS native tools
- Enable infrastructure as code for standardization

The strategy emphasizes rapid value realization through early quick wins while maintaining a steady progression of more complex transformations. This balanced approach ensures meeting the 12-month datacenter exit timeline while maximizing modernization opportunities.

---

## Cost Analysis and TCO






## AWS Cost Summary

The following table provides a side-by-side comparison of all three pricing options:

| Cost Component | Option 1: EC2 Instance SP (3yr) + RDS Partial Upfront | Option 2: Compute SP (3yr) + RDS No Upfront (1yr×3) | Option 3: Hybrid (EC2 + EKS + RDS) |
|----------------|------------------------------------------------------|-----------------------------------------------------|------------------------------------|
| **EC2 Monthly Cost** | $11,926.43 | $12,855.16 | $10,699.47 |
| **EKS Monthly Cost** | - | - | $608.86 |
| **RDS Monthly Cost** | $4,767.79 | $21,217.07 | $4,767.79 |
| **Total Monthly Cost** | $16,694.22 | $34,072.22 | $22,618.04 |
| **Total Annual Cost (ARR)** | $200,330.66 | $408,866.67 | $271,416.42 |
| **3-Year Total (monthly only)** | $600,991.99 | $1,226,600.00 | $944,780.33 |
| **RDS Upfront Fees (one-time)** | $130,531.00 | $0.00 | $130,531.00 |
| **3-Year Total (incl. upfront)** | $731,522.99 | $1,226,600.00 | $944,780.33 |

**Notes:**
- Option 1: 3-Year EC2 Instance Savings Plan + 3-Year RDS Partial Upfront (lowest cost)
- Option 2: 3-Year Compute Savings Plan + 1-Year RDS No Upfront renewed 3 times (highest cost)
- Option 3: Hybrid approach with containerization for suitable workloads (strategic value)
- All costs include AWS Backup with intelligent tiering

### Recommended Option

**Option 1 (3-Year EC2 Instance Savings Plan)**

**Decision Tier:** Tier 3: EKS Premium 20%-50%

**Rationale:** Option 1 (3-Year EC2 Instance Savings Plan) recommended for cost optimization ($16,694.22/month). Option 3 (Hybrid EC2 + EKS) available as strategic alternative for 29.15% premium ($213,257.34 over 3 years) if containerization and Kubernetes ecosystem are organizational priorities.

**Cost Savings:** $17,378.00/month vs Option 2 (51.0% savings)
**3-Year Savings:** $625,608.00 over 3 years

**📊 Detailed Analysis Available:**
- **IT Inventory Pricing Excel** (`it_inventory_aws_pricing_*.xlsx`): Server-by-server and database-by-database cost breakdown, instance type mappings, storage costs, RDS configurations, and backup costs
- **EKS Migration Analysis Excel** (`eks_migration_analysis.xlsx`): EKS cluster design, VM categorization, capacity planning, and ROI analysis
- See Excel files for complete VM-level details, right-sizing recommendations, and cost optimization opportunities

## Migration Cost Ramp

Based on 12-month migration timeline using Option 1 pricing:

- **Months 1-4**: $5,008.27/month (30% of workloads)
- **Months 5-8**: $11,685.95/month (70% of workloads)
- **Months 9-12**: $16,694.22/month (100% of workloads)

## Business Value Justification

Beyond cost considerations, AWS migration delivers strategic business value:

- **Agility and Speed**: Rapid provisioning and deployment capabilities accelerate time-to-market
- **Innovation Platform**: Access to 200+ AWS services enables new capabilities (AI/ML, analytics, IoT)
- **Scalability**: Elastic infrastructure scales with business growth without upfront investment
- **Operational Excellence**: Managed services reduce operational overhead and improve reliability
- **Security and Compliance**: Enterprise-grade security controls and compliance certifications
- **Global Reach**: Deploy applications closer to customers with AWS global infrastructure
- **Modernization**: Container-based architecture with EKS enables DevOps practices and microservices
- **Reduced Technical Debt**: Eliminate aging infrastructure and legacy technology constraints
- **Focus on Core Business**: Shift IT resources from infrastructure management to innovation

---

## Migration Roadmap

# Migration Roadmap

Based on the completed infrastructure analysis and dependency mapping, the following 12-month migration roadmap has been established:

## Migration Wave Plan

| Wave | Timeline | Scope | Key Activities |
|------|----------|-------|----------------|
| Wave 1 | Months 3-5 | 79 servers, 12 applications (CRM, CMDB, Finance) | - Independent workloads migration<br>- Initial database migrations<br>- Low-risk applications |
| Wave 2 | Months 6-8 | 20 servers, 2 applications (GL, Web apps) | - Applications with dependencies<br>- Complex integrations<br>- Database platform upgrades |
| Wave 3 | Months 9-11 | 101 servers, remaining apps | - Mission-critical workloads<br>- Complex database migrations<br>- High-dependency systems |

## Foundation and Optimization Phases

| Phase | Timeline | Key Activities |
|-------|----------|----------------|
| Mobilize | Months 1-2 | - Landing zone implementation<br>- Migration factory setup<br>- Wave 1 preparation |
| Optimize | Month 12 | - Performance tuning<br>- Cost optimization<br>- DC decommissioning |

## Key Milestones

- Month 1: Landing zone operational
- Month 3: First production workload migrated
- Month 5: Wave 1 completion (40% workloads)
- Month 8: Wave 2 completion (50% workloads)
- Month 11: Wave 3 completion (remaining workloads)
- Month 12: Data center exit complete

## Success Criteria

- Zero critical business disruptions during migration
- 100% of identified workloads migrated within 12 months
- All applications meeting or exceeding pre-migration performance
- Security controls validated for all migrated workloads
- Achieved planned cost optimization targets

## Dependencies and Prerequisites

- Landing zone must be operational before Wave 1
- Network connectivity established between AWS and on-premises
- Security controls validated before each wave
- Application teams trained prior to their respective waves
- Database migration tools configured before database moves

Note: Wave plan generated from IT Infrastructure Inventory dependency analysis. Wave assignments are based on application dependencies and business criticality assessment.

---

## Benefits and Risks

### Benefits and Business Value

1. **Financial Benefits**
- Predictable monthly costs with gradual migration ramp-up aligned to 3-year savings plan
- Elimination of hardware refresh cycles for 200 servers and 14 databases
- Resource optimization through right-sizing of 1,172 vCPUs and 6.5TB RAM
- Cost reduction through retirement of 10 redundant servers identified in analysis
- Consolidation savings through containerization of 23 Linux workloads

2. **Operational Benefits**
- Simplified management of predominantly Linux environment (196 Linux, 4 Windows servers)
- Enhanced database management through migration of 14 databases to RDS
- Improved monitoring through AWS native tools, replacing current manual processes
- Automated patching and updates for 200 servers, reducing NOC workload
- Streamlined deployment through containerization of 23 compatible applications
- Integration with existing ITIL processes and 24/7 NOC operations

3. **Strategic Benefits**
- Modernization path for legacy applications identified in assessment
- Enhanced analytics capabilities through AWS services for 5.3TB data footprint
- Accelerated application deployment through containerization and CI/CD
- Global scalability for business expansion beyond current datacenter
- Access to AWS innovation services (AI/ML, analytics) for future growth
- Improved business agility through cloud-native architecture

4. **Security and Compliance Benefits**
- Enhanced security controls addressing current framework gaps identified in MRA
- Automated security monitoring replacing manual processes
- Improved encryption implementation across infrastructure
- Strengthened compliance posture for PCI DSS requirements
- Centralized security management through AWS Security Hub

### Risks and Mitigation

1. **Technical Risks**
- Limited cloud expertise (MRA score: 2.5/5 for Platform & Architecture) → Mitigation: Intensive AWS training program for 30 key personnel
- Container adoption complexity for 23 Linux VMs → Mitigation: Phased containerization approach with focused EKS training
- Database migration complexity for 14 instances → Mitigation: Utilize AWS DMS with comprehensive testing plan
- Application dependencies in 200-server estate → Mitigation: Detailed wave planning with dependency mapping

2. **Organizational Risks**
- Significant skills gap (15% current AWS knowledge) → Mitigation: Partner-led training and certification program
- Change management challenges (MRA People score: 2.8/5) → Mitigation: Establish Cloud Center of Excellence
- Limited DevOps experience for container operations → Mitigation: Dedicated DevOps training and tooling implementation
- Process transformation needs → Mitigation: ITIL-aligned cloud operational procedures

3. **Business Risks**
- Tight 12-month migration timeline for 200 servers → Mitigation: Parallel wave execution with dedicated teams
- Performance impact during migration → Mitigation: Comprehensive pre-migration testing and validation
- Business continuity during database migrations → Mitigation: Zero-downtime migration strategies with rollback plans
- Resource constraints across 45-person IT team → Mitigation: Strategic partner augmentation and clear prioritization

---

## Recommendations and Next Steps

### Strategic Recommendations
1. **Accelerated Migration Path** 
   - Prioritize rehost (70 servers) for quick wins in first 4 months
   - Leverage MRA findings to address critical skills gap through parallel training program
   - Establish container strategy for 30 identified replatform candidates

2. **Modernization Framework**
   - Implement infrastructure-as-code from day one using AWS CloudFormation
   - Create automated deployment pipelines for standardized Linux workloads
   - Develop reusable patterns for database migrations to RDS

3. **Risk Mitigation Strategy**
   - Address security readiness gaps identified in MRA
   - Establish cloud center of excellence (CCoE) to drive standardization
   - Implement comprehensive monitoring and cost management

### Immediate Actions
- Launch AWS Landing Zone implementation
- Begin application dependency mapping using AWS Application Discovery Service
- Initiate cloud skills development program (addressing MRA gap)
- Create detailed migration runbooks for Linux workloads
- Set up AWS Control Tower for multi-account governance
- Establish migration factory team structure
- Deploy initial CI/CD pipeline for test migrations

### Recommended Deep-Dive Assessments
- **Application Portfolio Analysis**: Detailed assessment of application modernization candidates
- **Security and Compliance Review**: Gap analysis against AWS security frameworks
- **Network Architecture Assessment**: Evaluate direct connect vs VPN requirements
- **Disaster Recovery Assessment**: Define RPO/RTO requirements for critical workloads

### 90-Day Action Plan

| Timeframe | Activity | Owner | Success Criteria |
|-----------|----------|-------|------------------|
| Week 1-2 | Launch Landing Zone | Cloud Team | AWS Control Tower operational |
| Week 3-4 | Complete dependency mapping | Migration Team | All app dependencies documented |
| Month 2 | Deploy first wave pilot | Migration Factory | 5 servers successfully migrated |
| Month 3 | Database migration pilot | DBA Team | 2 databases migrated to RDS |

### Decision Points and Go/No-Go Criteria
- **Landing Zone Readiness**: Security controls implemented, networking configured
- **Migration Factory**: Team trained, runbooks tested, automation validated
- **Application Readiness**: Dependencies mapped, migration patterns validated
- **Database Migration**: Successful pilot completion, minimal downtime achieved
- **Skills Readiness**: Core team completed AWS training (per MRA requirement)

---


## Appendix: AWS Partner Programs for Migration and Modernization

This appendix provides information about AWS partner programs that can support your migration journey.

### Core Migration Programs

#### 1. MAP (Migration Acceleration Program)
Comprehensive cloud migration program with three phases: Assess, Mobilize, and Migrate & Modernize. Provides funding to offset initial migration costs and accelerate cloud adoption.

**Learn more:** [AWS Migration Acceleration Program](https://aws.amazon.com/migration-acceleration-program/)

#### 2. OLA (Optimization and Licensing Assessment)
Helps assess on-premises environments and provides data-driven recommendations for migration optimization. Analyzes current licensing and resource utilization to optimize cloud costs.

**Learn more:** [AWS Optimization and Licensing Assessment](https://aws.amazon.com/optimization-and-licensing-assessment/)

#### 3. ISV Workload Migration Program (WMP)
Specifically designed for Independent Software Vendor workload migrations. Supports partners migrating ISV applications to AWS across all major geographies.

**Learn more:** [AWS Partner Funding Programs](https://aws.amazon.com/partners/funding/)

#### 4. VMware Migration Programs
- **AWS Transform for VMware:** Streamlined service for migrating VMware workloads to AWS
- **Amazon Elastic VMware Service (Amazon EVS):** Fastest path to migrate and operate VMware workloads on AWS
- **VMware Migration Accelerator (VMA):** Provides credits when migrating VMware workloads to Amazon EC2

**Learn more:** [VMware on AWS Migration](https://aws.amazon.com/vmware/)

#### 5. POC (Proof of Concept) Program
Supports proof of concept projects that can include migration assessment phases. Available for smaller projects under $10,000 with Partner Referral ownership.

**Learn more:** [AWS Partner Programs](https://aws.amazon.com/partners/programs/)

### Additional Resources

#### AWS Application Migration Service (MGN)
Simplifies and expedites migration to AWS by automatically converting source servers to run natively on AWS.

**Learn more:** [AWS Application Migration Service](https://aws.amazon.com/application-migration-service/)

#### AWS Database Migration Service (DMS)
Helps migrate databases to AWS quickly and securely with minimal downtime.

**Learn more:** [AWS Database Migration Service](https://aws.amazon.com/dms/)

#### AWS Migration Evaluator
Provides a clear baseline of your current on-premises footprint and projects costs for running applications in AWS.

**Learn more:** [AWS Migration Evaluator](https://aws.amazon.com/migration-evaluator/)

---

*For the most current information about AWS partner programs and eligibility requirements, please consult with your AWS account team or visit the AWS Partner Network portal.*



## Document Information

**Generated by:** AWS Migration Business Case Generator  
**Generation Method:** Multi-Stage AI Analysis  
**Model:** us.anthropic.claude-3-5-sonnet-20241022-v2:0  
**Date:** Wed 14 Jan 2026 14:54:53 GMT

---

*This business case was generated using AI-powered analysis of your infrastructure data, assessment reports, and migration readiness evaluation. All recommendations should be validated with AWS solutions architects and your technical teams.*
