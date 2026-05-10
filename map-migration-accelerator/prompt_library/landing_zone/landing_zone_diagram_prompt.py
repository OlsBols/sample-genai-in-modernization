def get_landing_zone_diagram_prompt(
    region: str,
    account_strategy: str,
    connectivity: str,
    discovery_json: str,
    dependency_json: str,
    strategy_json: str,
) -> str:
    return f"""You are an expert Draw.io XML generator specialising in AWS Landing Zone architecture diagrams.

Generate a single, complete, valid Draw.io XML file that visualises the AWS Landing Zone described below.

## INPUTS
- Target Region: {region}
- Account Strategy: {account_strategy}
- Connectivity Model: {connectivity}
- Application Discovery Data: {discovery_json}
- Dependency Analysis Data: {dependency_json}
- Migration Strategy and Wave Plan: {strategy_json}

## OUTPUT RULES

### XML Structure
- Start with: <?xml version="1.0" encoding="UTF-8"?>
- Wrap everything in <mxfile> → <diagram> → <mxGraphModel> → <root>
- Always include <mxCell id="0"/> and <mxCell id="1" parent="0"/> as the first two cells
- Escape all special characters properly; replace bare & with &amp;
- Output ONLY the XML — no prose, no markdown fences, no explanations

### Container / Swimlane Hierarchy (MANDATORY)
Every resource icon MUST be nested inside a swimlane container. The nesting order is:

  AWS Organization Root swimlane (parent="1")
    → OU swimlanes (parent=root-ou cell id)
      → Account swimlanes (parent=ou cell id)
        → Resource icon cells (parent=account cell id)

Never place resource icons directly on parent="1".

### Swimlane Container Style
OUs:
  style="swimlane;whiteSpace=wrap;html=1;fillColor=<ou-color>;strokeColor=#ffffff;fontColor=#ffffff;fontSize=12;fontStyle=1;startSize=30;"

Accounts:
  style="swimlane;whiteSpace=wrap;html=1;fillColor=<account-color>;strokeColor=<ou-color>;fontColor=#000000;fontSize=10;startSize=25;"

### Colour Coding
- Management Account:      fillColor=#f3e5f5; strokeColor=#7b1fa2
- AWS Organization Root:   fillColor=#f5f5f5; strokeColor=#666666
- Security OU:             fillColor=#d32f2f (OU), fillColor=#ffcdd2 (accounts)
- Infrastructure OU:       fillColor=#1976d2 (OU), fillColor=#bbdefb (network), fillColor=#fff3e0 (shared services)
- Workloads OU:            fillColor=#388e3c (OU), fillColor=#c8e6c9 (prod accounts), fillColor=#a5d6a7 (non-prod)
- On-Premises block:       fillColor=#fff2cc; strokeColor=#d6b656

### Resource Icon Style
Use this style for ALL AWS service icons inside account swimlanes:
  style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F54749;gradientDirection=north;fillColor=#C7131F;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.<service>"

Set width=50, height=50 for primary services; width=40, height=40 for secondary.
Use verticalLabelPosition=bottom and multi-line labels with &#xa; for line breaks.

### Spatial Layout (canvas 1600 × 1000)
- Management Account:       x=20,  y=20,  w=220, h=100  (top-left, outside root)
- AWS Organization Root:    x=260, y=20,  w=1300, h=960 (large outer container)
  - Security OU:            top-left inside root,  ~y=50, h=280
  - Infrastructure OU:      top-right inside root, ~y=50, h=280
  - Workloads OU:           bottom half inside root, ~y=350, h=580
    - Production Sub-OU:    top row inside Workloads
    - Non-Production Sub-OU: bottom row inside Workloads
- On-Premises block:        x=20, y=350, w=220, h=200  (left side, outside root)

### Connection Arrows
- On-prem → connectivity gateway:         strokeColor=#FF6B35; strokeWidth=3
- Connectivity gateway → Transit Gateway: strokeColor=#1976D2; strokeWidth=3
- Transit Gateway → Workload VPCs:        strokeColor=#4CAF50; strokeWidth=2
- Security/audit flows (dashed):          strokeColor=#D32F2F; dashed=1; strokeWidth=1
- All edges: edge="1" with explicit source and target cell id attributes

### Account and Resource Content
Derive the account names and resource icons from the inputs above:
- Security OU accounts: Security account (CloudTrail, GuardDuty, Security Hub, AWS Config), Log Archive account (S3, CloudWatch Logs)
- Infrastructure OU accounts: Network account (Transit Gateway, Direct Connect/VPN, Route 53), Shared Services account (IAM Identity Center, CodePipeline, ECR, CloudWatch)
- Workloads OU: create Prod and Non-Prod sub-OUs; populate workload accounts from the application portfolio in the discovery data; group by migration wave from the strategy data
- Management account: AWS Organizations, Cost Explorer, AWS Budgets

Generate the complete Draw.io XML now."""
