import sys
import os

# Add the agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from migration_plan import read_migration_plan_framework

print("=" * 80)
print("Migration Plan Data Extraction Test")
print("=" * 80)

# Test framework reading
print("\n1. AWS MIGRATION PLAN FRAMEWORK")
print("-" * 80)
try:
    framework = read_migration_plan_framework()
    print(f"✓ Loaded migration plan framework successfully ({len(framework)} characters)")
    print(f"  First 500 characters:")
    print(f"  {framework[:500]}...")
except Exception as e:
    print(f"✗ Error reading framework: {e}")

print("\n" + "=" * 80)
print("Data extraction test completed!")
print("=" * 80)
print("\nNote: Migration plan agent will:")
print("- Analyze all previous agent outputs")
print("- Assess readiness for each phase (Assess, Mobilize, Migrate, Modernize)")
print("- Recommend if further assessment is needed")
print("- Provide detailed phase-specific plans")
