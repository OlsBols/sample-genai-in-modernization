import sys
import os

# Add the agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from atx_analysis import agent

# Run the ATX analysis agent
question = """
Analyze the AWS Transform for VMware (ATX) assessment outputs available in the input folder:
- analysis.xlsx (VMware environment data and cost analysis)
- business_case.pptx (Executive business case presentation)
- report.pdf (Detailed technical assessment report)

Provide a comprehensive analysis of the VMware environment and AWS migration recommendations 
covering all key aspects for building a business case for VMware to AWS migration.
"""

print("=" * 80)
print("Running AWS Transform for VMware (ATX) Analysis Agent...")
print("=" * 80)

result = agent(question)

print("\n" + "=" * 80)
print("ATX ANALYSIS RESULTS")
print("=" * 80)
print(result.message)
