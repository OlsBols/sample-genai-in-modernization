import sys
import os

# Add the agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from mra_analysis import read_docx_file, read_markdown_file

print("=" * 80)
print("Migration Readiness Assessment (MRA) Data Extraction Test")
print("=" * 80)

# Test Markdown file
print("\n1. MRA MARKDOWN FILE")
print("-" * 80)
try:
    md_content = read_markdown_file("aws-customer-migration-readiness-assessment.md")
    print(f"✓ Loaded MRA Markdown file successfully ({len(md_content)} characters)")
    print(f"  First 500 characters:")
    print(f"  {md_content[:500]}...")
except Exception as e:
    print(f"✗ Error reading MRA Markdown: {e}")

# Test Word document (if available)
print("\n2. MRA WORD DOCUMENT")
print("-" * 80)
try:
    docx_content = read_docx_file("Example Customer MRA Summary v2.docx")
    print(f"✓ Loaded MRA Word document successfully ({len(docx_content)} characters)")
    print(f"  First 500 characters:")
    print(f"  {docx_content[:500]}...")
except Exception as e:
    print(f"✗ Error reading MRA Word document: {e}")
    print(f"  (This is expected if the .docx file doesn't exist)")

print("\n" + "=" * 80)
print("Data extraction test completed!")
print("=" * 80)
