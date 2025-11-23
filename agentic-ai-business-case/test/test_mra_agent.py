import sys
import os

# Add the agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from mra_analysis import agent

# Run the MRA analysis agent
question = """
Analyze the Migration Readiness Assessment (MRA) document available in the input folder:
- aws-customer-migration-readiness-assessment.md

Provide a comprehensive analysis covering all readiness dimensions including business, people, 
process, technology, security, operations, and financial readiness. Include gap analysis and 
actionable recommendations for improving migration readiness.
"""

print("=" * 80)
print("Running Migration Readiness Assessment (MRA) Analysis Agent...")
print("=" * 80)

result = agent(question)

print("\n" + "=" * 80)
print("MRA ANALYSIS RESULTS")
print("=" * 80)
print(result.message)
