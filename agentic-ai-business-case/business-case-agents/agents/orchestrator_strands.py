#!/usr/bin/env python3
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from utils.strands_client import StrandsBedrockClient
from utils.data_loader import CustomerDataLoader
from utils.customer_ready_pdf import CustomerReadyPDFGenerator
from utils.markdown_generator import BusinessCaseMarkdownGenerator

# Import individual agents
from agents import (
    data_ingestion_agent,
    company_intelligence_agent,
    industry_benchmark_agent,
    tco_calculation_agent,
    modernization_scenario_agent,
    genai_opportunity_agent,
    security_framework_agent,
    landing_zone_agent,
    financial_modeling_agent,
    risk_assessment_agent,
    productivity_impact_agent,
    report_generation_agent
)

class BusinessCaseOrchestrator:
    """Orchestrates prompt-based agents to generate comprehensive business case with PDF output"""
    
    def __init__(self, customer_data_path: str, output_dir: str = './output'):
        self.customer_data_path = customer_data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Strands client
        from utils.strands_client import StrandsBedrockClient
        self.strands_client = StrandsBedrockClient()
        self.data_loader = CustomerDataLoader(customer_data_path)
        
        # Initialize knowledge base ID
        try:
            import json
            with open('deployment/kb_config.json', 'r') as f:
                kb_config = json.load(f)
                self.kb_id = kb_config.get('bucket_name', 'business-case-kb-us-east-1')
        except:
            self.kb_id = 'business-case-kb-us-east-1'  # Default fallback
        
        # Initialize PDF and Markdown generators
        sample_pdf_path = "/Users/arptsha/Downloads/Business_Case_Hackathon/AnyTech_Partner_data/sample_business_case.pdf"
        self.pdf_generator = CustomerReadyPDFGenerator()
        self.md_generator = BusinessCaseMarkdownGenerator()
        
        # Load customer data
        self.customer_data = self.data_loader.get_all_customer_data()
    
    def run_business_case_generation(self):
        """Execute all agents and generate PDF business case"""
        print("🚀 Starting AWS Business Case Generation with Strands SDK")
        print(f"📁 Customer data: {self.customer_data_path}")
        print(f"📄 Output directory: {self.output_dir}")
        
        # Phase 1: Data Analysis
        print("\n" + "="*50)
        print("PHASE 1: DATA ANALYSIS & INTELLIGENCE")
        print("="*50)
        
        phase1_results = {}
        
        # Data Ingestion
        print("\n→ Data Ingestion Agent...")
        phase1_results['data_ingestion'] = data_ingestion_agent.execute(
            self.strands_client, self.customer_data
        )
        print("✓ Completed")
        
        # Company Intelligence
        print("\n→ Company Intelligence Agent...")
        phase1_results['company_intelligence'] = company_intelligence_agent.execute(
            self.strands_client, self.customer_data
        )
        print("✓ Completed")
        
        # Industry Benchmark
        print("\n→ Industry Benchmark Agent...")
        phase1_results['industry_benchmark'] = industry_benchmark_agent.execute(
            self.strands_client, self.customer_data
        )
        print("✓ Completed")
        
        # Phase 2: Financial Analysis
        print("\n" + "="*50)
        print("PHASE 2: FINANCIAL ANALYSIS")
        print("="*50)
        
        phase2_results = {}
        
        # TCO Calculation
        print("\n→ TCO Calculation Agent...")
        phase2_results['tco_calculation'] = tco_calculation_agent.execute(
            self.strands_client, self.customer_data, phase1_results
        )
        print("✓ Completed")
        
        # Modernization Scenario
        print("\n→ Modernization Scenario Agent...")
        phase2_results['modernization_scenario'] = modernization_scenario_agent.execute(
            self.strands_client, self.customer_data, phase1_results
        )
        print("✓ Completed")
        
        # GenAI Opportunity
        print("\n→ GenAI Opportunity Agent...")
        phase2_results['genai_opportunity'] = genai_opportunity_agent.execute(
            self.strands_client, self.customer_data
        )
        print("✓ Completed")
        
        # Phase 3: Technical Architecture
        print("\n" + "="*50)
        print("PHASE 3: TECHNICAL ARCHITECTURE")
        print("="*50)
        
        phase3_results = {}
        
        # Security Framework
        print("\n→ Security Framework Agent...")
        phase3_results['security_framework'] = security_framework_agent.execute(
            self.strands_client, self.customer_data
        )
        print("✓ Completed")
        
        # Landing Zone Design
        print("\n→ Landing Zone Design Agent...")
        phase3_results['landing_zone'] = landing_zone_agent.execute(
            self.strands_client, self.customer_data
        )
        print("✓ Completed")
        
        # Phase 4: Business Case Finalization
        print("\n" + "="*50)
        print("PHASE 4: BUSINESS CASE FINALIZATION")
        print("="*50)
        
        # Combine all results
        all_results = {**phase1_results, **phase2_results, **phase3_results}
        
        # Financial Modeling
        print("\n→ Financial Modeling Agent...")
        all_results['financial_modeling'] = financial_modeling_agent.execute(
            self.strands_client, self.customer_data, all_results, self.kb_id
        )
        print("✓ Completed")
        
        # Risk Assessment
        print("\n→ Risk Assessment Agent...")
        all_results['risk_assessment'] = risk_assessment_agent.execute(
            self.strands_client, self.customer_data
        )
        print("✓ Completed")
        
        # Productivity Impact
        print("\n→ Productivity Impact Agent...")
        all_results['productivity_impact'] = productivity_impact_agent.execute(
            self.strands_client, self.customer_data
        )
        print("✓ Completed")
        
        # Generate PDF Business Case
        print("\n" + "="*50)
        print("GENERATING BUSINESS CASE REPORTS")
        print("="*50)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate PDF
        pdf_filename = f"business_case_{timestamp}.pdf"
        pdf_path = self.output_dir / pdf_filename
        
        print(f"\n→ Generating PDF: {pdf_filename}")
        self.pdf_generator.generate_customer_ready_pdf(all_results, str(pdf_path), "Customer")
        print("✓ PDF Generated Successfully")
        
        # Generate Markdown
        md_filename = f"business_case_{timestamp}.md"
        md_path = self.output_dir / md_filename
        
        print(f"\n→ Generating Markdown: {md_filename}")
        self.md_generator.generate_business_case(all_results, str(md_path))
        print("✓ Markdown Generated Successfully")
        
        # Save JSON results
        json_filename = f"business_case_data_{timestamp}.json"
        json_path = self.output_dir / json_filename
        
        with open(json_path, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        print(f"\n📄 Business Case PDF: {pdf_path}")
        print(f"📝 Business Case Markdown: {md_path}")
        print(f"📊 Raw Data JSON: {json_path}")
        print("\n✅ Business Case Generation Complete!")
        
        return all_results, str(pdf_path), str(md_path)

def main():
    parser = argparse.ArgumentParser(description='Generate AWS Business Case using Strands SDK')
    parser.add_argument('--customer-data', required=True, help='Path to customer data directory')
    parser.add_argument('--output-dir', default='./output', help='Output directory for results')
    
    args = parser.parse_args()
    
    try:
        orchestrator = BusinessCaseOrchestrator(args.customer_data, args.output_dir)
        results, pdf_path, md_path = orchestrator.run_business_case_generation()
        
        print(f"\n🎉 Success! Business case generated:")
        print(f"   📄 PDF: {pdf_path}")
        print(f"   📝 Markdown: {md_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
