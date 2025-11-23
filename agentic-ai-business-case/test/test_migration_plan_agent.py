import sys
import os

# Add the agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from migration_plan import agent

# Run the migration plan agent
question = """
Analyze all available assessment data and create a comprehensive AWS migration plan.

Consider the following data sources:
- IT Infrastructure Inventory analysis
- RVTool VMware assessment
- ATX VMware assessment
- MRA organizational readiness
- Migration strategy recommendations
- AWS cost analysis

Provide specific recommendations for each phase:
1. ASSESS: Is further assessment needed or are we ready for Mobilize?
2. MOBILIZE: What activities are needed? Timeline? Resources?
3. MIGRATE: Detailed wave-by-wave plan with timeline
4. MODERNIZE: Roadmap and priorities

Include:
- Phase readiness assessment
- Gap analysis
- Risk assessment
- Success metrics
- Next steps and decision points
"""

print("=" * 80)
print("Running Migration Plan Analysis Agent...")
print("=" * 80)

result = agent(question)

print("\n" + "=" * 80)
print("MIGRATION PLAN ANALYSIS RESULTS")
print("=" * 80)
print(result.message)
