import sys
import os

# Add the agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from migration_strategy import agent

# Run the migration strategy agent
question = """
Analyze the available infrastructure data and recommend an optimal migration strategy 
using the AWS 6Rs framework. 

Consider:
- IT Infrastructure Inventory data
- RVTool VMware Assessment data
- ATX VMware Assessment data
- MRA Organizational Readiness data

Provide a comprehensive migration strategy with:
1. Analysis of available data sources
2. Windows Server assessment (check if >20 servers for OLA requirement)
3. Application categorization and 6Rs recommendations
4. Migration wave planning with timelines
5. Cost savings estimates
6. Risk mitigation strategies

If application portfolio assessment is not available, use industry-standard framework 
and clearly state assumptions.
"""

print("=" * 80)
print("Running Migration Strategy Analysis Agent...")
print("=" * 80)

result = agent(question)

print("\n" + "=" * 80)
print("MIGRATION STRATEGY ANALYSIS RESULTS")
print("=" * 80)
print(result.message)
