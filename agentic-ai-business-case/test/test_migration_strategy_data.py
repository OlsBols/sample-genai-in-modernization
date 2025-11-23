import sys
import os

# Add the agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from migration_strategy import read_migration_strategy_framework, read_portfolio_assessment

print("=" * 80)
print("Migration Strategy Data Extraction Test")
print("=" * 80)

# Test framework reading
print("\n1. AWS 6Rs MIGRATION STRATEGY FRAMEWORK")
print("-" * 80)
try:
    framework = read_migration_strategy_framework()
    print(f"✓ Loaded migration strategy framework successfully ({len(framework)} characters)")
    print(f"  First 500 characters:")
    print(f"  {framework[:500]}...")
except Exception as e:
    print(f"✗ Error reading framework: {e}")

# Test portfolio assessment reading (if available)
print("\n2. APPLICATION PORTFOLIO ASSESSMENT")
print("-" * 80)
try:
    portfolio = read_portfolio_assessment("application-portfolio.csv")
    print(f"✓ Loaded application portfolio successfully")
    print(f"  First 500 characters:")
    print(f"  {portfolio[:500]}...")
except Exception as e:
    print(f"✗ Portfolio assessment not available: {e}")
    print(f"  (This is expected if the file doesn't exist)")
    print(f"  Agent will use industry-standard framework as fallback")

print("\n" + "=" * 80)
print("Data extraction test completed!")
print("=" * 80)
print("\nNote: Migration strategy agent will:")
print("- Use portfolio assessment if available")
print("- Fall back to industry-standard 6Rs framework if not available")
print("- Clearly state assumptions and recommend conducting portfolio assessment")
