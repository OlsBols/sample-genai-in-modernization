"""Generate clean markdown business case reports"""
import re
from datetime import datetime

class BusinessCaseMarkdownGenerator:
    """Generate clean, readable markdown business case"""
    
    def generate_business_case(self, agent_results: dict, output_path: str):
        """Generate markdown business case"""
        
        content = self._generate_header()
        
        # Executive Summary
        if 'company_intelligence' in agent_results:
            content += self._format_section("Executive Summary", 
                                          agent_results['company_intelligence'].get('output', ''))
        
        # Technical Assessment
        if 'data_ingestion' in agent_results:
            content += self._format_section("Technical Assessment", 
                                          agent_results['data_ingestion'].get('output', ''))
        
        # Financial Analysis & TCO
        if 'tco_calculation' in agent_results:
            content += self._format_section("Financial Analysis & TCO", 
                                          agent_results['tco_calculation'].get('output', ''))
        
        # Migration Strategy
        if 'modernization_scenario' in agent_results:
            content += self._format_section("Migration Strategy & Modernization", 
                                          agent_results['modernization_scenario'].get('output', ''))
        
        # GenAI Opportunities
        if 'genai_opportunity' in agent_results:
            content += self._format_section("GenAI Innovation Opportunities", 
                                          agent_results['genai_opportunity'].get('output', ''))
        
        # Security Framework
        if 'security_framework' in agent_results:
            content += self._format_section("Security & Compliance Framework", 
                                          agent_results['security_framework'].get('output', ''))
        
        # Risk Assessment
        if 'risk_assessment' in agent_results:
            content += self._format_section("Risk Assessment & Mitigation", 
                                          agent_results['risk_assessment'].get('output', ''))
        
        # Implementation Plan
        if 'landing_zone' in agent_results:
            content += self._format_section("Implementation Roadmap", 
                                          agent_results['landing_zone'].get('output', ''))
        
        # Financial Modeling
        if 'financial_modeling' in agent_results:
            content += self._format_section("Financial Modeling & ROI Analysis", 
                                          agent_results['financial_modeling'].get('output', ''))
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def _generate_header(self) -> str:
        """Generate markdown header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"""# AWS Migration Business Case

**Generated:** {timestamp}  
**Executive Summary & Strategic Analysis**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Technical Assessment](#technical-assessment)
3. [Financial Analysis & TCO](#financial-analysis--tco)
4. [Migration Strategy & Modernization](#migration-strategy--modernization)
5. [GenAI Innovation Opportunities](#genai-innovation-opportunities)
6. [Security & Compliance Framework](#security--compliance-framework)
7. [Risk Assessment & Mitigation](#risk-assessment--mitigation)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Financial Modeling & ROI Analysis](#financial-modeling--roi-analysis)

---

"""
    
    def _format_section(self, title: str, content: str) -> str:
        """Format a section with proper markdown"""
        if not content:
            return ""
        
        # Clean the content
        content = self._clean_content(content)
        
        # Create anchor-friendly title
        anchor = title.lower().replace(' ', '-').replace('&', '').replace('  ', '-')
        
        section = f"\n## {title}\n\n"
        
        # Process content line by line
        lines = content.split('\n')
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    section += "\n"
                    in_list = False
                continue
            
            # Handle headers that are already in markdown format
            if line.startswith('#'):
                if in_list:
                    section += "\n"
                    in_list = False
                # Convert to appropriate level (add one level since we're in a section)
                level = len(line) - len(line.lstrip('#'))
                new_level = min(level + 2, 6)  # Max h6
                section += f"{'#' * new_level} {line.lstrip('# ')}\n\n"
            
            # Handle bullet points
            elif line.startswith(('-', '•', '*')):
                if not in_list:
                    in_list = True
                bullet_text = line[1:].strip()
                section += f"- {bullet_text}\n"
            
            # Handle numbered lists
            elif re.match(r'^\d+\.', line):
                if in_list and not re.match(r'^\d+\.', lines[lines.index(line)-1] if lines.index(line) > 0 else ""):
                    section += "\n"
                in_list = True
                section += f"{line}\n"
            
            # Handle key metrics (lines with $ or %)
            elif ('$' in line or '%' in line or 'ROI' in line) and len(line) < 200:
                if in_list:
                    section += "\n"
                    in_list = False
                section += f"**{line}**\n\n"
            
            # Handle section headers (lines ending with colon)
            elif line.endswith(':') and len(line) < 100:
                if in_list:
                    section += "\n"
                    in_list = False
                section += f"### {line[:-1]}\n\n"
            
            # Regular paragraph
            else:
                if in_list:
                    section += "\n"
                    in_list = False
                section += f"{line}\n\n"
        
        return section + "\n---\n"
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        # Fix common encoding issues
        content = content.replace('â€™', "'")
        content = content.replace('â€œ', '"')
        content = content.replace('â€', '"')
        content = content.replace('â€"', '-')
        
        return content.strip()
