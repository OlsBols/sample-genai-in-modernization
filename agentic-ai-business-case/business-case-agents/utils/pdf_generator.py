import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import json
import re

class BusinessCasePDFGenerator:
    """Generate professional PDF business case"""
    
    def __init__(self, sample_pdf_path: str = None):
        self.sample_pdf_path = sample_pdf_path
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup professional PDF styles"""
        # Check if styles already exist before adding
        style_names = [style.name for style in self.styles.byName.values()]
        
        if 'BusinessTitle' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BusinessTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                spaceBefore=20,
                textColor=colors.HexColor('#1f4e79'),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
        
        if 'BusinessSubtitle' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BusinessSubtitle',
                parent=self.styles['Normal'],
                fontSize=14,
                spaceAfter=30,
                spaceBefore=10,
                textColor=colors.HexColor('#4472c4'),
                alignment=TA_CENTER,
                fontName='Helvetica'
            ))
        
        if 'SectionHeader' not in style_names:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=18,
                spaceBefore=30,
                textColor=colors.HexColor('#1f4e79'),
                fontName='Helvetica-Bold',
                borderWidth=0,
                borderPadding=0,
                backColor=colors.HexColor('#f8f9fa'),
                leftIndent=0,
                rightIndent=0
            ))
        
        if 'SubHeader' not in style_names:
            self.styles.add(ParagraphStyle(
                name='SubHeader',
                parent=self.styles['Heading2'],
                fontSize=13,
                spaceAfter=12,
                spaceBefore=18,
                textColor=colors.HexColor('#2e5090'),
                fontName='Helvetica-Bold'
            ))
        
        if 'BodyText' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                spaceBefore=6,
                alignment=TA_JUSTIFY,
                fontName='Helvetica',
                leading=15,
                leftIndent=0,
                rightIndent=0
            ))
        
        if 'BulletPoint' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BulletPoint',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=8,
                spaceBefore=4,
                leftIndent=20,
                fontName='Helvetica',
                leading=14
            ))
        
        if 'Highlight' not in style_names:
            self.styles.add(ParagraphStyle(
                name='Highlight',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                spaceBefore=8,
                textColor=colors.HexColor('#c5504b'),
                fontName='Helvetica-Bold',
                backColor=colors.HexColor('#fff2f1'),
                borderWidth=1,
                borderColor=colors.HexColor('#c5504b'),
                borderPadding=6,
                leftIndent=10,
                rightIndent=10
            ))
        
    def _process_text_for_pdf(self, text: str) -> list:
        """Process text content for professional PDF formatting"""
        story_elements = []
        
        if not text:
            return story_elements
            
        text = self._clean_text(text)
        
        # Split into paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        for paragraph in paragraphs:
            # Check if it's a numbered list item
            if re.match(r'^\d+\.', paragraph):
                # Split numbered sections
                lines = paragraph.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if re.match(r'^\d+\.', line):
                        # Main numbered item
                        story_elements.append(Paragraph(line, self.styles['SubHeader']))
                        story_elements.append(Spacer(1, 8))
                    elif line.startswith('-'):
                        # Sub-bullet
                        bullet_text = '• ' + line[1:].strip()
                        story_elements.append(Paragraph(bullet_text, self.styles['BulletPoint']))
                    else:
                        # Regular text under numbered item
                        story_elements.append(Paragraph(line, self.styles['BodyText']))
            
            # Check for section headers (short lines ending with colon)
            elif paragraph.endswith(':') and len(paragraph) < 100:
                if any(word in paragraph.lower() for word in 
                      ['summary', 'analysis', 'overview', 'strategy', 'framework', 'assessment', 'recommendations']):
                    story_elements.append(Paragraph(paragraph, self.styles['SectionHeader']))
                    story_elements.append(Spacer(1, 12))
                else:
                    story_elements.append(Paragraph(paragraph, self.styles['SubHeader']))
                    story_elements.append(Spacer(1, 8))
            
            # Check for bullet points
            elif paragraph.startswith(('-', '•', '*')):
                lines = paragraph.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith(('-', '•', '*')):
                        bullet_text = '• ' + line[1:].strip()
                        story_elements.append(Paragraph(bullet_text, self.styles['BulletPoint']))
                    elif line:
                        story_elements.append(Paragraph(line, self.styles['BodyText']))
            
            # Check for key metrics/highlights
            elif ('$' in paragraph or '%' in paragraph or 'ROI' in paragraph or 
                  'savings' in paragraph.lower() or 'cost' in paragraph.lower()) and len(paragraph) < 200:
                story_elements.append(Paragraph(paragraph, self.styles['Highlight']))
                story_elements.append(Spacer(1, 10))
            
            # Regular paragraph - break into sentences if too long
            else:
                if len(paragraph) > 500:
                    # Split long paragraphs into sentences
                    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk + sentence) < 400:
                            current_chunk += sentence + " "
                        else:
                            if current_chunk:
                                story_elements.append(Paragraph(current_chunk.strip(), self.styles['BodyText']))
                            current_chunk = sentence + " "
                    
                    if current_chunk:
                        story_elements.append(Paragraph(current_chunk.strip(), self.styles['BodyText']))
                else:
                    story_elements.append(Paragraph(paragraph, self.styles['BodyText']))
            
            # Add spacing between paragraphs
            story_elements.append(Spacer(1, 10))
        
        return story_elements

    def generate_business_case(self, agent_results: dict, output_path: str):
        """Generate professional PDF business case"""
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=letter,
            leftMargin=0.75*inch, 
            rightMargin=0.75*inch,
            topMargin=1*inch, 
            bottomMargin=1*inch
        )
        story = []
        
        # Title Page
        story.append(Paragraph("AWS Migration Business Case", self.styles['BusinessTitle']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Executive Summary & Strategic Analysis", self.styles['BusinessSubtitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Table of Contents placeholder
        story.append(Paragraph("Table of Contents", self.styles['SectionHeader']))
        toc_items = [
            "1. Executive Summary",
            "2. Technical Assessment", 
            "3. Financial Analysis & TCO",
            "4. Migration Strategy & Modernization",
            "5. GenAI Innovation Opportunities",
            "6. Security & Compliance Framework", 
            "7. Risk Assessment & Mitigation",
            "8. Implementation Roadmap",
            "9. Financial Modeling & ROI Analysis"
        ]
        for item in toc_items:
            story.append(Paragraph(item, self.styles['BodyText']))
        story.append(PageBreak())
        
        # Executive Summary
        if 'company_intelligence' in agent_results:
            story.append(Paragraph("1. Executive Summary", self.styles['SectionHeader']))
            story.append(Spacer(1, 15))
            content = agent_results['company_intelligence'].get('output', '')
            if content:
                story.extend(self._process_text_for_pdf(content))
                story.append(PageBreak())
        
        # Technical Assessment
        if 'data_ingestion' in agent_results:
            story.append(Paragraph("2. Technical Assessment", self.styles['SectionHeader']))
            story.append(Spacer(1, 15))
            content = agent_results['data_ingestion'].get('output', '')
            if content:
                story.extend(self._process_text_for_pdf(content))
                story.append(PageBreak())
        
        # Financial Analysis
        if 'tco_calculation' in agent_results:
            story.append(Paragraph("3. Financial Analysis & TCO", self.styles['SectionHeader']))
            story.append(Spacer(1, 15))
            content = agent_results['tco_calculation'].get('output', '')
            if content:
                story.extend(self._process_text_for_pdf(content))
                story.append(PageBreak())
        
        # Migration Strategy
        if 'modernization_scenario' in agent_results:
            story.append(Paragraph("4. Migration Strategy & Modernization", self.styles['SectionHeader']))
            story.append(Spacer(1, 15))
            content = agent_results['modernization_scenario'].get('output', '')
            if content:
                story.extend(self._process_text_for_pdf(content))
                story.append(PageBreak())
        
        # GenAI Opportunities
        if 'genai_opportunity' in agent_results:
            story.append(Paragraph("5. GenAI Innovation Opportunities", self.styles['SectionHeader']))
            story.append(Spacer(1, 15))
            content = agent_results['genai_opportunity'].get('output', '')
            if content:
                story.extend(self._process_text_for_pdf(content))
                story.append(PageBreak())
        
        # Security Framework
        if 'security_framework' in agent_results:
            story.append(Paragraph("6. Security & Compliance Framework", self.styles['SectionHeader']))
            story.append(Spacer(1, 15))
            content = agent_results['security_framework'].get('output', '')
            if content:
                story.extend(self._process_text_for_pdf(content))
                story.append(PageBreak())
        
        # Risk Assessment
        if 'risk_assessment' in agent_results:
            story.append(Paragraph("7. Risk Assessment & Mitigation", self.styles['SectionHeader']))
            story.append(Spacer(1, 15))
            content = agent_results['risk_assessment'].get('output', '')
            if content:
                story.extend(self._process_text_for_pdf(content))
                story.append(PageBreak())
        
        # Implementation Plan
        if 'landing_zone' in agent_results:
            story.append(Paragraph("8. Implementation Roadmap", self.styles['SectionHeader']))
            story.append(Spacer(1, 15))
            content = agent_results['landing_zone'].get('output', '')
            if content:
                story.extend(self._process_text_for_pdf(content))
                story.append(PageBreak())
        
        # Financial Modeling
        if 'financial_modeling' in agent_results:
            story.append(Paragraph("9. Financial Modeling & ROI Analysis", self.styles['SectionHeader']))
            story.append(Spacer(1, 15))
            content = agent_results['financial_modeling'].get('output', '')
            if content:
                story.extend(self._process_text_for_pdf(content))
        
        doc.build(story)
        return output_path
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common formatting issues
        text = text.replace('â€™', "'")
        text = text.replace('â€œ', '"')
        text = text.replace('â€', '"')
        text = text.replace('â€"', '-')
        
        return text
