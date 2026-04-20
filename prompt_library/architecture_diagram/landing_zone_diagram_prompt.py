"""Prompt for generating a Draw.io XML architecture diagram for the AWS Landing Zone.

Reuses the Draw.io XML generation rules from architecture_diagram_prompt.py
and adds landing zone design context derived from the same inputs as the
Landing Zone Agent — enabling parallel execution.
"""

from prompt_library.architecture_diagram.architecture_diagram_prompt import (
    get_architecture_diagram_prompt,
)


def get_landing_zone_diagram_prompt(
    region: str,
    account_strategy: str,
    connectivity: str,
    discovery_json: str,
    dependency_json: str,
    strategy_json: str,
) -> str:
    """Build a prompt for generating a Draw.io XML landing zone architecture diagram.

    Uses the same inputs as the Landing Zone Agent so both can run in parallel.
    The diagram agent independently derives the architecture from the design rules
    embedded in this prompt.

    Args:
        region: Target AWS region (e.g. eu-west-2).
        account_strategy: Account strategy (e.g. Multi-Account).
        connectivity: Network connectivity model (e.g. Hybrid with Direct Connect).
        discovery_json: Serialized JSON of the discovery result.
        dependency_json: Serialized JSON of the dependency result.
        strategy_json: Serialized JSON of the strategy result.

    Returns:
        Full prompt string for the architecture diagram agent.
    """

    # Build a rich description that encodes the landing zone design rules
    description = f"""AWS Landing Zone Architecture for cloud migration.

## INPUTS
- Target Region: {region}
- Account Strategy: {account_strategy}
- Connectivity Model: {connectivity}
- Application Discovery Data: {discovery_json}
- Dependency Analysis Data: {dependency_json}
- Migration Strategy and Wave Plan: {strategy_json}

## LANDING ZONE DESIGN RULES (derive architecture from these)

### Account Structure (OU Hierarchy)
- Root OU at the top
- Security OU: Security account (CloudTrail, GuardDuty, Security Hub, Config), Log Archive account
- Infrastructure OU: Network account (Transit Gateway, Direct Connect/VPN, Route 53), Shared Services account (CI/CD, DNS, artifact repos)
- Workloads OU: Split into Prod and Non-Prod sub-OUs, with workload accounts derived from the application portfolio environments
- Management account at the root level for AWS Organizations and billing

### Network Topology (Hub-Spoke via Transit Gateway)
- Central Transit Gateway in the Network account
- Hub VPC for shared services and connectivity
- Spoke VPCs for each workload environment (Prod, Non-Prod)
- On-premises connectivity via {connectivity}
- Each VPC has: Public subnets (ALB, NAT Gateway), Private subnets (application workloads), Isolated subnets (databases, sensitive data)
- Route 53 private hosted zones for internal DNS resolution
- VPC endpoints for AWS services (S3, DynamoDB, etc.)

### Security Baseline
- AWS CloudTrail organization trail (centralized in Security account)
- Amazon GuardDuty across all accounts
- AWS Security Hub for compliance dashboards
- AWS Config rules for configuration compliance
- Centralized logging to S3 in Log Archive account
- KMS key hierarchy for encryption (per-account keys managed centrally)
- SCPs on each OU for guardrails

### Shared Services
- AWS IAM Identity Center (SSO) for federated access
- Centralized CI/CD pipeline (CodePipeline / CodeBuild)
- Shared container registry (ECR) if container workloads exist
- Centralized monitoring (CloudWatch cross-account dashboards)

### Workload Placement
- Map application groups from the strategy wave plan to workload accounts
- High-criticality apps in dedicated Prod accounts with stricter SCPs
- Non-production environments (Dev, Test, Staging) in Non-Prod accounts
- Shared infrastructure dependencies co-located or connected via Transit Gateway

## CRITICAL LAYOUT RULES — STRICTLY FOLLOW

### Nesting Structure (MANDATORY)
Every AWS service icon MUST be placed INSIDE a container (swimlane). Never place standalone resource icons at the root level.
The nesting hierarchy is:
  Root OU (outermost swimlane, parent="1")
    → OU swimlanes (parent=root-ou)
      → Account swimlanes (parent=ou)
        → Resource icons (parent=account)

### Swimlane Container Style
Use this style for ALL OU and Account containers:
- OUs: style="swimlane;whiteSpace=wrap;html=1;fillColor=<color>;strokeColor=#ffffff;fontColor=#ffffff;fontSize=12;fontStyle=1;"
- Accounts: style="swimlane;whiteSpace=wrap;html=1;fillColor=<lighter-color>;strokeColor=<ou-color>;fontColor=#000000;fontSize=10;"

### Colour Coding
- Security OU / accounts: fillColor=#d32f2f (OU), fillColor=#ffcdd2 (accounts)
- Infrastructure OU / accounts: fillColor=#1976d2 (OU), fillColor=#bbdefb (network), fillColor=#fff3e0 (shared services)
- Workloads OU: fillColor=#388e3c (OU), fillColor=#c8e6c9 (prod accounts), fillColor=#a5d6a7 (non-prod)
- On-Premises: fillColor=#fff2cc;strokeColor=#d6b656
- Management Account: fillColor=#f3e5f5;strokeColor=#7b1fa2

### Spatial Layout (canvas 1400×900)
- Management Account: top-left corner (x=20, y=20, w=200, h=120)
- AWS Organization Root: large container (x=240, y=20, w=1140, h=860)
  - Security OU: top-left inside root (y offset ~40)
  - Infrastructure OU: top-right inside root (y offset ~40)
  - Workloads OU: bottom half inside root (y offset ~360)
    - Production Sub-OU: top row inside Workloads
    - Non-Production Sub-OU: bottom row inside Workloads
- On-Premises: left side, outside AWS root (x=20, y=300)

### Connection Arrows
- On-prem → Direct Connect: strokeColor=#FF6B35, strokeWidth=3
- Direct Connect → Transit Gateway: strokeColor=#1976D2, strokeWidth=3
- Transit Gateway → Workload VPCs: strokeColor=#4CAF50, strokeWidth=2
- Security flows (dashed): strokeColor=#D32F2F, dashed=1
- Use edge="1" with source/target attributes referencing cell IDs

### Resource Icon Sizing
- Primary services: width=50, height=50
- Secondary services inside small containers: width=40, height=40
- Keep spacing of at least 20px between icons inside a container

### DO NOT
- Do NOT place resource icons directly on parent="1" (root canvas) — they must be inside a swimlane container
- Do NOT create a flat horizontal row of icons — always nest inside account/OU containers
- Do NOT mix swimlane containers and standalone icons at the same hierarchy level
"""

    return get_architecture_diagram_prompt(description)
