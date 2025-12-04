# AWS Deprecated Services Reference

**Purpose**: This document tracks AWS services that are deprecated or scheduled for end-of-life to ensure business cases only recommend current, actively supported services.

**Official Source**: https://aws.amazon.com/products/lifecycle/

## Known Deprecated Services (Do NOT Recommend)

### Migration & Modernization Services
- **AWS Migration Hub** - DEPRECATED
  - **Replacement**: AWS Application Migration Service (MGN) for rehost migrations
  - **Status**: Service being discontinued
  - **Migration Path**: Use AWS MGN for server migrations, AWS Database Migration Service (DMS) for databases

- **AWS Migration Hub Refactor Spaces** - DEPRECATED
  - **Replacement**: AWS Application Migration Service (MGN)
  - **Status**: Service being discontinued

- **AWS Application Discovery Service** - DEPRECATED
  - **Replacement**: AWS Application Migration Service (MGN) with integrated discovery
  - **Status**: Service being discontinued

- **AWS Mainframe Modernization Service** - DEPRECATED
  - **Replacement**: Partner solutions or custom modernization approaches
  - **Status**: Service being discontinued

### Developer Tools
- **Amazon CodeCatalyst** - DEPRECATED
  - **Replacement**: AWS CodePipeline, AWS CodeBuild, AWS CodeDeploy, GitHub Actions
  - **Status**: Service being discontinued
  - **Migration Path**: Use native AWS DevOps services or third-party CI/CD tools

- **Amazon CodeGuru Reviewer** - DEPRECATED
  - **Replacement**: Amazon Q Developer (includes code review capabilities)
  - **Status**: Service being discontinued
  - **Migration Path**: Migrate to Amazon Q Developer for AI-powered code reviews

- **.NET Modernization Tools** - DEPRECATED
  - **Replacement**: AWS Toolkit for .NET, manual modernization approaches
  - **Status**: Service being discontinued

### Storage & Data Services
- **Amazon Cloud Directory** - DEPRECATED
  - **Replacement**: Amazon Cognito, AWS Directory Service, or custom directory solutions
  - **Status**: Service being discontinued

- **Amazon Glacier (standalone, vault-based service)** - DEPRECATED
  - **Replacement**: Amazon S3 Glacier storage classes (S3 Glacier Instant Retrieval, Flexible Retrieval, Deep Archive)
  - **Status**: Standalone service deprecated, use S3 storage classes instead
  - **Migration Path**: Use S3 Lifecycle policies to transition to Glacier storage classes

- **Amazon S3 Object Lambda** - DEPRECATED
  - **Replacement**: AWS Lambda with S3 event notifications, or process data before storing in S3
  - **Status**: Service being discontinued

### Security & Fraud Detection
- **Amazon Fraud Detector** - DEPRECATED
  - **Replacement**: Amazon SageMaker for custom fraud detection models, or third-party solutions
  - **Status**: Service being discontinued

### IoT & Edge Computing
- **AWS IoT SiteWise Edge Data Processing Pack** - DEPRECATED
  - **Replacement**: AWS IoT Greengrass with custom components
  - **Status**: Service being discontinued

- **AWS IoT SiteWise Monitor** - DEPRECATED
  - **Replacement**: Amazon Managed Grafana, custom dashboards with AWS IoT SiteWise APIs
  - **Status**: Service being discontinued

### Snow Family
- **AWS Snowball Edge Compute Optimized** - DEPRECATED
  - **Replacement**: AWS Snowball Edge Storage Optimized (with compute capabilities)
  - **Status**: Compute Optimized variant being discontinued

- **AWS Snowball Edge Storage Optimized** - DEPRECATED
  - **Replacement**: AWS Snowcone, AWS Snowball (newer models), AWS DataSync
  - **Status**: Older models being phased out

### Systems Management
- **AWS Systems Manager - Change Manager** - DEPRECATED
  - **Replacement**: AWS Systems Manager Change Calendar, AWS Config for change tracking
  - **Status**: Service being discontinued

- **AWS Systems Manager - Incident Manager** - DEPRECATED
  - **Replacement**: Amazon CloudWatch with SNS for incident response, third-party incident management tools
  - **Status**: Service being discontinued

### Life Sciences
- **AWS HealthOmics - Variant and Annotation Store** - DEPRECATED
  - **Replacement**: AWS HealthOmics Analytics Store (updated version)
  - **Status**: Specific component deprecated, use updated HealthOmics services

### Workstation & Remote Access
- **Amazon Web Access Client for PCoIP (STXHD)** - DEPRECATED
  - **Replacement**: Amazon WorkSpaces with native clients, Amazon AppStream 2.0
  - **Status**: PCoIP client deprecated

### Rendering & Media
- **AWS Thinkbox Deadline 10** - DEPRECATED
  - **Replacement**: AWS Deadline Cloud (managed service)
  - **Status**: Self-managed Deadline 10 being replaced by managed service

### Mobile & Application Services
- **Amazon Cognito Sync** - DEPRECATED
  - **Replacement**: AWS AppSync with DataStore, or Amazon Cognito User Pools
  - **Status**: End of support
  - **Migration Path**: Use AppSync DataStore for offline sync capabilities

### Compute
- **EC2-Classic** - RETIRED (August 2022)
  - **Replacement**: EC2-VPC (default for all new accounts)
  - **Note**: All workloads must use VPC

### Database
- **Amazon SimpleDB** - Limited support
  - **Replacement**: Amazon DynamoDB
  - **Note**: SimpleDB still available but not recommended for new workloads

## Services with Version Deprecations

### Container Services
- **ECS Container Agent versions < 1.x** - Older versions deprecated
  - **Action**: Always use latest ECS agent version

### Database Engines
- **RDS MySQL 5.5, 5.6** - End of life
  - **Replacement**: MySQL 5.7, 8.0
- **RDS PostgreSQL < 11** - Older versions deprecated
  - **Replacement**: PostgreSQL 11+
- **RDS SQL Server 2008, 2012** - End of support
  - **Replacement**: SQL Server 2016+

### Operating Systems
- **Amazon Linux 1 (AMI)** - End of standard support (December 2023)
  - **Replacement**: Amazon Linux 2 or Amazon Linux 2023
  - **Note**: AL2023 is the recommended version

## Recommended Active Services for Migration

### Migration & Modernization (Use These)
- ✅ **AWS Application Migration Service (MGN)** - Primary rehost migration service
- ✅ **AWS Database Migration Service (DMS)** - Database migrations
- ✅ **AWS Migration Evaluator** - TCO assessment and planning
- ✅ **AWS DataSync** - Data transfer service

### Developer Tools (Use These)
- ✅ **Amazon Q Developer and Kiro** - AI-powered code assistance and review (replaces CodeGuru Reviewer)
- ✅ **AWS CodePipeline** - CI/CD orchestration
- ✅ **AWS CodeBuild** - Build service
- ✅ **AWS CodeDeploy** - Deployment automation
- ✅ **AWS CodeArtifact** - Artifact repository

### Storage (Use These)
- ✅ **Amazon S3 with Glacier storage classes** - Use S3 Glacier Instant Retrieval, Flexible Retrieval, or Deep Archive (not standalone Glacier)
- ✅ **Amazon EFS** - Elastic file system
- ✅ **Amazon FSx** - Managed file systems

### Systems Management (Use These)
- ✅ **AWS Systems Manager** - Core systems management (avoid deprecated Change Manager and Incident Manager)
- ✅ **Amazon CloudWatch** - Monitoring and observability
- ✅ **AWS Config** - Configuration management and compliance

## Best Practices for Business Case Generation

1. **Always verify service status** before including in recommendations
2. **Check AWS lifecycle page** for latest deprecation announcements
3. **Recommend current versions** of database engines and operating systems
4. **Use modern alternatives** when legacy services are found in current infrastructure
5. **Include migration notes** when replacing deprecated services
6. **Prefer AWS Application Migration Service (MGN)** over deprecated Migration Hub
7. **Use Amazon Q Developer** instead of CodeGuru Reviewer for code reviews

## Regular Updates Required

This document should be reviewed and updated:
- **Monthly**: Check AWS lifecycle page for new announcements
- **Before major releases**: Verify all service recommendations
- **When errors occur**: Add newly discovered deprecated services

## Additional Resources

- AWS Service Lifecycle: https://aws.amazon.com/products/lifecycle/
- AWS What's New: https://aws.amazon.com/new/
- AWS End of Support Calendar: https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html

---

**Last Updated**: December 4, 2024
**Next Review**: January 2025
**Source**: https://aws.amazon.com/products/lifecycle/ (verified December 2024)
